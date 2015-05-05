import pandas as pd
import plotly.plotly as py
from plotly.graph_objs import *
from collections import defaultdict
from colors import normalize,get_scales,colorgen,to_rgba
import copy
from IPython.display import Image,display


def getLayout(theme='solar',title='',xTitle='',yTitle='',zTitle='',barmode='',
				gridcolor=None,zerolinecolor=None,margin=None,annotations=None,is3d=False):
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
	if theme=='solar':
		layout=Layout(legend=Legend(bgcolor='charcoal',font={'color':'pearl'}),
						paper_bgcolor='charcoal',plot_bgcolor='charcoal',
						yaxis=YAxis(tickfont={'color':'grey12'},gridcolor='grey08',title=yTitle,
								 titlefont={'color':'pearl'},zerolinecolor='grey09'),
						xaxis=XAxis(tickfont={'color':'grey12'},gridcolor='grey08',title=xTitle,
								titlefont={'color':'pearl'},zerolinecolor='grey09'),
						titlefont={'color':'pearl'})
		if annotations:
			annotations.update({'arrowcolor':'grey11','font':{'color':'pearl'}})

	elif theme=='pearl':
		layout=Layout(legend=Legend(bgcolor='pearl02',font={'color':'pearl06'}),
						paper_bgcolor='pearl02',plot_bgcolor='pearl02',
						yaxis=YAxis(tickfont={'color':'pearl06'},gridcolor='pearl04' if is3d else 'pearl03',title=yTitle,
								  titlefont={'color':'pearl06'},zeroline=False,zerolinecolor='pearl04' if is3d else 'pearl03'),
						xaxis=XAxis(tickfont={'color':'pearl06'},gridcolor='pearl04' if is3d else 'pearl03',title=xTitle,
								  titlefont={'color':'pearl06'},zerolinecolor='pearl04' if is3d else 'pearl03'))
		if annotations:
			annotations.update({'arrowcolor':'pearl04','font':{'color':'pearl06'}})
	elif theme=='white':
		layout=Layout(legend=Legend(bgcolor='white',font={'color':'pearl06'}),
						paper_bgcolor='white',plot_bgcolor='white',
						yaxis=YAxis(tickfont={'color':'pearl06'},gridcolor='pearl04' if is3d else 'pearl03',title=yTitle,
								  titlefont={'color':'pearl06'},zerolinecolor='pearl04' if is3d else 'pearl03'),
						xaxis=XAxis(tickfont={'color':'pearl06'},gridcolor='pearl04' if is3d else 'pearl03',title=xTitle,
								  titlefont={'color':'pearl06'},zerolinecolor='pearl04' if is3d else 'pearl03'))
		if annotations:
			annotations.update({'arrowcolor':'pearl04','font':{'color':'pearl06'}})
	if barmode:
		layout.update({'barmode':barmode})
	if title:
		layout.update({'title':title})
	if annotations:
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
			margin=dict(zip(('l','r','b','t'),margin))
		layout.update(margin=margin)

	if is3d:
		zaxis=layout['xaxis'].copy()
		zaxis.update(title=zTitle)
		scene=Scene(xaxis=layout['xaxis'],yaxis=layout['yaxis'],zaxis=zaxis)
		layout.update(scene=scene)
		del layout['xaxis']
		del layout['yaxis']


	def updateColors(layout):
		for k,v in layout.items():
			if isinstance(v,dict):
				updateColors(v)
			else:
				if 'color' in k.lower():
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


