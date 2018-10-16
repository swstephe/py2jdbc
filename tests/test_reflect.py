# -*- coding: utf8 -*-
import logging
from py2jdbc.wrap import get_env
from py2jdbc.lang import Class, Integer
import py2jdbc.reflect
from tests.config import JAVA_OPTS

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

_env = None


def setup_module():
    global _env
    _env = get_env(**JAVA_OPTS)


def test_reflect_field():
    global _env
    integer_cls = _env.get('java.lang.Integer')
    assert isinstance(integer_cls, Integer)
    cls = _env.get('java.lang.Class')
    assert isinstance(cls, Class)
    modifier_cls = _env.get('java.lang.reflect.Modifier')
    inst = cls(integer_cls.cls)
    assert isinstance(inst, Class.Instance)
    field = inst.getDeclaredField('MAX_VALUE')
    assert field.getName() == 'MAX_VALUE'
    assert modifier_cls.isStatic(field.getModifiers())


def test_reflect_method():
    global _env
    integer_cls = _env.get('java.lang.Integer')
    assert isinstance(integer_cls, Integer)
    cls = _env.get('java.lang.Class')
    assert isinstance(cls, Class)
    modifier_cls = _env.get('java.lang.reflect.Modifier')
    inst = cls(integer_cls.cls)
    assert isinstance(inst, Class.Instance)
    method = inst.getDeclaredMethod('intValue')
    assert method.getName() == 'intValue'
    modifiers = method.getModifiers()
    assert not modifier_cls.isStatic(modifiers)
    assert modifier_cls.isPublic(modifiers)
