################
#   tools.py   #
################

import plotly.plotly as py
import plotly.offline as py_offline
from plotly.graph_objs import Figure,XAxis,YAxis,Annotation,Layout,Data,ErrorY,ErrorX,Scatter,Line
#from .plotlytools import getLayout
from .colors import normalize,to_rgba
from . import auth
from .utils import merge_dict
import numpy as np
import copy

def strip_figures(figure):
	"""
	Strips a figure into multiple figures with a trace on each of them

	Parameters:
	-----------
		figure : Figure
			Plotly Figure
	"""
	fig=[]
	for trace in figure['data']:
		fig.append(Figure(data=[trace],layout=figure['layout']))
	return fig


def get_base_layout(figs):
	"""
	Generates a layout with the union of all properties of multiple
	figures' layouts

	Parameters:
	-----------
		fig : list(Figures)
			List of Plotly Figures
	"""
	layout={}
	for fig in figs:
		for k,v in list(fig['layout'].items()):
			layout[k]=v
	return layout

def figures(df,specs):
	"""
	Generates multiple Plotly figures for a given DataFrame

	Parameters:
	-----------
		df : DataFrame
			Pandas DataFrame
		specs : list(dict)
			List of dictionaries with the properties 
			of each figure. 
			All properties avaialbe can be seen with
			help(cufflinks.pd.DataFrame.iplot)
	"""
	figs=[]
	for spec in specs:
		figs.append(df.figure(**spec))
	return figs

def merge_figures(figures):
	figure=Figure()
	data=Data()
	for fig in figures:
		for trace in fig['data']:
			data.append(trace)
	layout=get_base_layout(figures)
	figure['data']=data
	figure['layout']=layout
	return figure

def subplots(figures,shape=None,
				  shared_xaxes=False, shared_yaxes=False,
				  start_cell='top-left', theme=None,base_layout=None,
				  **kwargs):
	"""
	Generates a subplot view for a set of figures
	This is a wrapper for plotly.tools.make_subplots

	Parameters:
	-----------
		figures : [Figures]
			List of Plotly Figures
		shape : (rows,cols)
			Tuple indicating the size of rows and columns
			If omitted then the layout is automatically set
		shared_xaxes : bool
			Assign shared x axes.
			If True, subplots in the same grid column have one common
			shared x-axis at the bottom of the grid.
		shared_yaxes : bool
			Assign shared y axes.
			If True, subplots in the same grid row have one common
			shared y-axis on the left-hand side of the grid.
		start_cell : string
				'bottom-left'
				'top-left'
			Choose the starting cell in the subplot grid used to set the
			domains of the subplots.
		theme : string
			Layout Theme
				solar
				pearl
				white		
			see cufflinks.getThemes() for all 
			available themes
		horizontal_spacing : float
				[0,1]
			Space between subplot columns.
		vertical_spacing : float
			Space between subplot rows.
		specs : list of dicts
			Subplot specifications.
				ex1: specs=[[{}, {}], [{'colspan': 2}, None]]
				ex2: specs=[[{'rowspan': 2}, {}], [None, {}]]

			- Indices of the outer list correspond to subplot grid rows
			  starting from the bottom. The number of rows in 'specs'
			  must be equal to 'rows'.

			- Indices of the inner lists correspond to subplot grid columns
			  starting from the left. The number of columns in 'specs'
			  must be equal to 'cols'.

			- Each item in the 'specs' list corresponds to one subplot
			  in a subplot grid. (N.B. The subplot grid has exactly 'rows'
			  times 'cols' cells.)

			- Use None for blank a subplot cell (or to move pass a col/row span).

			- Note that specs[0][0] has the specs of the 'start_cell' subplot.

			- Each item in 'specs' is a dictionary.
				The available keys are:

				* is_3d (boolean, default=False): flag for 3d scenes
				* colspan (int, default=1): number of subplot columns
					for this subplot to span.
				* rowspan (int, default=1): number of subplot rows
					for this subplot to span.
				* l (float, default=0.0): padding left of cell
				* r (float, default=0.0): padding right of cell
				* t (float, default=0.0): padding right of cell
				* b (float, default=0.0): padding bottom of cell

			- Use 'horizontal_spacing' and 'vertical_spacing' to adjust
			  the spacing in between the subplots.

		insets : list of dicts
			Inset specifications.

			- Each item in 'insets' is a dictionary.
				The available keys are:

				* cell (tuple, default=(1,1)): (row, col) index of the
					subplot cell to overlay inset axes onto.
				* is_3d (boolean, default=False): flag for 3d scenes
				* l (float, default=0.0): padding left of inset
					  in fraction of cell width
				* w (float or 'to_end', default='to_end') inset width
					  in fraction of cell width ('to_end': to cell right edge)
				* b (float, default=0.0): padding bottom of inset
					  in fraction of cell height
				* h (float or 'to_end', default='to_end') inset height
					  in fraction of cell height ('to_end': to cell top edge)
	"""
	if not isinstance(figures,list):
		figures=[figures]

	if shape:
		rows,cols=shape
		if len(figures)>rows*cols:
			raise Exception("Invalid shape for the number of figures given")
	else:
		if len(figures)==1:
			cols=1
			rows=1
		else:
			cols=2
			rows=len(figures)/2+len(figures)%2
	sp=get_subplots(rows=rows,cols=cols,
				  shared_xaxes=shared_xaxes, shared_yaxes=shared_yaxes,
				  start_cell=start_cell, theme=theme,base_layout=base_layout,
				  **kwargs)
	list_ref=(col for row in sp._grid_ref for col in row)
	for i in range(len(figures)):
		while True:
			lr=next(list_ref)
			if lr is not None:
				break
		for _ in figures[i]['data']:
			for axe in lr:
				_.update({'{0}axis'.format(axe[0]):axe})
			sp['data'].append(_)
	# Remove extra plots
	for k in list(sp['layout'].keys()):
		try:
			if int(k[-1])>len(figures):
				del sp['layout'][k]
		except:
			pass
	return sp


