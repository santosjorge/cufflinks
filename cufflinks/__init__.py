"""

A productivity tool that binds pandas and plotly.
It also provides tools for color generation and transformation. 

Author: @jorgesantos

"""



from . import datetools
from . import utils
from . import datagen
from . import tools
from . import colors
from . import pandastools
from . import ta

from .plotlytools import *
from plotly.plotly import plot
from .utils import pp
from .tools import subplots,scatter_matrix,figures
from .extract import to_df
from .auth import set_config_file,get_config_file
from .offline import is_offline,go_offline,go_online
from .version import __version__

try:
	if get_config_file()['offline']:
		go_offline()
	else:
		go_online()
except:
	pass
