py2jdbc
=======

``py2jdbc`` is a Python module that accesses JDBC-compliant databases.
It implements the `Python Database API Specification 2.0`_
specification.

- Documentation: http://py2jdbc.readthedocs.org/
- Source: https://github.com/swstephe/py2jdbc
- Download: https://pypi.python.org/pypi/py2jdbc

.. image:: https://travis-ci.org/swstephe/py2jdbc.svg?branch=master
    :target: https://travis-ci.org/swstephe/py2jdbc
    :alt: continuous integration build status

.. image:: https://readthedocs.org/projects/py2jdbc/badge/
    :target: https://py2jdbc.readthedocs.org/
    :alt: documentation

.. image:: https://img.shields.io/pypi/v/py2jdbc.svg
    :target: https://pypy.org/projects/py2jdbc


Installation
------------

::

    pip install py2jdbc


This module currently uses `ctypes`_ for ffi access to the JNI API.
Other branches will consider switching to Cython/Pyrex or writing pure C++ extensions.


Quick Start
-----------

::

    conn = py2jdbc.onnect('jdbc:sqlite::memory:')
    c = conn.cursor()
    c.execute("""
        create table tests(
            id integer primary key,
            name text not null
        )
    """)
    c.execute("insert into tests(id, name) values (?, ?)", (1, 'Hello World'))
    for row in c.execute("select * from test"):
        print(row)
    c.close()
    conn.close()


Or even::

    with py2jdbc.connect('jdbc:sqlite::memory:') as conn:
        with conn.cursor() as c:
            c.execute("""
                create table tests(
                    id integer primary key,
                    name text not null
                )
            """)
            c.execute("insert into tests(id, name) values (?, ?)", (1, 'Hello World'))
            for row in c.execute("select * from test"):
                print(row)


Connect
~~~~~~~

Connect to your database with ``py2jdbc.connect`` by passing your JDBC URL.  By
default, your Java classpath will be loaded from any CLASSPATH environment
variable, and any jar in a lib directory under your current working directory.
You can also pass the CLASSPATH in the connection call::

    py2jdbc.connect('jdbc:sqlite::memory:', classpath=['path1', 'path2'])

This returns the ``Connection`` object.

Execute
~~~~~~~

Bind variables use question marks, like JDBC, and can bind to sequences or generators::

    # insert a row
    c.execute("insert into tests(id, name) values (?, ?)", (1, "Hello World"))

    # insert 10 rows
    c.executemany("insert into tests(id, name) values (?, ?)",
        (i + 1, 'testing')
        for i in range(10)
    )

Select
~~~~~~

Selecting from a database will automatically describe the result set and try to
convert values to standard Python types::

    c.execute("select * from test")
    for row in c:
        print(row)  # -> [1, 'Hello World']


.. _Python Database API Specification 2.0: https://www.python.org/dev/peps/pep-0249/
.. _ctypes: https://docs.python.org/3/library/ctypes.html