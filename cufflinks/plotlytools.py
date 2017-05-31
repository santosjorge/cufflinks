import pandas as pd
import plotly.plotly as py
import time
import copy
from plotly.graph_objs import *
from collections import defaultdict
from IPython.display import display,Image
from .colors import normalize,get_scales,colorgen,to_rgba,get_colorscale
from .utils import check_kwargs, deep_update, kwargs_from_keyword
from . import tools 
from . import offline
from . import auth
from . import ta


__TA_KWARGS = ['min_period','center','freq','how','rsi_upper','rsi_lower','boll_std','fast_period',
			   'slow_period','signal_period']


def iplot_to_dict(data):
	d=collections.defaultdict(dict)
	for i in data:
		for k,v in list(i.items()):
			d[i['name']][k]=v
	return d 

def dict_to_iplot(d):
	l=[]
	for k,v in list(d.items()):
		l.append(v)
	return Data(l)


def _to_iplot(self,colors=None,colorscale=None,kind='scatter',mode='lines',symbol='dot',size='12',fill=False,
		width=3,dash='solid',sortbars=False,keys=False,bestfit=False,bestfit_colors=None,
		mean=False,mean_colors=None,asDates=False,asTimestamp=False,text=None,**kwargs):
	"""
	Generates a plotly Data object 

	Parameters
	----------
		colors : list or dict
			{key:color} to specify the color for each column
			[colors] to use the colors in the defined order
		colorscale : str 
			Color scale name
			Only valid if 'colors' is null
			See cufflinks.colors.scales() for available scales
		kind : string
			Kind of chart
				scatter
				bar
		mode : string
			Plotting mode for scatter trace
				lines
				markers
				lines+markers
				lines+text
				markers+text
				lines+markers+text		
		symbol : string
			The symbol that is drawn on the plot for each marker
			Valid only when mode includes markers
				dot
				cross
				diamond
				square
				triangle-down
				triangle-left
				triangle-right
				triangle-up
				x
		size : string or int 
			Size of marker 
			Valid only if marker in mode
		fill : bool
			Filled Traces
		width : int
			Line width
		dash : string
			Drawing style of lines
				solid
				dash
				dashdot
				dot
		sortbars : bool
			Sort bars in descending order
			* Only valid when kind='bar'
		keys : list of columns
			List of columns to chart.
			Also can be usded for custom sorting.
		bestfit : boolean or list
			If True then a best fit line will be generated for 
			all columns. 
			If list then a best fit line will be generated for 
			each key on the list. 
		bestfit_colors : list or dict
			{key:color} to specify the color for each column
			[colors] to use the colors in the defined order
		asDates : bool
			If true it forces truncates times from a DatetimeIndex
		
	""" 
	df=self.copy()

	if asTimestamp:
		x=[_ for _ in df.index]
	elif df.index.__class__.__name__ in ('PeriodIndex','DatetimeIndex'):
		if asDates:
			df.index=df.index.date
		x=df.index.format()
	elif isinstance(df.index,pd.MultiIndex):
		x=['({0})'.format(','.join(_)) for _ in df.index.values]
	else:
		x = df.index.values
	lines={}
	if type(df)==pd.core.series.Series:
		df=pd.DataFrame({df.name:df})

	if not keys:		
		if 'bar' in kind:
			if sortbars:
				keys=list(df.sum().sort(inplace=False,ascending=False).keys())
			else:
				keys=list(df.keys())
		else:
			keys=list(df.keys())

	colors=get_colors(colors,colorscale,keys)
	dash=get_items_as_list(dash,keys,'dash')
	symbol=get_items_as_list(symbol,keys,'symbol')
	mode=get_items_as_list(mode,keys,'mode')
	width=get_items_as_list(width,keys,'width')
	for key in keys:
		lines[key]={}
		lines[key]["x"]=x
		lines[key]["y"]=df[key].fillna('').values
		lines[key]["name"]=str(key)
		if text is not None:
			lines[key]["text"]=text
		if 'bar' in kind:
			lines[key]["marker"]={'color':to_rgba(colors[key],.6),'line':{'color':colors[key],'width':1}}
		else:
			lines[key]["line"]={'color':colors[key],'width':width[key],'dash':dash[key]}
			lines[key]["mode"]=mode[key]
			if 'marker' in mode[key]:
				lines[key]["marker"]=Marker(symbol=symbol[key],size=size)
			if fill:
				lines[key]["fill"]='tonexty' if kind=='area' else 'tozeroy'
				lines[key]["fillcolor"]=to_rgba(colors[key],kwargs['opacity'] if 'opacity' in kwargs else .3		)
	if 'bar' in kind:
		lines_plotly=[Bar(lines[key]) for key in keys]
	else:
		lines_plotly=[Scatter(lines[key]) for key in keys]
	for trace in lines_plotly:
		if isinstance(trace['name'],pd.tslib.Timestamp):
			trace.update(name=str(trace['name']))

	if bestfit:
		if type(bestfit)==list:
			keys=bestfit
		d={}
		for key in keys:
			bestfit=df[key].bestfit()
			d[bestfit.formula]=bestfit
		bestfit_lines=pd.DataFrame(d).to_iplot(bestfit=False,colors=bestfit_colors,kind='scatter',asTimestamp=asTimestamp)
		for line in bestfit_lines:
			line['line']['dash']='dash'
			if not bestfit_colors:
				line['line']['color']=to_rgba(line['line']['color'],.6)
		data=Data(lines_plotly)
		data.extend(bestfit_lines)
		return data

	if mean:
		if type(mean)==list:
			keys=mean
		d={}
		for key in keys:
			mean=df[key].mean()
			d['MEAN({key})'.format(key=key)]=pd.Series([mean]*len(df[key]),index=df[key].index)
		mean_lines=pd.DataFrame(d).to_iplot(mean=False,colors=mean_colors,kind='scatter',asTimestamp=asTimestamp)
		for line in mean_lines:
			line['line']['dash']='dash'
			if not mean_colors:
				line['line']['color']=to_rgba(line['line']['color'],.6)
		data=Data(lines_plotly)
		data.extend(mean_lines)
		return data
	return Data(lines_plotly)

