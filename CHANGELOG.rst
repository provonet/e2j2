Changelog
=========
0.6.0 (2020-08-11)

Add
---
- add marker sets there is support for the following marker sets

1. {%, %}, {{, }}, {#, #}
2. {%, %}, {=, =}, {#, #}
3. <%, %>, <=, =>, <#, #>
4. [%, %], [=, =], [#, #]
5. {%, %), (=, =), (#, #)

- start and end markers for the tag config block are now configurable (--config-start, --config-end)


0.5.2 (2020-07-30)
------------------

Fixed
-----
- merge config in tag with existing config

Add
---
- add escape tag, this tag can be used for escaping e2j2 tags in strings

Note
----
- command line flags with underscores are now deprecated and will be removed in later version

0.5.1 (2020-07-28)
-------------------
Known issues
------------
- potential conflicts with twopass rendering if strings start with text similar to e2j2 tags
- flatten option for dict values ignores existing config values

Fixed
-----
- only check for nested tags in strings

0.5.0 (2020-07-21)
-------------------
Added
-----
- Add support for rendering tags in json objects and lists in combination with twopass rendering:
    So now it is possible to render base64 encoded strings within a json tag within the same environment variable.

    example:

    with:

    export MY_NESTED_VAR='json:{"ip_regex": "base64:Xig/Oig/OjI1WzAtNV18MlswLTRdWzAtOV18WzAxXT9bMC05XVswLTldPylcLil7M30oPzoyNVswLTVdfDJbMC00XVswLTldfFswMV0/WzAtOV1bMC05XT8pJA=="}'

    the template

    {{ MY_NESTED_VAR }}

    will render to:

    {"ip_regex": "^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"}

- Add python 3.9 to the list of supported python versions

Breaking change:
----------------
python 2.7.x is no longer supported!
python 3.4.x is no longer supported!

0.4.10 (2020-01-14)
-------------------

Changed
-------
consul and vault tokens can now point to a file (use the file: tag to point to a file)

0.4.9 (2019-12-16)
------------------

Changed
-------
- follow symlinks when recursive flag is set

0.4.8 (2019-12-04)
------------------

Added
-----
- support jinja2 filters provided by the jinja2-ansible-filters library if installed

Fixed
-----
- fix handling consul keys containing newlines and double quote characters 
 
0.4.7 (2019-11-25)
------------------

Fixed
-----
- searchlist is required even if E2J2_SEARCHLIST is set

0.4.6 (2019-11-24)
------------------

Added
-----
- add flag to run command after initial template run
- add config option to json, jsonfile, consul, dns, and vault tag to flatten the returned json object

Changed
-------
- disable run on initial template run

0.4.5 (2019-11-19)
------------------

Changed
-------
- add test run to watch, only apply changes if test is successful

0.4.4 (2019-11-18)
------------------

Fixed
-----
- config var missing in get_var call
- fix message repeat filter in stdout function
- support ipv6 address in nameserver field of dns tag


0.4.3 (2019-11-15)
------------------

Added
-----
- add --splay flag, to configure delay of watchlist polls
- alias flags for no color, white/black list and jinja2 markers

Fixed
-----
- stacktrace on ctrl-c
- warning message in yellow with --no-color flag
- multiple script runs (one for each template), should be just one

0.4.2 (2019-11-14)
------------------

Fixed
-----
- fixed incompatibility issue with python 2.7 and watchlist option

0.4.1 (2019-11-13)
------------------

Fixed
-----
- set default value for filelist flag to empty list

0.4.0 (2019-11-12)
------------------

Added
-----
- add dns tag (currently includes support of record types A, AAAA, and SRV)
- config file support
- watch for changes on consul, vault and dns tags and render on change (Experimental)
- add run flag, this flag can be used to execute shell commands after rendering templates (Experimental)

Fixed
-----
- show only line numbers on a limited set up exceptions

0.3.0 (2019-10-25)
------------------

Changed
-------
- show line numbers on rendering errors
- envvar tag errors are now disabled as warnings as they are non fatal

Breaking change:
----------------
- envvar tag errors will result in undefined variables previously they contained an error message 

0.2.1 (2019-10-23)
------------------

Added
-----
- add --stacktrace flag to include a python stack trace in the error file (thanks: Sylvia van Os/TheLastProject)

Changed
- show jinja2 render error in console output (thanks: Marco Verleun)

Fixed
- Fix for pip install issues
- Pass exit code to calling shell 

0.2.0 (2019-07-23)
------------------

Added
-----
- vault secrets support
- per tag config (for the consul and vault tags)
- add support for token variables (for the consul and vault tags)

Changed
-------
- Add json schema validation for consul and vault config

0.1.21 (2019-07-09)
-------------------

Fixed
-----
- Fix issue with included templates in other directories

Added
-----
- Add option to "copy" file ownership and file permissions

0.1.20 (2019-06-12)
-------------------

Fixed
-----
- fix "only render one file" issue

0.1.19 (2019-06-10)
-------------------

Added
-----
- add option to whitelist / blacklist environment variables

Fixed
-----
- set proper exit codes (0=success / 1=failure)

Changed
-------
- add unittests
- add functional tests

0.1.18 (2019-05-17)
-------------------

Fixed
-----
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