def get_subplots(rows=1,cols=1,
				  shared_xaxes=False, shared_yaxes=False,
				  start_cell='top-left', theme=None,base_layout=None,
				  **kwargs):

	"""
	Generates a subplot view for a set of figures

	Parameters:
	-----------
		rows : int 
			Number of rows
		cols : int
			Number of cols
		shared_xaxes : bool
			Assign shared x axes.
			If True, subplots in the same grid column have one common
			shared x-axis at the bottom of the gird.
		shared_yaxes : bool
			Assign shared y axes.
			If True, subplots in the same grid row have one common
			shared y-axis on the left-hand side of the gird.
		start_cell : string
				'bottom-left'
				'top-left'
			Choose the starting cell in the subplot grid used to set the
			domains of the subplots.
		theme : string
			Layout Theme
				solar
				pearl
				white		
			see cufflinks.getThemes() for all 
			available themes
		horizontal_spacing : float
				[0,1]
			Space between subplot columns.
		vertical_spacing : float
			Space between subplot rows.
		specs : list of dicts
			Subplot specifications.
				ex1: specs=[[{}, {}], [{'colspan': 2}, None]]
				ex2: specs=[[{'rowspan': 2}, {}], [None, {}]]

			- Indices of the outer list correspond to subplot grid rows
			  starting from the bottom. The number of rows in 'specs'
			  must be equal to 'rows'.

			- Indices of the inner lists correspond to subplot grid columns
			  starting from the left. The number of columns in 'specs'
			  must be equal to 'cols'.

			- Each item in the 'specs' list corresponds to one subplot
			  in a subplot grid. (N.B. The subplot grid has exactly 'rows'
			  times 'cols' cells.)

			- Use None for blank a subplot cell (or to move pass a col/row span).

			- Note that specs[0][0] has the specs of the 'start_cell' subplot.

			- Each item in 'specs' is a dictionary.
				The available keys are:

				* is_3d (boolean, default=False): flag for 3d scenes
				* colspan (int, default=1): number of subplot columns
					for this subplot to span.
				* rowspan (int, default=1): number of subplot rows
					for this subplot to span.
				* l (float, default=0.0): padding left of cell
				* r (float, default=0.0): padding right of cell
				* t (float, default=0.0): padding right of cell
				* b (float, default=0.0): padding bottom of cell

			- Use 'horizontal_spacing' and 'vertical_spacing' to adjust
			  the spacing in between the subplots.

		insets : list of dicts
			Inset specifications.

			- Each item in 'insets' is a dictionary.
				The available keys are:

				* cell (tuple, default=(1,1)): (row, col) index of the
					subplot cell to overlay inset axes onto.
				* is_3d (boolean, default=False): flag for 3d scenes
				* l (float, default=0.0): padding left of inset
					  in fraction of cell width
				* w (float or 'to_end', default='to_end') inset width
					  in fraction of cell width ('to_end': to cell right edge)
				* b (float, default=0.0): padding bottom of inset
					  in fraction of cell height
				* h (float or 'to_end', default='to_end') inset height
					  in fraction of cell height ('to_end': to cell top edge)
	"""

	if not theme:
		theme = auth.get_config_file()['theme']

	layout= base_layout if base_layout else getLayout(theme)
	sp=py.plotly.tools.make_subplots(rows=rows,cols=cols,shared_xaxes=shared_xaxes,
										   shared_yaxes=shared_yaxes,print_grid=False,
											start_cell=start_cell,**kwargs)
	for k,v in list(layout.items()):
		if not isinstance(v,XAxis) and not isinstance(v,YAxis):
			sp['layout'].update({k:v})
			
	if 'subplot_titles' in kwargs:
		if 'annotations' in layout:
			annotation=sp['layout']['annotations'][0]
		else:
			annotation=getLayout(theme,annotations=Annotation(text=''))['annotations']
		for ann in sp['layout']['annotations']:
			ann['font'].update(color=annotation['font']['color'])

	def update_items(sp_item,layout,axis):
		for k,v in list(layout[axis].items()):
			sp_item.update({k:v})

	for k,v in list(sp['layout'].items()):
		if isinstance(v,XAxis):
			update_items(v,layout,'xaxis1')
		elif isinstance(v,YAxis):
			update_items(v,layout,'xaxis1')
			
	return sp

# Candlesticks and OHLC

def _ohlc_dict(df):
	c_dir={}
	ohlc=['open','high','low','close']
	for c in df.columns:
		for _ in ohlc:
			if _ in c.lower():
				c_dir[_]=c
	return c_dir

def get_ohlc(df,up_color=None,down_color=None,theme=None,**kwargs):
	ohlc=['open','high','low','close']
	if not theme:
		theme = auth.get_config_file()['theme']    
	c_dir=_ohlc_dict(df)
	args=[df[c_dir[_]] for _ in ohlc]
	args.append(df.index)
	fig=py.plotly.tools.FigureFactory.create_ohlc(*args,**kwargs)
	ohlc_bars=Figure()
	ohlc_bars['data']=fig['data']
	ohlc_bars['layout']=fig['layout']
	data=ohlc_bars['data']
	if up_color:
		data[0]['line'].update(color=normalize(up_color))
	if down_color:
		data[1]['line'].update(color=normalize(down_color))
	ohlc_bars['layout']['hovermode']='closest'
	layout=getLayout(theme=theme)
	ohlc_bars['layout']=merge_dict(layout,ohlc_bars['layout'])
	return ohlc_bars

