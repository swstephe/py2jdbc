# -*- coding: utf8 -*-
import datetime
import os
from getpass import getuser
import logging

import six
import py2jdbc
import pytest
from tests.config import (
    MAX_INT,
    LIB
)

JAR_FILE = os.path.join(LIB, 'mysql-connector-java-8.0.12.jar')
if not os.path.exists(JAR_FILE):
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
    cx = py2jdbc.connect('jdbc:mysql://{}@localhost/py2jdbc'.format(getuser()))
    cu = cx.cursor()
    cu.execute("drop table if exists tests")
    cu.execute("""
    create table tests(
        id integer primary key,
        name varchar(20) not null,
        bit_field bit,
        tinyint_field tinyint,
        boolean_field boolean,
        smallint_field smallint,
        mediumint_field mediumint,
        int_field int,
        bigint_field bigint,
        decimal_field decimal(10, 5),
        float_field float(10, 5),
        double_field double(10, 5),
        date_field date,
        datetime_field datetime,
        timestamp_field timestamp null,
        time_field time,
        varchar_field varchar(20) character set utf8,
        text_field text character set latin1,
        char_field char(10),
        longtext_field longtext,
        nchar_field national char(10),
        binary_field binary(10),
        blob_field blob,
        enum_field enum('foo', 'bar', 'baz'),
        set_field set('one', 'two', 'three')
    )""")
    cu.execute("insert into tests(id, name) values (?, ?)", (1, 'setup'))
    cu.close()


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
        ('id', py2jdbc.INTEGER, 11, None, 11, 0, False),
        ('name', py2jdbc.VARCHAR, 20, None, 20, 0, False),
        (field, desc[0], desc[1], None, desc[2], desc[3], True),
    )
    row = cu.fetchall()
    assert row == ((id, name, value),)


def test_bit():
    _test_field(2, 'bit', 1, py2jdbc.BIT, 1, 1, 0)


def test_tinyint():
    _test_field(3, 'tinyint', 15, py2jdbc.TINYINT, 4, 4, 0)


def test_boolean():
    _test_field(4, 'boolean', True, py2jdbc.BIT, 1, 1, 0)


def test_smallint():
    _test_field(5, 'smallint', 123, py2jdbc.SMALLINT, 6, 6, 0)


def test_mediumint():
    _test_field(6, 'mediumint', 123456, py2jdbc.INTEGER, 9, 9, 0)


def test_int():
    _test_field(7, 'int', -567890, py2jdbc.INTEGER, 11, 11, 0)


def test_bigint():
    _test_field(8, 'bigint', 12345678012345, py2jdbc.BIGINT, 20, 20, 0)


def test_decimal():
    _test_field(9, 'decimal', 12345.67871, py2jdbc.DECIMAL, 12, 10, 5)


def test_float():
    _test_field(10, 'float', 12345.67871, py2jdbc.REAL, 10, 10, 5)


def test_double():
    _test_field(11, 'double', 12345.67871, py2jdbc.DOUBLE, 10, 10, 5)


def test_date():
    _test_field(12, 'date', datetime.date(2014, 7, 14), py2jdbc.DATE, 10, 10, 0)


def test_datetime():
    _test_field(13, 'datetime', datetime.datetime(2015, 8, 16, 1, 2, 3),
                py2jdbc.TIMESTAMP, 19, 19, 0)


def test_timestamp():
    _test_field(14, 'timestamp', datetime.datetime(2016, 9, 18, 2, 4, 6),
                py2jdbc.TIMESTAMP, 19, 19, 0)


def test_time():
    _test_field(15, 'time', datetime.time(18, 15, 4), py2jdbc.TIME, 10, 10, 0)


def test_varchar():
    _test_field(16, 'varchar', 'this is a varchar', py2jdbc.VARCHAR, 20, 20, 0)


def test_text():
    _test_field(17, 'text', 'this is a text field', py2jdbc.LONGVARCHAR, 0xffff, 0xffff, 0)


def test_char():
    _test_field(18, 'char', 'char field', py2jdbc.CHAR, 10, 10, 0)


