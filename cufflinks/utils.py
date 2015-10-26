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
				print (preString+tab+'{')
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

## Kwargs handlers

def kwargs_from_keyword(from_kwargs,to_kwargs,keyword,clean_origin=True):
	"""
	Looks for keys of the format keyword_value. 
	And return a dictionary with {keyword:value} format

	Parameters:
	-----------
		from_kwargs : dict
			Original dictionary
		to_kwargs : dict
			Dictionary where the items will be appended
		keyword : string
			Keyword to look for in the orginal dictionary
		clean_origin : bool
			If True then the k,v pairs from the original 
			dictionary are deleted
	"""
	for k in list(from_kwargs.keys()):
		if '{0}_'.format(keyword) in k:
			to_kwargs[k.replace('{0}_'.format(keyword),'')]=from_kwargs[k]
			if clean_origin:
				del from_kwargs[k]
	return to_kwargs

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

def deep_update(d,d_update):
	"""
	Updates the values (deep form) of a given dictionary

	Parameters:
	-----------
		d : dict
			dictionary that contains the values to update
		d_update : dict
			dictionary to be updated
	"""
	for k,v in list(d_update.items()):
		if isinstance(v,dict):
			if k in d:
				deep_update(d[k],v)
			else:
				d[k]=v
		else:
			d[k]=v
	return d
