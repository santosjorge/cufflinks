"""

A productivity tool that binds pandas and plotly.
Kudos to the Plotly team!

Author: @jorgesantos

"""
from __future__ import absolute_import

from . import date_tools
from . import utils
from . import datagen
from . import tools
from . import colors
from . import pandastools
from . import ta

from .plotlytools import *
from plotly.plotly import plot
from .colors import cnames, get_colorscale
from .utils import pp
from .tools import subplots,scatter_matrix,figures,getLayout,getThemes,getTheme
from .extract import to_df
from .auth import set_config_file,get_config_file
from .quant_figure import QuantFig
from .offline import is_offline,go_offline,go_online
from .version import __version__

import sys
if sys.version_info.major >= 3:
    from io import StringIO
else:
    from StringIO import StringIO

class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout

with Capturing() as output:
    try:
        if get_config_file()['offline']:
            go_offline()
        else:
            go_online()
    except:
        pass
