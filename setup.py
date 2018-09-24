from setuptools import setup

description = 'e2j2 is a commandline utility to render text/configuration files from jinja2 templates'

setup(name='e2j2',
      version='0.1.10',
      description=description,
      long_description=open('README.rst').read() + '\n\n' + open('CHANGELOG.rst').read(),
      install_requires=['jinja2>=2.9.0', 'python-consul>=0.6.0', 'deepmerge>=0.0.4'],
      url='http://github.com/provonet/e2j2',
      author='Johan Bakker',
      author_email='johan.bakker@gmail.com',
      license='MIT',
      package_data={'': ['LICENSE', 'README.rst', 'CHANGELOG.rst']},
      packages=['e2j2', 'e2j2.helpers'],
      scripts=['bin/e2j2'],
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: System :: Systems Administration',
        'Topic :: Software Development :: Libraries'
        ],
      zip_safe=True)
