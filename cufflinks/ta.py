## TECHNICHAL ANALYSIS
import pandas as pd
import numpy as np
# import talib
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
	elif type(df_or_figure)==Figure or type(df_or_figure) == dict:
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
		
	for v in list(c_dir.values()):
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
		## === talib ==== 
		# _df['RSI']=pd.Series(talib.RSI(df[column].values,periods),index=df.index)
		## === /talib ==== 

		## === pure python ==== 
		_df['Up']=df[column].diff().apply(lambda x:x if x>0 else 0)
		_df['Down']=df[column].diff().apply(lambda x:-x if x<0 else 0)
		_df['UpAvg']=_df['Up'].rolling(window=periods).mean()
		_df['DownAvg']= _df['Down'].rolling(window=periods).mean()
		_df['RSI']=100-(100/(1+_df['UpAvg']/_df['DownAvg']))
		## === /pure python ==== 

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

		## === talib ==== 
		# _df['SMA']=pd.Series(talib.MA(df[column].values,periods),index=df.index)
		## === /talib ==== 

		## === pure python ==== 
		_df['SMA']=df[column].rolling(periods).mean()
		## === /pure python ==== 

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
		
		## === talib ==== 
		# _df['EMA']=pd.Series(talib.EMA(df[column].values,periods),index=df.index)
		## === /talib ==== 

		## === pure python ==== 
		_df['EMA']=df[column].ewm(span=periods,min_periods=periods,adjust=False).mean()
		## === /pure python ==== 

		return rename(df,_df,study,periods,column,include,str,detail)
	column=make_list(column)
	periods=make_list(periods)
	__df=pd.concat([_ema(df,column=x,periods=y,include=False,str=str) for y in periods for x in column],axis=1)
	if include:
		return pd.concat([df,__df],axis=1)
	else:
		return __df

def dmi(df,periods=14,high='high',low='low',close='close',include=True,str='{name}({period})',**kwargs):
	return adx(df,periods=periods,high=high,low=low,close=close,di=True,include=include,str=str,**kwargs)

def adx(df,periods=14,high='high',low='low',close='close',di=False,include=True,str='{name}({period})',**kwargs):
	def _adx(df,periods,high,low,close,include,str,detail):
		study='ADX'
		_df=pd.DataFrame()
		## === talib ==== 
		# _df['ADX']=pd.Series(talib.ADX(df[high].values,
		#					   df[low].values,df[close].values,
		#     				   periods),index=df.index)
		## === /talib ==== 

		## === pure python ==== 
		def smooth(col):
			sm=col.rolling(periods).sum()
			for _ in list(range(periods+1,len(col))):
				sm.iloc[_]=sm.iloc[_-1]-(1.0*sm.iloc[_-1]/periods)+col.iloc[_]
			return sm

		def smooth2(col):
			sm=col.rolling(periods).mean()
			for _ in list(range(periods*2,len(col))):
				sm.iloc[_]=((sm.iloc[_-1]*(periods-1))+col[_])/periods
			return sm

		_df['TR']=pd.DataFrame(dict(enumerate([df[high]-df[low],abs(df[high]-df[close].shift(1)),
                             abs(df[low]-df[close].shift(1))]))).apply(max,axis=1)
		__df=pd.DataFrame(dict(enumerate([df[high]-df[high].shift(1),df[low].shift(1)-df[low]])))
		_df['DM+']=__df.apply(lambda x:max(x[0],0) if x[0]>x[1] else 0,axis=1)
		_df['DM-']=__df.apply(lambda x:max(x[1],0) if x[1]>x[0] else 0,axis=1)
		_df.iloc[0]=np.nan
		_df_smooth=_df.apply(smooth)
		
		_df['DI+']=100.0*_df_smooth['DM+']/_df_smooth['TR']
		_df['DI-']=100.0*_df_smooth['DM-']/_df_smooth['TR']
		dx=pd.DataFrame(100*abs(_df['DI+']-_df['DI-'])/(_df['DI+']+_df['DI-']))
		
		_df['ADX']=dx.apply(smooth2)[0]
		## === /pure python ==== 
		return rename(df,_df,study,periods,'',include,str,detail,output=output)
	detail=kwargs.get('detail',False)
	periods=make_list(periods)
	output=['ADX','DI+','DI-'] if di else ['ADX']
	__df=pd.concat([_adx(df,periods=y,high=high,low=low,close=close,include=False,str=str,detail=detail) for y in periods],axis=1)
	if include:
		return pd.concat([df,__df],axis=1)
	else:
		return __df

