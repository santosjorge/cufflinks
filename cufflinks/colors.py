import collections
import numpy as np


# Colour Definitions
# ---------------------------------

grid='#434343'
tickfont='#666666'
charcoal="#151516"
pearl='#D9D9D9'
orange='#ff9933'
blue='#3780bf'
pink='#f08'
green='#32ab60'
red='#db4052'
purple='#6432AB'
white="#FFFFFF"
black="#000000"
grey02="#E2E2E2"
grey03="#C2C2C2"
grey04="#8C8C8C"
grey05="#666570"
grey06="#3C3C42"
grey07="#36363C"
grey08="#252529"
grey09="#1E1E21"
grey10="#1A1A1C"
grey11="#151516"
grey12="#0A0A0A"
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
	Converts 3 value hex to a 6 value equivalent

	Parameters:
	-----------
		color : string
			Color representation on hex or rgb

	Example:
		normalize('#f03')
	"""
	if '#' not in color:
		return normalize(eval(color))
	elif len(color)==7:
		return color
	else:
		color=color[1:]
		return '#'+''.join([x*2 for x in list(color)])

def rgb_to_hex(color):
	"""
	Converts from rgb to hex

	Parameters:
	-----------
		color : string
			Color representation on hex or rgb

	Example:
		rgb_to_hex('rgb(23,25,24')
	"""
	rgb=eval(color.replace('rgb',''))
	return '#'+''.join(map(chr, rgb)).encode('hex')

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
