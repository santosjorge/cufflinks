## TECHNICHAL ANALYSIS
import pandas as pd
import numpy as np
import talib
from plotly.graph_objs import Figure
from .utils import make_list


class StudyError(Exception):
	pass

def _ohlc_dict(df_or_figure,open='',high='',low='',close='',volume='',
			   validate='',**kwargs):
	"""
	Returns a dictionary with the actual column names that 
	correspond to each of the OHLCV values.

	df_or_figure :  DataFrame or Figure
	open : string
		Column name to be used for OPEN values
	high : string
		Column name to be used for HIGH values
	low : string
		Column name to be used for LOW values
	close : string
		Column name to be used for CLOSE values
	volume : string
		Column name to be used for VOLUME values
	validate : string
		Validates that the stated column exists
		Example:
			validate='ohv' | Will ensure Open, High
							 and close values exist. 
	"""
	c_dir={}
	ohlcv=['open','high','low','close','volume']
	if type(df_or_figure)==pd.DataFrame:
		cnames=df_or_figure.columns
	elif type(df_or_figure)==Figure:
		cnames=df_or_figure.axis['ref'].keys()
	elif type(df_or_figure)==pd.Series:
		cnames=[df_or_figure.name]
	c_min=dict([(v.lower(),v) for v in cnames])
	for _ in ohlcv:
		if _ in c_min.keys():
			c_dir[_]=c_min[_]
		else:
			for c in cnames:
				if _ in c.lower():
					c_dir[_]=c

	if open:
		c_dir['open']=open
	if high:
		c_dir['high']=high
	if low:
		c_dir['low']=low
	if close:
		c_dir['close']=close
	if volume:
		c_dir['volume']=volume
		
	for k,v in c_dir.items():
		if v not in cnames:
			raise StudyError('{0} is not a valid column name'.format(v))

	if validate:
			errs=[]
			val=validate.lower()
			s_names=dict([(_[0],_) for _ in ohlcv])
			cols=[_[0] for _ in c_dir.keys()]
			for _ in val:
				if _ not in cols:
					errs.append(s_names[_])
			if errs:
				raise StudyError('Missing Columns: {0}'.format(', '.join(errs)))

	return c_dir


def get_column_name(name,study=None,str=None,period=None,column=None,period_dict=None):
	if str:
		if period_dict:
			if name in period_dict:
				period=period_dict[name]
		study='' if name.lower()==study.lower() else study
		return str.format(study=study,period=period,column=column,name=name)
	else:
		return name

def validate(df,column=None):
	if isinstance(df,pd.DataFrame):
		if column is not None:
			df=pd.DataFrame(df[column])
			_df=pd.DataFrame()
		elif len(df.columns)>1:
			raise StudyError("DataFrame needs to be a single column \n"
							"Or the column name needs to be specified")
		else:
			df=df.copy()
			_df=pd.DataFrame()
			column=df.columns[0]
	else:
		df=pd.DataFrame(df)
		_df=pd.DataFrame()
		column=df.columns[0]
	return df,_df,column

def rename(df,_df,study,periods,column,include,str,detail,output=None,period_dict=None):
	d_name=dict([(i,get_column_name(i,study=study,str=str,
					period=periods,column=column,period_dict=period_dict)) for i in _df.columns])

	_df=_df.rename(columns=d_name)
	if detail:
		__df=_df
	elif output:
		__df=_df[[d_name[_] for _ in output]]
	else:
		__df=_df[d_name[study]]

	if include:
		return pd.concat([df,__df],axis=1)
	else:
		return __df

"""

INIDICATORS

"""

def rsi(df,periods=14,column=None,include=True,str='{name}({column},{period})',detail=False,**kwargs):
	def _rsi(df,periods,column,include,str,detail):
		study='RSI'
		df,_df,column=validate(df,column)
		_df['RSI']=pd.Series(talib.RSI(df[column].values,periods),index=df.index)
		return rename(df,_df,study,periods,column,include,str,detail)
	column=make_list(column)
	periods=make_list(periods)
	__df=pd.concat([_rsi(df,column=x,periods=y,include=False,str=str,detail=detail) for y in periods for x in column],axis=1)
	if include:
		return pd.concat([df,__df],axis=1)
	else:
		return __df


def sma(df,periods=21,column=None,include=True,str='{name}({column},{period})',detail=False):
	def _sma(df,periods,column,include,str,detail=False):
		study='SMA'
		df,_df,column=validate(df,column)
		_df['SMA']=pd.Series(talib.MA(df[column].values,periods),index=df.index)
		return rename(df,_df,study,periods,column,include,str,detail)
	column=make_list(column)
	periods=make_list(periods)
	__df=pd.concat([_sma(df,column=x,periods=y,include=False,str=str) for y in periods for x in column],axis=1)
	if include:
		return pd.concat([df,__df],axis=1)
	else:
		return __df

