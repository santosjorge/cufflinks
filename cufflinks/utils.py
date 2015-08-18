import pickle

def merge_dict(d1,d2):
	d=d2.copy()
	for k,v in list(d1.items()):
		if k not in d:
			d[k]=v
		else:
			if isinstance(v,dict):
				d[k]=merge_dict(d1[k],d[k])
	return d


def pp(el,preString=''):
	""" 
	Formats (prettyprint) a concatenated dictionary
	"""
	tab=' '*4
	if isinstance(el,dict):
		keys=list(el.keys())
		keys.sort()
		for key in keys:
			val=el[key]
			if isinstance(val,dict) or isinstance(val,list):
				print('%s%s :' % (preString,key))
				pp(val,preString+tab)
			else:
				print('%s%s  =  %s' % (preString,key,val))
	
	elif isinstance(el,list):
		print(preString+tab+'[')
		preString+=tab	
		for _ in el:
			if isinstance(_,dict):
				print(preString+tab+'{')
				pp(_,preString+tab*2)
				print(preString+tab+'}')
			elif isinstance(_,list):
				print(preString+tab+'[')
				pp(_,preString+tab)
				print(preString+tab+']')
			else:
				pp(_,preString+tab)
			#print preString+'      '+str('-')*10            
		print(preString	+']')
	else:
		print(preString+str(el))	

def inverseDict(d):
	"""
	Returns a dictionay indexed by values {value_k:key_k}
	Parameters:
	-----------
		d : dictionary
	"""
	dt={}
	for k,v in list(d.items()):
		if type(v) in (list,tuple):
			for i in v:
				dt[i]=k
		else:
			dt[v]=k
	return dt	

def check_kwargs(global_kwargs,values,local_kwargs=None):
	local_kwargs={} if not local_kwargs else local_kwargs
	for kw in values:
		if kw in global_kwargs:
			local_kwargs[kw]=global_kwargs[kw]
	return local_kwargs

def save_pickle(obj,filename):
	"""
	Serializes a given object
	Parameters:
	-----------
		obj : object
		filename : string
	"""
	return pickle.dump(obj,open(filename,'wb'))

def load_pickle(filename):
	"""
	Loads a serialized object
	Parameters:
	-----------
		filename : string
	"""
	return pickle.load(open(filename,'rb'))