def _to_iplot(self,colors=None,colorscale=None,kind='scatter',mode='lines',symbol='dot',size='12',fill=False,
		width=3,sortbars=False,keys=False,bestfit=False,bestfit_colors=None,asDates=False,**kwargs):
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
	if df.index.__class__.__name__ in ('PeriodIndex','DatetimeIndex'):
		if asDates:
			df.index=df.index.date
		x=df.index.format()
	else:
		x = df.index.values
	lines={}
	if type(df)==pd.core.series.Series:
		df=pd.DataFrame({df.name:df})
	if not keys:		
		if kind=='bar':
			if sortbars:
				keys=df.sum().sort(inplace=False,ascending=False).keys()
			else:
				keys=df.keys()
		else:
			keys=df.keys()
	colors=get_colors(colors,colorscale,keys)
	for key in keys:
		lines[key]={}
		lines[key]["x"]=x
		lines[key]["y"]=df[key].fillna('').values
		lines[key]["name"]=key
		if kind=='bar':
			lines[key]["marker"]={'color':to_rgba(colors[key],.6),'line':{'color':colors[key],'width':1}}
		else:
			lines[key]["line"]={'color':colors[key],'width':width}
			lines[key]["mode"]=mode
			if 'marker' in mode:
				lines[key]["marker"]=Marker(symbol=symbol,size=size)
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

