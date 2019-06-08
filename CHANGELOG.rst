Changelog
=========

0.1.18 (2019-05-17)
-------------------

-  Fix bug in consul parser

.. _section-1:

0.1.17 (2019-05-17)
-------------------

Fixed
-----

-  Fix bug with include statements in jinja2 template

.. _section-2:

0.1.16 (2019-05-16)
-------------------

.. _fixed-1:

Fixed
-----

-  Fix bug with default jinja marker

.. _section-3:

0.1.15 (2019-05-16)
-------------------

Changed
-------

-  add options to overwrite the default jinja2 markers (block start/end,
   variable start/end and comment start/end)

Breaking change
~~~~~~~~~~~~~~~

-  removed “hack” for twopass rendering, you can use the new marker for
   handling conflicting characters in your template

.. _section-4:

0.1.14 (2019-04-30)
-------------------

.. _fixed-2:

Fixed
~~~~~

-  preserve newlines at end of file
-  CVE-2019-10906, module now requires jinja2>=2.10.1

.. _section-5:

0.1.13 (2019-03-29)
-------------------

.. _fixed-3:

Fixed
~~~~~

-  Fix for ignored raw tag with two-pass rendering

.. _section-6:

0.1.12 (2019-03-14)
-------------------

Added
~~~~~

-  add support for two pass rendering

.. _section-7:

0.1.11 (2019-01-30)
-------------------

.. _changed-1:

Changed
~~~~~~~

-  Changed behavior of nested keys with the consul tag.

example: in consul we have an key key1/key2/123 envvar
KEY=consul:key1/key2 => {{ KEY }} will now render to 123 and no longer
to {“key2”: 123}

.. _section-8:

0.1.10 (2018-09-24)
-------------------

.. _added-1:

Added
~~~~~

-  add file tag, this tag will place the content of the file into the
   variable

.. _section-9:

0.1.9 (2018-09-21)
------------------

.. _fixed-4:

Fixed
~~~~~

-  fix import issue on python 2.7

.. _section-10:

0.1.8 (2018-09-21)
------------------

.. _changed-2:

Changed
~~~~~~~

-  handle hashrocket characters in json tag (as produced by hiera)

.. _section-11:

0.1.7 (2018-09-20)
------------------

.. _added-2:

Added
~~~~~

-  Add list tag which will parse a comma separated list

.. _section-12:

0.1.6 (2018-05-17)
------------------

.. _changed-3:

Changed
~~~~~~~

-  Improved error messages
-  Handle json decode errors

.. _section-13:

0.1.5 (2018-05-11)
------------------

.. _added-3:

Added
~~~~~

-  add no-color option

.. _section-14:

0.1.4 (2017-08-21)
------------------

.. _added-4:

Added
~~~~~

-  add version option
-  add file list option

.. _fixed-5:

Fixed
~~~~~

-  Fix bug with empty consul key values

.. _section-15:

0.1.3 (2017-07-11)
------------------

.. _breaking-change-1:

Breaking change
~~~~~~~~~~~~~~~

-  the consul tags will now use default jinja2 objects, this breaks the
   previous behaviour of separation by underscores

.. _changed-4:

Changed
~~~~~~~

-  remove dependency click, use argparse instead.

.. _fixed-6:

Fixed
~~~~~

-  make sure that bytes are casted to strings (for base64 and consul
   tags)

.. _section-16:

0.1.2 (2017-05-17)
------------------

.. _fixed-7:

Fixed
~~~~~

-  additional fix for install issue on python2 (added MANIFEST.in)

.. _section-17:

0.1.1 (2017-05-17)
------------------

.. _fixed-8:

Fixed
~~~~~

-  add README.rst and CHANGELOG.rst as package_data this fixes install
   issue with python 2.x

Removed
~~~~~~~

-  remove dependency colorama

.. _changed-5:

Changed
~~~~~~~

-  move methods to separate helper files

.. _section-18:

0.1.0 (2017-05-16)
------------------

.. _added-5:

Added
~~~~~

-  add short options for extention (-e) searchlist (-s) and noop (-N)
-  add (MIT) license

.. _changed-6:

Changed
~~~~~~~

-  e2j2 is now packaged as pip package
-  split script and module, script will be installed in /usr/bin or
   /usr/local/bin

.. _section-19:

0.0.2 (2017-05-16)
------------------

.. _added-6:

Added
~~~~~

-  Add recurse flag

.. _changed-7:

Changed
~~~~~~~

-  Searchlist is no longer a required option e2j2 will use the current
   directory as default
-  Recursion is no longer on by default
-  Improve error handling, e2j2 will now report failures and render
   \*.err files which will make debugging errors much easier

.. _section-20:

0.0.1 (2017-05-01)
------------------

Initial release
