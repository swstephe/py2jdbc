#!/usr/bin/env python
#  -*- coding: utf8 -*-
from __future__ import absolute_import
from __future__ import print_function

from setuptools import setup

setup(
    name='py2jdbc',
    version='0.0.4',
    license='BSD 2-Clause License',
    description="Python DBI interface to JDBC databases",
    long_description="""
``py2jdbc`` is an open source Python module that accesses JDBC-compliant databases.
It implements the DB API 2.0 specification.

- Documentation: http://py2jdbc.readthedocs.org/
- Source: https://github.com/swstephe/py2jdbc
- Download: https://pypi.python.org/pypi/py2jdbc
    """,
    author='Scott Stephens',
    author_email='scott@ariftek.com',
    url='https://github.com/swstephe/py2jdbc',
    packages=['py2jdbc'],
    package_dir={'': '.'},
    py_modules=['py2jdbc'],
    include_package_data=True,
    zip_safe=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Database',
    ],
    keywords='Database, JDBC, JNI, PyPy'
)
