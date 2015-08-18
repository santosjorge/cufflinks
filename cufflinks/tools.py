from ._tools import (
    strip_figures,
    get_base_layout,
    figures,
    merge_figures,
    subplots,
    get_subplots,
    _ohlc_dict,
    get_ohlc,
    get_candle,
    scatter_matrix,
    trace_dict,
    get_ref,
    get_def,
    get_len,
    get_which,
    get_ref_axis,
    get_dom,
    axis,
    _set_axis,
    get_shape,
    get_error_bar,
    set_errors,
    go_offline,
    is_offline
)

from plotly.graph_objs import Figure

Figure.axis=axis
Figure.trace_dict=trace_dict
Figure.set_axis=_set_axis 
