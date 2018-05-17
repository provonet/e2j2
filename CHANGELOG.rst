Changelog
=========

0.1.6 (2018-05-17)
------------------

Changed
~~~~~~~

-  Improved error messages
-  Handle json decode errors

.. _section-1:

0.1.5 (2018-05-11)
------------------

Added
~~~~~

-  add no-color option

.. _section-2:

0.1.4 (2017-08-21)
------------------

.. _added-1:

Added
~~~~~

-  add version option
-  add file list option

Fixed
~~~~~

-  Fix bug with empty consul key values

.. _section-3:

0.1.3 (2017-07-11)
------------------

Breaking change
~~~~~~~~~~~~~~~

-  the consul tags will now use default jinja2 objects, this breaks the
   previous behaviour of separation by underscores

.. _changed-1:

Changed
~~~~~~~

-  remove dependency click, use argparse instead.

.. _fixed-1:

Fixed
~~~~~

-  make sure that bytes are casted to strings (for base64 and consul
   tags)

.. _section-4:

0.1.2 (2017-05-17)
------------------

.. _fixed-2:

Fixed
~~~~~

-  additional fix for install issue on python2 (added MANIFEST.in)

.. _section-5:

0.1.1 (2017-05-17)
------------------

.. _fixed-3:

Fixed
~~~~~

-  add README.rst and CHANGELOG.rst as package_data this fixes install
   issue with python 2.x

Removed
~~~~~~~

-  remove dependency colorama

.. _changed-2:

Changed
~~~~~~~

-  move methods to separate helper files

.. _section-6:

0.1.0 (2017-05-16)
------------------

.. _added-2:

Added
~~~~~

-  add short options for extention (-e) searchlist (-s) and noop (-N)
-  add (MIT) license

.. _changed-3:

Changed
~~~~~~~

-  e2j2 is now packaged as pip package
-  split script and module, script will be installed in /usr/bin or
   /usr/local/bin

.. _section-7:

0.0.2 (2017-05-16)
------------------

.. _added-3:

Added
~~~~~

-  Add recurse flag

.. _changed-4:

Changed
~~~~~~~

-  Searchlist is no longer a required option e2j2 will use the current
   directory as default
-  Recursion is no longer on by default
-  Improve error handling, e2j2 will now report failures and render
   \*.err files which will make debugging errors much easier

.. _section-8:

0.0.1 (2017-05-01)
------------------

Initial release
