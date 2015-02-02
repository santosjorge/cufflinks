
def dictTabbed(el,preString=''):
	""" 
	Formats (prettyprint) a concatenated dictionary
	"""
	if type(el)==dict:
		for key,val in el.items():
			if type(val) in (dict,list):
				print '%s%s :' % (preString,key)
				dictTabbed(val,preString+'    ')
			else:
				print '%s%s  =  %s' % (preString,key,val)
	elif type(el)==list:
		for _ in el:
			dictTabbed(_,preString+'      ')
			print preString+'      '+str('-')*10            
	else:
		print preString+str(el)	

def inverseDict(d):
	"""
	Returns a dictionay indexed by values {value_k:key_k}
	Parameters:
	-----------
		d : dictionary
	"""
	dt={}
	for k,v in d.items():
		if type(v) in (list,tuple):
			for i in v:
				dt[i]=k
		else:
			dt[v]=k
	return dt	