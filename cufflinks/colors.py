##
# Special thanks to @krey for the python3 support
##

import numpy as np
import colorsys
import colorlover as cl
import operator
import copy

from collections import deque
from six import string_types
from IPython.display import HTML, display

from .utils import inverseDict
from .auth import get_config_file


class CufflinksError(Exception):
    pass


def to_rgba(color, alpha):
    """
    Converts from hex|rgb to rgba

    Parameters:
    -----------
            color : string
                    Color representation on hex or rgb
            alpha : float
                    Value from 0 to 1.0 that represents the 
                    alpha value.

    Example:
            to_rgba('#E1E5ED',0.6)
            to_rgba('#f03',0.7)
            to_rgba('rgb(23,23,23)',.5)
    """
    if type(color) == tuple:
        color, alpha = color
    color = color.lower()
    if 'rgba' in color:
        cl = list(eval(color.replace('rgba', '')))
        if alpha:
            cl[3] = alpha
        return 'rgba' + str(tuple(cl))
    elif 'rgb' in color:
        r, g, b = eval(color.replace('rgb', ''))
        return 'rgba' + str((r, g, b, alpha))
    else:
        return to_rgba(hex_to_rgb(color), alpha)


def hex_to_rgb(color):
    """
    Converts from hex to rgb

    Parameters:
    -----------
            color : string
                    Color representation on hex or rgb

    Example:
            hex_to_rgb('#E1E5ED')
            hex_to_rgb('#f03')
    """
    color = normalize(color)
    color = color[1:]
    # return 'rgb'+str(tuple(ord(c) for c in color.decode('hex')))
    return 'rgb' + str((int(color[0:2], base=16), int(color[2:4], base=16), int(color[4:6], base=16)))


def normalize(color):
    """
    Returns an hex color

    Parameters:
    -----------
            color : string
                    Color representation in rgba|rgb|hex

    Example:
            normalize('#f03')
    """
    if type(color) == tuple:
        color = to_rgba(*color)
    if 'rgba' in color:
        return rgb_to_hex(rgba_to_rgb(color))
    elif 'rgb' in color:
        return rgb_to_hex(color)
    elif '#' in color:
        if len(color) == 7:
            return color
        else:
            color = color[1:]
            return '#' + ''.join([x * 2 for x in list(color)])
    else:
        try:
            return normalize(cnames[color.lower()])
        except:
            raise CufflinksError('Not a valid color: ' + color)


def rgb_to_hex(color):
    """
    Converts from rgb to hex

    Parameters:
    -----------
            color : string
                    Color representation on hex or rgb

    Example:
            rgb_to_hex('rgb(23,25,24)')
    """
    rgb = eval(color.replace('rgb', ''))
    # return '#'+''.join(map(chr, rgb)).encode('hex')
    return '#' + ''.join(['{0:02x}'.format(x).upper() for x in rgb])


def rgba_to_rgb(color, bg='rgb(255,255,255)'):
    """
    Converts from rgba to rgb

    Parameters:
    -----------
            color : string
                    Color representation in rgba
            bg : string
                    Color representation in rgb

    Example:
            rgba_to_rgb('rgb(23,25,24,.4)''
    """
    def c_tup(c):
        return eval(c[c.find('('):])
    color = c_tup(color)
    bg = hex_to_rgb(normalize(bg))
    bg = c_tup(bg)
    a = color[3]
    r = [int((1 - a) * bg[i] + a * color[i]) for i in range(3)]
    return 'rgb' + str(tuple(r))


def hex_to_hsv(color):
    """
    Converts from hex to hsv

    Parameters:
    -----------
            color : string
                    Color representation on color

    Example:
            hex_to_hsv('#ff9933')
    """
    color = normalize(color)
    color = color[1:]
    # color=tuple(ord(c)/255.0 for c in color.decode('hex'))
    color = (int(color[0:2], base=16) / 255.0, int(color[2:4],
                                                   base=16) / 255.0, int(color[4:6], base=16) / 255.0)
    return colorsys.rgb_to_hsv(*color)


