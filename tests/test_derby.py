# -*- coding: utf8 -*-
import datetime
import os
import logging

import six
import py2jdbc
from py2jdbc.jni import jfloat
import pytest
from tests.config import HAS_DERBY, MAX_INT

if not HAS_DERBY:
    if pytest.__version__ < '3.0.0':
        pytest.skip()
    else:
        pytestmark = pytest.mark.skip


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
cx = None
cu = None


def setup():
    global cx, cu
    cx = py2jdbc.connect('jdbc:derby:py2jdbc_derby;create=true')
    cu = cx.cursor()
    tables = cx.tables(tables='TESTS')
    if tables:
        cu.execute("drop table tests")
    cu.execute("""
    create table tests(
        id integer primary key,
        name varchar(20) not null,
        bigint_field bigint,
        blob_field blob,
        boolean_field boolean,
        char_field char(10),
        clob_field clob,
        date_field date,
        decimal_field decimal(10, 5),
        double_field double,
        float_field float(5),
        integer_field integer,
        long_varchar_field long varchar,
        numeric_field numeric(10, 5),
        real_field real,
        smallint_field smallint,
        time_field time,
        timestamp_field timestamp,
        varchar_field varchar(50)
    )""")
    cu.execute("insert into tests(id, name) values (?, ?)", (1, 'setup'))


def teardown():
    global cx, cu
    cu.close()
    cx.close()


# noinspection PyShadowingBuiltins
def _test_field(id, typ, value, *desc):
    name, field = (s.format(typ) for s in ('test_{}', '{}_field'))
    cu.execute("delete from tests where id = ?", (id,))
    cu.execute(
        "insert into tests (id, name, {}) values (?, ?, ?)".format(field),
        (id, name, value)
    )
    cu.execute("select id, name, {} from tests where id = ?".format(field), (id,))
    assert cu.description == (
        ('ID', py2jdbc.INTEGER, 11, None, 10, 0, False),
        ('NAME', py2jdbc.VARCHAR, 20, None, 20, 0, False),
        (field.upper(), desc[0], desc[1], None, desc[2], desc[3], True),
    )
    row = cu.fetchall()
    if six.PY2 and hasattr(value, '__getitem__') and isinstance(value[0], int):
        value = ''.join(map(chr, value))
    assert row == ((id, name, value),)


def test_bigint():
    _test_field(2, 'bigint', 12345678012345, py2jdbc.BIGINT, 20, 19, 0)


def test_blob():
    value = os.urandom(1024)
    if six.PY2:
        value = map(ord, value)
    _test_field(3, 'blob', value, py2jdbc.BLOB, MAX_INT, MAX_INT, 0)


def test_boolean():
    _test_field(4, 'boolean', True, py2jdbc.BOOLEAN, 5, 1, 0)


def test_char():
    _test_field(5, 'char', 'char field', py2jdbc.CHAR, 10, 10, 0)


CLOB = """\
A moment of happiness,
you and I sitting on the verandah,
apparently two, but one in soul, you and I.

We feel the flowing water of life here,
you and I, with the garden's beauty
and the birds singing.

The stars will be watching us,
and we will show them
what it is to be a thin crescent moon.
You and I unselfed, will be together,
indifferent to idle speculation, you and I.

The parrots of heaven will be cracking sugar
as we laugh together, you and I.

In one form upon this earth,
and in another form in a timeless sweet land.
"""


def test_clob():
    _test_field(6, 'clob', CLOB, py2jdbc.CLOB, MAX_INT, MAX_INT, 0)


def test_date():
    _test_field(7, 'date', datetime.date(2014, 7, 14), py2jdbc.DATE, 10, 10, 0)


def test_decimal():
    _test_field(8, 'decimal', 12345.67871, py2jdbc.DECIMAL, 12, 10, 5)


def test_double():
    _test_field(9, 'double', 12345.67871, py2jdbc.DOUBLE, 24, 15, 0)


def test_float():
    _test_field(10, 'float', 12345, py2jdbc.REAL, 15, 7, 0)


def test_integer():
    _test_field(11, 'integer', -567890, py2jdbc.INTEGER, 11, 10, 0)


def test_long_varchar():
    _test_field(12, 'long_varchar', CLOB, py2jdbc.LONGVARCHAR, 32700, 32700, 0)


def test_numeric():
    _test_field(13, 'numeric', 564.342, py2jdbc.NUMERIC, 12, 10, 5)


def test_real():
    _test_field(14, 'real', jfloat(789.2012).value, py2jdbc.REAL, 15, 7, 0)


