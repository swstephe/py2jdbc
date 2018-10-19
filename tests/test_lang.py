# -*- coding: utf8 -*-
import logging
import six
import pytest
from py2jdbc.jni import jdouble, jobject
from py2jdbc.wrap import get_env
from py2jdbc.lang import (
    Object,
    LangException
)
from tests.config import (
    CLASSPATH, JAVA_OPTS,
    MAX_BYTE,
    MAX_CHAR,
    MAX_SHORT,
    MAX_LONG,
    MAX_INT,
    MAX_FLOAT,
    MAX_DOUBLE
)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

_env = None


def setup_module():
    global _env
    _env = get_env(**JAVA_OPTS)


def test_object():
    global _env
    cls = _env.get('java.lang.Object')
    obj1 = cls.new()
    assert isinstance(obj1, Object.Instance)
    assert obj1.toString().startswith('java.lang.Object@')
    obj2 = cls.new()
    assert isinstance(obj2, Object.Instance)
    assert obj2.toString().startswith('java.lang.Object@')
    assert obj1 != obj2
    assert obj1.hashCode() != obj2.hashCode()


def test_boolean():
    global _env
    cls = _env.get('java.lang.Boolean')
    obj1 = cls.new('true')
    obj2 = cls.new(True)
    obj3 = cls.new(False)
    assert obj1 == obj2
    assert obj1 != obj3
    assert bool(obj1) is True
    assert obj1
    assert not obj3
    del obj3
    del obj2
    del obj1


def test_char():
    cls = _env.get('java.lang.Character')
    assert cls.MAX_VALUE == six.unichr(MAX_CHAR)
    obj1 = cls.new(six.unichr(191))
    assert obj1.charValue() == six.unichr(191)
    obj2 = cls.new(six.unichr(191))
    obj3 = cls.new(six.unichr(1001))
    assert obj1 == obj2
    assert obj1 != obj3


def test_byte():
    cls = _env.get('java.lang.Byte')
    assert cls.MAX_VALUE == MAX_BYTE
    obj1 = cls.new('123')
    obj2 = cls.new(123)
    obj3 = cls.new(64)
    assert obj1 == obj2
    assert obj1 != obj3
    assert int(obj1) == 123
    assert float(obj1) == 123.0


def test_short():
    cls = _env.get('java.lang.Short')
    assert cls.MAX_VALUE == MAX_SHORT
    obj1 = cls.new('123')
    obj2 = cls.new(123)
    obj3 = cls.new(64)
    assert obj1 == obj2
    assert obj1 != obj3
    assert int(obj1) == 123
    assert float(obj1) == 123.0


def test_int():
    cls = _env.get('java.lang.Integer')
    assert cls.MAX_VALUE == MAX_INT
    obj1 = cls.new('123')
    obj2 = cls.new(123)
    obj3 = cls.new(64)
    assert obj1 == obj2
    assert obj1 != obj3
    assert int(obj1) == 123
    assert float(obj1) == 123.0


def test_long():
    cls = _env.get('java.lang.Long')
    assert cls.MAX_VALUE == MAX_LONG
    obj1 = cls.new('123')
    obj2 = cls.new(123)
    obj3 = cls.new(64)
    assert obj1 == obj2
    assert obj1 != obj3
    assert int(obj1) == 123
    assert float(obj1) == 123.0


def test_float():
    cls = _env.get('java.lang.Float')
    assert cls.MAX_VALUE == MAX_FLOAT
    obj1 = cls.new('123')
    obj2 = cls.new(123)
    obj3 = cls.new(64)
    assert obj1 == obj2
    assert obj1 != obj3
    assert int(obj1) == 123
    assert float(obj1) == 123.0


def test_double():
    cls = _env.get('java.lang.Double')
    assert cls.MAX_VALUE == jdouble(MAX_DOUBLE).value
    value = jdouble(1234.5678901234).value
    obj = cls.new(value)
    assert obj.doubleValue() == value
    obj1 = cls.new('-123')
    obj2 = cls.new(-123)
    obj3 = cls.new(-64)
    assert obj1 == obj2
    assert obj1 != obj3
    assert int(obj1) == -123
    assert float(obj1) == -123.0


def test_system():
    cls = _env.get('java.lang.System')
    assert cls.getProperty('java.class.path') == CLASSPATH
    assert isinstance(cls.out, jobject)


def test_class():
    cls = _env.get('java.lang.Class')
    cls2 = cls.forName('java.lang.System')
    assert cls2.getName() == 'java.lang.System'
    with pytest.raises(LangException.Instance) as e:
        cls.forName('foo.bar.baz')
        assert 'java.lang.ClassNotFoundException' in e


def test_exception():
    global _env
    cls = _env.get('java.lang.Integer')
    with pytest.raises(LangException.Instance) as excinfo:
        cls.valueOf('abc')
    assert 'java.lang.NumberFormatException' in excinfo.value.message
