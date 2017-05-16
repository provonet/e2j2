from setuptools import setup

description = 'e2j2 is a commandline utility to render text/configuration files from jinja2 templates'

setup(name='e2j2',
      version='0.1.1',
      description=description,
      long_description=open('README.rst').read() + '\n\n' + open('CHANGELOG.rst').read(),
      install_requires = ['jinja2>=2.9.0', 'click>=6.7', 'python-consul==0.6.0'],
      url='http://github.com/provonet/e2j2',
      author='Johan Bakker',
      author_email='johan.bakker@gmail.com',
      license='MIT',
      packages=['e2j2', 'e2j2.helpers'],
      scripts=['bin/e2j2'],
      zip_safe=True)
