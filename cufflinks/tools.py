import plotly.plotly as py
import plotly.offline as py_offline
import pandas as pd
from plotly.graph_objs import *
from .colors import normalize,to_rgba
from .themes import THEMES
from . import auth
from . import ta
from .utils import merge_dict,deep_update, check_kwargs,kwargs_from_keyword,dict_replace_keyword
import numpy as np
import copy

__LAYOUT_VALID_KWARGS = ['legend','logx','logy','layout_update','title',
					'xrange','yrange','zrange','rangeselector','rangeslider','showlegend','fontfamily']

__SHAPES_KWARGS = ['vline','hline','shapes','hspan','vspan']

__GEO_KWARGS=['projection','showframe','showlakes','coastlinecolor','countrywidth','countrycolor',
			 'showsubunits','bgcolor','showrivers','subunitcolor','showcountries','riverwidth','scope',
			 'rivercolor','lataxis','subunitwidth','showocean','oceancolor','lakecolor','showland','lonaxis',
			 'framecolor','coastlinewidth','landcolor','showcoastlines','framewidth','resolution','projection_type']

__ANN_KWARGS=['xref','yref','text','showarrow',
				 'arrowhead','ax','ay','textangle','arrowsize',
				 'arrowwidth','arrowcolor','fontcolor','fontsize','xanchor','yanchor','align']

__LAYOUT_AXIS=['autorange','autotick','backgroundcolor','categoryarray','categoryarraysrc','categoryorder',
			   'dtick','exponentformat','fixedrange','gridcolor','gridwidth','hoverformat','linecolor','linewidth',
			   'mirror','nticks','showaxeslabels','showbackground','showexponent','showgrid','showline','showspikes',
			   'showticklabels','showtickprefix','showticksuffix','spikecolor','spikesides','spikethickness',
			   'tick0','tickangle','tickcolor','tickfont','tickformat','ticklen','tickmode','tickprefix','ticks',
			   'ticksuffix','ticktext','ticktextsrc','tickvals','tickvalssrc','tickwidth','titlefont',
			   'zeroline','zerolinecolor','zerolinewidth']

__LAYOUT_AXIS_X=['xaxis_'+_ for _ in XAxis().__dir__()]
__LAYOUT_AXIS_Y=['yaxis_'+_ for _ in YAxis().__dir__()]

__LAYOUT_KWARGS = []
[__LAYOUT_KWARGS.extend(_) for _ in [__LAYOUT_VALID_KWARGS,__SHAPES_KWARGS,__GEO_KWARGS,__ANN_KWARGS,__LAYOUT_AXIS,
									 __LAYOUT_AXIS_X,__LAYOUT_AXIS_Y]]

def getTheme(theme=None):
	"""
	Returns a theme definition.

	To see the colors translated (hex) use
	cufflinks.getLayout(theme) instead.
	"""
	if not theme:
		theme = auth.get_config_file()['theme']

	if theme in THEMES:
		return copy.deepcopy(THEMES[theme])
	else:
		raise Exception("Invalid Theme: {0}".format(theme))

def getThemes():
	"""
	Returns the list of available themes
	"""
	return list(THEMES.keys())

