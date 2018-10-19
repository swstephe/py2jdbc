# -*- coding: utf8 -*-
import logging
import six
from tests.config import (
    CLASSPATH,
    MAX_INT
)
import py2jdbc
import pytest

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
cx = None
cu = None


def setup():
    global cx, cu
    cx = py2jdbc.connect('jdbc:sqlite::memory:', classpath=CLASSPATH)
    cu = cx.cursor()
    cu.execute("""
    create table tests(
        id integer primary key,
        name text not null,
        integer_field integer,
        real_field real,
        text_field text,
        blob_field blob
    )""")
    cu.execute("insert into tests(id, name) values (?, ?)", (1, 'setup'))
    cu.close()


def teardown():
    global cx, cu
    cu.close()
    cx.close()


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


def test_execute_arg_int():
    global cu
    cu.execute("insert into tests(id, name, integer_field) values (?, ?, ?)",
               (2, 'test_execute_arg_int', 42))
    cu.execute("select integer_field from tests where id = ?", (2,))
    row = cu.fetchone()
    assert row[0] == 42


def test_execute_arg_float():
    global cu
    cu.execute("insert into tests(id, name, real_field) values (?, ?, ?)",
               (3, 'test_execute_arg_float', 2500.32))
    cu.execute("select real_field from tests where id = ?", (3,))
    row = cu.fetchone()
    assert row[0] == 2500.32


def test_execute_arg_string():
    global cu
    cu.execute("insert into tests(id, name, text_field) values (?, ?, ?)",
               (4, 'test_execute_arg_string', 'Hugo'))
    cu.execute("select text_field from tests where id = ?", (4,))
    row = cu.fetchone()
    assert row[0] == 'Hugo'


def test_execute_arg_string_with_zero_byte():
    global cu
    cu.execute("insert into tests(id, name, text_field) values (?, ?, ?)",
               (5, 'test_execute_arg_string_with_zero_byte', six.u("Hu\u0000go")))
    cu.execute("select text_field from tests where id = ?", (5,))
    row = cu.fetchone()
    assert row[0] == six.u("Hu\u0000go")


def test_execute_wrong_no_of_args1():
    global cu
    with pytest.raises(py2jdbc.ProgrammingError):
        cu.execute("insert into tests(id, name) values (?, ?)",
                   (6, 'test_execute_wrong_no_of_args1', "Egon"))


def test_execute_wrong_no_of_args2():
    global cu
    with pytest.raises(py2jdbc.OperationalError):
        cu.execute("insert into tests(id) values (?)")


def test_execute_param_list():
    global cu
    cu.execute("insert into tests(id, name) values (8, 'test_execute_param_list')")
    cu.execute("select name from tests where name=?", ['test_execute_param_list'])
    row = cu.fetchone()
    assert row[0] == 'test_execute_param_list'


def test_execute_param_sequence():
    class L(object):
        def __len__(self):
            return 1

        def __getitem__(self, x):
            assert x == 0
            return 'test_execute_param_sequence'

    cu.execute("insert into tests(id, name) values (9, 'test_execute_param_sequence')")
    cu.execute("select name from tests where name=?", L())
    row = cu.fetchone()
    assert row[0] == 'test_execute_param_sequence'


def test_close():
    c = cx.cursor()
    c.close()


def test_rowcount_execute():
    cu.execute("delete from tests")
    cu.execute("insert into tests(id, name) values (1, 'test_rowcount_execute')")
    cu.execute("insert into tests(id, name) values (2, 'test_rowcount_execute')")
    cu.execute("update tests set name='foo'")
    assert cu.rowcount == 2


def test_rowcount_executemany():
    cu.execute("delete from tests")
    cu.executemany("insert into tests(id, name) values (?, ?)", [
        (1, 'test_rowcount_executemany'),
        (2, 'test_rowcount_executemany'),
        (3, 'test_rowcount_executemany')
    ])
    assert cu.rowcount == 3


def test_rowcount_executemany2():
    global cx
    with cx.cursor() as c:
        c.execute("delete from tests")
        c.executemany("insert into tests(id, name) values (?, ?)", [
            (1, 'test_rowcount_executemany2'),
            (2, 'test_rowcount_executemany2'),
            (3, 'test_rowcount_executemany2'),
            (4, 'test_rowcount_executemany2')
        ])
        assert c.rowcount == 4


def test_executemany_sequence():
    cu.execute("delete from tests")
    cu.executemany("insert into tests(id, name, real_field) values (?, ?, ?)", [
        (i + 1, 'test_executemany_sequence', 3.14 * i)
        for i in range(10)
    ])
    assert cu.rowcount == 10


def test_executemany_generator():
    def mygen():
        for i in range(5):
            yield (i + 1, 'test_executemany_generator')

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
        cu.executemany("insert into tests(id, name, real_field) values (?, ?, ?)",
                       11, 'test_executemany_not_iterable', 42)


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
    cu.execute("insert into tests(id, name, text_field) values (15, 'test_array_size', 'A')")
    cu.execute("insert into tests(id, name, text_field) values (16, 'test_array_size', 'B')")
    cu.execute("insert into tests(id, name, text_field) values (17, 'test_array_size', 'C')")
    cu.execute("select text_field from tests")
    res = cu.fetchmany()
    assert len(res) == 2
    res = cu.fetchmany()
    assert len(res) == 1


def test_fetchmany():
    global cu
    cu.execute("delete from tests")
    cu.execute("insert into tests(id, name, text_field) values (18, 'test_fetchmany', 'foo')")
    cu.execute("select text_field from tests")
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
        ('id', py2jdbc.INTEGER, MAX_INT, None, 0, 0, False),
        ('name', py2jdbc.VARCHAR, MAX_INT, None, 0, 0, True),
        ('integer_field', py2jdbc.INTEGER, MAX_INT, None, 0, 0, True),
        ('real_field', py2jdbc.REAL, MAX_INT, None, 0, 0, True),
        ('text_field', py2jdbc.VARCHAR, MAX_INT, None, 0, 0, True),
        ('blob_field', py2jdbc.BLOB, MAX_INT, None, 0, 0, True),
    )
    cu.execute("select null from tests")
    assert cu.description == (
        ('null', py2jdbc.NULL, MAX_INT, None, 0, 0, True),
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
