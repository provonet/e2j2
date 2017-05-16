#!/bin/bash
VERSION='0.1.0'
pandoc --from=markdown --to=rst --output=README.rst README.md
pandoc --from=markdown --to=rst --output=CHANGELOG.rst CHANGELOG.md
python setup.py sdist bdist_wheel
twine register dist/e2j2-${VERSION}.tar.gz
twine upload dist/e2j2-${VERSION}.tar.gz
twine upload dist/e2j2-${VERSION}-py3-none-any.whl