def color_range(color, N=20):
    """
    Generates a scale of colours from a base colour

    Parameters:
    -----------
            color : string
                    Color representation in hex
            N   : int
                    number of colours to generate

    Example:
            color_range('#ff9933',20)
    """
    color = normalize(color)
    org = color
    color = hex_to_hsv(color)
    HSV_tuples = [(color[0], x, color[2]) for x in np.arange(0, 1, 2.0 / N)]
    HSV_tuples.extend([(color[0], color[1], x)
                       for x in np.arange(0, 1, 2.0 / N)])
    hex_out = []
    for c in HSV_tuples:
        c = colorsys.hsv_to_rgb(*c)
        c = [int(_ * 255) for _ in c]
        # hex_out.append("#"+"".join([chr(x).encode('hex') for x in c]))
        hex_out.append("#" + "".join(['{0:02x}'.format(x) for x in c]))
    if org not in hex_out:
        hex_out.append(org)
    hex_out.sort()
    return hex_out


def color_table(color, N=1, sort=False, sort_values=False, inline=False, as_html=False):
    """
    Generates a colour table 

    Parameters:
    -----------
            color : string | list | dict
                    Color representation in rgba|rgb|hex
                    If a list of colors is passed then these
                    are displayed in a table
            N   : int
                    number of colours to generate
                    When color is not a list then it generaes 
                    a range of N colors
            sort : bool 
                    if True then items are sorted
            sort_values : bool 
                    if True then items are sorted by color values.
                    Only applies if color is a dictionary
            inline : bool
                    if True it returns single line color blocks
            as_html : bool
                    if True it returns the HTML code

    Example:
            color_table('#ff9933')
            color_table(cufflinks.cnames)
            color_table(['pink','salmon','yellow'])
    Note:
            This function only works in iPython Notebook
    """
    if isinstance(color, list):
        c_ = ''
        rgb_tup = [normalize(c) for c in color]
        if sort:
            rgb_tup.sort()
    elif isinstance(color, dict):
        c_ = ''
        items = [(k, normalize(v), hex_to_hsv(normalize(v)))
                 for k, v in list(color.items())]
        if sort_values:
            items = sorted(items, key=operator.itemgetter(2))
        elif sort:
            items = sorted(items, key=operator.itemgetter(0))
        rgb_tup = [(k, v) for k, v, _ in items]
    else:
        c_ = normalize(color)
        if N > 1:
            rgb_tup = np.array(color_range(c_, N))[::-1]
        else:
            rgb_tup = [c_]

    def _color(c):
        if hex_to_hsv(c)[2] < .5:
            color = "#ffffff"
            shadow = '0 1px 0 #000'
        else:
            color = "#000000"
            shadow = '0 1px 0 rgba(255,255,255,0.6)'
        if c == c_:
            border = " border: 1px solid #ffffff;"
        else:
            border = ''
        return color, shadow, border

    s = '<ul style="list-style-type: none;">' if not inline else ''
    for c in rgb_tup:
        if isinstance(c, tuple):
            k, c = c
            k += ' : '
        else:
            k = ''
        if inline:
            s += '<div style="background-color:{0};height:20px;width:20px;display:inline-block;"></div>'.format(
                c)
        else:
            color, shadow, border = _color(c)
            s += """<li style="text-align:center;""" + border + """line-height:30px;background-color:""" + c + """;"> 
            <span style=" text-shadow:""" + shadow + """; color:""" + color + """;">""" + k + c.upper() + """</span>
            </li>"""
    s += '</ul>' if not inline else ''
    if as_html:
        return s
    return display(HTML(s))


def colorgen(colors=None, n=None, scale=None, theme=None):
    """
    Returns a generator with a list of colors
    and gradients of those colors

    Parameters:
    -----------
            colors : list(colors)
                    List of colors to use

    Example:
            colorgen()
            colorgen(['blue','red','pink'])
            colorgen(['#f03','rgb(23,25,25)'])
    """
    from .themes import THEMES
    step = .1
    if not colors:
        if not scale:
            if not theme:
                scale = get_config_file()['colorscale']
            else:
                scale = THEMES[theme]['colorscale']
        colors = get_scales(scale)
    dq = deque(colors)
    if len(dq) == 0:
        dq = deque(get_scales('ggplot'))
    if n:
        step = len(dq) * 0.8 / n if len(dq) * 8 < n else .1
    for i in np.arange(.2, 1, step):
        for y in dq:
            yield to_rgba(y, 1 - i + .2)
        dq.rotate(1)