def get_candle(df,up_color=None,down_color=None,theme=None,**kwargs):
	ohlc=['open','high','low','close']
	if not theme:
		theme = auth.get_config_file()['theme']    
	layout=getLayout(theme=theme)
	c_dir=_ohlc_dict(df)
	args=[df[c_dir[_]] for _ in ohlc]
	args.append(df.index)
	fig=py.plotly.tools.FigureFactory.create_candlestick(*args,**kwargs)
	candle=Figure()
	candle['data']=fig['data']
	candle['layout']=layout
	data=candle['data']
	def update_color(n,color):
		data[n]['fillcolor']=normalize(color)
		data[n]['line'].update(color=normalize(color))
	if up_color:
		update_color(0,up_color)
	if down_color:
		update_color(1,down_color)
	candle['layout']['hovermode']='closest'
	layout=getLayout(theme=theme)
	candle['layout']=merge_dict(layout,candle['layout'])
	return candle

def scatter_matrix(df,theme=None,bins=10,color='grey',size=2):
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
	"""
	if not theme:
		theme = auth.get_config_file()['theme']
	
	figs=[]
	for i in df.columns:
		for j in df.columns:
			if i==j:
				fig=df.iplot(kind='histogram',keys=[i],asFigure=True,bins=bins)
				figs.append(fig)
			else:
				figs.append(df.iplot(kind='scatter',mode='markers',x=j,y=i,asFigure=True,size=size,colors=[color]))
	layout=getLayout(theme)
	layout['xaxis1'].update(showgrid=False)
	layout['yaxis1'].update(showgrid=False)
	sm=subplots(figs,shape=(len(df.columns),len(df.columns)),shared_xaxes=False,shared_yaxes=False,
					  horizontal_spacing=.05,vertical_spacing=.07,base_layout=layout)
	sm['layout'].update(bargap=.02,showlegend=False)
	return sm

## Trace dictionary

@property
def trace_dict(self):
	d={}
	for trace in range(len(self['data'])):
		trace_=self['data'][trace]
		name = '{0}_'.format(trace_['name']) if trace_['name'] in d else trace_['name']
		d[name]=trace
	return d


## Axis Definition

def get_ref(figure):
	d={}
	for trace in figure['data']:
		name = '{0}_'.format(trace['name']) if trace['name'] in d else trace['name']
		x = trace['xaxis'] if 'xaxis' in trace else 'x1'
		y = trace['yaxis'] if 'yaxis' in trace else 'y1'
		d[name]=(x,y)
	return d

def get_def(figure):
	d={}
	items=list(figure['layout']['scene'].items()) if 'scene' in figure['layout'] else list(figure['layout'].items())
	for k,v in items:
		if 'axis' in k:
			d['{0}{1}'.format(k[0],1 if k[-1]=='s' else k[-1])]=v
	return d

def get_len(figure):
	d={}
	keys=list(figure['layout']['scene'].keys()) if 'scene' in figure['layout'] else list(figure['layout'].keys())
	for k in keys:
		if 'axis' in k:
			d[k[0]] = d[k[0]]+1 if k[0] in d else 1
	return d

def get_which(figure):
	d={}
	keys=list(figure['layout']['scene'].keys()) if 'scene' in figure['layout'] else list(figure['layout'].keys())
	for k in keys:
		if 'axis' in k:
			if k[0] in d:
				d[k[0]].append('{0}{1}'.format(k[0],k[-1]))
			else:
				d[k[0]]=['{0}{1}'.format(k[0],'1' if k[-1]=='s' else k[-1])]
	return d

def get_ref_axis(figure):
	d={}
	for k,v in list(get_ref(figure).items()):
		for i in v:
			if i not in d:
				d[i]=[]
			d[i].append(k)
	return d

def get_dom(figure):
	d={}
	which=get_which(figure)
	axis_def=get_def(figure)
	for k in ('x','y'):
		d[k]={}
		for y in which[k]:
			item=axis_def[y]
			domain='[0.0, 1.0]' if 'domain' not in item else str(item['domain'])
			if domain not in d[k]:
				d[k][domain]={}
			s='left' if k=='y' else 'bottom'
			side=s if 'side' not in item else item['side']
			d[k][domain][side]=y
	return d

@property
def axis(self):
	return {'ref':get_ref(self),
			'ref_axis':get_ref_axis(self),
			'def':get_def(self),
			'len':get_len(self),
			'which':get_which(self),
			'dom':get_dom(self)}    

### Set Axis


def _set_axis(self,traces,on=None,side='right',title=''):
	"""
	Sets the axis in which each trace should appear
	If the axis doesn't exist then a new axis is created

	Parameters:
	-----------
		traces : list(str)
			List of trace names 
		on : string
			The axis in which the traces should be placed. 
			If this is not indicated then a new axis will be
			created
		side : string
			Side where the axis will be placed
				'left'
				'right'
		title : string
			Sets the title of the axis
			Applies only to new axis
	"""
	fig=Figure(self.copy())
	if not isinstance(traces,list):
		traces=[traces]

	def update_data(trace,y):
		anchor=fig.axis['def'][y]['anchor'] if 'anchor' in fig.axis['def'][y] else 'x1'
		idx=fig.trace_dict[trace] if isinstance(trace,str) else trace
		fig['data'][idx]['xaxis']=anchor
		fig['data'][idx]['yaxis']=y

	for trace in traces:
		if on:
			if on not in fig.axis['def']:
				raise Exception('"on" axis does not exists: {0}'.format(on))
			update_data(trace,y=on)
		else:
			curr_x,curr_y=fig.axis['ref'][trace]
			domain='[0.0, 1.0]' if 'domain' not in fig.axis['def'][curr_y] else str(fig.axis['def'][curr_y]['domain'])
			try:
				new_axis=fig.axis['dom']['y'][domain][side]
			except KeyError:
				axis=YAxis(fig.axis['def'][curr_y].copy())
				### check overlaying values
				axis.update(title=title,overlaying=curr_y,side=side,anchor=curr_x)
				axis_idx=str(fig.axis['len']['y']+1)
				fig['layout']['yaxis{0}'.format(axis_idx)]=axis
				new_axis='y{0}'.format(axis_idx)
			update_data(trace,y=new_axis)


	for k in list(fig.axis['def'].keys()):
		id='{0}axis{1}'.format(k[0],k[-1:])
		if k not in fig.axis['ref_axis']:
			try:
				del fig['layout'][id]
			except KeyError:
				pass

	return fig

### Shapes

def get_shape(kind='line',x=None,y=None,x0=None,y0=None,x1=None,y1=None,span=0,color='red',dash='solid',width=1,
				fillcolor=None,fill=False,opacity=1,xref='x',yref='y'):
	"""
	Returns a plotly shape

	Parameters:
	-----------
		kind : string
			Shape kind
				line
				rect
				circle
		x : float 
			x values for the shape. 
			This assumes x0=x1
		x0 : float
			x0 value for the shape
		x1 : float
			x1 value for the shape
		y : float 
			y values for the shape. 
			This assumes y0=y1
		y0 : float
			y0 value for the shape
		y1 : float
			y1 value for the shape
		color : string
			color for shape line
		dash : string
			line style
				solid
				dash
				dashdot
				dot 
		width : int
			line width
		fillcolor : string
			shape fill color
		fill : bool
			If True then fill shape 
			If not fillcolor then the 
			line color will be used
		opacity : float [0,1]
			opacity of the fill 
		xref : string
			Sets the x coordinate system 
			which this object refers to
				'x'
				'paper'
				'x2' etc
		yref : string
			Sets the y coordinate system 
			which this object refers to
				'y'
				'paper'
				'y2' etc
	"""
	if not x1:
		if not x0:
			if not x:
				xref='paper'
				x0=0
				x1=1
			else:
				x0=x1=x
		else:
			x1=x0
	if not y1:
		if not y0:
			if not y:
				yref='paper'
				y0=0
				y1=1
			else:
				y0=y1=y
		else:
			y1=y0

	shape = {	'x0':x0,
				'y0':y0,
				'x1':x1,
				'y1':y1,
				'line' : {
					'color':normalize(color),
					'width':width,
					'dash':dash				
					},
				'xref':xref,
				'yref':yref
				}

	if kind=='line':	
		shape['type']='line'

	elif kind=='circle':
		shape['type']='circle'
		
	elif kind=='rect':
		shape['type']='rect'
	else:
		raise Exception("Invalid or unkown shape type : {0}".format(kind))

	if (fill or fillcolor) and kind!='line':
		fillcolor = color if not fillcolor else fillcolor
		fillcolor=to_rgba(normalize(fillcolor),opacity)
		shape['fillcolor']=fillcolor

	return shape

### Error Bars

def get_error_bar(axis='y',type='data',values=None,values_minus=None,color=None,thickness=1,width=5,
				 opacity=1):
	error=ErrorY() if axis=='y' else ErrorX()
	if type=='data':
		if isinstance(values,list) or isinstance(values,np.ndarray):
			if values_minus:
				if len(values)!=len(values_minus):
					raise Exception('Array values need to be of same length')
				error.update(symmetric=False,arrayminus=values_minus)
			error.update(array=values)
		else:
			if values_minus:
				if isinstance(values_minus,list) or isinstance(a,np.ndarray):
					raise Exception('Values should be of same type (int, float)')
				error.udpate(symmetric=False,valueminus=values_minus)
			error.update(value=values)
	elif type in ['percent','constant']:
		if isinstance(values,list) or isinstance(values,np.ndarray):
			raise Exception('Value should be of type (int, float)')
		error.update(value=values)
	elif type=='sqrt':
		pass
	else:
		raise Exception('Invalid type: {0}'.format(type))
	error.update(type=type,thickness=thickness,width=width,visible=True,opacity=opacity)
	if color:
		error.update(color=normalize(color))
	return error

def set_errors(figure,trace=None,axis='y',type='data',values=None,values_minus=None,color=None,thickness=1,width=None,
				 opacity=None,**kwargs):
	figure=Figure(copy.deepcopy(figure))
	if 'value' in kwargs:
		values=kwargs['value']
	data=figure['data']
	if 'continuous' not in type:
		width=width if width else 5
		opacity=opacity if opacity else 1
		error=get_error_bar(axis=axis,type=type,values=values,values_minus=values_minus,
							color=color,thickness=thickness,width=width,opacity=opacity)
		if trace:
			data[figure.trace_dict[trace]].update({'error_{0}'.format(axis):error})
		else:
			for trace in data:
				trace.update({'error_{0}'.format(axis):error})
	else:
		width=width if width else .5
		opacity=opacity if opacity else .3
		def get_traces(trace,value,type,color=None,width=.2,opacity=.3):
			if 'percent' in type:
				y_up=trace['y']*(1+value/100.00)
				y_down=trace['y']*(1-value/100.00)
			else:
				y_up=trace['y']+value
				y_down=trace['y']-value            
			y=trace['y']
			upper=Scatter(y=y_up,mode='lines',showlegend=False,
							 line=Line(width=width),x=trace['x'])
			if 'yaxis' in trace:
				upper['yaxis']=trace['yaxis']
			if color:
				color=normalize(color)
			else:
				if 'color' in trace['line']:
					color=trace['line']['color']
				else:
					color='charcoal'
			upper['line']['color']=color
			lower=upper.copy()
			name=trace['name']+'_' if 'name' in trace else ''
			upper.update(name=name+'upper')
			color=to_rgba(normalize(color),opacity)
			lower.update(fill='tonexty',fillcolor=color,name=name+'lower',y=y_down)
			return upper,lower
		if trace:
			traces=[figure.trace_dict[trace]]
		else:
			traces=list(range(len(figure['data'])))
		for i in traces:
				trace=figure['data'][i]
				upper,lower=get_traces(trace,values,type,color=color,width=width,opacity=opacity)
				figure['data'].extend([upper,lower]) 
	return figure

### Offline

def go_offline(offline=True):
	if offline:
		py_offline.init_notebook_mode()
		py_offline.__PLOTLY_OFFLINE_INITIALIZED=True
	else:
		py_offline.__PLOTLY_OFFLINE_INITIALIZED=False

def is_offline():
	return py_offline.__PLOTLY_OFFLINE_INITIALIZED

######################
#   plotlytools.py   #
######################

import pandas as pd
import plotly.plotly as py

#from . import tools
import sys
tools = sys.modules[__name__]

from . import offline
from plotly.graph_objs import *
from collections import defaultdict
from .colors import normalize,get_scales,colorgen,to_rgba
from .themes import THEMES
from .utils import check_kwargs
from IPython.display import display,Image
import time
import copy
from . import auth
from . import ta



def getTheme(theme):
	return THEMES[theme]

def getThemes():
	return list(THEMES.keys())

__LAYOUT_KWARGS = ['legend','vline','hline','vspan','hspan','shapes','logx','logy']
__TA_KWARGS = ['min_period','center','freq','how','rsi_upper','rsi_lower','boll_std','fast_period',
			   'slow_period','signal_period','study_colors','study_colorscale']

def getLayout(theme=None,title='',xTitle='',yTitle='',zTitle='',barmode='',bargap=None,bargroupgap=None,
				gridcolor=None,zerolinecolor=None,margin=None,annotations=False,is3d=False,**kwargs):
	"""
	Generates a plotly Layout

	Parameters:
	-----------
		theme : string
			Layout Theme
				solar
				pearl
				white
		title : string
			Chart Title
		xTitle : string
			X Axis Title
		yTitle : string
			Y Axis Title
		zTitle : string
			Z Axis Title
			Applicable only for 3d charts
		barmode : string 
			Mode when displaying bars
				group
				stack
				overlay
		bargap : float
			Sets the gap between bars
				[0,1)
			Applicabe for bar and histogram plots
		bargroupgap : float
			Set the gap between groups
				[0,1)
			Applicabe for bar and histogram plots			
		gridcolor : string
				grid color
		zerolinecolor : string
				zero line color
		margin : dict or tuple
				Dictionary (l,r,b,t) or
				Tuple containing the left,
				right, bottom and top margins
		annotations : dictionary
			Dictionary of annotations
			{x_point : text}
		is3d : bool
			Indicates if the layout is for a 3D chart
	"""


	for key in list(kwargs.keys()):
		if key not in __LAYOUT_KWARGS:
			raise Exception("Invalid keyword : '{0}'".format(key))
	
	if not theme:
		theme = auth.get_config_file()['theme']

	size=None
	if annotations:
		if 'font' in annotations:
			if 'size' in annotations['font']:
				size=annotations['font']['size']

	def update_annotations(annotations,font_color,arrow_color):
		if annotations:
			if isinstance(annotations,dict):
				annotations=[annotations]
			for i in annotations:
				i.update(dict(arrowcolor=arrow_color,font={'color':font_color}))

	if theme=='ggplot':
		layout=Layout(legend=Legend(bgcolor='white',font={'color':'grey10'}),
						paper_bgcolor='white',plot_bgcolor='#E5E5E5',
						yaxis1=YAxis(tickfont={'color':'grey10'},gridcolor='#F6F6F6',title=yTitle,
								 titlefont={'color':'grey10'},zerolinecolor='#F6F6F6'),
						xaxis1=XAxis(tickfont={'color':'grey10'},gridcolor='#F6F6F6',title=xTitle,
								titlefont={'color':'grey10'},zerolinecolor='#F6F6F6',showgrid=True),
						titlefont={'color':'charcoal'})
		update_annotations(annotations,'grey10','grey10')

	if theme=='solar':
		layout=Layout(legend=Legend(bgcolor='charcoal',font={'color':'pearl'}),
						paper_bgcolor='charcoal',plot_bgcolor='charcoal',
						yaxis1=YAxis(tickfont={'color':'grey12'},gridcolor='grey08',title=yTitle,
								 titlefont={'color':'pearl'},zerolinecolor='grey09'),
						xaxis1=XAxis(tickfont={'color':'grey12'},gridcolor='grey08',title=xTitle,
								titlefont={'color':'pearl'},zerolinecolor='grey09'),
						titlefont={'color':'pearl'})
		update_annotations(annotations,'pearl','grey11')

	elif theme=='space':
		layout=Layout(legend=Legend(bgcolor='grey03',font={'color':'pearl'}),
						paper_bgcolor='grey03',plot_bgcolor='grey03',
						yaxis1=YAxis(tickfont={'color':'grey12'},gridcolor='grey08',title=yTitle,
								 titlefont={'color':'pearl'},zerolinecolor='grey09'),
						xaxis1=XAxis(tickfont={'color':'grey12'},gridcolor='grey08',title=xTitle,
								titlefont={'color':'pearl'},zerolinecolor='grey09'),
						titlefont={'color':'pearl'})
		update_annotations(annotations,'pearl','red')

	elif theme=='pearl':
		layout=Layout(legend=Legend(bgcolor='pearl02',font={'color':'pearl06'}),
						paper_bgcolor='pearl02',plot_bgcolor='pearl02',
						yaxis1=YAxis(tickfont={'color':'pearl06'},gridcolor='pearl04' if is3d else 'pearl03',title=yTitle,
								  titlefont={'color':'pearl06'},zeroline=False,zerolinecolor='pearl04' if is3d else 'pearl03'),
						xaxis1=XAxis(tickfont={'color':'pearl06'},gridcolor='pearl04' if is3d else 'pearl03',title=xTitle,
								  titlefont={'color':'pearl06'},zerolinecolor='pearl04' if is3d else 'pearl03'))
		update_annotations(annotations,'pearl06','pearl04')

	elif theme=='white':
		layout=Layout(legend=Legend(bgcolor='white',font={'color':'pearl06'}),
						paper_bgcolor='white',plot_bgcolor='white',
						yaxis1=YAxis(tickfont={'color':'pearl06'},gridcolor='pearl04' if is3d else 'pearl03',title=yTitle,
								  titlefont={'color':'pearl06'},zerolinecolor='pearl04' if is3d else 'pearl03'),
						xaxis1=XAxis(tickfont={'color':'pearl06'},gridcolor='pearl04' if is3d else 'pearl03',title=xTitle,
								  titlefont={'color':'pearl06'},zerolinecolor='pearl04' if is3d else 'pearl03'))
		update_annotations(annotations,'pearl06','pearl04')
	
	if barmode:
		layout.update({'barmode':barmode})
	if bargroupgap:
		layout.update({'bargroupgap':bargroupgap})
	if bargap:
		layout.update(bargap=bargap)
	if title:
		layout.update({'title':title})
	if annotations:
		if size:
			annotations['font']['size']=size
		layout.update({'annotations':annotations})
	if gridcolor:
		for k in layout:
			if 'axis' in k:
				layout[k].update(gridcolor=normalize(gridcolor))
	if zerolinecolor:
		for k in layout:
			if 'axis' in k:
				layout[k].update(zerolinecolor=normalize(zerolinecolor))
	if margin:
		if isinstance(margin,dict):
			margin=margin
		else:
			margin=dict(list(zip(('l','r','b','t'),margin)))
		layout.update(margin=margin)

	if is3d:
		zaxis=layout['xaxis1'].copy()
		zaxis.update(title=zTitle)
		scene=Scene(xaxis1=layout['xaxis1'],yaxis1=layout['yaxis1'],zaxis=zaxis)
		layout.update(scene=scene)
		del layout['xaxis1']
		del layout['yaxis1']


	## Kwargs

	if 'legend' in kwargs:
		layout['showlegend']=kwargs['legend']

	if 'logy' in kwargs:
		if kwargs['logy']:
			layout['yaxis1']['type']='log'

	if 'logx' in kwargs:
		if kwargs['logx']:
			layout['xaxis1']['type']='log'

	# Shapes 

	if any(k in kwargs for k in ['vline','hline','shapes','hspan','vspan']):
		shapes=[]

		def get_shapes(xline):
			orientation=xline[0]
			xline=kwargs[xline]
			if isinstance(xline,list):
				for x_i in xline:
					if isinstance(x_i,dict):
						x_i['kind']='line'
						shapes.append(tools.get_shape(**x_i))
					else:						
						if orientation=='h':
							shapes.append(tools.get_shape(kind='line',y=x_i))
						else:
							shapes.append(tools.get_shape(kind='line',x=x_i))
			elif isinstance(xline,dict):
				shapes.append(tools.get_shape(**xline))
			else:
				if orientation=='h':
					shapes.append(tools.get_shape(kind='line',y=xline))			
				else:
					shapes.append(tools.get_shape(kind='line',x=xline))			

		def get_span(xspan):
			orientation=xspan[0]
			xspan=kwargs[xspan]
			if isinstance(xspan,list):
				for x_i in xspan:
					if isinstance(x_i,dict):
						x_i['kind']='rect'
						shapes.append(tools.get_shape(**x_i))
					else:
						v0,v1=x_i
						if orientation=='h':
							shapes.append(tools.get_shape(kind='rect',y0=v0,y1=v1,fill=True,opacity=.5))
						else:
							shapes.append(tools.get_shape(kind='rect',x0=v0,x1=v1,fill=True,opacity=.5))
			elif isinstance(xspan,dict):
				xspan['kind']='rect'
				shapes.append(tools.get_shape(**xspan))
			elif isinstance(xspan,tuple):
				v0,v1=xspan
				if orientation=='h':
					shapes.append(tools.get_shape(kind='rect',y0=v0,y1=v1,fill=True,opacity=.5))
				else:
					shapes.append(tools.get_shape(kind='rect',x0=v0,x1=v1,fill=True,opacity=.5))
			else:
				raise Exception('Invalid value for {0}span: {1}'.format(orientation,xspan))

		if 'hline' in kwargs:
			get_shapes('hline')
		if 'vline' in kwargs:
			get_shapes('vline')
		if 'hspan' in kwargs:
			get_span('hspan')
		if 'vspan' in kwargs:
			get_span('vspan')
		if 'shapes' in kwargs:
			shapes_=kwargs['shapes']
			if isinstance(shapes_,list):
				for i in shapes_:
					shp=i if 'type' in i else tools.get_shape(**i)
					shapes.append(shp)
			elif isinstance(shapes_,dict):
					shp=shapes_ if 'type' in shapes_ else tools.get_shape(**shapes_)
					shapes.append(shp)
			else:
				raise Exception("Shapes need to be either a dict or list of dicts")


		layout['shapes']=shapes

	def updateColors(layout):
		for k,v in list(layout.items()):
			if isinstance(v,dict):
				updateColors(v)
			else:
				if isinstance(v,list):
					for _ in v:
						if isinstance(_,dict):
							updateColors(_)
				if 'color' in k.lower():
					if 'rgba' not in v:
						layout[k]=normalize(v)
		return layout
	
	return updateColors(layout)

def getAnnotations(df,annotations):
	"""
	Generates an annotations object

	Parameters:
	-----------
		df : DataFrame
			Original DataFrame of values
		annotations : dictionary 
			Dictionary of annotations
			{x_point : text}
	"""
	l=[]
	if 'title' in annotations:
		l.append(
				Annotation(
						text=annotations['title'],
						showarrow=False,
						x=0,
						y=1,
						xref='paper',
						yref='paper',
						font={'size':24}
					)
			)
	else:
		for k,v in list(annotations.items()):
			maxv=df.ix[k].sum() if k in df.index else 0
			l.append(
					 Annotation(
								x=k,
								y=maxv,
								xref='x',
								yref='y',
								text=v,
								showarrow=True,
								arrowhead=7,
								ax=0,
								ay=-100,
								textangle=-90
								)
					 )
	return Annotations(l)

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
		width=3,sortbars=False,keys=False,bestfit=False,bestfit_colors=None,asDates=False,
		asTimestamp=False,text=None,**kwargs):
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
	for key in keys:
		lines[key]={}
		lines[key]["x"]=x
		lines[key]["y"]=df[key].fillna('').values
		lines[key]["name"]=key
		if text is not None:
			lines[key]["text"]=text
		if 'bar' in kind:
			lines[key]["marker"]={'color':to_rgba(colors[key],.6),'line':{'color':colors[key],'width':1}}
		else:
			lines[key]["line"]={'color':colors[key],'width':width}
			lines[key]["mode"]=mode
			if 'marker' in mode:
				lines[key]["marker"]=Marker(symbol=symbol,size=size)
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
	return Data(lines_plotly)

def _iplot(self,data=None,layout=None,filename='',world_readable=None,
			kind='scatter',title='',xTitle='',yTitle='',zTitle='',theme=None,colors=None,colorscale=None,fill=False,width=None,
			mode='lines',symbol='dot',size=12,barmode='',sortbars=False,bargap=None,bargroupgap=None,bins=None,histnorm='',
			histfunc='count',orientation='v',boxpoints=False,annotations=None,keys=False,bestfit=False,
			bestfit_colors=None,categories='',x='',y='',z='',text='',gridcolor=None,zerolinecolor=None,margin=None,
			labels=None,values=None,secondary_y='',subplots=False,shape=None,error_x=None,error_y=None,error_type='data',
			asFrame=False,asDates=False,asFigure=False,
			asImage=False,dimensions=(1116,587),asPlot=False,asUrl=False,online=None,**kwargs):
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
		world_readable : bool
			If False then it will be saved as a private file
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
		colors : list or dict
			{key:color} to specify the color for each column
			[colors] to use the colors in the defined order
		colorscale : str 
			Color scale name
			If the color name is preceded by a minus (-) 
			then the scale is inversed
			Only valid if 'colors' is null
			See cufflinks.colors.scales() for available scales
		fill : bool
			Filled Traces		
		width : int
			Line width	
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
	"""

	# Look for invalid kwargs
	valid_kwargs = ['color','opacity','column','columns','labels','text']
	PIE_KWARGS=['sort','pull','hole','textposition','textinfo','linecolor']
	OHLC_KWARGS=['up_color','down_color']
	SUBPLOT_KWARGS=['horizontal_spacing', 'vertical_spacing',
					'specs', 'insets','start_cell','shared_xaxes','shared_yaxes','subplot_titles']
	ERROR_KWARGS=['error_trace','error_values_minus','error_color','error_thickness',
					'error_width','error_opacity']
	kwargs_list = [__LAYOUT_KWARGS,OHLC_KWARGS,PIE_KWARGS,SUBPLOT_KWARGS,ERROR_KWARGS]
	[valid_kwargs.extend(_) for _ in kwargs_list]
	

	for key in list(kwargs.keys()):
		if key not in valid_kwargs:
			raise Exception("Invalid keyword : '{0}'".format(key))

	# Setting default values
	if not colors:
		colors=kwargs['color'] if 'color' in kwargs else colors
	if isinstance(colors,str):
		colors=[colors]
	opacity=kwargs['opacity'] if 'opacity' in kwargs else 0.8

	# Get values from config theme
	if theme is None:
		theme = auth.get_config_file()['theme']
	theme_config=getTheme(theme)
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

	# We assume we are good citizens
	validate=True
	

	if not layout:
		l_kwargs=dict([(k,kwargs[k]) for k in __LAYOUT_KWARGS if k in kwargs])
		if annotations:
				annotations=getAnnotations(self.copy(),annotations)
		layout=getLayout(theme=theme,xTitle=xTitle,yTitle=yTitle,zTitle=zTitle,title=title,barmode=barmode,
								bargap=bargap,bargroupgap=bargroupgap,annotations=annotations,gridcolor=gridcolor,
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
												line=Line(width=width)),textfont=getLayout(theme=theme)['xaxis1']['titlefont'])
					if '3d' in kind:
						_data=Scatter3d(x=_x,y=_y,z=_z,mode=mode,name=_,
								marker=Marker(color=colors[_],symbol=symbol,size=_size,opacity=opacity,
												line=Line(width=width)),textfont=getLayout(theme=theme)['xaxis1']['titlefont'])
					else:
						_data=Scatter(x=_x,y=_y,mode=mode,name=_,
								marker=Marker(color=colors[_],symbol=symbol,size=_size,opacity=opacity,
												line=Line(width=width)),textfont=getLayout(theme=theme)['xaxis1']['titlefont'])
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
				data=df.to_iplot(colors=colors,colorscale=colorscale,kind=kind,fill=fill,width=width,sortbars=sortbars,keys=keys,
						bestfit=bestfit,bestfit_colors=bestfit_colors,asDates=asDates,mode=mode,symbol=symbol,size=size,
						text=text,**kwargs)				
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
								line=Line(width=width),textfont=getLayout(theme=theme)['xaxis1']['titlefont'])
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
						__=Histogram(x=df[_].values.tolist(),marker=Marker(color=clrs[_]),name=_,
								line=Line(width=width),orientation=orientation,
								opacity=kwargs['opacity'] if 'opacity' in kwargs else .8, histfunc=histfunc, 
								histnorm=histnorm) 
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
				x=self[x].values.tolist() if x else self.index.values.tolist()
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
			elif kind in ['candle','ohlc']:
				d=tools._ohlc_dict(self)
				if len(list(d.keys()))!=4:
					raise Exception("OHLC type of charts require an Open, High, Low and Close column")				
				ohlc_kwargs=check_kwargs(kwargs,OHLC_KWARGS)
				if kind=='candle':					
					fig=tools.get_candle(self,theme=theme,**ohlc_kwargs)
				else:
					fig=tools.get_ohlc(self,theme=theme,**ohlc_kwargs)
				if bestfit:
					df=self.copy()
					bf=_to_iplot(self[d['close']],bestfit=True,bestfit_colors=bestfit_colors,asTimestamp=True)
					fig['data'].append(bf[1])
				data=fig['data']
				layout=fig['layout']
	if world_readable is None:
			world_readable = auth.get_config_file()['world_readable']

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
		py.image.save_as(figure,filename='img/'+filename,format='png',
			width=dimensions[0],height=dimensions[1])
		return display(Image('img/'+filename+'.png'))
	elif asPlot:
		return py.plot(figure,world_readable=world_readable,filename=filename,validate=validate)
	elif asUrl:
		return py.plot(figure,world_readable=world_readable,filename=filename,validate=validate,auto_open=False)
	else:
		return iplot(figure,world_readable=world_readable,filename=filename,validate=validate,online=online)


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


