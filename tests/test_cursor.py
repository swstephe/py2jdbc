# -*- coding: utf8 -*-
import logging
from tests.config import CLASSPATH
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
    cu.execute("create table tests(id integer primary key, name text, income number)")
    cu.execute("insert into tests(name) values (?)", ('foo',))
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
    cu.execute("insert into tests(id) values (?)", (42,))


def test_execute_arg_float():
    global cu
    cu.execute("insert into tests(income) values (?)", (2500.32,))


def test_execute_arg_string():
    global cu
    cu.execute("insert into tests(name) values (?)", ("Hugo",))


# def test_execute_wrong_no_of_args1():
#     global cu
#     with pytest.raises(py2jdbc.OperationalError):
#         cu.execute("insert into tests(id) values (?)", (17, "Egon"))
#
#
def test_execute_wrong_no_of_args2():
    global cu
    with pytest.raises(py2jdbc.OperationalError):
        cu.execute("insert into tests(id) values (?)")


def test_execute_param_list():
    global cu
    cu.execute("insert into tests(name) values ('foo')")
    cu.execute("select name from tests where name=?", ['foo'])
    row = cu.fetchone()
    assert row[0] == 'foo'


def test_execute_param_sequence():
    class L(object):
        def __len__(self):
            return 1

        def __getitem__(self, x):
            assert x == 0
            return 'foo'

    cu.execute("insert into tests(name) values ('foo')")
    cu.execute("select name from tests where name=?", L())
    row = cu.fetchone()
    assert row[0] == 'foo'


def test_close():
    c = cx.cursor()
    c.close()


def test_rowcount_execute():
    cu.execute("delete from tests")
    cu.execute("insert into tests(name) values ('foo')")
    cu.execute("insert into tests(name) values ('foo')")
    cu.execute("update tests set name='bar'")
    assert cu.rowcount == 2


def test_rowcount_executemany():
    cu.execute("delete from tests")
    cu.executemany("insert into tests(name) values (?)", [(1,), (2,), (3,)])
    assert cu.rowcount == 3


def test_executemany_sequence():
    cu.executemany("insert into tests(income) values (?)", [(x,) for x in range(100, 110)])


def test_executemany_generator():
    def mygen():
        for i in range(5):
            yield (i,)

    cu.executemany("insert into tests(income) values (?)", mygen())


def test_executemany_wrong_sql_arg():
    with pytest.raises(ValueError):
        cu.executemany(42, [(3,)])


def test_executemany_not_iterable():
    with pytest.raises(TypeError):
        cu.executemany("insert into tests(income) values (?)", 42)


def test_fetch_iter():
    global cu
    cu.execute("delete from tests")
    cu.execute("insert into tests(id) values (?)", (5,))
    cu.execute("insert into tests(id) values (?)", (6,))
    cu.execute("select id from tests order by id")
    lst = [row[0] for row in cu]
    assert lst[0] == 5
    assert lst[1] == 6


def test_fetch_one():
    global cu
    cu.execute("select name from tests")
    row = cu.fetchone()
    assert row[0] == 'foo'
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
    cu.execute("insert into tests(name) values ('A')")
    cu.execute("insert into tests(name) values ('B')")
    cu.execute("insert into tests(name) values ('C')")
    cu.execute("select name from tests")
    res = cu.fetchmany()
    assert len(res) == 2


# def test_fetchmany():
#     global cu
#     cu.execute("select name from tests")
#     res = cu.fetchmany(100)
#     assert len(res) == 1
#     res = cu.fetchmany(100)
#     assert res == []
#
#
def test_fetchmany_kwargs():
    cu.execute("select name from tests")
    res = cu.fetchmany(size=100)
    assert len(res) == 1


# def test_fetchall():
#     cu.execute("select name from tests")
#     res = cu.fetchall()
#     assert len(res) == 1
#     res = cu.fetchall()
#     assert res == []
#
#
# def test_setinputsizes():
#     cu.setinputsizes([3, 4, 5])
#
#
# def test_setoutputsize():
#     cu.setoutputsize(5, 0)
#
#
# def test_setoutputsize_no_column():
#     cu.setoutputsize(42)
#
#
# def test_cursor_connection():
#     global cx, cu
#     assert cu.connection == cx
