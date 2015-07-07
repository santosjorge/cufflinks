"""

A productivity tool that binds pandas and plotly.
It also provides tools for color generation and transformation. 

Author: @jorgesantos

"""


import colors
import datetools
import utils
import datagen
import tools
import pandastools

from plotlytools import *
from plotly.plotly import plot,iplot
from utils import pp
from tools import subplots,scatter_matrix,figures
from extract import to_df
from auth import set_config_file,get_config_file
from version import __version__

