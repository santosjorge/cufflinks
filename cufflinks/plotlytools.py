from ._tools import (
    getTheme,
    getThemes,
    getLayout,
    getAnnotations,
    iplot_to_dict,
    dict_to_iplot,
    _to_iplot,
    _iplot,
    get_colors,
    _scatter_matrix,
    _figure,
    iplot,
    _ta_figure,
    _ta_plot, 
)

import pandas as pd

pd.DataFrame.to_iplot=_to_iplot
pd.DataFrame.scatter_matrix=_scatter_matrix
pd.DataFrame.figure=_figure
pd.DataFrame.ta_plot=_ta_plot
pd.DataFrame.iplot=_iplot
pd.DataFrame.ta_figure=_ta_figure
pd.Series.ta_figure=_ta_figure
pd.Series.ta_plot=_ta_plot
pd.Series.figure=_figure
pd.Series.to_iplot=_to_iplot
pd.Series.iplot=_iplot
