# py2jdbc

py2jdbc is an open source Python module that accesses JDBC-compliant databases.
It implements the [DB API 2.0](https://www.python.orgfdev/peps/pep-0249)
specification.

The easiest way to install is to use pip:

    pip install py2jdbc

This module currently uses [ctypes](https://docs.python.org/3/library/ctypes.html)
for ffi access to the JNI API.  Other branches will consider switching to Cython/Pyrex
or writing pure C++ extensions.
