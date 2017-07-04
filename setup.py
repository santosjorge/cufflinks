from setuptools import setup

setup(name='cufflinks',
      version='0.12.0',
      description='Productivity Tools for Plotly + Pandas',
      author='Jorge Santos',
      author_email='santos.jorge@gmail.com',
      license='MIT',
      keywords = ['pandas', 'plotly', 'plotting'],
      url = 'https://github.com/santosjorge/cufflinks',
      packages=['cufflinks'],
      install_requires = ['pandas','plotly>=2.0.0','colorlover>=0.2','TA-Lib==0.4.10'],
	  zip_safe=False)
