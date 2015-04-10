##Cufflinks

This library binds the power of [plotly](http://www.plot.ly) with the flexibility of [pandas](http://pandas.pydata.org/) for easy plotting.

This library is available on https://github.com/santosjorge/cufflinks

This tutorial assumes that the plotly user credentials have already been configured as stated on the [getting started](https://plot.ly/python/getting-started/) guide.

A full tutorial for Plotly integration can be seen [here](http://nbviewer.ipython.org/gist/santosjorge/cfaaf43b40db19d6127a).

There is also an example for color management which can be found [here](http://nbviewer.ipython.org/gist/santosjorge/00ca17b121fa2463e18b)


### Release Notes

#### v0.3

* Integration with [colorlover](https://github.com/jackparmer/colorlover/)
** Support for scales `iplot(scale='accent')` to plot a chart using an *accent* color scale
** cufflinks.scales() to see all available scales
* Support for named colors
** `iplot(colors=['pink','red','yellow'])`