def _iplot(self,data=None,layout=None,filename='',sharing=None,
			kind='scatter',title='',xTitle='',yTitle='',zTitle='',theme=None,colors=None,colorscale=None,fill=False,width=None,
			dash='solid',mode='lines',symbol='dot',size=12,barmode='',sortbars=False,bargap=None,bargroupgap=None,bins=None,histnorm='',
			histfunc='count',orientation='v',boxpoints=False,annotations=None,keys=False,bestfit=False,
			bestfit_colors=None,mean=False,mean_colors=None,categories='',x='',y='',z='',text='',gridcolor=None,
			zerolinecolor=None,margin=None,labels=None,values=None,secondary_y='',secondary_y_title='',subplots=False,shape=None,error_x=None,
			error_y=None,error_type='data',locations=None,lon=None,lat=None,asFrame=False,asDates=False,asFigure=False,
			asImage=False,dimensions=None,asPlot=False,asUrl=False,online=None,**kwargs):
	"""
	Returns a plotly chart either as inline chart, image of Figure object

	Parameters:
	-----------
		data : Data
			Plotly Data Object.
			If not entered then the Data object will be automatically
			generated from the DataFrame.
		data : Data
			Plotly Data Object.
			If not entered then the Data object will be automatically
			generated from the DataFrame.
		layout : Layout
			Plotly layout Object
			If not entered then the Layout objet will be automatically
			generated from the DataFrame.
		filename : string
			Filename to be saved as in plotly account
		sharing : string
			Sets the sharing level permission
				public - anyone can see this chart
				private - only you can see this chart
				secret - only people with the link can see the chart
		kind : string
			Kind of chart
				scatter
				bar
				box
				spread
				ratio
				heatmap
				surface
				histogram
				bubble
				bubble3d
				scatter3d	
				scattergeo
				ohlc
				candle
				pie
				choroplet	
		title : string
			Chart Title				
		xTitle : string
			X Axis Title
		yTitle : string
			Y Axis Title
				zTitle : string
		zTitle : string
			Z Axis Title
			Applicable only for 3d charts
		theme : string
			Layout Theme
				solar
				pearl
				white		
			see cufflinks.getThemes() for all 
			available themes
		colors : dict, list or string
			{key:color} to specify the color for each column
			[colors] to use the colors in the defined order
		colorscale : string
			Color scale name
			If the color name is preceded by a minus (-) 
			then the scale is inversed
			Only valid if 'colors' is null
			See cufflinks.colors.scales() for available scales
		fill : bool
			Filled Traces		
		width : dict, list or string
				string : applies to all traces
				list : applies to each trace in the order 
						specified
				dict: {column:value} for each column in 
						the dataframe
			Line width	
		dash : dict, list or string
				string : applies to all traces
				list : applies to each trace in the order 
						specified
				dict: {column:value} for each column in 
						the dataframe
			Drawing style of lines
				solid
				dash
				dashdot
				dot
		mode : dict, list or string
				string : applies to all traces
				list : applies to each trace in the order 
						specified
				dict: {column:value} for each column in 
						the dataframe
			Plotting mode for scatter trace
				lines
				markers
				lines+markers
				lines+text
				markers+text
				lines+markers+text		
		symbol : dict, list or string
				string : applies to all traces
				list : applies to each trace in the order 
						specified
				dict: {column:value} for each column in 
						the dataframe
			The symbol that is drawn on the plot for each marker
			Valid only when mode includes markers
				dot
				cross
				diamond
				square
				triangle-down
				triangle-left
				triangle-right
				triangle-up
				x
		size : string or int 
			Size of marker 
			Valid only if marker in mode
		barmode : string
			Mode when displaying bars
				group
				stack
				overlay
			* Only valid when kind='bar'
		sortbars : bool
			Sort bars in descending order
			* Only valid when kind='bar'
		bargap : float
			Sets the gap between bars
				[0,1)
			* Only valid when kind is 'histogram' or 'bar'
		bargroupgap : float
			Set the gap between groups
				[0,1)
			* Only valid when kind is 'histogram' or 'bar'		
		bins : int
			Specifies the number of bins 
			* Only valid when kind='histogram'
		histnorm : string
				'' (frequency)
				percent
				probability
				density
				probability density
			Sets the type of normalization for an histogram trace. By default
			the height of each bar displays the frequency of occurrence, i.e., 
			the number of times this value was found in the
			corresponding bin. If set to 'percent', the height of each bar
			displays the percentage of total occurrences found within the
			corresponding bin. If set to 'probability', the height of each bar
			displays the probability that an event will fall into the
			corresponding bin. If set to 'density', the height of each bar is
			equal to the number of occurrences in a bin divided by the size of
			the bin interval such that summing the area of all bins will yield
			the total number of occurrences. If set to 'probability density',
			the height of each bar is equal to the number of probability that an
			event will fall into the corresponding bin divided by the size of
			the bin interval such that summing the area of all bins will yield
			1.
			* Only valid when kind='histogram'
		histfunc : string
				count
				sum
				avg
				min
				max
		   Sets the binning function used for an histogram trace. 
			* Only valid when kind='histogram'           
		orientation : string
				h 
				v
			Sets the orientation of the bars. If set to 'v', the length of each
 |          bar will run vertically. If set to 'h', the length of each bar will
 |          run horizontally
			* Only valid when kind is 'histogram','bar' or 'box'
		boxpoints : string
			Displays data points in a box plot
				outliers
				all
				suspectedoutliers
				False
		annotations : dictionary
			Dictionary of annotations
			{x_point : text}
		keys : list of columns
			List of columns to chart.
			Also can be usded for custom sorting.
		bestfit : boolean or list
			If True then a best fit line will be generated for
			all columns.
			If list then a best fit line will be generated for
			each key on the list.
		bestfit_colors : list or dict
			{key:color} to specify the color for each column
			[colors] to use the colors in the defined order	
		categories : string
			Name of the column that contains the categories
		x : string
			Name of the column that contains the x axis values		
		y : string
			Name of the column that contains the y axis values
		z : string
			Name of the column that contains the z axis values					
		text : string
			Name of the column that contains the text values	
		gridcolor : string
			Grid color	
		zerolinecolor : string
			Zero line color
		margin : dict or tuple
			Dictionary (l,r,b,t) or
			Tuple containing the left,
			right, bottom and top margins
		labels : string
			Name of the column that contains the labels.
			* Only valid when kind='pie' 
		values : string
			Name of the column that contains the values.
			* Only valid when kind='pie'
		secondary_y : string or list(string)
			Name(s) of the column to be charted on the 
			right hand side axis
		secondary_y_title : string
			Title of the secondary axis
		subplots : bool
			If true then each trace is placed in 
			subplot layout
		shape : (rows,cols)
			Tuple indicating the size of rows and columns
			If omitted then the layout is automatically set
			* Only valid when subplots=True
		error_x : int or float or [int or float]
			error values for the x axis
		error_y : int or float or [int or float]
			error values for the y axis
		error_type : string
			type of error bars
				'data' 
				'constant'
				'percent'
				'sqrt'
				'continuous'
				'continuous_percent'
		asFrame : bool
			If true then the data component of Figure will
			be of Pandas form (Series) otherwise they will 
			be index values
		asDates : bool
			If true it truncates times from a DatetimeIndex
		asFigure : bool
			If True returns plotly Figure
		asImage : bool
			If True it returns Image
			* Only valid when asImage=True
		dimensions : tuple(int,int)
			Dimensions for image
				(width,height)		
		asPlot : bool
			If True the chart opens in browser
		asUrl : bool
			If True the chart url is returned. No chart is displayed. 
		online : bool
			If True then the chart is rendered on the server 
			even when running in offline mode. 

		Other Kwargs
		============
		
		Pie charts
			sort : bool
				If True it sorts the labels by value
			pull : float [0-1]
				Pulls the slices from the centre 
			hole : float [0-1]
				Sets the size of the inner hole
			textposition : string 
				Sets the position of the legends for each slice
					outside
					inner
			textinfo : string 
				Sets the information to be displayed on 
				the legends 
					label
					percent
					value
					* or ony combination of the above using 
					  '+' between each item
					  ie 'label+percent'

		Histogram
			line_color : string
				specifies the line color of the histogram

		Error Bars
			error_trace : string
				Name of the column for which error should be 
				plotted. If omitted then errors apply to all 
				traces.
			error_values_minus : int or float or [int or float]
				Values corresponding to the span of the error bars 
				below the trace coordinates
			error_color : string
				Color for error bars
			error_thickness : float 
				Sets the line thickness of the error bars
			error_width :  float
				Sets the width (in pixels) of the cross-bar at both 
				ends of the error bars
			error_opacity : float [0,1]
				Opacity for the error bars

		Subplots
			horizontal_spacing : float [0,1]
				Space between subplot columns.
			vertical_spacing : float [0,1]
				Space between subplot rows.
			subplot_titles : bool
				If True, chart titles are plotted
				at the top of each subplot
			shared_xaxes : bool
				Assign shared x axes.
				If True, subplots in the same grid column have one common
				shared x-axis at the bottom of the grid.
			shared_yaxes : bool
				Assign shared y axes.
				If True, subplots in the same grid row have one common
				shared y-axis on the left-hand side of the grid.

		Shapes
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
			hpsan : (y0,y1)
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
		
		Axis Ranges
			xrange : [lower_bound,upper_bound]
				Sets the range for the x axis
			yrange : [lower_bound,upper_bound]
				Sets the range for the y axis
			zrange : [lower_bound,upper_bound]
				Sets the range for the z axis
				
		Explicit Layout Updates
			layout_update : dict
				The layout will be modified with all 
				the explicit values stated in the 
				dictionary. 
				It will not apply if layout is passed
				as parameter.


		Range Selector
			rangeselector : dict
				Defines a rangeselector object
				see help(cf.tools.get_range_selector) for more information
				Example:
					{'steps':['1y','2 months','5 weeks','ytd','2mtd'],
					 'axis':'xaxis1', 'bgcolor' : ('blue',.3),
					 'x': 0.2 , 'y' : 0.9}

		Range Slider
			rangeslider : bool or dict
				Defines if a rangeslider is displayed
				If bool: 
					True : Makes it visible
				if dict:
					Rangeslider object
				Example:
					{'bgcolor':('blue',.3),'autorange':True}

		Annotations
			fontcolor : str
				Text color for annotations
			fontsize : int
				Text size for annotations
			textangle : int
				Textt angle 
			See https://plot.ly/python/reference/#layout-annotations 
			for a complete list of valid parameters.
	"""

	# Look for invalid kwargs
	# _native_iplot = ['layout','filename','sharing',
	# 		'kind','title','xTitle','yTitle','zTitle','theme','colors','colorscale','fill','width',
	# 		'dash','mode','symbol','size','barmode','sortbars','bargap','bargroupgap','bins','histnorm',
	# 		'histfunc','orientation','boxpoints','annotations','keys','bestfit',
	# 		'bestfit_colors','mean','mean_colors','categories','x','y','z','text','gridcolor',
	# 		'zerolinecolor','margin','labels','values','secondary_y','secondary_y_title','subplots','shape','error_x',
	# 		'error_y','error_type','locations','lon','lat','asFrame','asDates','asFigure',
	# 		'asImage','dimensions','asPlot','asUrl','online']
	valid_kwargs = ['color','opacity','column','columns','labels','text','world_readable','colorbar']
	TRACE_KWARGS = ['hoverinfo']
	PIE_KWARGS=['sort','pull','hole','textposition','textinfo','linecolor']
	OHLC_KWARGS=['up_color','down_color','open','high','low','close','volume','name','decreasing','increasing']
	SUBPLOT_KWARGS=['horizontal_spacing', 'vertical_spacing',
					'specs', 'insets','start_cell','shared_xaxes','shared_yaxes','subplot_titles']
	GEO_KWARGS=['locationmode','locationsrc','geo','lon','lat']
	ERROR_KWARGS=['error_trace','error_values_minus','error_color','error_thickness',
					'error_width','error_opacity']
	kwargs_list = [tools.__LAYOUT_KWARGS,TRACE_KWARGS,
				   OHLC_KWARGS,PIE_KWARGS,SUBPLOT_KWARGS,GEO_KWARGS,ERROR_KWARGS]
	[valid_kwargs.extend(_) for _ in kwargs_list]

	dict_modifiers_keys = ['line']
	dict_modifiers={}

	for k in dict_modifiers_keys:
		dict_modifiers[k]=kwargs_from_keyword(kwargs,{},k,True)
	

	for key in list(kwargs.keys()):
		if key not in valid_kwargs:
			raise Exception("Invalid keyword : '{0}'".format(key))

	# Setting default values
	if not colors:
		colors=kwargs['color'] if 'color' in kwargs else colors
	if isinstance(colors,str):
		colors=[colors]
	opacity=kwargs['opacity'] if 'opacity' in kwargs else 0.8
	if not dimensions:
		dimensions=auth.get_config_file()['dimensions']

	# Get values from config theme
	if theme is None:
		theme = auth.get_config_file()['theme']
	theme_config=tools.getTheme(theme)
	if colorscale is None:
		colorscale=theme_config['colorscale'] if 'colorscale' in theme_config else 'dflt'
	if width is None:
		if kind != 'pie':
			width=theme_config['linewidth'] if 'linewidth' in theme_config else 2
	# if bargap is None:
	# 	bargap=theme_config['bargap'] if 'bargap' in theme_config else 0

	# In case column was used instead of keys
	if 'column' in kwargs:
		keys=[kwargs['column']] if isinstance(kwargs['column'],str) else kwargs['column']
	if 'columns' in kwargs:
		keys=[kwargs['columns']] if isinstance(kwargs['columns'],str) else kwargs['columns']
	kind='line' if kind=='lines' else kind

	# Figure generators
	def get_marker(marker={}):
		if 'line' in dict_modifiers:
			if 'color' not in dict_modifiers['line']:
				if 'linecolor' in tools.getTheme(theme=theme):
					linecolor=normalize(tools.getTheme(theme=theme)['linecolor'])
				else: 
					linecolor=tools.getLayout(theme=theme)['xaxis1']['titlefont']['color']
				dict_modifiers['line']['color']=linecolor			
			dict_modifiers['line']=tools.updateColors(dict_modifiers['line'])
			marker['line']=deep_update(marker['line'],dict_modifiers['line'])
		return marker

	# We assume we are good citizens
	validate=True
	

	if not layout:
		l_kwargs=dict([(k,kwargs[k]) for k in tools.__LAYOUT_KWARGS if k in kwargs])
		if annotations:
			ann_kwargs=check_kwargs(kwargs,tools.__ANN_KWARGS,clean_origin=True)
			annotations=tools.getAnnotations(self.copy(),annotations,kind=kind,theme=theme,**ann_kwargs)


		layout=tools.getLayout(kind=kind,theme=theme,xTitle=xTitle,yTitle=yTitle,zTitle=zTitle,title=title,barmode=barmode,
								bargap=bargap,bargroupgap=bargroupgap,annotations=annotations,gridcolor=gridcolor,
							   dimensions=dimensions,
								zerolinecolor=zerolinecolor,margin=margin,is3d='3d' in kind,**l_kwargs)

	if not data:
		if categories:
			data=Data()
			if 'bar' in kind:
				df=self.copy()
				df=df.set_index(categories)
				fig=df.figure(kind=kind,colors=colors,colorscale=colorscale,fill=fill,width=width,sortbars=sortbars,
						asDates=asDates,mode=mode,symbol=symbol,size=size,text=text,barmode=barmode,orientation=orientation)
				data=fig['data']			
			else:
				_keys=pd.unique(self[categories])
				colors=get_colors(colors,colorscale,_keys)	
				mode='markers' if 'markers' not in mode else mode 
				for _ in _keys:
					__=self[self[categories]==_].copy()
					if text:
						_text=__[text] if asFrame else __[text].values
					_x=__[x] if asFrame else __[x].values
					_y=__[y] if asFrame else __[y].values
					if z:
						_z=__[z] if asFrame else __[z].values
					if 'bubble' in kind:
						rg=__[size].values
						rgo=self[size].values
						_size=[int(100*(float(i)-rgo.min())/(rgo.max()-rgo.min()))+12 for i in rg]		
					else:
						_size=size
					_data=Scatter3d(x=_x,y=_y,mode=mode,name=_,
								marker=Marker(color=colors[_],symbol=symbol,size=_size,opacity=opacity,
												line=Line(width=width)),textfont=tools.getLayout(theme=theme)['xaxis1']['titlefont'])
					if '3d' in kind:
						_data=Scatter3d(x=_x,y=_y,z=_z,mode=mode,name=_,
								marker=Marker(color=colors[_],symbol=symbol,size=_size,opacity=opacity,
												line=Line(width=width)),textfont=tools.getLayout(theme=theme)['xaxis1']['titlefont'])
					else:
						_data=Scatter(x=_x,y=_y,mode=mode,name=_,
								marker=Marker(color=colors[_],symbol=symbol,size=_size,opacity=opacity,
												line=Line(width=width)),textfont=tools.getLayout(theme=theme)['xaxis1']['titlefont'])
					if text:
						_data.update(text=_text)
					data.append(_data)
		else:
			if kind in ('scatter','spread','ratio','bar','barh','area','line'):
				df=self.copy()
				if type(df)==pd.core.series.Series:
					df=pd.DataFrame({df.name:df})
				if x:
					df=df.set_index(x)
				if y:
					df=df[y]
				if kind=='area':
					df=df.transpose().fillna(0).cumsum().transpose()
				if text:
					if not isinstance(text,list):
						text=self[text].values
				data=df.to_iplot(colors=colors,colorscale=colorscale,kind=kind,fill=fill,width=width,dash=dash,sortbars=sortbars,keys=keys,
						bestfit=bestfit,bestfit_colors=bestfit_colors,mean=mean,mean_colors=mean_colors,asDates=asDates,mode=mode,symbol=symbol,size=size,
						text=text,**kwargs)		
				trace_kw=check_kwargs(kwargs,TRACE_KWARGS)
				for trace in data:
					trace.update(**trace_kw)		
						
				if kind in ('spread','ratio'):
						if kind=='spread':
							trace=self.apply(lambda x:x[0]-x[1],axis=1)
							positive=trace.apply(lambda x:x if x>=0 else pd.np.nan)
							negative=trace.apply(lambda x:x if x<0 else pd.np.nan)
							trace=pd.DataFrame({'positive':positive,'negative':negative})
							trace=trace.to_iplot(colors={'positive':'green','negative':'red'},width=0.5)
						else:
							trace=self.apply(lambda x:x[0]*1.0/x[1],axis=1).to_iplot(colors=['green'],width=1)
						trace.update({'xaxis':'x2','yaxis':'y2','fill':'tozeroy',
										'name':kind.capitalize(),'connectgaps':False,'showlegend':False})
						data.append(Scatter(trace[0]))
						if kind=='spread':
							data.append(Scatter(trace[1]))
						layout['yaxis1'].update({'domain':[.3,1]})
						layout['yaxis2']=copy.deepcopy(layout['yaxis1'])
						layout['xaxis2']=copy.deepcopy(layout['xaxis1'])
						layout['yaxis2'].update(domain=[0,.25],title=kind.capitalize())
						layout['xaxis2'].update(anchor='y2',showticklabels=False)
						layout['hovermode']='x'
				if 'bar' in kind:
					if 'stack' in barmode:
						layout['legend'].update(traceorder='normal')
					orientation = 'h' if kind=='barh' else orientation
					for trace in data:
						trace.update(orientation=orientation)
						if kind=='barh':
							trace['x'],trace['y']=trace['y'],trace['x']	
						
			elif kind=='bubble':
				mode='markers' if 'markers' not in mode else mode 
				x=self[x].values.tolist()
				y=self[y].values.tolist()
				z=size if size else z
				rg=self[z].values
				z=[int(100*(float(_)-rg.min())/(rg.max()-rg.min()))+12 for _ in rg]
				text=kwargs['labels'] if 'labels' in kwargs else text
				labels=self[text].values.tolist() if text else ''
				clrs=colors if colors else get_scales(colorscale)
				clrs=[clrs] if not isinstance(clrs,list) else clrs
				clrs=[clrs[0]]*len(x)
				marker=Marker(color=clrs,size=z,symbol=symbol,
								line=Line(width=width))
				trace=Scatter(x=x,y=y,marker=marker,mode='markers',text=labels)
				data=Data([trace])
			elif kind in ('box','histogram','hist'):
				if isinstance(self,pd.core.series.Series):
					df=pd.DataFrame({self.name:self})
				else:
					df=self.copy()
				data=Data()
				clrs=get_colors(colors,colorscale,df.columns)
				if 'hist' in kind:
					barmode = 'overlay' if barmode=='' else	 barmode 
					layout.update(barmode=barmode) 
				columns=keys if keys else df.columns
				for _ in columns:
					if kind=='box':
						__=Box(y=df[_].values.tolist(),marker=Marker(color=clrs[_]),name=_,
								line=Line(width=width),boxpoints=boxpoints)
					else:
						__=Histogram(x=df[_].values.tolist(),name=_,
								marker=Marker(color=clrs[_], line=Line(width=width)),
								orientation=orientation,
								opacity=kwargs['opacity'] if 'opacity' in kwargs else .8, histfunc=histfunc,
								histnorm=histnorm)

						__['marker']=get_marker(__['marker'])

						if orientation=='h':
							__['y']=__['x']
							del __['x']
						if bins:
							if orientation=='h':
								__.update(nbinsy=bins)	
							else:
								__.update(nbinsx=bins)
					data.append(__)

			elif kind in ('heatmap','surface'):
				if x:
					x=self[x].values.tolist()
				else:
					if self.index.__class__.__name__ in ('PeriodIndex','DatetimeIndex'):
						x=self.index.format()
					else:
						x=self.index.values.tolist()
				y=self[y].values.tolist() if y else self.columns.values.tolist()
				z=self[z].values.tolist() if z else self.values.transpose()
				scale=get_scales('rdbu') if not colorscale else get_scales(colorscale)
				colorscale=[[float(_)/(len(scale)-1),scale[_]] for _ in range(len(scale))]
				if kind=='heatmap':
					data=Data([Heatmap(z=z,x=x,y=y,colorscale=colorscale)])
				else:
					data=Data([Surface(z=z,x=x,y=y,colorscale=colorscale)])

			elif kind in ('scatter3d','bubble3d'):
				data=Data()
				keys=self[text].values if text else list(range(len(self)))
				colors=get_colors(colors,colorscale,keys,asList=True)
				df=self.copy()
				df['index']=keys
				if kind=='bubble3d':
					rg=self[size].values
					size=[int(100*(float(_)-rg.min())/(rg.max()-rg.min()))+12 for _ in rg]
				else:
					size=[size for _ in range(len(keys))]	

				_data=Scatter3d(x=df[x].values.tolist(),y=df[y].values.tolist(),z=df[z].values.tolist(),mode=mode,name=keys,
									marker=Marker(color=colors,symbol=symbol,size=size,opacity=.8))
				if text:
					_data.update(text=keys)
				data.append(_data)

			elif kind=='pie':
				labels=self[labels].values.tolist()
				values=self[values].values.tolist()
				marker={'colors':get_colors(colors,colorscale,labels,asList=True)}
				line={}
				if 'linecolor' in kwargs:
					line['color']=kwargs['linecolor'] 
				if width:
					line['width']=width 
				if line:
					marker['line']=line
				pie={'type':'pie','values':values,'labels':labels,'name':'',
					 'marker':marker}
				for kw in ['sort','pull','hole','textposition','textinfo']:
					if kw in kwargs:
						pie[kw]=kwargs[kw]
				data=Data()
				del layout['xaxis1']
				del layout['yaxis1']
				data.append(pie)
				validate=False

			elif kind in ('old_candle','old_ohlc'):
				d=ta._ohlc_dict(self)
				if len(list(d.keys()))!=4:
					raise Exception("OHLC type of charts require an Open, High, Low and Close column")				
				ohlc_kwargs=check_kwargs(kwargs,OHLC_KWARGS)
				if kind=='old_candle':					
					fig=tools.get_candle(self,theme=theme,layout=layout,**ohlc_kwargs)
				else:
					fig=tools.get_ohlc(self,theme=theme,layout=layout,**ohlc_kwargs)
				if bestfit:
					df=self.copy()
					bf=_to_iplot(self[d['close']],bestfit=True,bestfit_colors=bestfit_colors,asTimestamp=True)
					fig['data'].append(bf[1])
				data=fig['data']
				layout=fig['layout']

			elif kind in ('candle','ohlc','candlestick'):
				kind='candlestick' if kind=='candle' else kind
				kw=check_kwargs(kwargs,OHLC_KWARGS)
				d=ta._ohlc_dict(self,validate='ohlc',**kw)
				_d=dict(type=kind,
							open=self[d['open']].values,
							high=self[d['high']].values,
							low=self[d['low']].values,
							close=self[d['close']].values,
							x=self.index
												)
				if 'name' in kw:
					_d['name']=kw['name']
				
				showlegend=False
				if 'showlegend' in kwargs:
					showlegend=kwargs['showlegend']
				else:
					if 'legend' in kwargs:
						if type(kwargs['legend'])==bool:
							showlegend=kwargs['legend']
				
				_d['increasing']=dict(line=dict(color=kw['up_color']) if 'up_color' in kw else dict(),showlegend=showlegend)
				_d['decreasing']=dict(line=dict(color=kw['down_color']) if 'down_color' in kw else dict(),showlegend=showlegend)
				for k in ('increasing','decreasing'):
					if k in kw:
						_d[k]=deep_update(_d[k],kw[k])
				
				_d['yaxis']='y2'
				data=[_d]



			elif kind in ('choropleth','scattergeo'):
				kw=check_kwargs(kwargs,GEO_KWARGS)
				if kind=='choropleth':
					if not all([x!=None for x in (locations,z)]):
						raise Exception("Choropleth maps require a 'location' and 'z' column names specified")
					geo_data={'type':'choropleth','locations':self[locations],'z':self[z],
							'colorscale':get_colorscale(colorscale),
							'marker':get_marker(Marker(line=Line(width=width)))}
				elif kind=='scattergeo':
					if not all([x!=None for x in (lon,lat)]):
						raise Exception("Scattergeo maps require a 'lon' and 'lat' column names specified")
					geo_data={'type':'scattergeo','lat':self[lat],'lon':self[lon],
							'marker':get_marker(Marker(line=Line(width=width),
												symbol=symbol,colorscale=get_colorscale(colorscale),
												color=self[z] if z else None))}
				if 'colorbar' in kwargs:
					geo_data['colorbar']=kwargs['colorbar']
				geo_data.update(kw)
				if text:
					geo_data.update(text=self[text])
				validate=False
				data=Data()
				data.append(geo_data)
	