def _iplot(self,data=None,layout=None,filename='',world_readable=False,
			kind='scatter',title='',xTitle='',yTitle='',zTitle='',theme='pearl',colors=None,colorscale=None,fill=False,width=2,
			mode='lines',symbol='dot',size=12,barmode='',sortbars=False,boxpoints=False,annotations=None,keys=False,bestfit=False,bestfit_colors=None,
			categories='',x='',y='',z='',text='',gridcolor=None,zerolinecolor=None,margin=None,
			asDates=False,asFigure=False,asImage=False,dimensions=(1116,587),
			asPlot=False,asUrl=False,**kwargs):
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
	"""

	if not colors:
		colors=kwargs['color'] if 'color' in kwargs else colors
	if isinstance(colors,str):
		colors=[colors]
	opacity=kwargs['opacity'] if 'opacity' in kwargs else 0.8

	if not layout:
		if annotations:
				annotations=getAnnotations(self.copy(),annotations)
		layout=getLayout(theme=theme,xTitle=xTitle,yTitle=yTitle,zTitle=zTitle,title=title,barmode=barmode,
								annotations=annotations,gridcolor=gridcolor,zerolinecolor=zerolinecolor,margin=margin,is3d='3d' in kind)

	if not data:
		if categories:
			data=Data()
			_keys=pd.unique(self[categories])
			colors=get_colors(colors,colorscale,_keys)	
			mode='markers' if 'markers' not in mode else mode 
			for _ in _keys:
				__=self[self[categories]==_].copy()
				if 'bubble' in kind:
					rg=__[size].values
					rgo=self[size].values
					_size=[int(100*(float(i)-rgo.min())/(rgo.max()-rgo.min()))+12 for i in rg]	
				else:
					_size=size
				_data=Scatter3d(x=__[x].values,y=__[y].values,mode=mode,name=_,
							marker=Marker(color=colors[_],symbol=symbol,size=_size,opacity=opacity,
											line=Line(width=width)),textfont=getLayout(theme=theme)['xaxis']['titlefont'])
				if '3d' in kind:
					_data=Scatter3d(x=__[x].values,y=__[y].values,z=__[z].values,mode=mode,name=_,
							marker=Marker(color=colors[_],symbol=symbol,size=_size,opacity=opacity,
											line=Line(width=width)),textfont=getLayout(theme=theme)['xaxis']['titlefont'])
				else:
					_data=Scatter(x=__[x].values,y=__[y].values,mode=mode,name=_,
							marker=Marker(color=colors[_],symbol=symbol,size=_size,opacity=opacity,
											line=Line(width=width)),textfont=getLayout(theme=theme)['xaxis']['titlefont'])
				if text:
					_data.update(text=__[text].values.tolist())
				data.append(_data)
		else:
			if kind in ('scatter','spread','ratio','bar'):
				data=self.to_iplot(colors=colors,colorscale=colorscale,kind=kind,fill=fill,width=width,sortbars=sortbars,keys=keys,
						bestfit=bestfit,bestfit_colors=bestfit_colors,asDates=asDates,mode=mode,symbol=symbol,size=size)				
				if kind in ('spread','ratio'):
						if kind=='spread':
							trace=self.apply(lambda x:x[0]-x[1],axis=1)
							positive=trace.apply(lambda x:x if x>=0 else pd.np.nan)
							negative=trace.apply(lambda x:x if x<0 else pd.np.nan)
							trace=pd.DataFrame({'positive':positive,'negative':negative})
							trace=trace.to_iplot(colors={'positive':'green','negative':'red'},width=0)
						else:
							trace=self.apply(lambda x:x[0]*1.0/x[1],axis=1).to_iplot()
						trace.update({'xaxis':'x2','yaxis':'y2','fill':'tozeroy',
										'name':kind.capitalize(),'connectgaps':False,'showlegend':False})
						data.append(Scatter(trace[0]))
						if kind=='spread':
							data.append(Scatter(trace[1]))
						layout['yaxis'].update({'domain':[.3,1]})
						layout['yaxis2']=copy.deepcopy(layout['yaxis'])
						layout['xaxis2']=copy.deepcopy(layout['xaxis'])
						layout['yaxis2'].update(domain=[0,.25],title=kind.capitalize())
						layout['xaxis2'].update(anchor='y2',showticklabels=False)
			elif kind=='bubble':
				mode='markers' if 'markers' not in mode else mode 
				x=self[x].values.tolist()
				y=self[y].values.tolist()
				z=size if size else z
				rg=self[z].values
				z=[int(100*(float(_)-rg.min())/(rg.max()-rg.min()))+12 for _ in rg]
				text=kwargs['labels'] if 'labels' in kwargs else text
				labels=self[text].values.tolist()
				clrs=get_colors(colors,colorscale,x).values()
				gen=colorgen()
				marker=Marker(color=clrs,size=z,symbol=symbol,
								line=Line(width=width),textfont=getLayout(theme=theme)['xaxis']['titlefont'])
				trace=Scatter(x=x,y=y,marker=marker,mode='markers',text=labels)
				data=Data([trace])
			elif kind in ('box','histogram'):
				data=Data()
				clrs=get_colors(colors,colorscale,self.columns)
				if kind=='histogram':
					layout.update(barmode='overlay') 
				for _ in self.columns:
					if kind=='box':
						__=Box(y=self[_].values.tolist(),marker=Marker(color=clrs[_]),name=_,
								line=Line(width=width),boxpoints=boxpoints)
					else:
						__=Histogram(x=self[_].values.tolist(),marker=Marker(color=clrs[_]),name=_,
								line=Line(width=width),
								opacity=kwargs['opacity'] if 'opacity' in kwargs else .8)
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
				keys=self[text].values if text else range(len(self))
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

	if not filename:
		if title:
			filename=title
		else:
			filename='Plotly Playground'

	if asFigure:
		return Figure(data=data,layout=layout)
	elif asImage:
		py.image.save_as(Figure(data=data,layout=layout),filename='img/'+filename,format='png',
			width=dimensions[0],height=dimensions[1])
		return display(Image('img/'+filename+'.png'))
	elif asPlot:
		return py.plot(Figure(data=data,layout=layout),world_readable=world_readable,filename=filename)
	elif asUrl:
		return py.plot(Figure(data=data,layout=layout),world_readable=world_readable,filename=filename,auto_open=False)
	else:
		return py.iplot(Figure(data=data,layout=layout),world_readable=world_readable,filename=filename)


def get_colors(colors,colorscale,keys,asList=False):
	if type(colors)!=dict:
			if not colors:
				if colorscale:
					colors=get_scales(colorscale,len(keys))
			clrgen=colorgen(colors,len(keys))
			if asList:
				colors=[clrgen.next() for _ in keys]
			else:
				colors={}
				for key in keys:
					colors[key]=clrgen.next()
	return colors



pd.DataFrame.to_iplot=_to_iplot
# pd.DataFrame.iplot_bubble=_iplot_bubble
pd.DataFrame.iplot=_iplot
pd.Series.to_iplot=_to_iplot
pd.Series.iplot=_iplot

