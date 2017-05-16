from setuptools import setup

setup(name='e2j2',
      version='0.1.0',
      description='e2j2 is a commandline utility to render text/configuration files from jinj2 templates',
      install_requires = ['jinja2>=2.9.0', 'click>=6.7', 'colorama>=0.3.7', 'python-consul==0.6.0'],
      url='http://github.com/provonet/e2j2',
      author='Johan Bakker',
      author_email='johan.bakker@gmail.com',
      license='MIT',
      packages=['e2j2'],
      scripts=['bin/e2j2'],
      zip_safe=True)