## Sharing Values
	if all(['world_readable' in kwargs,sharing is None]):
		sharing=kwargs['world_readable']
	if isinstance(sharing,bool):
			if sharing:
				sharing='public'
			else:
				sharing='private'
	if sharing is None:
		sharing=auth.get_config_file()['sharing']

	if not filename:
		if title:
			filename=title
		else:
			filename='Plotly Playground {0}'.format(time.strftime("%Y-%m-%d %H:%M:%S"))

	

## Figure defintion
	figure=Figure()
	figure['data']=data
	figure['layout']=layout

## Check secondary axis
	if secondary_y:
		figure=figure.set_axis(secondary_y,side='right')
		if secondary_y_title:
			figure.layout.yaxis2.title=secondary_y_title

## Error Bars
	if kind in ('scatter','bar','barh','lines'):
		if any([error_x,error_y]):
			def set_error(axis,**kwargs):
				return tools.set_errors(figure,axis=axis,**kwargs)
			kw=check_kwargs(kwargs,ERROR_KWARGS)
			kw=dict([(k.replace('error_',''),v) for k,v in list(kw.items())])
			kw['type']=error_type
			if error_x:
				kw['values']=error_x
				figure=set_error('x',**kw)
			if error_y:
				kw['values']=error_y
				figure=set_error('y',**kw)