# NEW STUFF


# Color Names
# ---------------------------------


cnames = {'aliceblue': '#F0F8FF',
          'antiquewhite':	 '#FAEBD7',
          'aqua':			 '#00FFFF',
          'aquamarine':		 '#7FFFD4',
          'azure':			 '#F0FFFF',
          'beige':			 '#F5F5DC',
          'bisque':			 '#FFE4C4',
          'black':			 '#000000',
          'blanchedalmond':	 '#FFEBCD',
          'blue':			 '#3780bf',
          'bluegray':		 '#565656',
          'bluepurple':		 '#6432AB',
          'blueviolet':		 '#8A2BE2',
          'brick':			 '#E24A33',
          'brightblue':		 '#0000FF',
          'brightred':		 '#FF0000',
          'brown':			 '#A52A2A',
          'burlywood':		 '#DEB887',
          'cadetblue':		 '#5F9EA0',
          'charcoal':		 '#151516',
          'chartreuse':		 '#7FFF00',
          'chocolate':		 '#D2691E',
          'coral':			 '#FF7F50',
          'cornflowerblue':	 '#6495ED',
          'cornsilk':		 '#FFF8DC',
          'crimson':			 '#DC143C',
          'cyan':			 '#00FFFF',
          'darkblue':		 '#00008B',
          'darkcyan':		 '#008B8B',
          'darkgoldenrod':	 '#B8860B',
          'darkgray':		 '#A9A9A9',
          'darkgreen':		 '#006400',
          'darkgrey':		 '#A9A9A9',
          'darkkhaki':		 '#BDB76B',
          'darkmagenta':		 '#8B008B',
          'darkolivegreen':	 '#556B2F',
          'darkorange':		 '#FF8C00',
          'darkorchid':		 '#9932CC',
          'darkred':			 '#8B0000',
          'darksalmon':		 '#E9967A',
          'darkseagreen':	 '#8FBC8F',
          'darkslateblue':	 '#483D8B',
          'darkslategray':	 '#2F4F4F',
          'darkslategrey':	 '#2F4F4F',
          'darkturquoise':	 '#00CED1',
          'darkviolet':		 '#9400D3',
          'deeppink':		 '#FF1493',
          'deepskyblue':		 '#00BFFF',
          'dimgray':			 '#696969',
          'dimgrey':			 '#696969',
          'dodgerblue':		 '#1E90FF',
          'firebrick':		 '#B22222',
          'floralwhite':		 '#FFFAF0',
          'forestgreen':		 '#228B22',
          'fuchsia':			 '#FF00FF',
          'gainsboro':		 '#DCDCDC',
          'ghostwhite':		 '#F8F8FF',
          'gold':			 '#FFD700',
          'goldenrod':		 '#DAA520',
          'grassgreen':		 '#32ab60',
          'gray':			 '#808080',
          'green':			 '#008000',
          'greenyellow':		 '#ADFF2F',
          'grey':			 '#808080',
          'grey01':			 '#0A0A0A',
          'grey02':			 '#151516',
          'grey03':			 '#1A1A1C',
          'grey04':			 '#1E1E21',
          'grey05':			 '#252529',
          'grey06':			 '#36363C',
          'grey07':			 '#3C3C42',
          'grey08':			 '#434343',
          'grey09':			 '#666570',
          'grey10':			 '#666666',
          'grey11':			 '#8C8C8C',
          'grey12':			 '#C2C2C2',
          'grey13':			 '#E2E2E2',
          'grey14':			 '#E5E5E5',
          'honeydew':		 '#F0FFF0',
          'hotpink':			 '#FF69B4',
          'indianred':		 '#CD5C5C',
          'indigo':			 '#4B0082',
          'ivory':			 '#FFFFF0',
          'java':			 '#17BECF',
          'khaki':			 '#F0E68C',
          'lavender':		 '#E6E6FA',
          'lavenderblush':	 '#FFF0F5',
          'lawngreen':		 '#7CFC00',
          'lemonchiffon':	 '#FFFACD',
          'lightpink2':		 '#fccde5',
          'lightpurple':		 '#bc80bd',
          'lightblue':		 '#ADD8E6',
          'lightcoral':		 '#F08080',
          'lightcyan':		 '#E0FFFF',
          'lightgoldenrodyellow':	 '#FAFAD2',
          'lightgray':		 '#D3D3D3',
          'lightgreen':		 '#90EE90',
          'lightgrey':		 '#D3D3D3',
          'lightivory':		 '#F6F6F6',
          'lightpink':		 '#FFB6C1',
          'lightsalmon':		 '#FFA07A',
          'lightseagreen':	 '#20B2AA',
          'lightskyblue':	 '#87CEFA',
          'lightslategray':	 '#778899',
          'lightslategrey':	 '#778899',
          'lightsteelblue':	 '#B0C4DE',
          'lightteal':		 '#8dd3c7',
          'lightyellow':		 '#FFFFE0',
          'lightblue2':		 '#80b1d3',
          'lightviolet':		 '#8476CA',
          'lime':			 '#00FF00',
          'lime2':			 '#8EBA42',
          'limegreen':		 '#32CD32',
          'linen':			 '#FAF0E6',
          'magenta':			 '#FF00FF',
          'maroon':			 '#800000',
          'mediumaquamarine': '#66CDAA',
          'mediumblue':		 '#0000CD',
          'mediumgray': 	 '#656565',
          'mediumorchid':	 '#BA55D3',
          'mediumpurple':	 '#9370DB',
          'mediumseagreen':	 '#3CB371',
          'mediumslateblue':	 '#7B68EE',
          'mediumspringgreen': '#00FA9A',
          'mediumturquoise':	 '#48D1CC',
          'mediumvioletred':	 '#C71585',
          'midnightblue':	 '#191970',
          'mintcream':		 '#F5FFFA',
          'mistyrose':		 '#FFE4E1',
          'moccasin':		 '#FFE4B5',
          'mustard':			 '#FBC15E',
          'navajowhite':		 '#FFDEAD',
          'navy':			 '#000080',
          'oldlace':			 '#FDF5E6',
          'olive':			 '#808000',
          'olivedrab':		 '#6B8E23',
          'orange':			 '#ff9933',
          'orangered':		 '#FF4500',
          'orchid':			 '#DA70D6',
          'palegoldenrod':	 '#EEE8AA',
          'palegreen':		 '#98FB98',
          'paleolive':		 '#b3de69',
          'paleturquoise':	 '#AFEEEE',
          'palevioletred':	 '#DB7093',
          'papayawhip':		 '#FFEFD5',
          'peachpuff':		 '#FFDAB9',
          'pearl':			 '#D9D9D9',
          'pearl02':			 '#F5F6F9',
          'pearl03':			 '#E1E5ED',
          'pearl04':			 '#9499A3',
          'pearl05':			 '#6F7B8B',
          'pearl06':			 '#4D5663',
          'peru':			 '#CD853F',
          'pink':			 '#ff0088',
          'pinksalmon':		 '#FFB5B8',
          'plum':			 '#DDA0DD',
          'polar':			 '#ACAFB5',
          'polarblue':		 '#0080F0',
          'polarbluelight':	 '#46A0F0',
          'polarcyan':		 '#ADFCFC',
          'polardark':		 '#484848',
          'polardiv':		 '#D5D8DB',
          'polardust':		 '#F2F3F7',
          'polargrey':		 '#505050',
          'polargreen':		 '#309054',
          'polarorange':		 '#EE7600',
          'polarpurple':		 '#6262DE',
          'polarred':		 '#D94255',
          'powderblue':		 '#B0E0E6',
          'purple':			 '#800080',
          'red':				 '#db4052',
          'rose':			 '#FFC0CB',
          'rosybrown':		 '#BC8F8F',
          'royalblue':		 '#4169E1',
          'saddlebrown':		 '#8B4513',
          'salmon':			 '#fb8072',
          'sandybrown':		 '#FAA460',
          'seaborn':			 '#EAE7E4',
          'seagreen':		 '#2E8B57',
          'seashell':		 '#FFF5EE',
          'sienna':			 '#A0522D',
          'silver':			 '#C0C0C0',
          'skyblue':			 '#87CEEB',
          'slateblue':		 '#6A5ACD',
          'slategray':		 '#708090',
          'slategrey':		 '#708090',
          'smurf':			 '#3E6FB0',
          'snow':			 '#FFFAFA',
          'springgreen':		 '#00FF7F',
          'steelblue':		 '#4682B4',
          'tan':				 '#D2B48C',
          'teal':			 '#008080',
          'thistle':			 '#D8BFD8',
          'tomato':			 '#FF6347',
          'turquoise':		 '#40E0D0',
          'violet':			 '#EE82EE',
          'wheat':			 '#F5DEB3',
          'white':			 '#FFFFFF',
          'whitesmoke':		 '#F5F5F5',
          'yellow':			 '#ffff33',
          'yellowgreen':		 '#9ACD32',
          "henanigans_bg":      "#242424",
          "henanigans_blue1":   "#5F95DE",
          "henanigans_blue2":   "#93B6E6",
          "henanigans_cyan1":   "#7EC4CF",
          "henanigans_cyan2":   "#B6ECF3",
          "henanigans_dark1":   "#040404",
          "henanigans_dark2":   "#141414",
          "henanigans_dialog1": "#444459",
          "henanigans_dialog2": "#5D5D7A",
          "henanigans_green1":  "#8BD155",
          "henanigans_green2":  "#A0D17B",
          "henanigans_grey1":   "#343434",
          "henanigans_grey2":   "#444444",
          "henanigans_light1":  "#A4A4A4",
          "henanigans_light2":  "#F4F4F4",
          "henanigans_orange1": "#EB9E58",
          "henanigans_orange2": "#EBB483",
          "henanigans_purple1": "#C98FDE",
          "henanigans_purple2": "#AC92DE",
          "henanigans_red1":    "#F77E70",
          "henanigans_red2":    "#DE958E",
          "henanigans_yellow1": "#E8EA7E",
          "henanigans_yellow2": "#E9EABE"
          }