def atr(df,periods=14,high='high',low='low',close='close',include=True,str='{name}({period})',**kwargs):
	def _atr(df,periods,high,low,close,include,str,detail=False):
		study='ATR'
		_df=pd.DataFrame()
		## === talib ==== 
		# _df['ATR']=pd.Series(talib.ATR(df[high].values,
		# 							   df[low].values,
		# 							   df[close].values,
		# 							   periods),index=df.index)
		## === /talib ==== 

		## === pure python ==== 
		_df['HmL']=df[high]-df[low]
		_df['HmC']=abs(df[high]-df[close].shift(1))
		_df['LmC']=abs(df[low]-df[close].shift(1))
		_df['TR']=_df.apply(max,axis=1)
		_df['ATR']=_df['TR'].rolling(periods).mean()
		## === /pure python ==== 
		return rename(df,_df,study,periods,'',include,str,detail)
	periods=make_list(periods)
	__df=pd.concat([_atr(df,periods=y,high=high,low=low,close=close,include=False,str=str) for y in periods],axis=1)
	if include:
		return pd.concat([df,__df],axis=1)
	else:
		return __df

def ptps(df,periods=14,initial='long',af=.02,high='high',low='low',include=True,str='{name}({period})',**kwargs):
	def _ptps(df,periods,high,low,include,str,detail):
		study='PTPS'
		_df=pd.DataFrame(columns=['SAR','LorS','EP','EP+-SAR','AF','AF_Diff','T_SAR','Reversal','LONG','SHORT'],
              index=df.index)
		_df=_df.reset_index()

		_df.loc[0,'LorS']=initial
		_df.loc[0,'T_SAR']=None
		_df.loc[0,'EP']=df[high][0] if initial=='long' else df[low][0]
		_df.loc[0,'AF']=af

		for _ in range(1,len(df)):
			# LorS - Long or Short
			if _df['LorS'][_-1]=='long':
				if _df['T_SAR'][_-1]>=df[low][_]:
					_df.loc[_,'LorS']='short'
				else:
					_df.loc[_,'LorS']=_df.loc[_-1,'LorS']
			else:
				if _df['T_SAR'][_-1]<=df[high][_]:
					_df.loc[_,'LorS']='long'
				else:
					_df.loc[_,'LorS']=_df.loc[_-1,'LorS']
			# SAR - Stop and Reversal
			if _==1:
				_df.loc[1,'SAR']=df[low][0] if initial=='long' else df[high][0]
			else:
				_df.loc[_,'SAR']=_df['EP'][_-1] if _df['LorS'][_-1]!=_df['LorS'][_] else _df['T_SAR'][_-1]
					
			# EP - Extreme Price
			if _df['LorS'][_]=='long':
				if _df['SAR'][_]>=df[low][_]:
					_df.loc[_,'EP']=df[low][_]
				else:
					_df.loc[_,'EP']=df[high][_] if df[high][_]>_df['EP'][_-1] else _df['EP'][_-1]
			else:
				if _df['SAR'][_]<=df[high][_]:
					_df.loc[_,'EP']=df[high][_]
				else:
					_df.loc[_,'EP']=df[low][_] if df[low][_]<_df['EP'][_-1] else _df['EP'][_-1]
					
			# EP+-SAR - Extreme Price +/- Stop and Reversal
			_df.loc[_,'EP+-SAR']=abs(_df['EP'][_]-_df['SAR'][_])
			
			# AF - Acceleration Factor
			if _df['LorS'][_]!=_df['LorS'][_-1]:
				_df.loc[_,'AF']=af
			else:
				if _df['LorS'][_]=='long':
					if _df['SAR'][_]>=df[low][_]:
						_df.loc[_,'AF']=af
					else:
						if (df[high][_]>_df['EP'][_-1] if _df['LorS'][_]=='long' else df[low][_]<_df['EP'][_-1]):
							_df.loc[_,'AF']=min(0.2,af+_df['AF'][_-1])
						else:
							_df.loc[_,'AF']=_df['AF'][_-1]
				else:
					if _df['SAR'][_]<=df[high][_]:
						_df.loc[_,'AF']=af
					else:
						if (df[high][_]>_df['EP'][_-1] if _df['LorS'][_]=='long' else df[low][_]<_df['EP'][_-1]):
							_df.loc[_,'AF']=min(0.2,af+_df['AF'][_-1])
						else:
							_df.loc[_,'AF']=_df['AF'][_-1]
			# AF Diff
			_df.loc[_,'AF_Diff']=_df['EP+-SAR'][_]*_df['AF'][_]
			
			# T_SAR - Tomorrow's Stop and Reversal
			if _df['LorS'][_]=='long':
				if _df['SAR'][_]>=df[low][_]:
					_df.loc[_,'T_SAR']=max(_df['SAR'][_]-_df['AF_Diff'][_],df[high][_],df[high][_-1])
				else:
					_df.loc[_,'T_SAR']=min(_df['SAR'][_]+_df['AF_Diff'][_],df[low][_],df[low][_-1])
			else:
				if _df['SAR'][_]<=df[high][_]:
					_df.loc[_,'T_SAR']=min(_df['SAR'][_]+_df['AF_Diff'][_],df[low][_],df[low][_-1])
				else:
					_df.loc[_,'T_SAR']=max(_df['SAR'][_]-_df['AF_Diff'][_],df[low][_],df[low][_-1])
					
			# Reversal
			if _df['LorS'][_-1]=='long':
				if _df['T_SAR'][_-1]>=df[low][_]:
					_df.loc[_,'Reversal']=_df['T_SAR'][_-1]
			else:
				if _df['T_SAR'][_-1]<=df[high][_]:
					_df.loc[_,'Reversal']=_df['T_SAR'][_-1]
		
		
		_df['LONG']=_df.apply(lambda x:x['T_SAR'] if x['LorS']=='long' else np.nan,axis=1)
		_df['SHORT']=_df.apply(lambda x:x['T_SAR'] if x['LorS']=='short' else np.nan,axis=1)
		_df=_df.set_index('index')
			
		return rename(df,_df,study,periods,'',include,str,detail,output=output)
	detail=kwargs.get('detail',False)
	periods=make_list(periods)
	output=['LONG','SHORT']
	__df=pd.concat([_ptps(df,periods=y,high=high,low=low,include=False,str=str,detail=detail) for y in periods],axis=1)
	if include:
		return pd.concat([df,__df],axis=1)
	else:
		return __df


