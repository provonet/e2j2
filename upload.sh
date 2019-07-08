#!/bin/bash
VERSION='0.1.21'
python setup.py sdist bdist_wheel
gpg --detach-sign -a dist/e2j2-${VERSION}.tar.gz
twine upload dist/e2j2-${VERSION}.tar.gz dist/e2j2-${VERSION}-py3-none-any.whl dist/e2j2-${VERSION}.tar.gz.asc
