###
# Tests require nose 1.3.x
###


import cufflinks as cf
import pandas as pd
import unittest
from nose.tools import assert_equals

##
## nosetests -xv tests.py --with-coverage --cover-package=cufflinks
##




class TestIPlot(unittest.TestCase):
	def setUp(self):
		self.df = pd.DataFrame(dict(x=[1, 2, 3], y=[4, 2, 1], c=[3, 1, 5]))

	def _iplot(self, df, **kwargs):
		return df.iplot(asFigure=True, **kwargs)

	def _ta(self, df, study, **kwargs):
		# print(study,kwargs)
		return df.ta_figure(study,**kwargs)

	def test_scatter_matrix(self):
		self.df.scatter_matrix(asFigure=True)

def test_irregular_subplots():
	df = cf.datagen.bubble(10, 50, mode='stocks')
	figs = cf.figures(df, [
		dict(kind='histogram', keys='x', color='blue'),
		dict(kind='scatter', mode='markers', x='x', y='y', size=5),
		dict(kind='scatter', mode='markers', x='x', y='y',
			 size=5, color='teal')],asList=True)
	figs.append(cf.datagen.lines(1).figure(bestfit=False, colors=['blue'],
										   bestfit_colors=['pink']))
	base_layout = cf.tools.get_base_layout(figs)
	sp = cf.subplots(figs, shape=(3, 2), base_layout=base_layout,
					 vertical_spacing=.15, horizontal_spacing=.03,
					 specs=[[{'rowspan': 2}, {}], [None, {}],
							[{'colspan': 2}, None]],
					 subplot_titles=['Histogram', 'Scatter 1',
									 'Scatter 2', 'Bestfit Line'])
	sp['layout'].update(showlegend=False)
	return sp


def bar_input_argument_tests():
	options = {
		'kind': ['bar', 'barh'],
		'barmode': ['stack', 'overlay', 'group'],
		'bargap': [0.1],
		'subplots': [True]
	}

	def bar_test(self, **kwargs):
		self._iplot(self.df, **kwargs)

	_generate_tests(TestIPlot, bar_test, 'bar', options)


def bar_row_input_argument_tests():
	options = {
		'kind': ['bar', 'barh'],
		'barmode': ['stack', 'overlay', 'group'],
		'bargap': [0.1],
		'subplots': [True]
	}

	def bar_row_test(self, **kwargs):
		self._iplot(self.df.ix[1], **kwargs)

	_generate_tests(TestIPlot, bar_row_test, 'bar_row', options)


def histogram_input_argument_tests():
	options = {
		'barmode': ['stack'],
		'bins': [20],
		'orientation': ['h', 'v'],
		'histnorm': ['probability','percent','density'],
		'subplots': [True],
		'line_color':['blue','#fa0']
	}

	def histogram_test(self, **kwargs):
		self._iplot(self.df, kind='histogram', **kwargs)

	_generate_tests(TestIPlot, histogram_test, 'histogram', options)


def heatmap_input_argument_tests():
	options = {}

	def heatmap_test(self, **kwargs):
		self._iplot(self.df, kind='heatmap', **kwargs)
		df=cf.datagen.heatmap()
		df.index=cf.pd.period_range('1/1/2016',periods=5)
		self._iplot(df,kind='heatmap', **kwargs)
		# df.iplot(kind='heatmap')

	_generate_tests(TestIPlot, heatmap_test, 'heatmap', options)

def box_input_argument_tests():
	options = {}

	def box_test(self, **kwargs):
		self._iplot(self.df, kind='box', **kwargs)

	_generate_tests(TestIPlot, box_test, 'box', options)


def area_plot_input_argument_tests():
	options = {
		'fill': [True],
		'opacity': [1],
		'kind': ['area']
	}

	def area_test(self, **kwargs):
		self._iplot(self.df, **kwargs)

	_generate_tests(TestIPlot, area_test, 'area', options)