def getLayout(kind=None,theme=None,title='',xTitle='',yTitle='',zTitle='',barmode='',bargap=None,bargroupgap=None,
			  margin=None, dimensions=None, width=None, height=None,
			  annotations=None,is3d=False,**kwargs):
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
		dimensions : tuple
			Dimensions of figure
		annotations : dict or list
			Dictionary of annotations
				{x_point : text}
			or
			List of Plotly Annotations
		is3d : bool
			Indicates if the layout is for a 3D chart

		Other Kwargs
		============

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
				dictionary

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


	for key in list(kwargs.keys()):
		if key not in __LAYOUT_KWARGS:
			raise Exception("Invalid keyword : '{0}'".format(key))

	if not theme:
		theme = auth.get_config_file()['theme']

	theme_data = getTheme(theme)
	layout=Layout(theme_data['layout'])
	layout['xaxis1'].update({'title':xTitle})
	layout['yaxis1'].update({'title':yTitle})

	fontfamily=kwargs.pop('fontfamily',None)
	if fontfamily:
		deep_update(layout,{'font':{'family':fontfamily}})


	if barmode:
		layout.update({'barmode':barmode})
	if bargroupgap:
		layout.update({'bargroupgap':bargroupgap})
	if bargap:
		layout.update(bargap=bargap)
	if title:
		layout.update({'title':title})
	if annotations:
		layout.update({'annotations':annotations})


	def update_axis(layout,axis='xy',**vals):
		for _x in axis:
			for k,v in list(vals.items()):
				if v==None:
					vals.pop(k)
			for k in layout:
				if '{0}{1}'.format(_x,'axis') in k:
					layout[k].update(**vals)
		return layout

	axis_kwargs=check_kwargs(kwargs,__LAYOUT_AXIS,{},True)
	xaxis_kwargs=kwargs_from_keyword(kwargs,{},'xaxis',True)
	yaxis_kwargs=kwargs_from_keyword(kwargs,{},'yaxis',True)
	
	for _x,_vals in (('xy',axis_kwargs),('x',xaxis_kwargs),('y',yaxis_kwargs)):
		layout=update_axis(layout,_x,**_vals)

	if margin:
		if isinstance(margin,dict):
			margin=margin
		else:
			margin=dict(list(zip(('l','r','b','t'),margin)))
		layout.update(margin=margin)

	if dimensions:
		layout.update(width=dimensions[0])
		layout.update(height=dimensions[1])

	if height:
		layout.update(height=height)
	if width:
		layout.update(width=width)
	if is3d:
		if '3d' in theme_data:
			layout=deep_update(layout,theme_data['3d'])
		zaxis=layout['xaxis1'].copy()
		zaxis.update(title=zTitle)
		scene=Scene(xaxis=layout['xaxis1'].copy(),yaxis=layout['yaxis1'].copy(),zaxis=zaxis)
		layout.update(scene=scene)
		del layout['xaxis1']
		del layout['yaxis1']

	## Axis Range
	for r in ['x','y','z']:
		if '{0}range'.format(r) in kwargs:
			if is3d:
				layout['scene']['{0}axis'.format(r)].update(range=kwargs['{0}range'.format(r)])
			else:
				layout['{0}axis1'.format(r)].update(range=kwargs['{0}range'.format(r)])

	# Need to update this for an add_axis approach. 
	if kind in ('candlestick','ohlc','candle'):
		layout['yaxis2']=layout['yaxis1'].copy()
		layout['yaxis1'].update(showticklabels=False)

	## Kwargs

	if 'legend' in kwargs:
		if type(kwargs['legend'])==bool:
			layout['showlegend']=kwargs['legend']
		elif type(kwargs['legend'])==str:
			if kwargs['legend']=='top':
				layout['legend'].update(orientation='h',yanchor='bottom',x=.3,y=.95)
			elif kwargs['legend']=='bottom':
				layout['legend'].update(orientation='h',yanchor='bottom',x=.3,y=-0.5)
			layout['showlegend']=True
		else:
			layout['legend']=kwargs['legend']
			layout['showlegend']=True

	if 'showlegend' in kwargs:
		layout['showlegend']=kwargs['showlegend']

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
						shapes.append(get_shape(**x_i))
					else:
						if orientation=='h':
							shapes.append(get_shape(kind='line',y=x_i))
						else:
							shapes.append(get_shape(kind='line',x=x_i))
			elif isinstance(xline,dict):
				shapes.append(get_shape(**xline))
			else:
				if orientation=='h':
					shapes.append(get_shape(kind='line',y=xline))
				else:
					shapes.append(get_shape(kind='line',x=xline))

		def get_span(xspan):
			orientation=xspan[0]
			xspan=kwargs[xspan]
			if isinstance(xspan,list):
				for x_i in xspan:
					if isinstance(x_i,dict):
						x_i['kind']='rect'
						shapes.append(get_shape(**x_i))
					else:
						v0,v1=x_i
						if orientation=='h':
							shapes.append(get_shape(kind='rect',y0=v0,y1=v1,fill=True,opacity=.5))
						else:
							shapes.append(get_shape(kind='rect',x0=v0,x1=v1,fill=True,opacity=.5))
			elif isinstance(xspan,dict):
				xspan['kind']='rect'
				shapes.append(get_shape(**xspan))
			elif isinstance(xspan,tuple):
				v0,v1=xspan
				if orientation=='h':
					shapes.append(get_shape(kind='rect',y0=v0,y1=v1,fill=True,opacity=.5))
				else:
					shapes.append(get_shape(kind='rect',x0=v0,x1=v1,fill=True,opacity=.5))
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
					shp=i if 'type' in i else get_shape(**i)
					shapes.append(shp)
			elif isinstance(shapes_,dict):
					shp=shapes_ if 'type' in shapes_ else get_shape(**shapes_)
					shapes.append(shp)
			else:
				raise Exception("Shapes need to be either a dict or list of dicts")


		layout['shapes']=shapes

	# Maps
	if kind in ('choropleth','scattergeo'):
		kw=check_kwargs(kwargs,__GEO_KWARGS)
		defaults={'projection':{'type':'equirectangular'},'showframe':False,'showcoastlines':False}
		for k,v in list(defaults.items()):
			if k not in kw:
				kw[k]=v
		kw_=kwargs_from_keyword(kw,{},'projection')
		deep_update(kw,kw_)
		layout['geo']=kw
		del layout['xaxis1']
		del layout['yaxis1']
		if not margin:
			layout['margin']={'autoexpand':True}

	# Range Selector
	if 'rangeselector' in kwargs:
		rs=kwargs['rangeselector']
		if 'axis' in rs:
			axis=rs['axis']
			del rs['axis']
		else:
			axis='xaxis1'
		layout[axis]['rangeselector']=get_range_selector(**rs)

	# Range Slider
	if 'rangeslider' in kwargs:
		if type(kwargs['rangeslider'])==bool:
			if kwargs['rangeslider']:
				layout['xaxis1']['rangeslider']=dict(visible=kwargs['rangeslider'])
			else:
				layout['xaxis1']['rangeslider']=dict(visible=False)
				# layout['yaxis1'].update(domain=(0,0))
		else:
			layout['xaxis1']['rangeslider']=kwargs['rangeslider']
	else:
		if kind in ('ohlc','candle','candlestick'):
			layout['xaxis1']['rangeslider']=dict(visible=False)
			# layout['yaxis1'].update(domain=(0,0))



	# Explicit Updates

	if 'layout_update' in kwargs:
		layout=deep_update(layout,kwargs['layout_update'])

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


