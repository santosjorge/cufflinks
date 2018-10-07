import pickle
import six
import copy


def is_string(val):
	return isinstance(val,six.string_types)

def is_list(val):
	return type(val) in (list,tuple)

def is_dict(val):
	return isinstance(val,dict)

def make_list(val):
	return [val] if not is_list(val) else val

def make_string(val):
	return str(val) if not is_string(val) else val

def make_dict_from_list(val):
	return dict([(_,None) for _ in val])

def merge_dict(d1,d2):
	"""
		d1 <-- d2
	"""
	d=copy.deepcopy(d2)
	for k,v in list(d1.items()):
		if k not in d:
			d[k]=v
		else:
			if isinstance(v,dict):
				d[k]=merge_dict(d1[k],d[k])
	return d

def dict_path(from_d,to_d={},l=[]):
	"""
	Returns a dictionary with the path in which each of the keys is found

	Parameters:
		from_d : dict
			Dictionary that contains all the keys, values
		to_d : dict
			Dictionary to which the results will be appended

	Example: 
		dict_path({'level1':{'level2':{'level3':'value'}}})
		Returns
			{'level1': [],
		 	 'level2': ['level1'],
		 	 'level3': ['level1', 'level2']
		 	}
	"""
	for k,v in list(from_d.items()):
		if isinstance(v,dict):
			to_d[k]=l
			_l=copy.deepcopy(l)
			_l.append(k)
			to_d=dict_path(from_d[k],to_d,_l)
		else:
			to_d[k]=l
	_to_d=to_d.copy()
	to_d={}
	return _to_d

def dict_update(d,k,val,d_ref=None):
    d_ref=d if not d_ref else d
    path=dict_path(d_ref)
    if path:
        reduce(dict.get, path[k],d).update({k:val})
    else:
        d.update(k=val)
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

def check_kwargs(global_kwargs,values,local_kwargs=None,clean_origin=False):
	local_kwargs={} if not local_kwargs else local_kwargs
	for kw in values:
		if kw in global_kwargs:
			local_kwargs[kw]=global_kwargs[kw]
			if clean_origin:
				del global_kwargs[kw]
	return local_kwargs

def dict_replace_keyword(d,keyword,kwargs,forceupdate=True):
	d=d.copy()
	for _k,_v in list(kwargs.items()):
				if keyword in _k:
					k=_k.replace(keyword,'')
					if keyword not in d:
						d[keyword]={k:_v}
					else:
						if forceupdate:
							d[keyword].update({k:_v})
						else:
							if k not in d[keyword]:	
								d[keyword].update({k:_v})
				else:
					if forceupdate:
						d[_k]=_v
					else:
						if _k not in d: 			
							d[_k]=_v
						
	return d

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
		elif isinstance(d,list):
			d.append({k:v})
		else:
			d[k]=v
	return d

def read_google(self,url,**kwargs):
	"""
	Reads a google sheet
	"""
	if url[-1]!='/':
		url+='/'
	return self.read_csv(url+'export?gid=0&format=csv',**kwargs)