def ema(df,periods=21,column=None,include=True,str='{name}({column},{period})',detail=False):
	def _ema(df,periods,column,include,str,detail=False):
		study='EMA'
		df,_df,column=validate(df,column)
		_df['EMA']=pd.Series(talib.EMA(df[column].values,periods),index=df.index)
		return rename(df,_df,study,periods,column,include,str,detail)
	column=make_list(column)
	periods=make_list(periods)
	__df=pd.concat([_ema(df,column=x,periods=y,include=False,str=str) for y in periods for x in column],axis=1)
	if include:
		return pd.concat([df,__df],axis=1)
	else:
		return __df

def atr(df,periods=21,high='high',low='low',close='close',include=True,str='{name}({period})',**kwargs):
	def _atr(df,periods,high,low,close,include,str,detail=False):
		study='ATR'
		_df=pd.DataFrame()
		_df['ATR']=pd.Series(talib.ATR(df[high].values,
									   df[low].values,
									   df[close].values,
									   periods),index=df.index)
		return rename(df,_df,study,periods,'',include,str,detail)
	periods=make_list(periods)
	__df=pd.concat([_atr(df,periods=y,high=high,low=low,close=close,include=False,str=str) for y in periods],axis=1)
	if include:
		return pd.concat([df,__df],axis=1)
	else:
		return __df

def correl(df,periods=21,columns=None,include=True,str=None,detail=False,how='value',**correl_kwargs):
	"""
		how : string
			value
			pct_chg
			diff
	"""
	def _correl(df,periods=21,columns=None,include=True,str=None,detail=False,**correl_kwargs):
		study='CORREL'
		df,_df,columns=validate(df,columns)

		_df['CORREL'] = df[columns[0]].rolling(window=periods,**correl_kwargs).corr(df[columns[1]])

		str=str if str else 'CORREL({column1},{column2},{period})'.format(column1=columns[0],column2=columns[1],period=periods)
		return rename(df,_df,study,periods,columns,include,str,detail)
	columns=df.columns if not columns else columns
	if len(columns) != 2: 
		raise StudyError("2 Columns need to be specified for a correlation study")
	periods=make_list(periods)
	if how=='pct_chg':
		df=df[columns].pct_change()
	elif how=='diff':
		df=df[columns].diff()
	__df=pd.concat([_correl(df,columns=columns,periods=y,include=False,str=str) for y in periods],axis=1)
	if include:
		return pd.concat([df,__df],axis=1)
	else:
		return __df

def boll(df,periods=20,boll_std=2,column=None,include=True,str='{name}({column},{period})',detail=False,**boll_kwargs):
	def _boll(df,periods,column):
		study='BOLL'
		df,_df,column=validate(df,column)
		upper,middle,lower=talib.BBANDS(df[column].values,periods,boll_std,boll_std)
		_df=pd.DataFrame({'SMA':middle,'UPPER':upper,'LOWER':lower},index=df.index)
		return rename(df,_df,study,periods,column,False,str,detail,output=output)
	column=make_list(column)
	periods=make_list(periods)
	output=['SMA','UPPER','LOWER']
	__df=pd.concat([_boll(df,column=x,periods=y) for y in periods for x in column],axis=1)
	if include:
		return pd.concat([df,__df],axis=1)
	else:
		return __df


def macd(df,fast_period=12,slow_period=26,signal_period=9,column=None,include=True,str=None,detail=False,**macd_kwargs):
	periods='({0},{1},{2})'.format(fast_period,slow_period,signal_period)
	def _macd(df,column,include):
		study='MACD'
		macd,signal,hist=talib.MACD(df[column].values,fast_period,slow_period,signal_period)
		_df=pd.DataFrame({'MACD':macd,'SIGNAL':signal},index=df.index)
		period_dict={'FAST':fast_period,
					 'SLOW':slow_period,
					 'MACD':'[{0},{1}]'.format(fast_period,slow_period),
					 'SIGNAL':signal_period}
		return rename(df,_df,study,periods,column,include,str,detail,output=output,period_dict=period_dict)
	
	if slow_period<fast_period:
		raise StudyError("slow_period cannot be less than fast_period")
	column=make_list(column)
	str=str if str else '{name}({column},{period})'
	output=['MACD','SIGNAL']
	__df=pd.concat([_macd(df,column=x,include=False) for x in column],axis=1)

	if include:
		return pd.concat([df,__df],axis=1)
	else:
		return __df


