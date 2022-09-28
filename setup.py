from setuptools import setup

setup(
   name='pyosh',
   version='0.1.0',
   author='Klaus G. Paul',
   author_email='20340525+KlausGPaul@users.noreply.github.com ',
   packages=['pyosh', 'pyosh.test'],
   scripts=[],
   url='http://pypi.python.org/pypi/pyosh/',
   license='LICENSE.txt',
   description='API scripts to access https://opensupplyhub.org Open Supply Hub\'s API',
   long_description=open('README.rst').read(),
   install_requires=[
       "requests",
       "pandas",
       "pytest",
   ],
)