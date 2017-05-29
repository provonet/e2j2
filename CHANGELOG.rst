Changelog
=========

0.1.3 unreleased (2017-05-29)
-----------------------------

Changed
~~~~~~~

-  remove dependency click, use argparse instead.

0.1.2 (2017-05-17)
------------------

Fixed
~~~~~

-  additional fix for install issue on python2 (added MANIFEST.in)

0.1.1 (2017-05-17)
------------------

Fixed
~~~~~

-  add README.rst and CHANGELOG.rst as package\_data this fixes install
   issue with python 2.x

Removed
~~~~~~~

-  remove dependency colorama

Changed
~~~~~~~

-  move methods to separate helper files

0.1.0 (2017-05-16)
------------------

Added
~~~~~

-  add short options for extention (-e) searchlist (-s) and noop (-N)
-  add (MIT) license

Changed
~~~~~~~

-  e2j2 is now packaged as pip package
-  split script and module, script will be installed in /usr/bin or
   /usr/local/bin

0.0.2 (2017-05-16)
------------------

Added
~~~~~

-  Add recurse flag

Changed
~~~~~~~

-  Searchlist is no longer a required option e2j2 will use the current
   directory as default
-  Recursion is no longer on by default
-  Improve error handling, e2j2 will now report failures and render
   \*.err files which will make debugging errors much easier

0.0.1 (2017-05-01)
------------------

Initial release