# Custom Color Scales
# ---------------------------------

_custom_scales = {
    'qual': {
        # dflt only exists to keep backward compatibility after issue 91
        'dflt': ['orange', 'blue', 'grassgreen', 'purple', 'red', 'teal', 'yellow', 'olive', 'salmon', 'lightblue2'],
        'original': ['orange', 'blue', 'grassgreen', 'purple', 'red', 'teal', 'yellow', 'olive', 'salmon', 'lightblue2'],
        'ggplot': ['brick', 'smurf', 'lightviolet', 'mediumgray', 'mustard', 'lime2', 'pinksalmon'],
        'polar': ['polarblue', 'polarorange', 'polargreen', 'polarpurple', 'polarred', 'polarcyan', 'polarbluelight'],
        'plotly' : ['rgb(31, 119, 180)', 'rgb(255, 127, 14)', 'rgb(44, 160, 44)', 'rgb(214, 39, 40)',
                    'rgb(148, 103, 189)', 'rgb(140, 86, 75)', 'rgb(227, 119, 194)', 'rgb(127, 127, 127)', 'rgb(188, 189, 34)', 'rgb(23, 190, 207)']
    },
    'div': {

    },
    'seq': {

    }

}


# ---------------------------------------------------------------
#  The below functions are based in colorlover by Jack Parmer
#  https://github.com/jackparmer/colorlover/
# ---------------------------------------------------------------


