import numpy as np
import pandas as pd
import string
from .auth import get_config_file

class CufflinksError(Exception):
		pass

def scatter3d(n_categories=5,n=10,prefix='category',mode=None):
	"""
	Returns a DataFrame with the required format for 
	a scatter3d plot

	Parameters:
	-----------
		n_categories : int
			Number of categories 
		n : int
			Number of points for each trace
		prefix : string
			Name for each trace
		mode : string
			Format for each item
				'abc' for alphabet columns
				'stocks' for random stock names
	"""
	categories=[]
	for i in range(n_categories):
		categories.extend([prefix+str(i+1)]*n)
	return pd.DataFrame({'x':np.random.randn(n*n_categories),
						 'y':np.random.randn(n*n_categories),
						 'z':np.random.randn(n*n_categories),
						 'text':getName(n*n_categories,mode=mode),
						 'categories':categories})

def bubble3d(n_categories=5,n=10,prefix='category',mode=None):
	"""
	Returns a DataFrame with the required format for 
	a bubble3d plot

	Parameters:
	-----------
		n_categories : int
			Number of categories 
		n : int
			Number of points for each trace
		prefix : string
			Name for each trace
		mode : string
			Format for each item
				'abc' for alphabet columns
				'stocks' for random stock names
	"""	
	categories=[]
	for i in range(n_categories):
		categories.extend([prefix+str(i+1)]*n)
	return pd.DataFrame({'x':np.random.randn(n*n_categories),
						 'y':np.random.randn(n*n_categories),
						 'z':np.random.randn(n*n_categories),
						 'size':np.random.randint(1,100,n*n_categories),
						 'text':getName(n*n_categories,mode=mode),
						 'categories':categories}) 

def bubble(n_categories=5,n=10,prefix='category',mode=None):
	"""
	Returns a DataFrame with the required format for 
	a bubble plot

	Parameters:
	-----------
		n_categories : int
			Number of categories 
		n : int
			Number of points for each category
		prefix : string
			Name for each category
		mode : string
			Format for each item
				'abc' for alphabet columns
				'stocks' for random stock names
	"""	
	categories=[]
	for i in range(n_categories):
		categories.extend([prefix+str(i+1)]*n)
	return pd.DataFrame({'x':np.random.randn(n*n_categories),
						 'y':np.random.randn(n*n_categories),
						 'size':np.random.randint(1,100,n*n_categories),
						 'text':getName(n*n_categories,mode=mode),
						 'categories':categories}) 

def pie(n_labels=5,mode=None):
	"""
	Returns a DataFrame with the required format for 
	a pie plot

	Parameters:
	-----------
		n_labels : int
			Number of labels 
		mode : string
			Format for each item
				'abc' for alphabet columns
				'stocks' for random stock names
	"""	
	return pd.DataFrame({'values':np.random.randint(1,100,n_labels),
						 'labels':getName(n_labels,mode=mode)})                               

def scatter(n_categories=5,n=10,prefix='category',mode=None):
	"""
	Returns a DataFrame with the required format for 
	a scatter plot

	Parameters:
	-----------
		n_categories : int
			Number of categories 
		n : int
			Number of points for each category
		prefix : string
			Name for each category
		mode : string
			Format for each item
				'abc' for alphabet columns
				'stocks' for random stock names
	"""	
	categories=[]
	for i in range(n_categories):
		categories.extend([prefix+str(i+1)]*n)
	return pd.DataFrame({'x':np.random.randn(n*n_categories),
						 'y':np.random.randn(n*n_categories),
						 'text':getName(n*n_categories,mode=mode),
						 'categories':categories})

def heatmap(n_x=5,n_y=10):
	"""
	Returns a DataFrame with the required format for 
	a heatmap plot

	Parameters:
	-----------
		n_x : int
			Number of x categories
		n_y : int
			Number of y categories
	"""	
	x=['x_'+str(_) for _ in range(n_x)]
	y=['y_'+str(_) for _ in range(n_y)]
	return pd.DataFrame(surface(n_x-1,n_y-1).values,index=x,columns=y)

def lines(n_traces=5,n=100,columns=None,dateIndex=True,mode=None):
	"""
	Returns a DataFrame with the required format for 
	a scatter (lines) plot

	Parameters:
	-----------
		n_traces : int
			Number of traces 
		n : int
			Number of points for each trace
		columns : [str]
			List of column names
		dateIndex : bool
			If True it will return a datetime index
			if False it will return a enumerated index
		mode : string
			Format for each item
				'abc' for alphabet columns
				'stocks' for random stock names
	"""	
	index=pd.date_range('1/1/15',periods=n) if dateIndex else list(range(n))
	df=pd.DataFrame(np.random.randn(n,n_traces),index=index,
		columns=getName(n_traces,columns=columns,mode=mode))
	return df.cumsum()  

