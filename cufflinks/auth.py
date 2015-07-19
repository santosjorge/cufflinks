"""
Based in Plotly's tools module
"""


import os
import json
import warnings
from offline import go_offline

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
				 		"world_readable" : False,
				 		"theme" : "pearl",
				 		"colorscale" : "dflt",
				 		"offline" : False,
				 		"offline_url":'',
				 		"offline_show_link" : True,
				 		"offline_link_text" : 'Export to plot.ly'
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


def set_config_file(world_readable=None,theme=None,colorscale=None,offline=None,
					offline_url=None,offline_show_link=None,offline_link_text=None):
	"""
	Set the keyword-value pairs in `~/.config`.

	"""
	if not _file_permissions:
		raise Exception("You don't have proper file permissions "
									 "to run this function.")
	config = get_config_file()
	if world_readable is not None:
		config['world_readable'] = world_readable
	if theme:
		config['theme']=theme
	if colorscale:
		config['colorscale']=colorscale
	if offline is not None:
		config['offline']=offline
		if offline:
			go_offline()
	if offline_url:
		config['offline_url']=offline_url
	if offline_show_link is not None:
		config['offline_show_link']=offline_show_link
	if offline_link_text:
		config['offline_link_text']=offline_link_text
	save_json_dict(CONFIG_FILE, config)
	ensure_local_files()  


def get_config_file(*args):
    """
    Return specified args from `~/.confg`. as dict.
    Returns all if no arguments are specified.

    Example:
        get_config_file('world_readable')

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