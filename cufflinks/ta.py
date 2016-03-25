## TECHNICHAL ANALYSIS
import pandas as pd
import numpy as np

class StudyError(Exception):
	pass

def _make_list(val):
	return val if isinstance(val,list) else [val]

def get_column_name(name,study=None,str=None,period=None,column=None,period_dict=None):
	if str:
		if period_dict:
			if name in period_dict:
				period=period_dict[name]
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

def rsi(df,periods=14,column=None,include=True,str=None,detail=False,**kwargs):
	def _rsi(df,periods=14,column=None,include=True,str=None,detail=False):
		study='RSI'
		df,_df,column=validate(df,column)
		_df['Up']=df[column].diff().apply(lambda x:x if x>0 else 0)
		_df['Down']=df[column].diff().apply(lambda x:-x if x<0 else 0)

		_df['UpAvg']=_df['Up'].rolling(window=periods).mean()
		_df['DownAvg']= df['Down'].rolling(window=periods).mean()

		
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

		_df['SMA'] = df[column].rolling(window=periods,**sma_kwargs).mean()

		
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
	periods=_make_list(periods)
	if how=='pct_chg':
		df=df[columns].pct_change()
	elif how=='diff':
		df=df[columns].diff()
	__df=pd.concat([_correl(df,columns=columns,periods=y,include=False,str=str) for y in periods],axis=1)
	if include:
		return pd.concat([df,__df],axis=1)
	else:
		return __df

def boll(df,periods=20,boll_std=2,column=None,include=True,str=None,detail=False,**boll_kwargs):
	def _boll(df,periods=21,column=None,include=True,str=None,detail=False,output=None,**boll_kwargs):
		study='BOLL'
		df,_df,column=validate(df,column)

		_df['SMA']=df[column].rolling(window=periods).mean()
		_df['UPPER']=_df['SMA']+df[column].rolling(window=periods).std()*boll_std
		_df['LOWER']=_df['SMA']-df[column].rolling(window=periods).std()*boll_std

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
	def _macd(df,periods=None,column=None,include=True,str=None,detail=False,
			  output=None,period_dict=None,**macd_kwargs):
		study='MACD'
		if slow_period<fast_period:
			raise StudyError("slow_period cannot be less than fast_period")
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
		period_dict={'FAST':fast_period,
					 'SLOW':slow_period,
					 'MACD':'({0},{1})'.format(fast_period,slow_period),
					 'SIGNAL':signal_period}
		return rename(df,_df,study,periods,column,include,str,detail,output=output,period_dict=period_dict)
	column=_make_list(column)
	str=str if str else '{name}({column},{period})'
	output=['MACD','SIGNAL']
	__df=pd.concat([_macd(df,column=x,include=False,str=str,detail=detail,
		output=output) for x in column],axis=1)
	

	if include:
		return pd.concat([df,__df],axis=1)
	else:
		return __df
