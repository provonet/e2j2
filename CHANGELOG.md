# Changelog

## 0.1.9 (2018-09-21)
### Fixed
- fix import issue on python 2.7

## 0.1.8 (2018-09-21)
### Added
- handle hashrocket characters in json tag (as produced by hiera)

## 0.1.7 (2018-09-20)
### Added
- Add list tag which will parse a comma separated list 

## 0.1.6 (2018-05-17)
### Changed
- Improved error messages
- Handle json decode errors

## 0.1.5 (2018-05-11)
### Added
- add no-color option

## 0.1.4 (2017-08-21)

### Added
- add version option
- add file list option

### Fixed
- Fix bug with empty consul key values

## 0.1.3 (2017-07-11)

### Breaking change
- the consul tags will now use default jinja2 objects, this breaks the previous behaviour of separation by underscores

### Changed
- remove dependency click, use argparse instead.

### Fixed
- make sure that bytes are casted to strings (for base64 and consul tags)

## 0.1.2 (2017-05-17)

### Fixed
- additional fix for install issue on python2 (added MANIFEST.in)

## 0.1.1 (2017-05-17)

### Fixed
- add README.rst and CHANGELOG.rst as package_data this fixes install issue with python 2.x

### Removed
- remove dependency colorama

### Changed
- move methods to separate helper files

## 0.1.0 (2017-05-16)

### Added
- add short options for extention (-e) searchlist (-s) and noop (-N)
- add (MIT) license

### Changed
- e2j2 is now packaged as pip package
- split script and module, script will be installed in /usr/bin or /usr/local/bin

## 0.0.2 (2017-05-16)

### Added
- Add recurse flag

### Changed
- Searchlist is no longer a required option e2j2 will use the current directory as default
- Recursion is no longer on by default
- Improve error handling, e2j2 will now report failures and render *.err files which will make debugging errors much easier

## 0.0.1 (2017-05-01)

Initial release
