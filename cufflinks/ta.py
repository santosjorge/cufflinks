## TECHNICHAL ANALYSIS
import pandas as pd
import numpy as np

def _make_list(val):
	return val if isinstance(val,list) else [val]

def get_column_name(name,study=None,str=None,period=None,column=None):
	if str:
		study='' if name==study else study
		return str.format(study=study,period=period,column=column,name=name)
	else:
		return name

def validate(df,column=None):
	if isinstance(df,pd.DataFrame):
		if column is not None:
			df=pd.DataFrame(df[column])
			_df=pd.DataFrame()
		elif len(df.columns)>1:
			raise Exception("DataFrame needs to be a single column \n"
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

def rename(df,_df,study,periods,column,include,str,detail,output=None):
	d_name=dict([(i,get_column_name(i,study=study,str=str,
					period=periods,column=column)) for i in _df.columns])

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

def rsi(df,periods=14,column=None,include=True,str=None,detail=False,**kwargs):
	def _rsi(df,periods=14,column=None,include=True,str=None,detail=False):
		study='RSI'
		df,_df,column=validate(df,column)
		_df['Up']=df[column].diff().apply(lambda x:x if x>0 else 0)
		_df['Down']=df[column].diff().apply(lambda x:-x if x<0 else 0)
		_df['UpAvg']=pd.rolling_mean(_df['Up'],window=periods)
		_df['DownAvg']=pd.rolling_mean(_df['Down'],window=periods)
		_df['RSI']=100-(100/(1+_df['UpAvg']/_df['DownAvg']))
		return rename(df,_df,study,periods,column,include,str,detail)
	column=_make_list(column)
	periods=_make_list(periods)
	str=str if str else '{name}({column},{period})'
	__df=pd.concat([_rsi(df,column=x,periods=y,include=False,str=str,detail=detail) for y in periods for x in column],axis=1)
	if include:
		return pd.concat([df,__df],axis=1)
	else:
		return __df



def sma(df,periods=21,column=None,include=True,str=None,detail=False,**sma_kwargs):
	def _sma(df,periods=21,column=None,include=True,str=None,detail=False,**sma_kwargs):
		study='SMA'
		df,_df,column=validate(df,column)
		_df['SMA']=pd.rolling_mean(df[column],periods,**sma_kwargs)
		str=str if str else '{name}({period})'
		return rename(df,_df,study,periods,column,include,str,detail)
	column=_make_list(column)
	periods=_make_list(periods)
	str=str if str else '{name}({column},{period})'
	__df=pd.concat([_sma(df,column=x,periods=y,include=False,str=str) for y in periods for x in column],axis=1)
	if include:
		return pd.concat([df,__df],axis=1)
	else:
		return __df

def boll(df,periods=20,boll_std=2,column=None,include=True,str=None,detail=False,**boll_kwargs):
	def _boll(df,periods=21,column=None,include=True,str=None,detail=False,output=None,**boll_kwargs):
		study='BOLL'
		df,_df,column=validate(df,column)
		_df['SMA']=pd.rolling_mean(df[column],periods)
		_df['UPPER']=_df['SMA']+pd.rolling_std(df[column],periods)*boll_std
		_df['LOWER']=_df['SMA']-pd.rolling_std(df[column],periods)*boll_std
		str=str if str else '{name}({period})'
		return rename(df,_df,study,periods,column,include,str,detail,output=output)
	column=_make_list(column)
	periods=_make_list(periods)
	str=str if str else '{name}({column},{period})'
	output=['SMA','UPPER','LOWER']
	__df=pd.concat([_boll(df,column=x,periods=y,include=False,str=str,detail=detail,output=output) for y in periods for x in column],axis=1)
	if include:
		return pd.concat([df,__df],axis=1)
	else:
		return __df

def macd(df,fast_period=12,slow_period=26,signal_period=9,column=None,include=True,str=None,detail=False,**macd_kwargs):
	def _macd(df,periods=21,column=None,include=True,str=None,detail=False,output=None,**macd_kwargs):
		study='MACD'
		if slow_period<fast_period:
			raise Exception("slow_period cannot be less than fast_period")
		def __macd(s,periods):
			macd_f=[]
			factor=2.0/(periods+1)
			macd_f.append(s[0])
			for i in range(1,len(s)):
				macd_f.append(s[i]*factor+macd_f[i-1]*(1-factor))
			return pd.Series(macd_f,index=s.index)
		df,_df,column=validate(df,column)
		_df['FAST']=__macd(df[column],fast_period)
		_df['SLOW']=__macd(df[column],slow_period)
		_df['MACD']=_df['FAST']-_df['SLOW']
		_df['SIGNAL']=__macd(_df['MACD'],signal_period)
		str=str if str else '{name}({period})'
		return rename(df,_df,study,periods,column,include,str,detail,output=output)
	column=_make_list(column)
	periods=_make_list(fast_period)
	str=str if str else '{name}({column},{period})'
	output=['MACD','SIGNAL']
	__df=pd.concat([_macd(df,column=x,periods=y,include=False,str=str,detail=detail,output=output) for y in periods for x in column],axis=1)
	if include:
		return pd.concat([df,__df],axis=1)
	else:
		return __df
