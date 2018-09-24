Introduction
============

.. _intro_installation:

Installation
------------

This package is available from the `Python Package Index
<http://pypi.python.org/pypi/py2jdbc>`_.  If you have `pip
<https://pip.pypa.io/>`_ you should be able to do::

    $ pip install petl

You can also download maually, extract and run ``python setup.py
install``.

to verify installation, the test suite can be run with `pytest
<https://pytest.org/>`_, e.g.::

    $ pip install pytest
    $ pytest

:mod:`py2jdbc` has been tested with Python version 2.7 and 3.7
under Linux and Windows operating systems.

.. _intro_dependencies:

Dependencies and extensions
---------------------------

This package is written in pure Python.  The only requirement is the `six
<https://pypi.org/project/six/>`_ module, for Python 2 and 3 compatibility.

.. _intro_design_goals:

Design goals
------------

This package is designed to conform to DBI 2.0, with an eye toward working
well with database ORM's, like SQLAlchemy.
