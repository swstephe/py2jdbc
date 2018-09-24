# -*- coding: utf8 -*-
import logging
from tests.config import CLASSPATH
import py2jdbc
import pytest

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
cx = None


def setup_module():
    global cx
    cx = py2jdbc.connect('jdbc:sqlite::memory:', classpath=CLASSPATH)
    assert isinstance(cx, py2jdbc.Connection)
    cu = cx.cursor()
    assert isinstance(cu, py2jdbc.Cursor)
    cu.execute("create table tests(id integer primary key, name text)")
    cu.execute("insert into tests(name) values (?)", ('foo',))
    cu.close()


def teardown_module():
    global cx
    cx.close()


def test_apilevel():
    assert py2jdbc.apilevel == '2.0', "apilevel is %s, should be 2.0" % py2jdbc.apilevel


def test_threadsafety():
    assert py2jdbc.threadsafety == 1, "threadsafety is %d, should be 1" % py2jdbc.threadsafety


def test_paramstyle():
    assert py2jdbc.paramstyle == 'qmark', \
        "paramstyle is '%s', should be 'qmark'" % py2jdbc.paramstyle


def test_warning():
    assert issubclass(py2jdbc.Warning, Exception), "Warning is not a subclass of Exception"


def test_error():
    assert issubclass(py2jdbc.Error, Exception), "Error is not a subclass of Exception"


def test_interface_error():
    assert issubclass(py2jdbc.InterfaceError, py2jdbc.Error), \
        "InterfaceError is not a subclass of Error"


def test_database_error():
    assert issubclass(py2jdbc.DatabaseError, py2jdbc.Error), \
        "DatabaseError is not a subclass of Error"


def test_operational_error():
    assert issubclass(py2jdbc.DataError, py2jdbc.DatabaseError), \
        "DataError is not a subclass of DatabaseError"


def test_integrity_error():
    assert issubclass(py2jdbc.OperationalError, py2jdbc.DatabaseError), \
        "OperationalError is not a subclass of DatabaseError"


def test_programming_error():
    assert issubclass(py2jdbc.IntegrityError, py2jdbc.DatabaseError), \
        "IntegrityError is not a subclass of DatabaseError"


def test_not_supported_error():
    assert issubclass(py2jdbc.NotSupportedError, py2jdbc.DatabaseError), \
        "NotSupportedError is not a subclass of DatabaseError"


def test_commit():
    global cx
    cx.commit()


def test_commit_after_no_changes():
    global cx
    cx.commit()
    cx.commit()


def test_rollback():
    global cx
    cx.rollback()


def test_rollback_after_no_changes():
    global cx
    cx.rollback()
    cx.rollback()


def test_cursor():
    global cx
    cx.cursor()


def test_failed_open():
    with pytest.raises(py2jdbc.OperationalError):
        py2jdbc.connect('jdbc:sqlite:/foo/bar/bla/23534/mydb.db')


def test_close():
    global cx
    cx.close()


def test_exceptions():
    global cx
    assert cx.Warning == py2jdbc.Warning
    assert cx.Error == py2jdbc.Error
    assert cx.InterfaceError == py2jdbc.InterfaceError
    assert cx.DatabaseError == py2jdbc.DatabaseError
    assert cx.DataError == py2jdbc.DataError
    assert cx.OperationalError == py2jdbc.OperationalError
    assert cx.IntegrityError == py2jdbc.IntegrityError
    assert cx.InternalError == py2jdbc.InternalError
    assert cx.ProgrammingError == py2jdbc.ProgrammingError
    assert cx.NotSupportedError == py2jdbc.NotSupportedError