## Subplots 

	if subplots:
		fig=tools.strip_figures(figure)
		kw=check_kwargs(kwargs,SUBPLOT_KWARGS)	
		if 'subplot_titles' in kwargs:
			if kwargs['subplot_titles']==True:
				kw['subplot_titles']=[d['name'] for d in data]
			else:
				kw['subplot_titles']=kwargs['subplot_titles']		
		figure=tools.subplots(fig,shape,base_layout=layout,theme=theme,**kw)


## Exports 
	validate = False if 'shapes' in layout else validate

	if asFigure:
		return figure
	elif asImage:
		if not dimensions:
			dimensions=(1000,500)
		try:
			py.image.save_as(figure,filename='img/'+filename,format='png',
				width=dimensions[0],height=dimensions[1])
			path='img/'+filename+'.png'
		except:
			py.image.save_as(figure,filename=filename,format='png',
				width=dimensions[0],height=dimensions[1])
			path=filename+'.png'
		return display(Image(path))
	elif asPlot:
		return py.plot(figure,sharing=sharing,filename=filename,validate=validate)
	elif asUrl:
		return py.plot(figure,sharing=sharing,filename=filename,validate=validate,auto_open=False)
	else:
		return iplot(figure,sharing=sharing,filename=filename,validate=validate,online=online)


