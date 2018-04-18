import plotly.offline as py_offline

### Offline Mode	

def run_from_ipython():
    try:
        __IPYTHON__
        return True
    except NameError:
        return False


def go_offline(connected=False):
    if run_from_ipython():
        try:
            py_offline.init_notebook_mode(connected)
        except TypeError:
            #For older versions of plotly
            py_offline.init_notebook_mode()
        py_offline.__PLOTLY_OFFLINE_INITIALIZED=True

def go_online():
	py_offline.__PLOTLY_OFFLINE_INITIALIZED=False

def is_offline():
	return py_offline.__PLOTLY_OFFLINE_INITIALIZED

def upgrade(url=None):
	from .auth import get_config_file
	if not url:
		if 'http' not in get_config_file()['offline_url']:
			raise Exception("No default offline URL set \n"
							"Please run cf.set_config_file(offline_url=xx) to set \n"
							"the default offline URL.")
		else:
			url=get_config_file()['offline_url']
	py_offline.download_plotlyjs(url)
