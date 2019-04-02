"""
Based in Plotly's tools module
"""


import os
import json
import warnings
from .offline import go_offline

package='cufflinks'

if os.path.exists(os.path.join(os.path.expanduser('~'),os.path.join('Dropbox','AppData'))):
	AUTH_DIR=os.path.join(os.path.join(os.path.expanduser('~'),os.path.join('Dropbox','AppData')),'.'+package)
else:
	AUTH_DIR = os.path.join(os.path.expanduser("~"), "."+package)

CREDENTIALS_FILE = os.path.join(AUTH_DIR, ".credentials")
CONFIG_FILE = os.path.join(AUTH_DIR, ".config")
TEST_DIR = os.path.join(os.path.expanduser("~"), ".test")
PICKLE_FILE=os.path.join(AUTH_DIR,".pickle")
TEST_FILE = os.path.join(AUTH_DIR, ".permission_test")

_FILE_CONTENT = {
				 CONFIG_FILE: {
				 		"sharing" : "public",
				 		"theme" : "pearl",
				 		"colorscale" : "dflt",
				 		"offline" : False,
				 		"offline_connected" : True,
				 		"offline_url":'',
				 		"offline_show_link" : True,
				 		"offline_link_text" : 'Export to plot.ly',
				 		"datagen_mode" : 'stocks',
				 		"dimensions" : None,
						"margin" : None,
						"offline_config" : None
						}
				 }

try:
	os.mkdir(TEST_DIR)
	os.rmdir(TEST_DIR)
	if not os.path.exists(AUTH_DIR):
		os.mkdir(AUTH_DIR)
	f = open(TEST_FILE, 'w')
	f.write('testing\n')
	f.close()
	os.remove(TEST_FILE)
	_file_permissions = True
except:
	_file_permissions = False                 


def get_path():
	return AUTH_DIR

def get_pickle_path():
	return PICKLE_FILE

def check_file_permissions():
	return _file_permissions

def ensure_local_files():
	"""
	Ensure that filesystem is setup/filled out in a valid way
	"""
	if _file_permissions:
		if not os.path.isdir(AUTH_DIR):
			os.mkdir(AUTH_DIR)
		for fn in [CONFIG_FILE]:
			contents = load_json_dict(fn)
			for key, val in list(_FILE_CONTENT[fn].items()):
				if key not in contents:
					contents[key] = val
			contents_keys = list(contents.keys())
			for key in contents_keys:
				if key not in _FILE_CONTENT[fn]:
					del contents[key]
			save_json_dict(fn, contents)
	else:
		warnings.warn("Looks like you don't have 'read-write' permission to "
					  "your 'home' ('~') directory")


def set_config_file(sharing=None,theme=None,colorscale=None,offline=None,offline_connected=None,
					offline_url=None,offline_show_link=None,offline_link_text=None,
					offline_config=None,
					datagen_mode=None,**kwargs):
	"""
	Set the keyword-value pairs in `~/.config`.

	sharing : string
			Sets the sharing level permission
				public - anyone can see this chart
				private - only you can see this chart
				secret - only people with the link can see the chart
	theme : string
			Sets the default theme
			See cufflinks.getThemes() for available themes 
	colorscale : string
			Sets the default colorscale
			See cufflinks.scales()
	offline : bool
			If true then the charts are rendered
			locally. 
	offline_connected : bool
			If True, the plotly.js library will be loaded
			from an online CDN. If False, the plotly.js library will be loaded locally
			from the plotly python package
	offline_show_link : bool
			If true then the chart will show a link to 
			plot.ly at the bottom right of the chart 
	offline_link_text : string
			Text to display as link at the bottom 
			right of the chart 
	offline_config : dict
			Additional configuration options
			For the complete list of config options check out: 
			https://github.com/plotly/plotly.js/blob/master/src/plot_api/plot_config.js
	datagen_mode : string
			Mode in which the data is generated
			by the datagen module
				stocks : random stock names are used for the index
				abc : alphabet values are used for the index
	dimensions : tuple
			Sets the default (width,height) of the chart
	margin : dict or tuple
			Dictionary (l,r,b,t) or
			Tuple containing the left,
			right, bottom and top margins
	"""
	if not _file_permissions:
		raise Exception("You don't have proper file permissions "
									 "to run this function.")
	valid_kwargs=['world_readable','dimensions','margin','offline_config']
	for key in list(kwargs.keys()):
		if key not in valid_kwargs:
			raise Exception("Invalid keyword : '{0}'".format(key))
	if all(['world_readable' in kwargs,sharing is None]):
		sharing=kwargs['world_readable']
	if isinstance(sharing,bool):
			if sharing:
				sharing='public'
			else:
				sharing='private'
	config = get_config_file()
	if sharing is not None:
		config['sharing'] = sharing
	if theme:
		config['theme']=theme
	if colorscale:
		config['colorscale']=colorscale
	if offline_connected:
		config['offline_connected']=offline_connected
	if offline is not None:
		config['offline']=offline
		if offline:
			go_offline()
	if datagen_mode:
		config['datagen_mode']=datagen_mode
	if offline_url:
		config['offline_url']=offline_url
	if offline_show_link is not None:
		config['offline_show_link']=offline_show_link
	if offline_link_text:
		config['offline_link_text']=offline_link_text
	if offline_config:
		config['offline_config']=offline_config
	for _ in valid_kwargs:
		if _ in kwargs:
			config[_]=kwargs[_]
	save_json_dict(CONFIG_FILE, config)
	ensure_local_files()  


def get_config_file(*args):
    """
    Return specified args from `~/.confg`. as dict.
    Returns all if no arguments are specified.

    Example:
        get_config_file('sharing')

    """
    if _file_permissions:
        ensure_local_files()  
        return load_json_dict(CONFIG_FILE, *args)
    else:
        return _FILE_CONTENT[CONFIG_FILE]


def load_json_dict(filename, *args):
	"""Checks if file exists. Returns {} if something fails."""
	data = {}
	if os.path.exists(filename):
		with open(filename, "r") as f:
			try:
				data = json.load(f)
				if not isinstance(data, dict):
					data = {}
			except:
				pass 
		if args:
			return {key: data[key] for key in args if key in data}
	return data


def save_json_dict(filename, json_dict):
	"""Will error if filename is not appropriate, but it's checked elsewhere.
	"""
	if isinstance(json_dict, dict):
		with open(filename, "w") as f:
			f.write(json.dumps(json_dict, indent=4))
	else:
		raise TypeError("json_dict was not a dictionay. couldn't save.")