_scales = None
_scales_names = None


def interp(colors, N):
    def _interp(colors, N):
        try:
            return cl.interp(colors, N)
        except:
            return _interp(colors, N + 1)
    c = _interp(colors, N)
    return list(map(rgb_to_hex, cl.to_rgb(c)))


def scales(scale=None):
    """
    Displays a color scale (HTML)

    Parameters:
    -----------
            scale : str
                    Color scale name
                    If no scale name is provided then all scales are returned
                            (max number for each scale)
                    If scale='all' then all scale combinations available 
                            will be returned

    Example:
            scales('accent')
            scales('all')
            scales()
    """
    if scale:
        if scale == 'all':
            display(HTML(cl.to_html(_scales)))
        else:
            display(HTML(cl.to_html(get_scales(scale))))
    else:
        s = ''
        keys = list(_scales_names.keys())
        keys.sort()
        for k in keys:
            scale = get_scales(k)
            s += '<div style="display:inline-block;padding:10px;"><div>{0}</div>{1}</div>'.format(
                k, cl.to_html(scale))
        display(HTML(s))

# Scales Dictionary
# ---------------------------------


def reset_scales():
    global _scales
    global _scales_names
    scale_cpy = cl.scales.copy()

    # Add custom scales
    for k, v in list(_custom_scales.items()):
        if v:
            for k_, v_ in list(v.items()):
                if str(len(v_)) not in scale_cpy:
                    scale_cpy[str(len(v_))] = {}
                scale_cpy[str(len(v_))][k][k_] = [
                    hex_to_rgb(normalize(_)) for _ in v_]

    # Dictionary by Type > Name > N
    _scales = {}
    for k, v in list(scale_cpy.items()):
        for k_, v_ in list(v.items()):
            if k_ not in _scales:
                _scales[k_] = {}
            for k__, v__ in list(v_.items()):
                if k__ not in _scales[k_]:
                    _scales[k_][k__] = {}
                _scales[k_][k__][k] = v__

    # Dictionary by Name > N
    _scales_names = {}
    for k, v in list(scale_cpy.items()):
        for k_, v_ in list(v.items()):
            for k__, v__ in list(v_.items()):
                k__ = k__.lower()
                if k__ not in _scales_names:
                    _scales_names[k__] = {}
                _scales_names[k__][k] = v__


