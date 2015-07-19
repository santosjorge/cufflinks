import plotly.offline as py_offline

### Offline Mode	

def go_offline(offline=True):
	if offline:
		py_offline.init_notebook_mode()
		py_offline.__PLOTLY_OFFLINE_INITIALIZED=True
	else:
		py_offline.__PLOTLY_OFFLINE_INITIALIZED=False

def is_offline():
	return py_offline.__PLOTLY_OFFLINE_INITIALIZED