def get_colors(colors,colorscale,keys,asList=False):
	if type(colors)!=dict:
			if not colors:
				if colorscale:
					colors=get_scales(colorscale,len(keys))
			clrgen=colorgen(colors,len(keys))
			if asList:
				colors=[next(clrgen) for _ in keys]
			else:
				colors={}
				for key in keys:
					colors[key]=next(clrgen)
	return colors

def get_items_as_list(items,keys,items_names='styles'):
	"""
	Returns a dict with an item per key

	Parameters:
	-----------
		items : string, list or dict
			Items (ie line styles)
		keys: list 
			List of keys
		items_names : string
			Name of items 
	"""
	if type(items)!=dict:
		if type(items)==list:
			if len(items)!=len(keys):
				raise Exception('List of {0} is not the same length as keys'.format(items_names))
			else:
				items=dict(zip(keys,items))
		else:
			items=dict(zip(keys,[items]*len(keys)))
	return items


def _scatter_matrix(self,theme=None,bins=10,color='grey',size=2, asFigure=False, **iplot_kwargs):
	"""
	Displays a matrix with scatter plot for each pair of 
	Series in the DataFrame.
	The diagonal shows a histogram for each of the Series

	Parameters:
	-----------
		df : DataFrame
			Pandas DataFrame
		theme : string
			Theme to be used (if not the default)
		bins : int
			Number of bins to use for histogram
		color : string
			Color to be used for each scatter plot
		size : int
			Size for each marker on the scatter plot
		iplot_kwargs : key-value pairs
			Keyword arguments to pass through to `iplot`
	"""
	sm=tools.scatter_matrix(self,theme=theme,bins=bins,color=color,size=size)
	if asFigure:
		return sm
	else:
		return iplot(sm,**iplot_kwargs)

