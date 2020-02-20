import pandas as pd
import re



def _screen(self,include=True,**kwargs):
	"""
	Filters a DataFrame for columns that contain the given strings. 
	Parameters:
	-----------
		include : bool
			If False then it will exclude items that match 
			the given filters.
			This is the same as passing a regex ^keyword
		kwargs : 
			Key value pairs that indicate the column and 
			value to screen for

	Example:
		df.screen(col1='string_to_match',col2=['string1','string2'])
	"""
	df=self.copy()
	for k,v in list(kwargs.items()):
		v=[v] if type(v)!=list else v
		if include:
			df=df[df[k].str.contains('|'.join(v),flags=re.IGNORECASE).fillna(False)]
		else:
			df=df[df[k].str.contains('|'.join(v),flags=re.IGNORECASE).fillna(False)==False]
	return df

def _swapcolumns(self):
	"""
	Swaps first and second columns. 
	Useful for inverting axis when plotting. 

	Example:
		df.swapcolumns()

	Returns : DataFrame

	"""
	return self.reindex_axis([self.columns[1],self.columns[0]],axis=1)

def bestfit(self):
	"""
	Returns a series with the bestfit values. 
	
	Example:
		Series.bestfit()

	Returns: series
		The returned series contains a parameter 
		called 'formula' which includes the string representation 
		of the bestfit line. 
	"""
	# statsmodel cannot be included on requirements.txt
	# see https://github.com/scikit-learn/scikit-learn/issues/4164
	# which shares the same issue as statsmodel
	try:
		import statsmodels.api as sm
	except:
		raise Exception("statsmodels is required: " \
						"please run " \
						"pip install statsmodels" )

	if isinstance(self.index, pd.DatetimeIndex):
		x=pd.Series(list(range(1,len(self)+1)),index=self.index)
	else:
		x=self.index.values
		
	x=sm.add_constant(x)
	model=sm.OLS(self,x)
	fit=model.fit()
	vals=fit.params.values
	best_fit=fit.fittedvalues
	# the below methods have been deprecated in Pandas
	# model=pd.ols(x=x,y=self,intercept=True)
	# best_fit=model.y_fitted
	best_fit.formula='%.2f*x+%.2f' % (vals[1],vals[0])
	return best_fit

def normalize(self,asOf=None,multiplier=100):
	"""
	Returns a normalized series or DataFrame
	
	Example:
		Series.normalize()

	Returns: series of DataFrame
	
	Parameters:
	-----------
		asOf : string
			Date format
			'2015-02-29'
		multiplier : int
			Factor by which the results will be adjusted
	"""
	if not asOf:
		x0=self.iloc[0]
	else:
		x0=self.loc[asOf]
	return self/x0*multiplier

def read_google(url,**kwargs):
	"""
	Reads a google sheet
	"""
	if url[-1]!='/':
		url+='/'
	return pd.read_csv(url+'export?gid=0&format=csv',**kwargs)

pd.DataFrame.screen=_screen
pd.DataFrame.swapcolumns=_swapcolumns
pd.DataFrame.normalize=normalize
pd.read_google=read_google
pd.Series.normalize=normalize
pd.Series.bestfit=bestfit

