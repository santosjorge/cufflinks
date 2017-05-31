
"""

QuantFigure allows you to create a persistent object. 
Annotations and Technical Studies can be added on demand. 

It accepts any dataframe with a timeseries index. 

Try it out:
	qf=cf.QuantFig(cf.datagen.ohlc())
	qf.iplot()

"""

from __future__ import absolute_import

import json
import copy
import pandas as pd

from . import tools
from . import ta
from . import utils
from . import colors
from . import auth
from . import date_tools

__QUANT_FIGURE_DATA = ['kind','showlegend','datalegend','name','slice','resample','bestfit',
						'text','title','yTitle','secondary_y_title','bestfit_colors','kind',
						'colorscale','xTitle','colors','secondary_y']
__QUANT_FIGURE_LAYOUT = ['annotations','showlegend','margin','rangeselector','rangeslider','shapes',
						 'width','height','dimensions']
__QUANT_FIGURE_THEME = ['theme','up_color','down_color']
__QUANT_FIGURE_PANELS = ['min_panel_size','spacing','top_margin','bottom_margin']

def get_layout_kwargs():
	return tools.__LAYOUT_KWARGS
def get_annotation_kwargs():
	return tools.__ANN_KWARGS
def get_shapes_kwargs(): return tools.__SHAPES_KWARGS