def bars(n=3,n_categories=3,prefix='category',columns=None,mode='abc'):
	"""
	Returns a DataFrame with the required format for 
	a bar plot

	Parameters:
	-----------
		n : int
			Number of points for each trace
		n_categories : int
			Number of categories for each point
		prefix : string
			Name for each category
		columns : [str]
			List of column names
		mode : string
			Format for each item
				'abc' for alphabet columns
				'stocks' for random stock names
	"""		
	categories=[]
	if not columns:
		columns=getName(n,mode=mode)
	for i in range(n_categories):
		categories.extend([prefix+str(i+1)])
	data=dict([(x,np.random.randint(1,100,n_categories)) for x in columns])
	return pd.DataFrame(data,index=categories)

def ohlc(n=100):
	"""
	Returns a DataFrame with the required format for 
	a scatter (lines) plot

	Parameters:
	-----------
		n_traces : int
			Number of traces 
		n : int
			Number of points for each trace
		columns : [str]
			List of column names
		mode : string
			Format for each item
				'abc' for alphabet columns
				'stocks' for random stock names
	"""	
	index=pd.date_range('1/1/15',periods=n*288,freq='5min',tz='utc')
	data=np.random.randn(n*288)
	data[0]=np.array([100])
	df=pd.DataFrame(data,index=index,
		columns=['a'])
	df=df.cumsum()  
	df=df.resample('1d',how='ohlc')
	# df.index=df.index.date
	return df['a']

def box(n_traces=5,n=100,mode=None):
	"""
	Returns a DataFrame with the required format for 
	a box plot

	Parameters:
	-----------
		n_traces : int
			Number of traces 
		n : int
			Number of points for each trace
		mode : string
			Format for each item
				'abc' for alphabet columns
				'stocks' for random stock names
	"""	
	df=pd.DataFrame([np.random.chisquare(np.random.randint(2,10),n_traces) for _ in range(n)],
		columns=getName(n_traces,mode=mode))
	return df       

def histogram(n_traces=1,n=500,mode=None):
	"""
	Returns a DataFrame with the required format for 
	a box plot

	Parameters:
	-----------
		n_traces : int
			Number of traces 
		n : int
			Number of points for each trace
		mode : string
			Format for each item
				'abc' for alphabet columns
				'stocks' for random stock names
	"""	
	df=pd.DataFrame(np.random.randn(n,n_traces)+np.random.randint(-1,2),
		columns=getName(n_traces,mode=mode))                     
	return df

def surface(n_x=20,n_y=20):
	"""
	Returns a DataFrame with the required format for 
	a surface plot

	Parameters:
	-----------
		n_x : int
			Number of points along the X axis
		n_y : int
			Number of points along the Y axis
	"""	
	x=[float(np.random.randint(0,100))]
	for i in range(n_x):
		x.append(x[:1][0]+np.random.randn()*np.random.randint(1,10))
	df=pd.DataFrame(x)
	for i in range(n_y):
		df[i+1]=df[i].map(lambda x:x+np.random.randn()*np.random.randint(1,10))
	return df	

def sinwave(n=4,inc=.25):
	"""
	Returns a DataFrame with the required format for 
	a surface (sine wave) plot

	Parameters:
	-----------
		n : int
			Ranges for X and Y axis (-n,n)
		n_y : int
			Size of increment along the axis
	"""	
	x=np.arange(-n,n,inc)
	y=np.arange(-n,n,inc)
	X,Y=np.meshgrid(x,y)
	R = np.sqrt(X**2 + Y**2)
	Z = np.sin(R)/(.5*R)
	return pd.DataFrame(Z,index=x,columns=y)

def getName(n=1,name=3,exchange=2,columns=None,mode='abc'):
	if columns:
		if isinstance(columns,str):
			columns=[columns]
		if n != len(columns):
			raise CufflinksError("Length of column names needs to be the \n"
				  "same length of traces")
	else:
		if mode is None:
			mode=get_config_file()['datagen_mode']
		if mode=='abc':
			columns=list(string.ascii_letters[:n])
		elif mode=='stocks':
			columns=[''.join(np.random.choice(list(string.ascii_uppercase),name)) + '.' + ''.join(np.random.choice(list(string.ascii_uppercase),exchange)) for _ in range(n)]
		else:
			raise CufflinksError("Unknown mode: {0}".format(mode))
	return columns




