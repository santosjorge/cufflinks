import plotly.plotly as py
import plotly.offline as py_offline
from plotly.graph_objs import *
from .colors import normalize,to_rgba
from .themes import THEMES
from . import auth
from .utils import merge_dict,deep_update, check_kwargs,kwargs_from_keyword
import numpy as np
import copy

__LAYOUT_VALID_KWARGS = ['legend','vline','hline','vspan','hspan','shapes','logx','logy','layout_update',
					'xrange','yrange','zrange']

__GEO_KWARGS=['projection','showframe','showlakes','coastlinecolor','countrywidth','countrycolor',
			 'showsubunits','bgcolor','showrivers','subunitcolor','showcountries','riverwidth','scope',
			 'rivercolor','lataxis','subunitwidth','showocean','oceancolor','lakecolor','showland','lonaxis',
			 'framecolor','coastlinewidth','landcolor','showcoastlines','framewidth','resolution','projection_type']

__LAYOUT_KWARGS = []
[__LAYOUT_KWARGS.extend(_) for _ in [__LAYOUT_VALID_KWARGS,__GEO_KWARGS]]

def getTheme(theme):
	"""
	Returns a theme definition.

	To see the colors translated (hex) use 
	cufflinks.getLayout(theme) instead.
	"""
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
			  gridcolor=None,zerolinecolor=None,margin=None, dimensions=None, width=None, height=None,
			  annotations=False,is3d=False,**kwargs):
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
		annotations : dictionary
			Dictionary of annotations
			{x_point : text}
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
			hline : [y0,y1]
				Draws a horizontal rectangle at the 
				indicated (y0,y1) positions.
				Extra parameters can be passed in
				the form of a dictionary (see shapes)
			vline : [x0,x1]
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

	theme_data = getTheme(theme)
	layout=theme_data['layout']
	layout['xaxis1'].update({'title':xTitle})
	layout['yaxis1'].update({'title':yTitle})
	if annotations:
		update_annotations(annotations,
						theme_data['annotations']['fontcolor'],
						theme_data['annotations']['arrowcolor'])
	
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
		values=['x','y','xref','yref','text','showarrow',
				 'arrowhead','ax','ay','textangle','arrowsize',
				 'arrowwidth','arrowcolor']
	return Annotations(l)

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
	"""
	figs=[]
	for spec in specs:
		figs.append(df.figure(**spec))
	if asList:
		return figs
	else:
		return merge_figures(figs)

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

def get_ohlc(df,up_color=None,down_color=None,theme=None,layout=None,**kwargs):
	layout=getLayout(theme=theme) if not layout else layout
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
	ohlc_bars['layout']=merge_dict(layout,ohlc_bars['layout'])
	return ohlc_bars

def get_candle(df,up_color=None,down_color=None,theme=None,layout=None,**kwargs):
	layout=getLayout(theme=theme) if not layout else layout
	ohlc=['open','high','low','close']
	if not theme:
		theme = auth.get_config_file()['theme']    
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

### Offline

def go_offline(offline=True):
	if offline:
		py_offline.init_notebook_mode()
		py_offline.__PLOTLY_OFFLINE_INITIALIZED=True
	else:
		py_offline.__PLOTLY_OFFLINE_INITIALIZED=False

def is_offline():
	return py_offline.__PLOTLY_OFFLINE_INITIALIZED


Figure.axis=axis
Figure.trace_dict=trace_dict	  
Figure.set_axis=_set_axis 
