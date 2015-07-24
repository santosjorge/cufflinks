import plotly.offline as py_offline

### Offline Mode	

def go_offline():
	py_offline.init_notebook_mode()
	py_offline.__PLOTLY_OFFLINE_INITIALIZED=True

def go_online():
	py_offline.__PLOTLY_OFFLINE_INITIALIZED=False

def is_offline():
	return py_offline.__PLOTLY_OFFLINE_INITIALIZED
