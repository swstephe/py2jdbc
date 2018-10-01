py2jdbc
=======

``py2jdbc`` is an open source Python module that accesses JDBC-compliant databases.
It implements the [DB API 2.0](https://www.python.orgfdev/peps/pep-0249)
specification.

- Documentation: http://py2jdbc.readthedocs.org/
- Source: https://github.com/swstephe/py2jdbc
- Download: https://pypi.python.org/pypi/py2jdbc

[![Build Status])(https://travis-ci.org/swstephe/py2jdbc.svg?branch=master)](https://travis-ci.org/swstephe/py2jdbc)
[![PyPI](https://img.shields.io/pypi/v/py2jdbc.svg)]()


Installation
------------

    pip install six
    pip install py2jdbc


This module currently uses [ctypes](https://docs.python.org/3/library/ctypes.html)
for ffi access to the JNI API.  Other branches will consider switching to Cython/Pyrex
or writing pure C++ extensions.
