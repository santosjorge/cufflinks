import collections
import numpy as np
import colorsys
from IPython.display import HTML,display

class CufflinksError(Exception):
		pass

# Colour Definitions
# ---------------------------------


orange='#ff9933'
blue='#3780bf'
pink='#ff0088'
green='#32ab60'
red='#db4052'
purple='#6432AB'
white="#FFFFFF"
black="#000000"


charcoal="#151516"
grey01="#0A0A0A"
grey02="#151516"
grey03="#1A1A1C"
grey04="#1E1E21"
grey05="#252529"
grey06="#36363C"
grey07="#3C3C42"
grey08="#434343"
grey09="#666570"
grey10="#666666"
grey11="#8C8C8C"
grey12="#C2C2C2"
grey13="#E2E2E2"

pearl='#D9D9D9'
pearl02="#F5F6F9"
pearl03="#E1E5ED"
pearl04="#9499A3"
pearl05="#6F7B8B"
pearl06="#4D5663"
seaborn="#EAE7E4"

def to_rgba(color,alpha):
	"""
	Converts from hex|rgb to rgba

	Parameters:
	-----------
		color : string
			Color representation on hex or rgb
		alpha : float
			Value from 0 to 1.0 that represents the 
			alpha value.

	Example:
		to_rgba('#E1E5ED',0.6)
		to_rgba('#f03',0.7)
		to_rgba('rgb(23,23,23)',.5)
	"""
	color=color.lower()
	if 'rgba' in color:
		cl=list(eval(color.replace('rgba','')))
		cl[3]=alpha
		return 'rgba'+str(tuple(cl))
	elif 'rgb' in color:
		r,g,b=eval(color.replace('rgb',''))
		return 'rgba'+str((r,g,b,alpha))
	else:
		return to_rgba(hex_to_rgb(color),alpha)

def hex_to_rgb(color):
	"""
	Converts from hex to rgb

	Parameters:
	-----------
		color : string
			Color representation on hex or rgb

	Example:
		hex_to_rgb('#E1E5ED')
		hex_to_rgb('#f03')
	"""
	color=normalize(color)
	color=color[1:]
	return 'rgb'+str(tuple(ord(c) for c in color.decode('hex')))

def normalize(color):
	"""
	Returns an hex color 

	Parameters:
	-----------
		color : string
			Color representation in rgba|rgb|hex

	Example:
		normalize('#f03')
	"""
	if 'rgba' in color:
		return rgb_to_hex(rgba_to_rgb(color))
	elif 'rgb' in color:
		return rgb_to_hex(color)
	elif '#' in color:
		if len(color)==7:
			return color
		else:
			color=color[1:]
			return '#'+''.join([x*2 for x in list(color)])
	else:
		try:
			return normalize(eval(color))
		except:
			raise CufflinksError('Not a valid color')


def rgb_to_hex(color):
	"""
	Converts from rgb to hex

	Parameters:
	-----------
		color : string
			Color representation on hex or rgb

	Example:
		rgb_to_hex('rgb(23,25,24)')
	"""
	rgb=eval(color.replace('rgb',''))
	return '#'+''.join(map(chr, rgb)).encode('hex')

def rgba_to_rgb(color,bg='rgb(255,255,255)'):
	"""
	Converts from rgba to rgb

	Parameters:
	-----------
		color : string
			Color representation in rgba
		bg : string
			Color representation in rgb

	Example:
		rgba_to_rgb('rgb(23,25,24,.4)''
	"""	
	def c_tup(c):
		return eval(c[c.find('('):])
	color=c_tup(color)
	bg=hex_to_rgb(normalize(bg))
	bg=c_tup(bg)
	a=color[3]
	r=[int((1-a)*bg[i]+a*color[i]) for i in range(3)]
	return 'rgb'+str(tuple(r))

def hex_to_hsv(color):
	"""
	Converts from hex to hsv

	Parameters:
	-----------
		color : string
			Color representation on color

	Example:
		hex_to_hsv('#ff9933')
	"""
	color=normalize(color)
	color=color[1:]
	color=tuple(ord(c)/255.0 for c in color.decode('hex'))
	return colorsys.rgb_to_hsv(*color)


def color_range(color,N=20):
	"""
	Generates a scale of colours from a base colour

	Parameters:
	-----------
		color : string
			Color representation in hex
		N   : int
			number of colours to generate

	Example:
		color_range('#ff9933',20)
	"""	
	color=normalize(color)
	org=color
	color=hex_to_hsv(color)
	HSV_tuples = [(color[0], x, color[2]) for x in np.arange(0,1,2.0/N)]
	HSV_tuples.extend([(color[0], color[1], x) for x in np.arange(0,1,2.0/N)])
	hex_out=[]
	for c in HSV_tuples:
		c = colorsys.hsv_to_rgb(*c)
		c = map(lambda _: int(_*255.0),c)
		hex_out.append("#"+"".join(map(lambda x: chr(x).encode('hex'),c)))
	if org not in hex_out:
		hex_out.append(org)
	hex_out.sort()
	return hex_out

def color_table(color,N=1):
	"""
	Generates a colour table 

	Parameters:
	-----------
		color : string or list
			Color representation in rgba|rgb|hex
			If a list of colors is passed then these
			are displayed in a table
		N   : int
			number of colours to generate
			When color is not a list then it generaes 
			a range of N colors

	Example:
		color_range('#ff9933',20)

	Note:
		This function only works in iPython Notebook
	"""		
	if type(color)==list:
		c_=''
		rgb_tup=[normalize(c) for c in color]
	else:
		c_=normalize(color)
		if N>1:
			rgb_tup=np.array(color_range(c_,N))
		else:
			rgb_tup=[c_]
	def _color(c):
		if hex_to_hsv(c)[2]<.5:
				color="#ffffff"
				shadow='0 1px 0 #000'
		else:
			color="#000000"
			shadow='0 1px 0 rgba(255,255,255,0.6)'
		if c==c_:
			border=" border: 1px solid #ffffff;"
		else:
			border='' 
		return color,shadow,border

	s='<ul style="list-style-type: none;">'
	for c in reversed(rgb_tup):
		color,shadow,border=_color(c)
		s+="""<li style="text-align:center;"""+border+"""line-height:30px;background-color:"""+ c + """;"> 
		<span style=" text-shadow:"""+shadow+"""; color:"""+color+""";">"""+c+"""</span>
		</li>"""
	s+='</ul>'
	return HTML(s)


def colorgen(colors=None):
	"""
	Returns a generator with a list of colors
	and gradients of those colors

	Parameters:
	-----------
		colors : list(colors)
			List of colors to use

	Example:
		colorgen()
		colorgen(['blue','red','pink'])
		colorgen(['#f03','rgb(23,25,25)'])
	"""
	if colors:
		dq=collections.deque(colors)
	else:
		dq=collections.deque([orange,blue,green,purple,red])
	for i in np.arange(0,1,.2):
		for y in dq:
			yield to_rgba(y,1-i)
		dq.rotate()
