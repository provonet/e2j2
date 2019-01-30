Changelog
=========

0.1.11
------

Changed
-------

-  Changed behavior of nested keys with the consul tag.

example: in consul we have an key key1/key2/123 envvar
KEY=consul:key1/key2 => {{ KEY }} will now render to 123 and no longer
to {“key2”: 123}

.. _section-1:

0.1.10 (2018-09-24)
-------------------

Added
~~~~~

-  add file tag, this tag will place the content of the file into the
   variable

.. _section-2:

0.1.9 (2018-09-21)
------------------

Fixed
~~~~~

-  fix import issue on python 2.7

.. _section-3:

0.1.8 (2018-09-21)
------------------

.. _added-1:

Added
~~~~~

-  handle hashrocket characters in json tag (as produced by hiera)

.. _section-4:

0.1.7 (2018-09-20)
------------------

.. _added-2:

Added
~~~~~

-  Add list tag which will parse a comma separated list

.. _section-5:

0.1.6 (2018-05-17)
------------------

.. _changed-1:

Changed
~~~~~~~

-  Improved error messages
-  Handle json decode errors

.. _section-6:

0.1.5 (2018-05-11)
------------------

.. _added-3:

Added
~~~~~

-  add no-color option

.. _section-7:

0.1.4 (2017-08-21)
------------------

.. _added-4:

Added
~~~~~

-  add version option
-  add file list option

.. _fixed-1:

Fixed
~~~~~

-  Fix bug with empty consul key values

.. _section-8:

0.1.3 (2017-07-11)
------------------

Breaking change
~~~~~~~~~~~~~~~

-  the consul tags will now use default jinja2 objects, this breaks the
   previous behaviour of separation by underscores

.. _changed-2:

Changed
~~~~~~~

-  remove dependency click, use argparse instead.

.. _fixed-2:

Fixed
~~~~~

-  make sure that bytes are casted to strings (for base64 and consul
   tags)

.. _section-9:

0.1.2 (2017-05-17)
------------------

.. _fixed-3:

Fixed
~~~~~

-  additional fix for install issue on python2 (added MANIFEST.in)

.. _section-10:

0.1.1 (2017-05-17)
------------------

.. _fixed-4:

Fixed
~~~~~

-  add README.rst and CHANGELOG.rst as package_data this fixes install
   issue with python 2.x

Removed
~~~~~~~

-  remove dependency colorama

.. _changed-3:

Changed
~~~~~~~

-  move methods to separate helper files

.. _section-11:

0.1.0 (2017-05-16)
------------------

.. _added-5:

Added
~~~~~

-  add short options for extention (-e) searchlist (-s) and noop (-N)
-  add (MIT) license

.. _changed-4:

Changed
~~~~~~~

-  e2j2 is now packaged as pip package
-  split script and module, script will be installed in /usr/bin or
   /usr/local/bin

.. _section-12:

0.0.2 (2017-05-16)
------------------

.. _added-6:

Added
~~~~~

-  Add recurse flag

.. _changed-5:

Changed
~~~~~~~

-  Searchlist is no longer a required option e2j2 will use the current
   directory as default
-  Recursion is no longer on by default
-  Improve error handling, e2j2 will now report failures and render
   \*.err files which will make debugging errors much easier

.. _section-13:

0.0.1 (2017-05-01)
------------------

Initial release