LONGTEXT = """\
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


def test_longtext():
    _test_field(19, 'longtext', LONGTEXT, py2jdbc.LONGVARCHAR, MAX_INT, MAX_INT, 0)


def test_nchar():
    _test_field(20, 'nchar', 'some nchar', py2jdbc.CHAR, 10, 10, 0)


def test_binary():
    # binary values are padded to column size
    _test_field(21, 'binary', os.urandom(10), py2jdbc.BINARY, 10, 10, 0)


def test_blob():
    _test_field(22, 'blob', os.urandom(100), py2jdbc.LONGVARBINARY, 0xffff, 0xffff, 0)


def test_enum():
    _test_field(23, 'enum', 'foo', py2jdbc.CHAR, 3, 3, 0)


def test_set():
    _test_field(24, 'set', 'two', py2jdbc.CHAR, 13, 13, 0)


def test_execute_no_args():
    global cu
    cu.execute("delete from tests")


def test_execute_illegal_sql():
    global cu
    with pytest.raises(py2jdbc.OperationalError):
        cu.execute("select asdf")


def test_execute_too_much_sql2():
    global cu
    cu.execute("select 5+4; -- foo bar")


def test_execute_too_much_sql3():
    global cu
    cu.execute("""
    select 5 + 4;

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
    cu.execute("insert into tests(id, name, varchar_field) values (?, ?, ?)",
               (25, 'with_zero_byte', six.u("Hu\u0000go")))
    cu.execute("select varchar_field from tests where id = ?", (25,))
    row = cu.fetchone()
    assert row[0] == six.u("Hu\u0000go")


def test_execute_wrong_no_of_args1():
    global cu
    with pytest.raises(py2jdbc.ProgrammingError):
        cu.execute("insert into tests(id, name) values (?, ?)",
                   (26, 'wrong_no_of_args1', "Egon"))


def test_execute_wrong_no_of_args2():
    global cu
    with pytest.raises(py2jdbc.OperationalError):
        cu.execute("insert into tests(id) values (?)")


def test_execute_param_list():
    global cu
    cu.execute("insert into tests(id, name) values (28, 'param_list')")
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

    cu.execute("insert into tests(id, name) values (29, 'param_sequence')")
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
    cu.execute("insert into tests(id, name, text_field) values (?, ?, ?)",
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
        ('id', py2jdbc.INTEGER, 11, None, 11, 0, False),
        ('name', py2jdbc.VARCHAR, 20, None, 20, 0, False),
        ('bit_field', py2jdbc.BIT, 1, None, 1, 0, True),
        ('tinyint_field', py2jdbc.dbi.TINYINT, 4, None, 4, 0, True),
        ('boolean_field', py2jdbc.BIT, 1, None, 1, 0, True),
        ('smallint_field', py2jdbc.dbi.SMALLINT, 6, None, 6, 0, True),
        ('mediumint_field', py2jdbc.dbi.INTEGER, 9, None, 9, 0, True),
        ('int_field', py2jdbc.dbi.INTEGER, 11, None, 11, 0, True),
        ('bigint_field', py2jdbc.dbi.BIGINT, 20, None, 20, 0, True),
        ('decimal_field', py2jdbc.dbi.DECIMAL, 12, None, 10, 5, True),
        ('float_field', py2jdbc.dbi.REAL, 10, None, 10, 5, True),
        ('double_field', py2jdbc.dbi.DOUBLE, 10, None, 10, 5, True),
        ('date_field', py2jdbc.dbi.DATE, 10, None, 10, 0, True),
        ('datetime_field', py2jdbc.dbi.TIMESTAMP, 19, None, 19, 0, True),
        ('timestamp_field', py2jdbc.dbi.TIMESTAMP, 19, None, 19, 0, True),
        ('time_field', py2jdbc.dbi.TIME, 10, None, 10, 0, True),
        ('varchar_field', py2jdbc.dbi.VARCHAR, 20, None, 20, 0, True),
        ('text_field', py2jdbc.dbi.LONGVARCHAR, 0xffff, None, 0xffff, 0, True),
        ('char_field', py2jdbc.dbi.CHAR, 10, None, 10, 0, True),
        ('longtext_field', py2jdbc.dbi.LONGVARCHAR, MAX_INT, None, MAX_INT, 0, True),
        ('nchar_field', py2jdbc.dbi.CHAR, 10, None, 10, 0, True),
        ('binary_field', py2jdbc.dbi.BINARY, 10, None, 10, 0, True),
        ('blob_field', py2jdbc.dbi.LONGVARBINARY, 0xffff, None, 0xffff, 0, True),
        ('enum_field', py2jdbc.dbi.CHAR, 3, None, 3, 0, True),
        ('set_field', py2jdbc.dbi.CHAR, 13, None, 13, 0, True),
    )
    cu.execute("select null from tests")
    assert cu.description == (
        ('NULL', py2jdbc.NULL, 0, None, 0, 0, True),
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
