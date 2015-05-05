import numpy as np
import pandas as pd
import string


def scatter3d(n_categories=5,n=10,prefix='category'):
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
	"""
	categories=[]
	for i in range(n_categories):
		categories.extend([prefix+str(i+1)]*n)
	return pd.DataFrame({'x':np.random.randn(n*n_categories),
						 'y':np.random.randn(n*n_categories),
						 'z':np.random.randn(n*n_categories),
						 'text':getName(n*n_categories),
						 'categories':categories})

def bubble3d(n_categories=5,n=10,prefix='category'):
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
	"""	
	categories=[]
	for i in range(n_categories):
		categories.extend([prefix+str(i+1)]*n)
	return pd.DataFrame({'x':np.random.randn(n*n_categories),
						 'y':np.random.randn(n*n_categories),
						 'z':np.random.randn(n*n_categories),
						 'size':np.random.randint(1,100,n*n_categories),
						 'text':getName(n*n_categories),
						 'categories':categories}) 

def bubble(n_categories=5,n=10,prefix='category'):
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
	"""	
	categories=[]
	for i in range(n_categories):
		categories.extend([prefix+str(i+1)]*n)
	return pd.DataFrame({'x':np.random.randn(n*n_categories),
						 'y':np.random.randn(n*n_categories),
						 'size':np.random.randint(1,100,n*n_categories),
						 'text':getName(n*n_categories),
						 'categories':categories})                             

def scatter(n_categories=5,n=10,prefix='category'):
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
	"""	
	categories=[]
	for i in range(n_categories):
		categories.extend([prefix+str(i+1)]*n)
	return pd.DataFrame({'x':np.random.randn(n*n_categories),
						 'y':np.random.randn(n*n_categories),
						 'text':getName(n*n_categories),
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

def lines(n_traces=5,n=100):
	"""
	Returns a DataFrame with the required format for 
	a scatter (lines) plot

	Parameters:
	-----------
		n_traces : int
			Number of traces 
		n : int
			Number of points for each trace
	"""	
	df=pd.DataFrame(np.random.randn(n,n_traces),index=pd.date_range('1/1/15',periods=n),
		columns=getName(n_traces))
	return df.cumsum()  

def box(n_traces=5,n=100):
	"""
	Returns a DataFrame with the required format for 
	a box plot

	Parameters:
	-----------
		n_traces : int
			Number of traces 
		n : int
			Number of points for each trace
	"""	
	df=pd.DataFrame([np.random.chisquare(np.random.randint(2,10),n_traces) for _ in range(n)],
		columns=getName(n_traces))
	return df       

def histogram(n_traces=1,n=500):
	"""
	Returns a DataFrame with the required format for 
	a box plot

	Parameters:
	-----------
		n_traces : int
			Number of traces 
		n : int
			Number of points for each trace
	"""	
	df=pd.DataFrame(np.random.randn(n,n_traces),
		columns=getName(n_traces))                     
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

def getName(n=1,name=3,exchange=2):
	return [''.join(np.random.choice(list(string.uppercase),name)) + '.' + ''.join(np.random.choice(list(string.uppercase),exchange)) for _ in range(n)]