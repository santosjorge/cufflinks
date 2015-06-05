"""

A productivity tool that binds pandas and plotly.
It also provides tools for color generation and transformation. 

Author: @jorgesantos

"""


from plotlytools import *
from pandastools import *
from utils import pp
from extract import to_df
import colors
import datetools
import utils
import datagen
from auth import set_config_file,get_config_file
from version import __version__