def cci(df,periods=14,high='high',low='low',close='close',include=True,str='{name}({period})',**kwargs):
	def _cci(df,periods,high,low,close,include,str,detail=False):
		study='CCI'
		_df=pd.DataFrame()
		## === talib ==== 
		# _df['CCI']=pd.Series(talib.CCI(df[high].values,
		# 							   df[low].values,
		# 							   df[close].values,
		# 							   periods),index=df.index)
		## === /talib ==== 

		## === pure python ==== 
		_df['tp']=df[[low,high,close]].mean(axis=1)
		_df['avgTp']=_df['tp'].rolling(window=periods).mean()
		mad = lambda x: np.fabs(x - x.mean()).mean()
		_df['mad']=_df['tp'].rolling(window=periods).apply(mad)
		_df['CCI']=(_df['tp']-_df['avgTp'])/(0.015*_df['mad'])
		## === /pure python ==== 

		return rename(df,_df,study,periods,'',include,str,detail)
	periods=make_list(periods)
	__df=pd.concat([_cci(df,periods=y,high=high,low=low,close=close,include=False,str=str) for y in periods],axis=1)
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

		## === talib ==== 
		# upper,middle,lower=talib.BBANDS(df[column].values,periods,boll_std,boll_std)
		# _df=pd.DataFrame({'SMA':middle,'UPPER':upper,'LOWER':lower},index=df.index)
		## === /talib ==== 

		## === pure python ==== 
		_df['SMA']=df[column].rolling(window=periods).mean()
		_df['UPPER']=_df['SMA']+df[column].rolling(window=periods).std()*boll_std
		_df['LOWER']=_df['SMA']-df[column].rolling(window=periods).std()*boll_std
		## === /pure python ==== 

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
		df,_df,column=validate(df,column)

		## === talib ==== 
		# macd,signal,hist=talib.MACD(df[column].values,fast_period,slow_period,signal_period)
		# _df=pd.DataFrame({'MACD':macd,'SIGNAL':signal},index=df.index)
		## === /talib ===

		## === pure python ===
		def __macd(s,periods):
			macd_f=[]
			factor=2.0/(periods+1)
			macd_f.append(s[0])
			for i in range(1,len(s)):
				macd_f.append(s[i]*factor+macd_f[i-1]*(1-factor))
			return pd.Series(macd_f,index=s.index)
		_df['FAST']=__macd(df[column],fast_period)
		_df['SLOW']=__macd(df[column],slow_period)
		_df['MACD']=_df['FAST']-_df['SLOW']
		_df['SIGNAL']=__macd(_df['MACD'],signal_period)
		## === /pure python ===

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