def _scatter_matrix(self,theme=None,bins=10,color='grey',size=2, **iplot_kwargs):
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
	return iplot(tools.scatter_matrix(self,theme=theme,bins=bins,color=color,size=size), **iplot_kwargs)

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

def iplot(data_or_figure,validate=True,world_readable=False,filename='',online=None):
	if offline.is_offline() and not online:
		show_link = auth.get_config_file()['offline_show_link']
		link_text = auth.get_config_file()['offline_link_text']
		return offline.py_offline.iplot(data_or_figure,show_link=show_link,link_text=link_text)
	else:
		if 'layout' in data_or_figure:
			validate = False if 'shapes' in data_or_figure['layout'] else validate
		return py.iplot(data_or_figure,validate=validate,world_readable=world_readable,
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
			 world_readable=None,filename='',**iplot_kwargs):
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
	"""
	if 'columns' in iplot_kwargs:
		column=iplot_kwargs['columns']
		del iplot_kwargs['columns']
	if 'period' in iplot_kwargs:
		periods=iplot_kwargs['period']
		del iplot_kwargs['periods']
	if world_readable is None:
			world_readable = auth.get_config_file()['world_readable']
	iplot_kwargs['world_readable']=world_readable

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

	study_kwargs={}
	for k in __TA_KWARGS:
		if k in iplot_kwargs:
			study_kwargs[k]=iplot_kwargs[k]
			del iplot_kwargs[k]
	if study=='rsi':
		rsi_upper=study_kwargs['rsi_upper'] if 'rsi_upper' in study_kwargs else 70
		rsi_lower=study_kwargs['rsi_lower'] if 'rsi_lower' in study_kwargs else 30
		if include:
			fig_0=self.figure(**iplot_kwargs)
			iplot_kwargs['colors']='blue' if 'study_colors' not in study_kwargs else study_kwargs['study_colors']
			df=ta.rsi(self,periods=periods,column=column,include=False,str=str,**study_kwargs)	
			fig_1=df.figure(**iplot_kwargs)
			subplots=get_subplots([fig_0,fig_1])
			yref='y2'
		else:
			df=ta.rsi(self,periods=periods,column=column,include=False,str=str,detail=detail,**study_kwargs)	
			iplot_kwargs['colors']='blue' if 'study_colors' not in study_kwargs else study_kwargs['study_colors']
			subplots=df.figure(**iplot_kwargs)
			yref='y1'
		shapes=[tools.get_shape(y=i,yref=yref,color=j,dash='dash') for (i,j) in [(rsi_lower,'green'),(rsi_upper,'red')]]
		subplots['layout']['shapes']=shapes
		return iplot(subplots,world_readable=world_readable,filename=filename)
	if study=='macd':
		if include:
			fig_0=self.figure(**iplot_kwargs)
			df=ta.macd(self,column=column,include=False,str=str,**study_kwargs)	
			fig_1=df.figure(**iplot_kwargs)
			subplots=get_subplots([fig_0,fig_1])
			return iplot(subplots,world_readable=world_readable,filename=filename)
		else:
			df=ta.macd(self,column=column,include=False,detail=detail,str=str,**study_kwargs)	
	if study=='sma':
		if not column:
			if isinstance(self,pd.DataFrame):
				df=self.copy()
				column=list(self.keys()).tolist()
			else:
				df=pd.DataFrame(self)
				column=list(df.keys()).tolist()
		df=ta.sma(self,periods=periods,column=column,include=include,str=str,detail=detail,**study_kwargs)	
	if study=='boll':
		if not column:
			if isinstance(self,pd.DataFrame):
				df=self.copy()
				column=list(self.keys()).tolist()
			else:
				df=pd.DataFrame(self)
				column=list(df.keys()).tolist()
		boll_std=study_kwargs['boll_std'] if 'boll_std' in study_kwargs else 2
		df=ta.boll(self,periods=periods,boll_std=boll_std,column=column,include=include,str=str,detail=True,**study_kwargs)	

	return df.iplot(**iplot_kwargs)