def _figure(self,**kwargs):
	"""
	Generates a Plotly figure for the given DataFrame

	Parameters:
	-----------
			All properties avaialbe can be seen with
			help(cufflinks.pd.DataFrame.iplot)
	"""
	kwargs['asFigure']=True
	return self.iplot(**kwargs)

def _layout(self,**kwargs):
	"""
	Generates a Plotly layout for the given DataFrame

	Parameters:
	-----------
			All properties avaialbe can be seen with
			help(cufflinks.pd.DataFrame.iplot)
	"""
	kwargs['asFigure']=True
	return self.iplot(**kwargs)['layout']


def iplot(data_or_figure,validate=True,sharing=None,filename='',online=None,**kwargs):
	"""
	Plots a figure in IPython

	data_or_figure : figure
		Plotly figure to be charted
	validate : bool
		If True then all values are validated before 
		it is charted
	sharing : string
		Sets the sharing level permission
			public - anyone can see this chart
			private - only you can see this chart
			secret - only people with the link can see the chart
	filename : string
		Name to be used to save the file in the server
	online : bool
		If True then charts are rendered in the server 

	Other Kwargs
	============

		legend : bool
			If False then the legend will not be shown		
	"""
	valid_kwargs=['world_readable','legend']
	for key in list(kwargs.keys()):
		if key not in valid_kwargs:
			raise Exception("Invalid keyword : '{0}'".format(key))
	if 'legend' in kwargs:
		if 'layout' in data_or_figure:
			data_or_figure['layout'].update(showlegend=kwargs['legend'])
	if all(['world_readable' in kwargs,sharing is None]):
		sharing=kwargs['world_readable']
	if isinstance(sharing,bool):
			if sharing:
				sharing='public'
			else:
				sharing='private'
	if sharing is None:
		sharing=auth.get_config_file()['sharing']
	if offline.is_offline() and not online:
		show_link = auth.get_config_file()['offline_show_link']
		link_text = auth.get_config_file()['offline_link_text']
		return offline.py_offline.iplot(data_or_figure,show_link=show_link,link_text=link_text)
	else:
		if 'layout' in data_or_figure:
			validate = False if 'shapes' in data_or_figure['layout'] else validate
		if not filename:
			filename='Plotly Playground {0}'.format(time.strftime("%Y-%m-%d %H:%M:%S"))
		return py.iplot(data_or_figure,validate=validate,sharing=sharing,
						filename=filename)