def getAnnotations(df,annotations,kind='lines',theme=None,**kwargs):
	"""
	Generates an annotations object

	Parameters:
	-----------
		df : DataFrame
			Original DataFrame of values
		annotations : dict or list
			Dictionary of annotations
			{x_point : text}
			or
			List of Plotly annotations
	"""
	


	

	for key in list(kwargs.keys()):
		if key not in __ANN_KWARGS:
			raise Exception("Invalid keyword : '{0}'".format(key))

	l=[]
	theme_data = getTheme(theme)

	kwargs['fontcolor']=kwargs.pop('fontcolor',theme_data['annotations']['fontcolor'])
	kwargs['arrowcolor']=kwargs.pop('arrowcolor',theme_data['annotations']['arrowcolor'])
	kwargs['fontsize']=kwargs.pop('fontsize',12)

	def check_ann(annotation):
		local_list=[]
		try:
			_annotation=dict_replace_keyword({},'font',annotation,False)
			_annotation=dict_replace_keyword(_annotation,'font',kwargs,False)
			local_list.append(Annotation(_annotation))
			
		except:
			if 'title' in annotation:
				local_list.append(
						Annotation(	
								text=annotation['title'],
								showarrow=False,
								x=0,
								y=1,
								xref='paper',
								yref='paper',
								font={'size':24 if not 'fontsize' in kwargs else kwargs['fontsize']}
							)
					)
				del annotation['title']
		
			for k,v in list(annotation.items()):
				if kind in ('candlestick','ohlc','candle'):
					d=ta._ohlc_dict(df)
					maxv=df[d['high']].ix[k]
					yref='y2'
				else:
					maxv=df.ix[k].sum() if k in df.index else 0
					yref='y1'
				ann=Annotation(
								x=k,
								y=maxv,
								xref='x',
								yref=yref,
								text=v,
								showarrow=True,
								arrowhead=7,
								ax=0,
								ay=-100,
								textangle=-90
								)
				local_list.append(ann)

			_l=[]
			for i in local_list:
				_l.append(dict_replace_keyword(i,'font',kwargs,True))
			
			local_list=_l

		return local_list

	if not isinstance(annotations,list):
		annotations=[annotations]	
	_list_ann=[]
	for ann in annotations:
		_list_ann.extend(check_ann(ann))
	return Annotations(_list_ann)


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