def test_smallint():
    _test_field(15, 'smallint', 9831, py2jdbc.SMALLINT, 6, 5, 0)


def test_time():
    _test_field(16, 'time', datetime.time(7, 8, 9), py2jdbc.TIME, 8, 8, 0)


def test_timestamp():
    _now = datetime.datetime.now().replace(microsecond=0)
    _test_field(17, 'timestamp', _now, py2jdbc.TIMESTAMP, 29, 29, 9)


def test_varchar():
    _test_field(18, 'varchar', 'this is a varchar', py2jdbc.VARCHAR, 50, 50, 0)


def test_execute_no_args():
    global cu
    cu.execute("delete from tests")


def test_execute_illegal_sql():
    global cu
    with pytest.raises(py2jdbc.OperationalError):
        cu.execute("select asdf")


def test_execute_too_much_sql2():
    global cu
    cu.execute("select 5+4 from SYSIBM.SYSDUMMY1 -- foo bar")


def test_execute_too_much_sql3():
    global cu
    cu.execute("""
    select 5 + 4
    from SYSIBM.SYSDUMMY1

    /*
    foo
    */
    """)


def test_execute_wrong_sql_arg():
    global cu
    with pytest.raises(ValueError):
        cu.execute(42)


def test_execute_arg_string_with_zero_byte():
    global cu
    _id = 19
    cu.execute("insert into tests(id, name, varchar_field) values (?, ?, ?)",
               (_id, 'with_zero_byte', six.u("Hu\u0000go")))
    cu.execute("select varchar_field from tests where id = ?", (_id, ))
    row = cu.fetchone()
    assert row[0] == six.u("Hu\u0000go")


def test_execute_wrong_no_of_args1():
    global cu
    with pytest.raises(py2jdbc.ProgrammingError):
        cu.execute("insert into tests(id, name) values (?, ?)",
                   (20, 'wrong_no_of_args1', "Egon"))


def test_execute_wrong_no_of_args2():
    global cu
    with pytest.raises(py2jdbc.OperationalError):
        cu.execute("insert into tests(id) values (?)")


def test_execute_param_list():
    global cu
    cu.execute("insert into tests(id, name) values (21, 'param_list')")
    cu.execute("select name from tests where name=?", ['param_list'])
    row = cu.fetchone()
    assert row[0] == 'param_list'


def test_execute_param_sequence():
    class L(object):
        def __len__(self):
            return 1

        def __getitem__(self, x):
            assert x == 0
            return 'param_sequence'

    cu.execute("insert into tests(id, name) values (22, 'param_sequence')")
    cu.execute("select name from tests where name=?", L())
    row = cu.fetchone()
    assert row[0] == 'param_sequence'


def test_close():
    c = cx.cursor()
    c.close()
    c.close()


def test_rowcount_execute():
    cu.execute("delete from tests")
    cu.execute("insert into tests(id, name) values (1, 'rowcount_execute')")
    cu.execute("insert into tests(id, name) values (2, 'rowcount_execute')")
    cu.execute("update tests set name='foo'")
    assert cu.rowcount == 2


def test_rowcount_executemany():
    cu.execute("delete from tests")
    cu.executemany("insert into tests(id, name) values (?, ?)", [
        (1, 'rowcount_executemany'),
        (2, 'rowcount_executemany'),
        (3, 'rowcount_executemany')
    ])
    assert cu.rowcount == 3


def test_rowcount_executemany2():
    global cx
    with cx.cursor() as c:
        c.execute("delete from tests")
        c.executemany("insert into tests(id, name) values (?, ?)", [
            (1, 'rc_executemany2'),
            (2, 'rc_executemany2'),
            (3, 'rc_executemany2'),
            (4, 'rc_executemany2')
        ])
        assert c.rowcount == 4


def test_executemany_sequence():
    cu.execute("delete from tests")
    cu.executemany("insert into tests(id, name, float_field) values (?, ?, ?)", [
        (i + 1, 'executemany_sequence', 3.14 * i)
        for i in range(10)
    ])
    assert cu.rowcount == 10


def test_executemany_generator():
    def mygen():
        for i in range(5):
            yield (i + 1, 'executemany_gen')

    cu.execute("delete from tests")
    cu.executemany("insert into tests(id, name) values (?, ?)", mygen())
    assert cu.rowcount == 5
    cu.execute("select count(*) from tests")
    row = cu.fetchone()
    assert row[0] == 5


def test_executemany_wrong_sql_arg():
    with pytest.raises(ValueError):
        cu.executemany(42, [(3,)])