def _ta_figure(self,**kwargs):
	"""
	Generates a Plotly figure for the given DataFrame

	Parameters:
	-----------
			All properties avaialbe can be seen with
			help(cufflinks.pd.DataFrame.iplot)
	"""
	kwargs['asFigure']=True
	return self.ta_plot(**kwargs)


def _ta_plot(self,study,periods=14,column=None,include=True,str=None,detail=False,
			 theme=None,sharing=None,filename='',asFigure=False,**iplot_kwargs):
	"""
	Generates a Technical Study Chart

	Parameters:
	-----------
			study : string
				Technical Study to be charted
					sma - 'Simple Moving Average'
					rsi - 'R Strength Indicator'
			periods : int
				Number of periods
			column : string
				Name of the column on which the
				study will be done
			include : bool
				Indicates if the input column(s)
				should be included in the chart
			str : string
				Label factory for studies
				The following wildcards can be used:
					{name} : Name of the column
					{study} : Name of the study
					{period} : Period used
				Examples:
					'study: {study} - period: {period}'
			detail : bool
				If True the supporting data/calculations
				are included in the chart 
			study_colors : string or [string]
				Colors to be used for the studies

		Study Specific Parameters
		-------------------------
		RSI 
			rsi_upper : int (0,100]
				Level for the upper rsi band
			rsi_lower : int (0,100]
				Level for the lower rsi band
		BOLL
			boll_std : int or float
				Number of standard deviations
		MACD
			fast_period : int
				Number of periods for the fast moving average
			slow_period : int
				Number of periods for the slow moving average
			signal_period : int
				Number of periods for the signal 
		CORREL
			how : string
				Method for the correlation calculation
					values
					pct_cht
					diff
					
	"""

	if 'columns' in iplot_kwargs:
		column=iplot_kwargs.pop('columns')
		
	if 'period' in iplot_kwargs:
		periods=iplot_kwargs.pop('period')
		
	if 'world_readable' in iplot_kwargs:
		sharing=iplot_kwargs.pop('world_readable')

	if 'study_color' in iplot_kwargs:
		iplot_kwargs['study_colors']=iplot_kwargs.pop('study_color')
		
	if sharing is None:
			sharing = auth.get_config_file()['sharing']
	if isinstance(sharing,bool):
			if sharing:
				sharing='public'
			else:
				sharing='private'
	iplot_kwargs['sharing']=sharing
	if theme is None:
		theme = iplot_kwargs.pop('study_theme',auth.get_config_file()['theme'])

	if not filename:
		if 'title' in iplot_kwargs:
			filename=iplot_kwargs['title']
		else:
			filename='Plotly Playground {0}'.format(time.strftime("%Y-%m-%d %H:%M:%S"))

	def get_subplots(figures):
		shape=(len(figures),1)
		layout=tools.get_base_layout(figures)
		subplots=tools.subplots(figures,shape=shape,shared_xaxes=True,base_layout=layout)
		if len(figures)==2:
			subplots['layout']['yaxis1']['domain']=[.27,1.0]
			subplots['layout']['yaxis2']['domain']=[0,.25]
		return subplots

	def get_study(df,func,iplot_kwargs,iplot_study_kwargs,str=None,include=False,column=None,inset=False):
		df=df.copy()
		if inset:
			if not column:
				if isinstance(df,pd.DataFrame):
					column=df.keys().tolist()
				else:
					df=pd.DataFrame(df)
					column=df.keys().tolist()
		if 'legend' in iplot_kwargs:
			iplot_study_kwargs['legend']=iplot_kwargs['legend']
		fig_0=df.figure(**iplot_kwargs)
		df_ta=func(df,column=column,include=False,str=str,**study_kwargs)	
		kind=iplot_kwargs['kind'] if 'kind' in iplot_kwargs else ''
		iplot_study_kwargs['kind']='scatter'
		iplot_study_kwargs['colors']='blue' if 'colors' not in iplot_study_kwargs else iplot_study_kwargs['colors']
		fig_1=df_ta.figure(theme=theme,**iplot_study_kwargs)
		if kind in ['candle','ohlc']:
				for i in fig_1['data']:
					i['x']=[pd.Timestamp(_) for _ in i['x']]
		if inset:
			figure=tools.merge_figures([fig_0,fig_1]) if include else fig_1
		else:
			figure=get_subplots([fig_0,fig_1]) if include else fig_1
		return figure

	study_kwargs={}  
	iplot_study_kwargs={}

	study_kwargs=check_kwargs(iplot_kwargs,__TA_KWARGS,{},clean_origin=True)
	iplot_study_kwargs=kwargs_from_keyword(iplot_kwargs,{},'study')

	study_kwargs.update({'periods':periods})

	ta_func = eval('ta.{0}'.format(study))

	inset=study in ('sma','boll','ema','atr')
	figure=get_study(self,ta_func,iplot_kwargs,iplot_study_kwargs,include=include,
				     column=column,str=str,inset=inset)

	if study=='rsi':
		rsi_upper=study_kwargs['rsi_upper'] if 'rsi_upper' in study_kwargs else 70
		rsi_lower=study_kwargs['rsi_lower'] if 'rsi_lower' in study_kwargs else 30
		yref='y2' if include else 'y1'
		shapes=[tools.get_shape(y=i,yref=yref,color=j,dash='dash') for (i,j) in [(rsi_lower,'green'),(rsi_upper,'red')]]
		figure['layout']['shapes']=shapes

	## Exports

	if asFigure:
		return figure
	else: 
		return iplot(figure,sharing=sharing,filename=filename)

def _fig_iplot(self,validate=True,sharing=None,filename='',online=None,**kwargs):
	"""
	Plots a figure in IPython

	validate : bool
		If True then all values are validated before 
		it is charted
	sharing : string
		Sets the sharing level permission
			public - anyone can see this chart
			private - only you can see this chart
			secret - only people with the link can see the chart
	filename : string
		Name to be used to save the file in the server
	online : bool
		If True then charts are rendered in the server 

	Other Kwargs
	============

		legend : bool
			If False then the legend will not be shown		
	"""
	return iplot(self,validate=True,sharing=None,filename='',online=None,**kwargs)


pd.DataFrame.to_iplot=_to_iplot
pd.DataFrame.scatter_matrix=_scatter_matrix
pd.DataFrame.figure=_figure
pd.DataFrame.layout=_layout
pd.DataFrame.ta_plot=_ta_plot
pd.DataFrame.iplot=_iplot
pd.DataFrame.ta_figure=_ta_figure
pd.Series.ta_figure=_ta_figure
pd.Series.ta_plot=_ta_plot
pd.Series.figure=_figure
pd.Series.to_iplot=_to_iplot
pd.Series.iplot=_iplot
Figure.iplot=_fig_iplot


