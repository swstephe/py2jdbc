# -*- coding: utf8 -*-
import logging
import six
import pytest
from py2jdbc import jni
from py2jdbc import wrap
from tests.config import CLASSPATH, JAVA_OPTS

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

_env = None


def setup_module():
    global _env
    _env = wrap.get_env(**JAVA_OPTS)


def test_boolean():
    cls = _env.classes['java.lang.Boolean']
    obj1 = cls.new('true')
    # obj2 = cls.new(True)
    # obj3 = cls.new(False)
    # assert obj1 == obj2
    # assert obj1 != obj3
    # assert bool(obj1) is True
    # assert obj1
    # assert not obj3
    # del obj3
    # del obj2
    del obj1


def test_char():
    cls = _env.classes['java.lang.Character']
    obj1 = cls.new(six.unichr(191))
    assert obj1.charValue() == six.unichr(191)
    obj2 = cls.new(six.unichr(191))
    obj3 = cls.new(six.unichr(1001))
    assert obj1 == obj2
    assert obj1 != obj3


def test_byte():
    cls = _env.classes['java.lang.Byte']
    obj1 = cls.new('123')
    obj2 = cls.new(123)
    obj3 = cls.new(64)
    assert obj1 == obj2
    assert obj1 != obj3
    assert int(obj1) == 123
    assert float(obj1) == 123.0


def test_short():
    cls = _env.classes['java.lang.Short']
    obj1 = cls.new('123')
    obj2 = cls.new(123)
    obj3 = cls.new(64)
    assert obj1 == obj2
    assert obj1 != obj3
    assert int(obj1) == 123
    assert float(obj1) == 123.0


def test_int():
    cls = _env.classes['java.lang.Integer']
    obj1 = cls.new('123')
    obj2 = cls.new(123)
    obj3 = cls.new(64)
    assert obj1 == obj2
    assert obj1 != obj3
    assert int(obj1) == 123
    assert float(obj1) == 123.0


def test_long():
    cls = _env.classes['java.lang.Long']
    obj1 = cls.new('123')
    obj2 = cls.new(123)
    obj3 = cls.new(64)
    assert obj1 == obj2
    assert obj1 != obj3
    assert int(obj1) == 123
    assert float(obj1) == 123.0


def test_float():
    cls = _env.classes['java.lang.Float']
    obj1 = cls.new('123')
    obj2 = cls.new(123)
    obj3 = cls.new(64)
    assert obj1 == obj2
    assert obj1 != obj3
    assert int(obj1) == 123
    assert float(obj1) == 123.0


def test_double():
    cls = _env.classes['java.lang.Double']
    obj1 = cls.new('-123')
    obj2 = cls.new(-123)
    obj3 = cls.new(-64)
    assert obj1 == obj2
    assert obj1 != obj3
    assert int(obj1) == -123
    assert float(obj1) == -123.0


def test_system():
    cls = _env.classes['java.lang.System']
    assert cls.getProperty('java.class.path') == CLASSPATH
    assert isinstance(cls.out, jni.jobject)


def test_class():
    cls = _env.classes['java.lang.Class']
    cls2 = cls.forName('java.lang.System')
    assert cls2.getName() == 'java.lang.System'
    with pytest.raises(wrap.JavaException) as e:
        cls.forName('foo.bar.baz')
        assert 'java.lang.ClassNotFoundException' in e


def test_calendar():
    cls = _env.classes['java.util.GregorianCalendar']
    assert cls is not None
    cal = cls.new(2018, 9, 26)
    assert cal.ERA == cls.AD
    assert cal.YEAR == 2018
    assert cal.MONTH == 9
    assert cal.DAY_OF_MONTH == 26
    cal.set(2018, 9, 26, 12, 34, 56)
    assert cal.ERA == cls.AD
    assert cal.YEAR == 2018
    assert cal.MONTH == 9
    assert cal.DAY_OF_MONTH == 26
    assert cal.HOUR == 0
    assert cal.HOUR_OF_DAY == 12
    assert cal.AM_PM == cls.PM
    assert cal.MINUTE == 34
    assert cal.SECOND == 56
    assert cal.MILLISECOND == 0


def test_drivermanager():
    cls = _env.classes['java.sql.DriverManager']
    conn = cls.getConnection('jdbc:sqlite::memory:')
    assert conn is not None
    value = conn.getAutoCommit()
    assert value in (True, False)
    conn.setAutoCommit(value)
    conn.close()


def test_types():
    cls = _env.classes['java.sql.Types']
    assert cls.VARCHAR == 12
