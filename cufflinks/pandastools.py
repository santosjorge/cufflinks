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
	x=pd.Series(list(range(1,len(self)+1)),index=self.index)
	model=pd.ols(x=x,y=self,intercept=True)
	best_fit=model.y_fitted
	best_fit.formula='%.2f*x+%.2f' % (model.beta.x,model.beta.intercept)
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
		x0=self.ix[0]
	else:
		x0=self.ix[asOf]
	return self/x0*multiplier

pd.DataFrame.screen=_screen
pd.DataFrame.swapcolumns=_swapcolumns
pd.DataFrame.normalize=normalize
pd.Series.normalize=normalize
pd.Series.bestfit=bestfit