def scatter_plot_input_argument_tests():
	options = {
		'x': ['x'],
		'y': ['y'],
		'mode': ['markers'],
		'symbol': ['circle-dot'],
		'colors': [['orange', 'teal']],
		'size': [10]
	}

	def scatter_test(self, **kwargs):
		self._iplot(self.df, **kwargs)

	_generate_tests(TestIPlot, scatter_test, 'scatter', options)


def bubble_chart_argument_tests():
	options = {
		'x': ['x'], 'y': ['y'], 'size': ['c']
	}

	def bubble_test(self, **kwargs):
		self._iplot(self.df, **kwargs)

	_generate_tests(TestIPlot, bubble_test, 'bubble', options)


def subplot_input_argument_tests():
	options = {
		'shape': [(3, 1)],
		'shared_xaxes': [True],
		'vertical_spacing': [0.02],
		'fill': [True],
		'subplot_titles': [True],
		'legend': [False]
	}

	def subplot_test(self, **kwargs):
		self._iplot(self.df, subplots=True, **kwargs)

	_generate_tests(TestIPlot, subplot_test, 'subplots', options)


def shape_input_argument_tests():
	df = cf.datagen.lines(3, columns=['a', 'b', 'c'])
	options = {
		'hline': [
			[2, 4],
			[dict(y=-1, color='blue', width=3),
			 dict(y=1, color='pink', dash='dash')]],
		'vline': [['2015-02-10']],
		'hspan': [[(-1, 1), (2, 5)]],
		'vspan': [{
			'x0': '2015-02-15', 'x1': '2015-03-15',
			'color': 'teal', 'fill': True, 'opacity': .4}]
	}

	def shape_tests(self, **kwargs):
		self._iplot(df, **kwargs)

	_generate_tests(TestIPlot, shape_tests, 'shape', options)

# colors

def color_normalize_tests():
	c=dict([(k.lower(),v.upper()) for k,v in list(cf.cnames.items())])
	d={}
	for k,v in list(c.items()):
		assert_equals(v,cf.normalize(k).upper())
	return 2

# technical analysis

def ta_tests():
	df=cf.datagen.lines(1,500)
	studies=['sma']
	options = {
		'periods' : [14]
	}

	def ta_tests(self, studies, **kwargs):
		for study in studies:
			self._ta(df, study, **kwargs)

	_generate_tests(TestIPlot, ta_tests, 'ta', options)

def quant_figure_tests():
	df=cf.datagen.ohlc()
	qf=cf.QuantFig(df)
	qf.add_sma()
	qf.add_atr()
	qf.add_bollinger_bands()
	return qf.figure()

# test generators


def _generate_tests(test_class, test_func, test_name, options):
	from itertools import chain, combinations, product

	def powerset(iterable):
		"powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
		s = list(iterable)
		return chain.from_iterable(combinations(s, r)
								   for r in range(len(s) + 1))
	key_value_tuple = {}
	for option, values in list(options.items()):
		key_value_tuple[option] = [(option, i) for i in values]

	for option_groups in powerset(key_value_tuple.values()):
		for input_kwargs in product(*option_groups):
			kwargs = {i[0]: i[1] for i in input_kwargs}
			setattr(
				test_class,
				'test_{}_{}'.format(test_name, '__'.join([
					'_'.join([str(s) for s in i])
					for i in kwargs.items()])),
				_generate_test(test_func, **kwargs))


def _generate_test(test_func, **kwargs):
	def test(self):
		test_func(self, **kwargs)

	return test



bar_input_argument_tests()
bar_row_input_argument_tests()
histogram_input_argument_tests()
box_input_argument_tests()
heatmap_input_argument_tests()
area_plot_input_argument_tests()
scatter_plot_input_argument_tests()
bubble_chart_argument_tests()
subplot_input_argument_tests()
shape_input_argument_tests()
test_irregular_subplots()
color_normalize_tests()
quant_figure_tests()
# ta_tests()


if __name__ == '__main__':
	unittest.main()
