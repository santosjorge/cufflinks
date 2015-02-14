
import colors

			
def pp(el,preString=''):
	""" 
	Formats (prettyprint) a concatenated dictionary
	"""
	tab=' '*4
	if isinstance(el,dict):
		keys=el.keys()
		keys.sort()
		for key in keys:
			val=el[key]
			if isinstance(val,dict) or isinstance(val,list):
				print '%s%s :' % (preString,key)
				pp(val,preString+tab)
			else:
				print '%s%s  =  %s' % (preString,key,val)
	
	elif isinstance(el,list):
		print preString+tab+'['
		preString+=tab	
		for _ in el:
			if isinstance(_,dict):
				print preString+tab+'{'
				pp(_,preString+tab*2)
				print preString+tab+'}'
			elif isinstance(_,list):
				print preString+tab+'['
				pp(_,preString+tab)
				print preString+tab+']'
			else:
				pp(_,preString+tab)
			#print preString+'      '+str('-')*10            
		print preString	+']'
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