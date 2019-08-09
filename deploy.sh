#!/usr/bin/env bash
version=`python -c 'import py2jdbc;print(py2jdbc.version)'`
twine upload dist/py2jdbc-${version}.tar.gz
