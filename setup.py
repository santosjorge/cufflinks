from setuptools import setup
from os import path
import io

here = path.abspath(path.dirname(__file__))
with io.open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    requires = f.read().split()

setup(
    name='cufflinks',
    version='0.17.3',
    description='Productivity Tools for Plotly + Pandas',
    author='Jorge Santos',
    author_email='santos.jorge@gmail.com',
    license='MIT',
    keywords=['pandas', 'plotly', 'plotting'],
    url='https://github.com/santosjorge/cufflinks',
    packages=['cufflinks'],
    package_data={'cufflinks': ['../helper/*.json']},
    include_package_data=True,
    install_requires=requires,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    zip_safe=False
)
