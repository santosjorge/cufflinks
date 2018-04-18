from .plotlytools import _iplot
import pandas as pd


class IPlotter():

    def __init__(self, df):
        self.df = df

    def scatter(self, *args, **kwargs):
        return _iplot(self=self.df, kind='scatter', *args, **kwargs)

    def heatmap(self, *args, **kwargs):
        return _iplot(self=self.df, kind='heatmap', *args, **kwargs)


def iplotter_prop(self):
    return IPlotter(df=self)


def define_iplot_as_namedomain():
    pd.DataFrame.iplot = property(iplotter_prop)
    return