def test_executemany_not_iterable():
    with pytest.raises(TypeError):
        cu.executemany("insert into tests(id, name, float_field) values (?, ?, ?)",
                       11, 'not_iterable', 42)


def test_fetch_iter():
    global cu
    cu.execute("delete from tests")
    cu.execute("insert into tests(id, name) values (?, ?)", (12, 'test_fetch_iter'))
    cu.execute("insert into tests(id, name) values (?, ?)", (13, 'test_fetch_iter'))
    cu.execute("select id from tests order by id")
    lst = [row[0] for row in cu]
    assert lst[0] == 12
    assert lst[1] == 13


def test_fetch_one():
    global cu
    cu.execute("delete from tests")
    cu.execute("insert into tests(id, name, varchar_field) values (?, ?, ?)",
               (14, 'test_fetch_one', 'foo'))
    cu.execute("select name from tests")
    row = cu.fetchone()
    assert row[0] == 'test_fetch_one'
    row = cu.fetchone()
    assert row is None


def test_fetch_one_no_statement():
    global cx
    c = cx.cursor()
    assert c.fetchone() is None


def test_array_size():
    global cu
    cu.arraysize = 2
    cu.execute("delete from tests")
    cu.execute("insert into tests(id, name, varchar_field)"
               " values (15, 'test_array_size', 'A')")
    cu.execute("insert into tests(id, name, varchar_field)"
               " values (16, 'test_array_size', 'B')")
    cu.execute("insert into tests(id, name, varchar_field)"
               " values (17, 'test_array_size', 'C')")
    cu.execute("select varchar_field from tests")
    res = cu.fetchmany()
    assert len(res) == 2
    res = cu.fetchmany()
    assert len(res) == 1


def test_fetchmany():
    global cu
    cu.execute("delete from tests")
    cu.execute("insert into tests(id, name, varchar_field)"
               " values (18, 'test_fetchmany', 'foo')")
    cu.execute("select varchar_field from tests")
    res = cu.fetchmany(100)
    assert len(res) == 1
    res = cu.fetchmany(100)
    assert len(res) == 0


def test_fetchmany_kwargs():
    cu.execute("select name from tests")
    res = cu.fetchmany(size=100)
    assert len(res) == 1


def test_description():
    global cu
    cu.execute("select * from tests")
    assert cu.description == (
        ('ID', py2jdbc.INTEGER, 11, None, 10, 0, False),
        ('NAME', py2jdbc.VARCHAR, 20, None, 20, 0, False),
        ('BIGINT_FIELD', py2jdbc.BIGINT, 20, None, 19, 0, True),
        ('BLOB_FIELD', py2jdbc.BLOB, MAX_INT, None, MAX_INT, 0, True),
        ('BOOLEAN_FIELD', py2jdbc.BOOLEAN, 5, None, 1, 0, True),
        ('CHAR_FIELD', py2jdbc.CHAR, 10, None, 10, 0, True),
        ('CLOB_FIELD', py2jdbc.CLOB, MAX_INT, None, MAX_INT, 0, True),
        ('DATE_FIELD', py2jdbc.DATE, 10, None, 10, 0, True),
        ('DECIMAL_FIELD', py2jdbc.DECIMAL, 12, None, 10, 5, True),
        ('DOUBLE_FIELD', py2jdbc.DOUBLE, 24, None, 15, 0, True),
        ('FLOAT_FIELD', py2jdbc.REAL, 15, None, 7, 0, True),
        ('INTEGER_FIELD', py2jdbc.INTEGER, 11, None, 10, 0, True),
        ('LONG_VARCHAR_FIELD', py2jdbc.LONGVARCHAR, 32700, None, 32700, 0, True),
        ('NUMERIC_FIELD', py2jdbc.NUMERIC, 12, None, 10, 5, True),
        ('REAL_FIELD', py2jdbc.REAL, 15, None, 7, 0, True),
        ('SMALLINT_FIELD', py2jdbc.SMALLINT, 6, None, 5, 0, True),
        ('TIME_FIELD', py2jdbc.TIME, 8, None, 8, 0, True),
        ('TIMESTAMP_FIELD', py2jdbc.TIMESTAMP, 29, None, 29, 9, True),
        ('VARCHAR_FIELD', py2jdbc.VARCHAR, 50, None, 50, 0, True),
    )


def test_fetchall():
    cu.execute("select name from tests")
    res = cu.fetchall()
    assert len(res) == 1
    res = cu.fetchall()
    assert res == tuple()


def test_cursor_connection():
    global cx, cu
    assert cu.connection == cx
