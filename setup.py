from setuptools import setup

description = 'e2j2 is a commandline utility to render text/configuration files from jinja2 templates' +\
              'from shell environment variables'

setup(name='e2j2',
      version='0.4.10',
      description=description,
      long_description=open('README.rst').read() + '\n\n' + open('CHANGELOG.rst').read(),
      install_requires=[
          'jinja2>=2.10.1',
          'python-consul>=0.6.0',
          'deepmerge>=0.0.4',
          'dnspython',
          'six',
          'jsonschema',
          'rfc3987',
          'munch'
      ],
      tests_require=['mock', 'unittest2', 'requests-mock', 'callee'],
      url='http://github.com/provonet/e2j2',
      author='Johan Bakker',
      author_email='johan.bakker@gmail.com',
      license='MIT',
      package_data={'': ['LICENSE', 'README.rst', 'CHANGELOG.rst']},
      packages=['e2j2', 'e2j2.helpers', 'e2j2.tags'],
      scripts=['bin/e2j2'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: System :: Systems Administration',
        'Topic :: Software Development :: Libraries'
        ],
      test_suite="tests",
      zip_safe=True)
