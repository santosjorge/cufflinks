import pandas as pd
import plotly.plotly as py
from plotly.graph_objs import *
import collections
from colors import *
import copy



def getLayout(theme='solar',title='',xTitle='',yTitle='',barmode='',annotations=None):
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
		barmode : string 
			Mode when displaying bars
				group
				stack
				overlay
		annotations : dictionary
			Dictionary of annotations
			{x_point : text}
	"""
	if theme=='solar':
		layout=Layout(legend=Legend(bgcolor=charcoal,font={'color':pearl}),
						paper_bgcolor=charcoal,plot_bgcolor=charcoal,
						yaxis=YAxis(tickfont={'color':grey12},gridcolor=grey08,title=yTitle,
								 titlefont={'color':pearl}),
						xaxis=XAxis(tickfont={'color':grey12},gridcolor=grey08,title=xTitle),
								titlefont={'color':pearl})
		if annotations:
			annotations.update({'arrowcolor':grey11,'font':{'color':pearl}})

	elif theme=='pearl':
		layout=Layout(legend=Legend(bgcolor=pearl02,font={'color':pearl06}),
						paper_bgcolor=pearl02,plot_bgcolor=pearl02,
						yaxis=YAxis(tickfont={'color':pearl06},gridcolor=white,title=yTitle,
								  titlefont={'color':pearl06},zeroline=False),
						xaxis=XAxis(tickfont={'color':pearl06},gridcolor=white,title=xTitle))
		if annotations:
			annotations.update({'arrowcolor':pearl04,'font':{'color':pearl06}})
	elif theme=='white':
		layout=Layout(legend=Legend(bgcolor=white,font={'color':pearl06}),
						paper_bgcolor=white,plot_bgcolor=white,
						yaxis=YAxis(tickfont={'color':pearl06},gridcolor=pearl03,title=yTitle,
								  titlefont={'color':pearl06},zeroline=False),
						xaxis=XAxis(tickfont={'color':pearl06},gridcolor=pearl03,title=xTitle))
		if annotations:
			annotations.update({'arrowcolor':pearl04,'font':{'color':pearl06}})
	if barmode:
		layout.update({'barmode':barmode})
	if title:
		layout.update({'title':title})
	if annotations:
		layout.update({'annotations':annotations})
	return layout

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
	for k,v in annotations.items():
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
		for k,v in i.items():
			d[i['name']][k]=v
	return d 

def dict_to_iplot(d):
	l=[]
	for k,v in d.items():
		l.append(v)
	return Data(l)


def _to_iplot(self,colors=None,kind='scatter',fill=False,sortbars=False,keys=False,
		bestfit=False,bestfit_colors=None,**kwargs):
	"""
	Generates a plotly Data object 

	Parameters
	----------
		colors : list or dict
			{key:color} to specify the color for each column
			[colors] to use the colors in the defined order
		kind : string
			Kind of chart
				scatter
				bar
		fill : bool
			Filled Traces
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
		
	""" 
	df=self.copy()
	if df.index.__class__.__name__ in ('PeriodIndex','DatetimeIndex'):
		x=df.index.format()
	else:
		x = df.index.values
	lines={}
	if type(df)==pd.core.series.Series:
		df=pd.DataFrame({'Series1':df})
	if not keys:		
		if kind=='bar':
			if sortbars:
				keys=df.sum().sort(inplace=False,ascending=False).keys()
			else:
				keys=df.keys()
		else:
			keys=df.keys()
	if type(colors)!=dict:
		clrgen=colorgen(colors)
		colors={}
		for key in keys:
			colors[key]=clrgen.next()
	for key in keys:
		lines[key]={}
		lines[key]["x"]=x
		lines[key]["y"]=df[key].values
		lines[key]["name"]=key
		if kind=='bar':
			lines[key]["marker"]={'color':to_rgba(colors[key],.6),'line':{'color':colors[key],'width':1}}
		else:
			lines[key]["line"]={'color':colors[key],'width':3}
			if fill:
				lines[key]["fill"]='tozeroy'
				lines[key]["fillcolor"]=to_rgba(colors[key],.3		)
		for k,v in kwargs.items():
			lines[key][k]=v
	if kind=='bar':
		lines_plotly=[Bar(lines[key]) for key in keys]
	else:
		lines_plotly=[lines[key] for key in keys]
	if bestfit:
		if type(bestfit)==list:
			keys=bestfit
		d={}
		for key in keys:
			bestfit=df[key].bestfit()
			d[bestfit.formula]=bestfit
		bestfit_lines=pd.DataFrame(d).to_iplot(bestfit=False,colors=bestfit_colors,kind='scatter')
		for line in bestfit_lines:
			line['line']['dash']='dash'
			if not bestfit_colors:
				line['line']['color']=to_rgba(line['line']['color'],.6)
		data=Data(lines_plotly)
		data.extend(bestfit_lines)
		return data
	return Data(lines_plotly)

def _iplot(self,data=None,layout=None,filename='Plotly Playground',world_readable=False,
			theme='pearl',xTitle='',yTitle='',colors=None,fill=False,kind='scatter',
			barmode='',title='',annotations=None,asFigure=False,asImage=False,
			dimensions=(1116,587),sortbars=False,keys=False,bestfit=False,bestfit_colors=None,
			asPlot=False,**kwargs):
	"""
	Returns a plotly chart either as inline chart, image of Figure object

	Parameters:
	-----------
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
		colors : list or dict
			{key:color} to specify the color for each column
			[colors] to use the colors in the defined order
		kind : string
			Kind of chart
				scatter
				bar
				spread
				ratio
		fill : bool
			Filled Traces
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
		barmode : string 
			Mode when displaying bars
				group
				stack
				overlay
			* Only valid when kind='bar'
		annotations : dictionary
			Dictionary of annotations
			{x_point : text}
		asFigure : bool
			If True returns plotly Figure
		asImage : bool
			If True it returns Image
		dimensions : tuple(int,int)
			Dimensions for image 
				(width,height)
			* Only valid when asImage=True

	"""
	if not data:
		data=self.to_iplot(colors,kind=kind,fill=fill,sortbars=sortbars,keys=keys,
				bestfit=bestfit,bestfit_colors=bestfit_colors)
	if not layout:
		if annotations:
			annotations=getAnnotations(self.copy(),annotations)
		layout=getLayout(theme=theme,xTitle=xTitle,yTitle=yTitle,title=title,barmode=barmode,
							annotations=annotations)
	if kind in ('spread','ratio'):
		if kind=='spread':
			trace=self.apply(lambda x:x[0]-x[1],axis=1).to_iplot()
		else:
			trace=self.apply(lambda x:x[0]*1.0/x[1],axis=1).to_iplot()
		trace.update({'xaxis':'x2','yaxis':'y2','fill':'tozeroy','name':kind.capitalize()})
		data.append(Scatter(trace[0]))
		layout['yaxis'].update({'domain':[.3,1]})
		layout['yaxis2']=copy.deepcopy(layout['yaxis'])
		layout['xaxis2']=copy.deepcopy(layout['xaxis'])
		layout['yaxis2'].update(domain=[0,.25],title=kind.capitalize())
		layout['xaxis2'].update(anchor='y2',showticklabels=False)
	elif kind=='bubble':
		x=self[kwargs['x']]
		y=self[kwargs['y']]
		z=self[kwargs['z']]/kwargs['scale']
		labels=self[kwargs['labels']]
		gen=colorgen()
		marker=Marker(color=[gen.next() for i in range(len(x))],size=z)
		trace=Scatter(x=x,y=y,marker=marker,mode='markers',text=labels)
		data=Data([trace])

	if asFigure:
		return Figure(data=data,layout=layout)
	elif asImage:
		py.image.save_as(Figure(data=data,layout=layout),filename=filename,format='png',
			width=dimensions[0],height=dimensions[1])
		return py.image.ishow(Figure(data=data,layout=layout))
	elif asPlot:
		return py.plot(Figure(data=data,layout=layout),world_readable=world_readable,filename=filename)
	else:
		return py.iplot(Figure(data=data,layout=layout),world_readable=world_readable,filename=filename)



pd.DataFrame.to_iplot=_to_iplot
pd.DataFrame.iplot=_iplot
pd.Series.to_iplot=_to_iplot
pd.Series.iplot=_iplot