class QuantFig(object):
	
	def __init__(self,df,kind='candlestick',columns=None,**kwargs):
		self.df=df
		self.studies={}
		self.data={}
		self.theme={}
		self.panels={}
		self.layout={}
		self.trendlines=[]
		self.kwargs={}

		# Set column names
		if not columns:
			columns={}
			for _ in ['open','high','low','close','volume']:
				columns[_]=kwargs.pop(_,'')
		self._d=ta._ohlc_dict(df,**columns)
		
		# Set initial annotations
		annotations={
			'values':[],
			'params':utils.check_kwargs(kwargs,get_annotation_kwargs(),{},clean_origin=True)
		}

		ann_values=kwargs.pop('annotations',None)
		
		if ann_values:
			if utils.is_list(ann_values):
				annotations['values'].extend(ann_values)
			else:
				annotations['values'].append(ann_values)

		# self.data initial values 
		self.data.update(datalegend=kwargs.pop('datalegend',True),name=kwargs.pop('name','Trace 1'),kind=kind)
		self.data.update(slice=kwargs.pop('slice',(None,None)),resample=kwargs.pop('resample',None))

		# self.layout initial values
		self.layout['shapes']=utils.check_kwargs(kwargs,get_shapes_kwargs(),{},clean_origin=True)
		for k,v in list(self.layout['shapes'].items()):
			if not isinstance(v,list):
				self.layout['shapes'][k]=[v]
		self.layout['rangeselector']=kwargs.pop('rangeselector',{'visible':False})
		self.layout['rangeslider']=kwargs.pop('rangeslider',False) 
		self.layout['margin']=kwargs.pop('margin',dict(t=30,b=30,r=30,l=30))
		self.layout['annotations']=annotations
		self.layout['showlegend']=kwargs.pop('showlegend',True)
		self.layout.update(utils.check_kwargs(kwargs,get_layout_kwargs(),{},clean_origin=True))
		
		# self.theme initial values
		self.theme['theme']=kwargs.pop('theme',auth.get_config_file()['theme'])
		self.theme['up_color']=kwargs.pop('up_color','java')
		self.theme['down_color']=kwargs.pop('down_color','grey')
		
		# self.panels initial values
		self.panels['min_panel_size']=kwargs.pop('min_panel_size',.15)
		self.panels['spacing']=kwargs.pop('spacing',.08)
		self.panels['top_margin']=kwargs.pop('top_margin',0.9)
		self.panels['bottom_margin']=kwargs.pop('top_margin',0)
		self.update(**kwargs)


	def _get_schema(self):
		"""
		Returns a dictionary with the schema for a QuantFigure

		"""
		d={}
		layout_kwargs=dict((_,'') for _ in get_layout_kwargs())
		for _ in ('data','layout','theme','panels'):
			d[_]={}
			for __ in eval('__QUANT_FIGURE_{0}'.format(_.upper())):
				layout_kwargs.pop(__,None)
				d[_][__]=None
		d['layout'].update(annotations=dict(values=[],
											params=utils.make_dict_from_list(get_annotation_kwargs())))
		d['layout'].update(shapes=utils.make_dict_from_list(get_shapes_kwargs()))
		[layout_kwargs.pop(_,None) for _ in get_annotation_kwargs()+get_shapes_kwargs()]
		d['layout'].update(**layout_kwargs)
		return d

	def _get_sliced(self,slice,df=None):
		"""
		Returns a sliced DataFrame

		Parameters
		----------
			slice : tuple(from,to)
				from : str
				to : str
					States the 'from' and 'to' values which 
					will get rendered as df.ix[from:to]
			df : DataFrame
				If omitted then the QuantFigure.DataFrame is resampled.
		"""

		df=self.df.copy() if df==None else df
		if type(slice) not in (list,tuple):
			raise Exception('Slice must be a tuple two values')
		if len(slice)!=2:
			raise Exception('Slice must be a tuple two values')
		a,b=slice
		a=None if a in ('',None) else utils.make_string(a)
		b=None if b in ('',None) else utils.make_string(b)
		return df.ix[a:b]

	def _get_resampled(self,rule,how={'ohlc':'last','volume':'sum'},df=None,**kwargs):
		"""
		Returns a resampled DataFrame

		Parameters
		----------
			rule : str
				the offset string or object representing target conversion
				for all aliases available see http://pandas.pydata.org/pandas-docs/stable/timeseries.html#offset-aliases
			how : str or dict
				states the form in which the resampling will be done.
				Examples:
					how={'volume':'sum'}
					how='count'
			df : DataFrame
				If omitted then the QuantFigure.DataFrame is resampled.
			kwargs
				For more information see http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.resample.html

		"""
		df=self.df.copy() if df is None else df
		if rule==None:
			return df 
		else:
			if isinstance(how,dict):
				if 'ohlc' in how:
					v=how.pop('ohlc')
					for _ in ['open','high','low','close']: 
						how[_]=v
				_how=how.copy()
				for _ in _how:
					if _ not in self._d:
						del how[_]
			return df.resample(rule=rule,**kwargs).apply(how)

	def update(self,**kwargs):
		"""
		Updates the values for a QuantFigure
		The key-values are automatically assigned to the correct 
		section of the QuantFigure
		"""
		if 'columns' in kwargs:
			self._d=ta._ohlc_dict(self.df,columns=kwargs.pop('columns',None))
		schema=self._get_schema()
		annotations=kwargs.pop('annotations',None)

		if annotations:
			self.layout['annotations']['values']=utils.make_list(annotations)
		for k,v in list(kwargs.items()):
			try:
				utils.dict_update(self.__dict__,k,v,schema)
			except:
				self.kwargs.update({k:v})

	def delete(self,*args):
		"""
		Deletes the values for a QuantFigure
		The key-values are automatically deleted from the correct 
		section of the QuantFigure
		"""
		if args:
			args=args[0] if utils.is_list(args[0]) else args
			path=utils.dict_path(self.__dict__)
			for _ in args:
				if _ in self.__dict__.keys():
					raise Exception('"{0}" cannot be deleted'.format(_))

			for a in args:
				try:
					if a in ('shapes'):
						self.layout[a].clear()
					elif a=='annotations':
						self.layout['annotations']={'values':[],'params':{}}
					else:
						del reduce(dict.get, path[a],self.__dict__)[a]
				except:
					raise Exception('Key: {0} not found'.format(a))

	
	def figure(self,**kwargs):
		"""
		
		Returns a Plotly figure

		"""
		kwargs['asFigure']=True
		return self.iplot(**kwargs)
	
	def _panel_domains(self,n=2,min_panel_size=.15,spacing=0.08,top_margin=1,bottom_margin=0):
		"""
		
		Returns the panel domains for each axis

		"""
		d={}
		for _ in range(n+1,1,-1):
			lower=round(bottom_margin+(min_panel_size+spacing)*(n+1-_),2)
			d['yaxis{0}'.format(_)]=dict(domain=(lower,lower+min_panel_size))
		top=d['yaxis2']['domain']
		d['yaxis2']['domain']=(top[0],top_margin)
		return d
	
	def _get_trendline(self,date0=None,date1=None,on=None,kind='trend',to_strfmt='%Y-%m-%d',from_strfmt='%d%b%y',**kwargs):
		"""
		Returns a trendline (line), support or resistance

		Parameters:
			date0 : string
				Trendline starting date			
			date1 :  string
				Trendline end date
			on : string
				Indicate the data series in which the 
				trendline should be based.
					'close'
					'high'
					'low'
					'open'			
			kind : string
				Defines de kind of trendline
					'trend'
					'resistance'
					'support'			
			mode : string
				Defines how the support/resistance will 
				be drawn
					'starttoened' : (x0,x1)
					'fromstart' : (x0,date0)
					'toend'	: (date0,x1)
			text : string
				If passed, then an annotation will be added 
				to the trendline (at mid point)
			from_strfmt : string
				Defines the date formating in which 
				date0 and date1 are stated. 
				default: '%d%b%y'				
			to_strfmt : string
				Defines the date formatting 
				to which it should be converted. 
				This should match the same format as the timeseries index. 
				default : '%Y-%m-%d'		
		"""
		ann_values=copy.deepcopy(get_annotation_kwargs())
		ann_values.extend(['x','y'])
		ann_kwargs=utils.check_kwargs(kwargs,ann_values,{},clean_origin=True)
		def position(d0,d1):
			return d0+(d1-d0)/2

		date0=kwargs.pop('date',date0)    
		date0=date_tools.stringToString(date0,from_strfmt,to_strfmt) if '-' not in date0 else date0
		
		if kind=='trend':
			date1=date_tools.stringToString(date1,from_strfmt,to_strfmt) if '-' not in date1 else date1
			on='close' if not on else on
			df=pd.DataFrame(self.df[self._d[on]])
			y0=kwargs.get('y0',df.ix[date0].values[0])
			y1=kwargs.get('y1',df.ix[date1].values[0])
			
		
		if kind in ('support','resistance'):
			mode=kwargs.pop('mode','starttoend')
			if not on:
				on='low' if kind=='support' else 'high'
			df=pd.DataFrame(self.df[self._d[on]])
			y0=kwargs.get('y0',df.ix[date0].values[0])
			y1=kwargs.get('y1',y0)
			if mode=='starttoend':
				date0=df.index[0]
				date1=df.index[-1]
			elif mode=='toend':
				date1=df.index[-1]
			elif mode=='fromstart':
				date1=date0
				date0=df.index[0]

		if isinstance(date0,pd.tslib.Timestamp):
			date0=date_tools.dateToString(date0,to_strfmt)
		if isinstance(date1,pd.tslib.Timestamp):
			date1=date_tools.dateToString(date1,to_strfmt)
		d={'x0':date0,'x1':date1,'y0':y0,'y1':y1}
		d.update(**kwargs)
		shape=tools.get_shape(**d)        

		
		if ann_kwargs.get('text',False):
			ann_kwargs['x']=ann_kwargs.get('x',date_tools.dateToString(position(date_tools.stringToDate(date0,to_strfmt),date_tools.stringToDate(date1,to_strfmt)),to_strfmt))
			ann_kwargs['y']=ann_kwargs.get('y',position(shape['y0'],shape['y1']))
		else:
			ann_kwargs={}
		return {'shape':shape,'annotation':ann_kwargs}

	def add_trendline(self,date0,date1,on='close',text=None,**kwargs):
		"""
		Adds a trendline to the QuantFigure. 
		Given 2 dates, the trendline is connected on the data points
		that correspond to those dates. 

		Parameters:
			date0 : string
				Trendline starting date
			date1 :  string
				Trendline end date
			on : string
				Indicate the data series in which the 
				trendline should be based.
					'close'
					'high'
					'low'
					'open'
			text : string
				If passed, then an annotation will be added 
				to the trendline (at mid point)

		kwargs:
			from_strfmt : string
				Defines the date formating in which 
				date0 and date1 are stated. 
				default: '%d%b%y'					
			to_strfmt : string
				Defines the date formatting 
				to which it should be converted. 
				This should match the same format as the timeseries index. 
				default : '%Y-%m-%d'		
		"""
		d={'kind':'trend','date0':date0,'date1':date1,'on':on,'text':text}
		d.update(**kwargs)
		self.trendlines.append(d)

	def add_support(self,date,on='low',mode='starttoend',text=None,**kwargs):
		"""
		Adds a support line to the QuantFigure

		Parameters:
			date0 : string
				The support line will be drawn at the 'y' level 
				value that corresponds to this date. 
			on : string
				Indicate the data series in which the 
				support line should be based.
					'close'
					'high'
					'low'
					'open'
			mode : string
				Defines how the support/resistance will 
				be drawn
					'starttoened' : (x0,x1)
					'fromstart' : (x0,date)
					'toend' : (date,x1)
			text : string
				If passed, then an annotation will be added 
				to the support line (at mid point)
		
		kwargs:	
			from_strfmt : string
				Defines the date formating in which 
				date0 and date1 are stated. 
				default: '%d%b%y'					
			to_strfmt : string
				Defines the date formatting 
				to which it should be converted. 
				This should match the same format as the timeseries index. 
				default : '%Y-%m-%d'		
		"""
		d={'kind':'support','date':date,'mode':mode,'on':on,'text':text}
		d.update(**kwargs)
		self.trendlines.append(d)

	def add_resistance(self,date,on='high',mode='starttoend',text=None,**kwargs):
		"""
		Adds a resistance line to the QuantFigure

		Parameters:
			date0 : string
				The resistance line will be drawn at the 'y' level 
				value that corresponds to this date. 
			on : string
				Indicate the data series in which the 
				resistance should be based.
					'close'
					'high'
					'low'
					'open'
			mode : string
				Defines how the support/resistance will 
				be drawn
					'starttoened' : (x0,x1)
					'fromstart' : (x0,date)
					'toend' : (date,x1)
			text : string
				If passed, then an annotation will be added 
				to the resistance (at mid point)
		
		kwargs:	
			from_strfmt : string
				Defines the date formating in which 
				date0 and date1 are stated. 
				default: '%d%b%y'					
			to_strfmt : string
				Defines the date formatting 
				to which it should be converted. 
				This should match the same format as the timeseries index. 
				default : '%Y-%m-%d'		
		"""
		d={'kind':'resistance','date':date,'mode':mode,'on':on,'text':text}
		d.update(**kwargs)
		self.trendlines.append(d)

	def add_annotations(self,annotations,**kwargs):
		"""
		Add an annotation to the QuantFigure. 

		Parameters:
			annotations : dict or list(dict,)
				Annotations can be on the form form of 
					{'date' : 'text'}
					and the text will automatically be placed at the 
					right level on the chart 
				or
					A Plotly fully defined annotation

		kwargs : 
			fontcolor : str
				Text color for annotations
			fontsize : int
				Text size for annotations
			textangle : int
				Textt angle 
			See https://plot.ly/python/reference/#layout-annotations 
			for a complete list of valid parameters.

		"""
		ann_kwargs=utils.check_kwargs(kwargs,get_annotation_kwargs(),{},clean_origin=True)
		if type(annotations)==list:
			self.layout['annotations']['values'].extend(annotations)
		else:
			self.layout['annotations']['values'].append(annotations)
		if ann_kwargs:
			self.layout['annotations']['params'].update(**ann_kwargs)

	def add_shapes(self,**kwargs):
		"""
		Add a shape to the QuantFigure. 

		kwargs : 
			hline : int, list or dict
				Draws a horizontal line at the
				indicated y position(s)
				Extra parameters can be passed in
				the form of a dictionary (see shapes)
			vline : int, list or dict
				Draws a vertical line at the
				indicated x position(s)
				Extra parameters can be passed in
				the form of a dictionary (see shapes)
			hspan : (y0,y1)
				Draws a horizontal rectangle at the
				indicated (y0,y1) positions.
				Extra parameters can be passed in
				the form of a dictionary (see shapes)
			vspan : (x0,x1)
				Draws a vertical rectangle at the
				indicated (x0,x1) positions.
				Extra parameters can be passed in
				the form of a dictionary (see shapes)
			shapes : dict or list(dict)
				List of dictionaries with the
				specifications of a given shape.
				See help(cufflinks.tools.get_shape)
				for more information
			
		"""
		kwargs=utils.check_kwargs(kwargs,get_shapes_kwargs(),{},clean_origin=True)
		for k,v in list(kwargs.items()):
			if k in self.layout['shapes']:
				if utils.is_list(v):
					self.layout['shapes'][k].extend(v)	
				else:
					self.layout['shapes'][k].append(v)
			else:
				self.layout['shapes'][k]=utils.make_list(v)

	# def add_study(self,name,params={}):
	# 	if 'kind' in params:
	# 			if params['kind'] in self._valid_studies:
	# 				self.studies[name]=params
	# 			else:
	# 				raise Exception('Invalid study: {0}'.format(params['kind']))
	# 	else:
	# 		raise Exception('Study kind required')

	def _add_study(self,study):
		"""
		Adds a study to QuantFigure.studies

		Parameters:
			study : dict
				{'kind':study_kind,
				 'params':study_parameters,
				 'display':display_parameters}
		"""
		str='{study} {name}({period})' if study['params'].get('str',None)==None else study['params']['str']
		study['params']['str']=str

		if not study['name']:
			study['name']=ta.get_column_name(study['kind'].upper(),study=study['kind'],
												str=str,
												period=study['params'].get('periods',None),
												column=study['params'].get('column',None))
				

		restore=study['display'].pop('restore',False)
		
		if restore:
			_=self.studies.pop(study['kind'],None)

		if study['kind'] in self.studies:
			try:
				id='{0} ({1})'.format(study['kind'],study['params']['periods'])
			except:
				id='{0} ({1})'.format(study['kind'],'(2)')
		else:
			id=study['kind']

		_id=id
		n=1
		while id in self.studies:
			id='{0} ({1})'.format(_id,n)
			n+=1
		self.studies[id]=study
	   
	def add_volume(self,colorchange=True,column=None,name='',str='{name}',**kwargs):
		"""
		Add 'volume' study to QuantFigure.studies

		Parameters:
			colorchange : bool
				If true then each volume bar will have a fill color 
				depending on if 'base' had a positive or negative
				change compared to the previous value
			column :string
				Defines the data column name that contains the volume data. 
				Default: 'volume'
			name : string
				Name given to the study
			str : string
				Label factory for studies
				The following wildcards can be used:
					{name} : Name of the column
					{study} : Name of the study
					{period} : Period used
				Examples:
					'study: {study} - period: {period}'
			
		kwargs : 
			base : string
				Defines the column which will define the
				positive/negative changes (if colorchange=True).
				Default = 'close'
			up_color : string
				Color for positive bars
			down_color : string
				Color for negative bars
		"""
		if not column:
			column=self._d['volume']
		up_color=kwargs.pop('up_color',self.theme['up_color'])
		down_color=kwargs.pop('down_color',self.theme['down_color'])
		study={'kind':'volume',
			   'name':name,
			   'params':{'changecolor':True,'base':'close','column':column,
						 'str':None},
			  'display':utils.merge_dict({'up_color':up_color,'down_color':down_color},kwargs)}
		self._add_study(study)

	def add_macd(self,fast_period=12,slow_period=26,signal_period=9,column=None,
				 name='',str=None,**kwargs):
		"""
		Add Moving Average Convergence Divergence (MACD) study to QuantFigure.studies

		Parameters:
			fast_period : int
				MACD Fast Period
			slow_period : int
				MACD Slow Period
			signal_period : int
				MACD Signal Period
			column :string
				Defines the data column name that contains the 
				data over which the study will be applied. 
				Default: 'close'
			name : string
				Name given to the study
			str : string
				Label factory for studies
				The following wildcards can be used:
					{name} : Name of the column
					{study} : Name of the study
					{period} : Period used
				Examples:
					'study: {study} - period: {period}'
		kwargs: 
			legendgroup : bool
				If true, all legend items are grouped into a 
				single one
			All formatting values available on iplot()
		"""

		if not column:
			column=self._d['close']
		study={'kind':'macd',
			   'name':name,
			   'params':{'fast_period':fast_period,'slow_period':slow_period,
						 'signal_period':signal_period,'column':column,
						 'str':str},
			  'display':utils.merge_dict({'legendgroup':False,'colors':['blue','red']},kwargs)}
		study['params']['periods']='[{0},{1},{2}]'.format(fast_period,slow_period,signal_period)
		self._add_study(study)

	
	def add_sma(self,periods=20,column=None,name='',
					str=None,**kwargs):
		"""
		Add Simple Moving Average (SMA) study to QuantFigure.studies

		Parameters:
			periods : int or list(int)
				Number of periods
			column :string
				Defines the data column name that contains the 
				data over which the study will be applied. 
				Default: 'close'
			name : string
				Name given to the study
			str : string
				Label factory for studies
				The following wildcards can be used:
					{name} : Name of the column
					{study} : Name of the study
					{period} : Period used
				Examples:
					'study: {study} - period: {period}'
		kwargs: 
			legendgroup : bool
				If true, all legend items are grouped into a 
				single one
			All formatting values available on iplot()
		"""
		if not column:
			column=self._d['close']
		study={'kind':'sma',
			   'name':name,
			   'params':{'periods':periods,'column':column,
						 'str':str},
			  'display':utils.merge_dict({'legendgroup':False},kwargs)}
		self._add_study(study)
		
	def add_rsi(self,periods=20,rsi_upper=70,rsi_lower=30,showbands=True,column=None,
						   name='',str=None,**kwargs):
		"""
		Add Relative Strength Indicator (RSI) study to QuantFigure.studies

		Parameters:
			periods : int or list(int)
				Number of periods
			rsi_upper : int 
				bounds [0,100]
				Upper (overbought) level
			rsi_lower : int
				bounds [0,100]
				Lower (oversold) level
			showbands : boolean
				If True, then the rsi_upper and
				rsi_lower levels are displayed
			column :string
				Defines the data column name that contains the 
				data over which the study will be applied. 
				Default: 'close'
			name : string
				Name given to the study
			str : string
				Label factory for studies
				The following wildcards can be used:
					{name} : Name of the column
					{study} : Name of the study
					{period} : Period used
				Examples:
					'study: {study} - period: {period}'
		kwargs: 
			legendgroup : bool
				If true, all legend items are grouped into a 
				single one
			All formatting values available on iplot()
		"""
		if not column:
			column=self._d['close']
		str=str if str else '{name}({column},{period})'

		study={'kind':'rsi',
			   'name':name,
			   'params':{'periods':periods,'column':column,
						 'str':str},
			  'display':utils.merge_dict({'legendgroup':True,'rsi_upper':rsi_upper,
						 'rsi_lower':rsi_lower,'showbands':showbands},kwargs)}
		self._add_study(study)
	
	def add_bollinger_bands(self,periods=20,boll_std=2,fill=True,column=None,name='',
						   str='{name}({column},{period})',**kwargs):
		"""
		Add Bollinger Bands (BOLL) study to QuantFigure.studies

		Parameters:
			periods : int or list(int)
				Number of periods
			boll_std : int
				Number of standard deviations for
				the bollinger upper and lower bands
			fill : boolean
				If True, then the innner area of the 
				bands will filled
			column :string
				Defines the data column name that contains the 
				data over which the study will be applied. 
				Default: 'close'
			name : string
				Name given to the study
			str : string
				Label factory for studies
				The following wildcards can be used:
					{name} : Name of the column
					{study} : Name of the study
					{period} : Period used
				Examples:
					'study: {study} - period: {period}'
		kwargs: 
			legendgroup : bool
				If true, all legend items are grouped into a 
				single one
			fillcolor : string
				Color to be used for the fill color.
				Example:
					'rgba(62, 111, 176, .4)'
			All formatting values available on iplot()
		"""
		if not column:
			column=self._d['close']
		study={'kind':'boll',
			   'name':name,
			   'params':{'periods':periods,'boll_std':boll_std,'column':column,
						'str':str},
			  'display':utils.merge_dict({'legendgroup':True,'fill':fill},kwargs)}
		self._add_study(study)

	def add_ema(self,periods=20,column=None,str=None,
						   name='',**kwargs):
		"""
		Add Exponential Moving Average (EMA) study to QuantFigure.studies

		Parameters:
			periods : int or list(int)
				Number of periods
			column :string
				Defines the data column name that contains the 
				data over which the study will be applied. 
				Default: 'close'
			name : string
				Name given to the study
			str : string
				Label factory for studies
				The following wildcards can be used:
					{name} : Name of the column
					{study} : Name of the study
					{period} : Period used
				Examples:
					'study: {study} - period: {period}'
		kwargs: 
			legendgroup : bool
				If true, all legend items are grouped into a 
				single one
			All formatting values available on iplot()
		"""
		if not column:
			column=self._d['close']
		study={'kind':'ema',
			   'name':name,
			   'params':{'periods':periods,'column':column,
						 'str':str},
			  'display':utils.merge_dict({'legendgroup':False},kwargs)}
		self._add_study(study)

	def add_atr(self,periods=14,high='high',low='low',close='close',str=None,
					name='',**kwargs):
		"""
		Add Average True Range (ATR) study to QuantFigure.studies

		Parameters:
			periods : int or list(int)
				Number of periods
			high : string
				Column that defines the high value
			low : string
				Column that defines the low value
			close : string
				Column that defines the close value
			column :string
				Defines the data column name that contains the 
				data over which the study will be applied. 
				Default: 'close'
			name : string
				Name given to the study
			str : string
				Label factory for studies
				The following wildcards can be used:
					{name} : Name of the column
					{study} : Name of the study
					{period} : Period used
				Examples:
					'study: {study} - period: {period}'
		kwargs: 
			legendgroup : bool
				If true, all legend items are grouped into a 
				single one
			All formatting values available on iplot()
		"""
		study={'kind':'atr',
			   'name':name,
			   'params':{'periods':periods,'high':high,'low':low,'close':close,
						 'str':str},
			  'display':utils.merge_dict({'legendgroup':False},kwargs)}
		self._add_study(study)		
			
	def add_cmci(self):
		pass

	def add_trender(self):
		pass

	def add_dmi(self):
		pass

	def add_ptps(self):
		pass

	def add_stochastic(self):
		pass

	def _get_study_figure(self,study_id,**kwargs):
		study=copy.deepcopy(self.studies[study_id])
		kind=study['kind']
		display=study['display']
		display['theme']=display.get('theme',self.theme['theme'])
		params=study['params']
		name=study['name']
		params.update(include=False)
		local_kwargs={}
		_slice=kwargs.pop('slice',self.data.get('slice',(None,None)))
		_resample=kwargs.pop('resample',self.data.get('resample',None))
		
		df=self._get_sliced(_slice).copy()
		if _resample:
			if utils.is_list(_resample):
				df=self._get_resampled(*_resample,df=df)
			elif utils.is_dict(_resample):
				_resample.update(df=df)
				df=self._get_resampled(**_resample)
			else:
				df=self._get_resampled(_resample,df=df)
		
		def get_params(locals_list,params,display,append_study=True):
			locals_list.append('legendgroup')
			local_kwargs=utils.check_kwargs(display,locals_list,{},True)
			display.update(kwargs)
			if append_study:
				display=dict([('study_'+k,v) for k,v in display.items()])
			params.update(display)
			return local_kwargs,params
 
		if kind=='volume':
			bar_colors=[]
			local_kwargs,params=get_params([],params,display,False)
			base=df[self._d[params['base']]]
			up_color=colors.normalize(display['up_color']) if 'rgba' not in display['up_color'] else display['up_color']
			down_color=colors.normalize(display['down_color']) if 'rgba' not in display['down_color'] else display['down_color']
			study_kwargs=utils.kwargs_from_keyword(kwargs,{},'study')

			for i in range(len(base)):
				if i != 0:
					if base[i] > base[i-1]:
						bar_colors.append(up_color)
					else:
						bar_colors.append(down_color)
				else:
					bar_colors.append(down_color)
			fig=df[params['column']].figure(kind='bar',theme=params['theme'],**kwargs)
			fig.data[0].update(marker=dict(color=bar_colors,line=dict(color=bar_colors)),
					  opacity=0.8)

		if kind in ('sma','ema','atr'):
			local_kwargs,params=get_params([],params,display)
			fig=df.ta_figure(study=kind,**params)

		if kind=='boll':
			local_kwargs,params=get_params(['fill','fillcolor'],params,display)
			fig=df.ta_figure(study=kind,**params)
			if local_kwargs['fill']:
				fillcolor=local_kwargs.pop('fillcolor',fig.data[2].line.get('color','rgba(200,200,200,.1)'))
				fillcolor=colors.to_rgba(fillcolor,.1)
				fig.data[2].update(fill='tonexty',fillcolor=fillcolor)
		
		if kind=='rsi':
			locals_list=['rsi_lower','rsi_upper','showbands']
			local_kwargs,params=get_params(locals_list,params,display)
			fig=df.ta_figure(study=kind,**params)
			del fig.layout['shapes']
			if local_kwargs['showbands']:
				up_color=kwargs.get('up_color',self.theme['up_color'])
				down_color=kwargs.get('down_color',self.theme['down_color'])
				for _ in ('rsi_lower','rsi_upper'):
					trace=fig.data[0].copy()
					trace.update(y=[local_kwargs[_] for x in trace['x']])
					trace.update(name='')
					color=down_color if 'lower' in _ else up_color
					trace.update(line=dict(color=color,width=1))
					fig.data.append(trace)
		
		if kind=='macd':
			local_kwargs,params=get_params([],params,display)
			fig=df.ta_figure(study=kind,**params)

		if local_kwargs.get('legendgroup',False):
			fig.update_traces(legendgroup=name,showlegend=False)
			fig.data[0].update(showlegend=True,name=name)
		
		return fig
	
	def iplot(self,**kwargs):
		
		layout=copy.deepcopy(self.layout)
		data=copy.deepcopy(self.data)
		self_kwargs=copy.deepcopy(self.kwargs)

		data['slice']=kwargs.pop('slice',data.pop('slice',(None,None)))
		data['resample']=kwargs.pop('resample',data.pop('resample',None))

		asFigure=kwargs.pop('asFigure',False)
		showstudies=kwargs.pop('showstudies',True)
		study_kwargs=utils.kwargs_from_keyword(kwargs,{},'study',True)
		datalegend=kwargs.pop('datalegend',data.pop('datalegend',data.pop('showlegend',True)))
		_slice=data.pop('slice')
		_resample=data.pop('resample')
		
		panel_data={}
		for k in ['min_panel_size','spacing','top_margin','bottom_margin']:
			panel_data[k]=kwargs.pop(k,self.panels[k])

		d=self_kwargs
		df=self._get_sliced(_slice).copy()
		if _resample:
			if utils.is_list(_resample):
				df=self._get_resampled(*_resample,df=df)
			elif utils.is_dict(_resample):
				_resample.update(df=df)
				df=self._get_resampled(**_resample)
			else:
				df=self._get_resampled(_resample,df=df)

		annotations=layout.pop('annotations')
		shapes=layout.pop('shapes')
		if not 'shapes' in shapes:
			shapes['shapes']=[]
		for trend in self.trendlines:
			_trend=self._get_trendline(**trend)
			shapes['shapes'].append(_trend['shape'])
			if 'text' in _trend['annotation']:
				annotations['values'].append(_trend['annotation'])
		shape_kwargs=utils.check_kwargs(kwargs,get_shapes_kwargs(),{},clean_origin=True)
		for k,v in list(shape_kwargs.items()):
			if k in shapes:
				shapes[k].append(v)
			else:
				shapes[k]=[v]
		for _ in [data,layout,
				  self.theme,{'annotations':annotations['values']},
				  annotations['params'],shapes]:
			if _:
				d=utils.merge_dict(d,_)
		d=utils.deep_update(d,kwargs)
		d=tools.updateColors(d)
		fig=df.figure(**d)
		if d['kind'] not in ('candle','candlestick','ohlc'):
			fig.move_axis(yaxis='y2')
		else:
			if not datalegend:
				fig.data[0]['decreasing'].update(showlegend=False)
				fig.data[0]['increasing'].update(showlegend=False)
		panel_data['n']=1
		which=fig.axis['which']['y']
		which.sort()
		max_panel=int(which[-1][1:])
		figures=[]
		if showstudies:
			kwargs=utils.check_kwargs(kwargs,['theme','up_color','down_color'],{},False)
			kwargs.update(**study_kwargs)
			kwargs.update(slice=_slice,resample=_resample)
			for k,v in list(self.studies.items()):
				study_fig=self._get_study_figure(k,**kwargs)
				if v['kind'] in ('boll','sma','ema'):
					study_fig.move_axis(yaxis='y2')                
				if v['kind'] in ('rsi','volume','macd','atr'):
					max_panel+=1
					panel_data['n']+=1
					study_fig.move_axis(yaxis='y{0}'.format(max_panel))
				figures.append(study_fig)
			figures.append(fig)
			fig=tools.merge_figures(figures)
			fig['layout']['xaxis1']['anchor']='y2'
		domains=self._panel_domains(**panel_data)
		fig.layout.update(**domains)
		if not d.get('rangeslider',False):
			try:
				del fig['layout']['yaxis1']
			except:
				pass
		if asFigure:
			return fig
		else:
			return fig.iplot()
	
	def __getitem__(self,key):
			return self.__dict__[key]
		
	def __repr__(self):
		_d=self.__dict__.copy()
		del _d['df']
		print(json.dumps(_d,sort_keys=True, indent=4))
		return ''