def get_scales(scale=None, n=None):
    """
    Returns a color scale 

    Parameters:
    -----------
            scale : str
                    Color scale name
                    If the color name is preceded by a minus (-) 
                    then the scale is inversed
            n : int
                    Number of colors 
                    If n < number of colors available for a given scale then 
                            the minimum number will be returned 
                    If n > number of colors available for a given scale then
                            the maximum number will be returned 

    Example:
            get_scales('accent',8)
            get_scales('pastel1')
    """
    if scale:
        is_reverse = False
        if scale[0] == '-':
            scale = scale[1:]
            is_reverse = True
        d = copy.deepcopy(_scales_names[scale.lower()])
        keys = list(map(int, list(d.keys())))
        cs = None
        if n:
            if n in keys:
                cs = d[str(n)]
            elif n < min(keys):
                cs = d[str(min(keys))]
        if cs is None:
            cs = d[str(max(keys))]
        if is_reverse:
            cs.reverse()
        return cs
    else:
        d = {}
        for k, v in list(_scales_names.items()):
            if isinstance(v, dict):
                keys = list(map(int, list(v.keys())))
                d[k] = v[str(max(keys))]
            else:
                d[k] = v
        return d


def get_colorscale(scale):
    """
    Returns a color scale to be used for a plotly figure

    Parameters:
    -----------
            scale : str or list
                    Color scale name
                    If the color name is preceded by a minus (-) 
                    then the scale is inversed.
                    Also accepts a list of colors (rgb,rgba,hex)

    Example:
            get_colorscale('accent')
            get_colorscale(['rgb(127,201,127)','rgb(190,174,212)','rgb(253,192,134)'])
    """

    if type(scale) in string_types:
        scale = get_scales(scale)
    else:
        if type(scale) != list:
            raise Exception(
                "scale needs to be either a scale name or list of colors")

    cs = [[1.0 * c / (len(scale) - 1), scale[c]] for c in range(len(scale))]
    cs.sort()
    return cs


reset_scales()
