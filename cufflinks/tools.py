import plotly.plotly as py
from plotly.graph_objs import Figure,XAxis,YAxis,Annotation
from plotlytools import getLayout
from colors import normalize,to_rgba
import auth


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
		for k,v in fig['layout'].items():
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
			lr=list_ref.next()
			if lr is not None:
				break
		for _ in figures[i]['data']:
			for axe in lr:
				_.update({'{0}axis'.format(axe[0]):axe})
			sp['data'].append(_)
	# Remove extra plots
	for k in sp['layout'].keys():
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
	for k,v in layout.items():
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
		for k,v in layout[axis].items():
			sp_item.update({k:v})

	for k,v in sp['layout'].items():
		if isinstance(v,XAxis):
			update_items(v,layout,'xaxis')
		elif isinstance(v,YAxis):
			update_items(v,layout,'xaxis')
			
	return sp



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
	layout['xaxis'].update(showgrid=False)
	layout['yaxis'].update(showgrid=False)
	sm=subplots(figs,shape=(len(df.columns),len(df.columns)),shared_xaxes=False,shared_yaxes=False,
					  horizontal_spacing=.05,vertical_spacing=.07,base_layout=layout)
	sm['layout'].update(bargap=.02,showlegend=False)
	return sm

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
	items=figure['layout']['scene'].items() if 'scene' in figure['layout'] else figure['layout'].items()
	for k,v in items:
		if 'axis' in k:
			d['{0}{1}'.format(k[0],1 if k[-1]=='s' else k[-1])]=v
	return d

def get_len(figure):
	d={}
	keys=figure['layout']['scene'].keys() if 'scene' in figure['layout'] else figure['layout'].keys()
	for k in keys:
		if 'axis' in k:
			d[k[0]] = d[k[0]]+1 if k[0] in d else 1
	return d

def get_which(figure):
	d={}
	keys=figure['layout']['scene'].keys() if 'scene' in figure['layout'] else figure['layout'].keys()
	for k in keys:
		if 'axis' in k:
			if k[0] in d:
				d[k[0]].append('{0}{1}'.format(k[0],k[-1]))
			else:
				d[k[0]]=['{0}{1}'.format(k[0],'1' if k[-1]=='s' else k[-1])]
	return d

@property
def axis(self):
	return {'ref':get_ref(self),
			'def':get_def(self),
			'len':get_len(self),
			'which':get_which(self)}    

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


Figure.axis=axis	   