def figures(df,specs,asList=False):
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
		asList : boolean
			If True, then a list of figures is returned.
			Otherwise a single (merged) figure is returned.
			Default : False
	"""
	figs=[]
	for spec in specs:
		figs.append(df.figure(**spec))
	if asList:
		return figs
	else:
		return merge_figures(figs)

def merge_figures(figures):
	"""
	Generates a single Figure from a list of figures

	Parameters:
	-----------
		figures : list(Figures)
			List of figures to be merged. 
	"""
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
		base_layout : layout (dict)
			Layout to be used as base where the subplots will be
			added
		subplot_titles : list(string)
			List of strings that contains the titles of each
			plot.
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
			rows=len(figures)//2+len(figures)%2
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

	# Check for non-cartesian plots
	data=sp['data']
	layout=sp['layout']
	for d in data:
		if d['type']=='pie':
			d['domain']={}
			d['domain']['x']=layout['xaxis{0}'.format(d['xaxis'][1:])]['domain']
			d['domain']['y']=layout['yaxis{0}'.format(d['yaxis'][1:])]['domain']
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

	# if 'subplot_titles' in kwargs:
	# 	if 'annotations' in layout:
	# 		annotation=sp['layout']['annotations'][0]
	# 	else:
	# 		annotation=getLayout(theme,annotations=[Annotation(text='')])['annotations']
	# 	for ann in sp['layout']['annotations']:
	# 		ann.update(font=dict(color=annotation['font']['color']))

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


def get_ohlc(df,up_color=None,down_color=None,theme=None,layout=None,**kwargs):
	layout=getLayout(theme=theme) if not layout else layout
	ohlc=['open','high','low','close']
	if not theme:
		theme = auth.get_config_file()['theme']
	c_dir=ta._ohlc_dict(df)
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
	ohlc_bars['layout']=merge_dict(layout,ohlc_bars['layout'])
	return ohlc_bars

def get_candle(df,up_color=None,down_color=None,theme=None,layout=None,**kwargs):
	layout=getLayout(theme=theme) if not layout else layout
	ohlc=['open','high','low','close']
	if not theme:
		theme = auth.get_config_file()['theme']
	c_dir=ta._ohlc_dict(df)
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
	fig=Figure()
	fig_cpy=self.copy()
	fig['data']=fig_cpy['data']
	fig['layout']=fig_cpy['layout']
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

# def _get_shapes(d):

# 	def get_shapes(xline):
# 		orientation=xline[0]
# 		xline=d[xline]
# 		if type(xline) in (list,tuple):
# 			for x_i in xline:
# 				if isinstance(x_i,dict):
# 					x_i['kind']='line'
# 					return get_shape(**x_i)
# 				else:
# 					if orientation=='h':
# 						return get_shape(kind='line',y=x_i)
# 					else:
# 						return get_shape(kind='line',x=x_i)
# 		elif isinstance(xline,dict):
# 			return get_shape(**xline)
# 		else:
# 			if orientation=='h':
# 				return get_shape(kind='line',y=xline)
# 			else:
# 				return get_shape(kind='line',x=xline)

# 	def get_span(xspan):
# 		orientation=xspan[0]
# 		xspan=d[xspan]
# 		if isinstance(xspan,list):
# 			for x_i in xspan:
# 				if isinstance(x_i,dict):
# 					x_i['kind']='rect'
# 					return get_shape(**x_i)
# 				else:
# 					v0,v1=x_i
# 					if orientation=='h':
# 						get_shape(kind='rect',y0=v0,y1=v1,fill=True,opacity=.5)
# 					else:
# 						get_shape(kind='rect',x0=v0,x1=v1,fill=True,opacity=.5)
# 		elif isinstance(xspan,dict):
# 			xspan['kind']='rect'
# 			return get_shape(**xspan)
# 		elif isinstance(xspan,tuple):
# 			v0,v1=xspan
# 			if orientation=='h':
# 				return get_shape(kind='rect',y0=v0,y1=v1,fill=True,opacity=.5)
# 			else:
# 				return get_shape(kind='rect',x0=v0,x1=v1,fill=True,opacity=.5)
# 		else:
# 			raise Exception('Invalid value for {0}span: {1}'.format(orientation,xspan))

# 	if 'hline' in d:
# 		return get_shapes('hline')
# 	if 'vline' in d:
# 		return get_shapes('vline')
# 	if 'hspan' in d:
# 		get_span('hspan')
# 	if 'vspan' in d:
# 		get_span('vspan')
# 	if 'shapes' in d:
# 		shapes_=kwargs['shapes']
# 		if isinstance(shapes_,list):
# 			for i in shapes_:
# 				shp=i if 'type' in i else get_shape(**i)
# 				shapes.append(shp)
# 		elif isinstance(shapes_,dict):
# 				shp=shapes_ if 'type' in shapes_ else get_shape(**shapes_)
# 				shapes.append(shp)
# 		else:
# 			raise Exception("Shapes need to be either a dict or list of dicts")

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

### Advanced Shapes

def get_trendline(df,date0,date1,column='close',**kwargs):
	df=pd.DataFrame(df[column])
	d={'x0':date0,
	   'x1':date1,
	   'y0':df.ix[date0].values[0],
	   'y1':df.ix[date1].values[0]}
	d.update(**kwargs)
	return d

### Range Selector

def get_range_selector(steps=['1m','1y'],bgcolor='rgba(150, 200, 250, 0.4)',x=0,y=0.9,
						visible=True,**kwargs):
	"""
	Returns a range selector
	Reference: https://plot.ly/python/reference/#layout-xaxis-rangeselector
	
	Parameters:
	-----------
		steps : string or list(string)
			Steps for the range
				Examples:
					['1y','2 months','5 weeks','ytd','2mtd']
		bgocolor : string or tuple(color,alpha)
			Background color
				Examples:
					'cyan'
					'rgba(232,214,10,.5)'
					('blue',.3)
		font_size : int
			Font size
		x : float
			Position along the x axis
			Domain (0,1)
		y : float
			Position along the y axis
			Domain (0,1)	
	"""
	import string

	def get_step(s):


		term=[]
		stepmode='backward'
		_s=s
		_s=_s.replace(' ','')
		_s=_s.lower()
		if _s in ['reset','all']:
			return {'count':1,'label':s,'step':'all'}
		if _s[-2:]=='td':
			_s=_s[:-2]
			stepmode='todate'
			if _s[0] not in string.digits:				
				_s='1'+_s
		if _s[0] not in string.digits:
			raise Exception('Invalid step format: {0}'.format(s))
		while _s[-1] not in string.digits:
			term.append(_s[-1])
			_s=_s[:-1]
		term.reverse()
		term=''.join(term)
		cnt=int(_s)
		term=term[:-1] if (term[-1]=='s' and len(term)>1) else term		
		if term in ['y','year','yr']:
					steps='year'
		elif term in ['w','week','wk']:
			steps='week'
		elif term in ['m','month','mth','mnth','mo']:
			steps='month'
		elif term in ['hr','hour']:
			steps='hour'
		elif term in ['min','minute','mn']:
			steps='minute'
		elif term in ['sec','sc','s']:
			steps='second'
		else:
			raise Exception('Invalid step format: {0}'.format(s))
		return {'count':cnt,'label':s,'step':steps,'stepmode':stepmode}

	rangeselector={
		'bgcolor':to_rgba(bgcolor,1),
		'x':x,
		'y':y,
		'visible':visible
	}

	kwargs['fontsize']=kwargs.get('fontsize',13)

	rangeselector=dict_replace_keyword(rangeselector,'font',kwargs,False)

	buttons=[]
	if type(steps) not in (list,tuple):
		steps=[steps]
	for s in steps:
		buttons.append(get_step(s))
	rangeselector['buttons']=buttons
	return rangeselector

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


def updateColors(d):
	for k,v in list(d.items()):
		if isinstance(v,dict):
			updateColors(v)
		else:
			if isinstance(v,list):
				if 'color' in k:
					d[k]=[normalize(_) for _ in v]
				else:
					for _ in v:
						if isinstance(_,dict):
							updateColors(_)
			else:
				if 'color' in k.lower():
					if 'rgba' not in v:
						d[k]=normalize(v)
	return d

def _nodata(self):
	d=[]
	# _=copy.deepcopy(self)
	for _ in self:
		d.append(copy.deepcopy(_))
	for _ in d:	
		for k,v in list(_.items()):
			if k in ('x','y','open','close','high','low','index','volume','line','marker'):
				try:
					_[k]=[]
				except:
					_[k]={}
	return d

def _figure_no_data(self):
	return {'data':self.data.nodata(),
	'layout':self.layout}

def _update_traces(self,**kwargs):
	for _ in self.data:
		_.update(**kwargs)

def _move_axis(self,xaxis=None,yaxis=None):
	def update_axis(self,axis):
		_axis=axis[0]
		from_axis=self.data[0].pop('{0}axis'.format(_axis),'{0}1'.format(_axis))
		from_axis=_axis+'axis'+from_axis[1:]
		to_axis=_axis+'axis'+axis[1:]
		self.layout[to_axis]=self.layout.pop(from_axis)
		self.update_traces(**{'{0}axis'.format(_axis):axis})
	
	if xaxis:
		update_axis(self,xaxis)
	if yaxis:
		update_axis(self,yaxis)

### Offline

def go_offline(connected = False, offline=True):
	if offline:
		py_offline.init_notebook_mode(connected)
		py_offline.__PLOTLY_OFFLINE_INITIALIZED=True
	else:
		py_offline.__PLOTLY_OFFLINE_INITIALIZED=False

def is_offline():
	return py_offline.__PLOTLY_OFFLINE_INITIALIZED



Figure.axis=axis
Figure.trace_dict=trace_dict
Figure.set_axis=_set_axis
Figure.update_traces=_update_traces
Figure.move_axis=_move_axis
Figure.nodata=_figure_no_data
Data.nodata=_nodata
