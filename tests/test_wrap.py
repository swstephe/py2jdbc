# -*- coding: utf8 -*-
import logging
import six
from py2jdbc.jni import JNI_FALSE, jfloat, jdouble
from py2jdbc.wrap import get_env
from py2jdbc.lang import Object, ArgumentError
from tests.config import JAVA_OPTS, FIELDS, STATIC_FIELDS

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

_env = None


class Custom(Object):
    class_name = 'Custom'

    class Instance(Object.Instance):
        def __init__(self, cls, obj):
            super(Custom.Instance, self).__init__(cls, obj)

        @property
        def booleanField(self):
            return self.cls.booleanField.get(self.obj)

        @booleanField.setter
        def booleanField(self, value):
            self.cls.booleanField.set(self.obj, value)

        @property
        def byteField(self):
            return self.cls.byteField.get(self.obj)

        @byteField.setter
        def byteField(self, value):
            self.cls.byteField.set(self.obj, value)

        @property
        def charField(self):
            return self.cls.charField.get(self.obj)

        @charField.setter
        def charField(self, value):
            self.cls.charField.set(self.obj, value)

        @property
        def shortField(self):
            return self.cls.shortField.get(self.obj)

        @shortField.setter
        def shortField(self, value):
            self.cls.shortField.set(self.obj, value)

        @property
        def intField(self):
            return self.cls.intField.get(self.obj)

        @intField.setter
        def intField(self, value):
            self.cls.intField.set(self.obj, value)

        @property
        def longField(self):
            return self.cls.longField.get(self.obj)

        @longField.setter
        def longField(self, value):
            self.cls.longField.set(self.obj, value)

        @property
        def floatField(self):
            return self.cls.floatField.get(self.obj)

        @floatField.setter
        def floatField(self, value):
            self.cls.floatField.set(self.obj, value)

        @property
        def doubleField(self):
            return self.cls.doubleField.get(self.obj)

        @doubleField.setter
        def doubleField(self, value):
            self.cls.doubleField.set(self.obj, value)

        @property
        def stringField(self):
            return self.cls.stringField.get(self.obj)

        @stringField.setter
        def stringField(self, value):
            self.cls.stringField.set(self.obj, value)

    def __init__(self, env):
        super(Custom, self).__init__(env)
        if self.class_name == Custom.class_name:
            self.cons = self.constructor()
        self.booleanField = self.field('booleanField', 'Z')
        self.byteField = self.field('byteField', 'B')
        self.charField = self.field('charField', 'C')
        self.shortField = self.field('shortField', 'S')
        self.intField = self.field('intField', 'I')
        self.longField = self.field('longField', 'J')
        self.floatField = self.field('floatField', 'F')
        self.doubleField = self.field('doubleField', 'D')
        self.stringField = self.field('stringField', 'Ljava/lang/String;')
        self._staticBooleanField = self.static_field('staticBooleanField', 'Z')
        self._staticByteField = self.static_field('staticByteField', 'B')
        self._staticCharField = self.static_field('staticCharField', 'C')
        self._staticShortField = self.static_field('staticShortField', 'S')
        self._staticIntField = self.static_field('staticIntField', 'I')
        self._staticLongField = self.static_field('staticLongField', 'J')
        self._staticFloatField = self.static_field('staticFloatField', 'F')
        self._staticDoubleField = self.static_field('staticDoubleField', 'D')
        self._staticStringField = self.static_field('staticStringField', 'Ljava/lang/String;')
        # methods
        self.staticVoidMethod = self.static_method('staticVoidMethod', '()V')
        self.staticBooleanMethod = self.static_method('staticBooleanMethod', '()Z')
        self.staticByteMethod = self.static_method('staticByteMethod', '()B')
        self.staticCharMethod = self.static_method('staticCharMethod', '()C')
        self.staticShortMethod = self.static_method('staticShortMethod', '()S')
        self.staticIntMethod = self.static_method('staticIntMethod', '()I')
        self.staticLongMethod = self.static_method('staticLongMethod', '()J')
        self.staticFloatMethod = self.static_method('staticFloatMethod', '()F')
        self.staticDoubleMethod = self.static_method('staticDoubleMethod', '()D')
        self.staticStringMethod = self.static_method('staticStringMethod',
                                                     '()Ljava/lang/String;')

    @property
    def staticBooleanField(self):
        return self._staticBooleanField.get(self.cls)

    @staticBooleanField.setter
    def staticBooleanField(self, value):
        self._staticBooleanField.set(self.cls, value)

    @property
    def staticByteField(self):
        return self._staticByteField.get(self.cls)

    @staticByteField.setter
    def staticByteField(self, value):
        self._staticByteField.set(self.cls, value)

    @property
    def staticCharField(self):
        return self._staticCharField.get(self.cls)

    @staticCharField.setter
    def staticCharField(self, value):
        self._staticCharField.set(self.cls, value)

    @property
    def staticShortField(self):
        return self._staticShortField.get(self.cls)

    @staticShortField.setter
    def staticShortField(self, value):
        self._staticShortField.set(self.cls, value)

    @property
    def staticIntField(self):
        return self._staticIntField.get(self.cls)

    @staticIntField.setter
    def staticIntField(self, value):
        self._staticIntField.set(self.cls, value)

    @property
    def staticLongField(self):
        return self._staticLongField.get(self.cls)

    @staticLongField.setter
    def staticLongField(self, value):
        self._staticLongField.set(self.cls, value)

    @property
    def staticFloatField(self):
        return self._staticFloatField.get(self.cls)

    @staticFloatField.setter
    def staticFloatField(self, value):
        self._staticFloatField.set(self.cls, value)

    @property
    def staticDoubleField(self):
        return self._staticDoubleField.get(self.cls)

    @staticDoubleField.setter
    def staticDoubleField(self, value):
        self._staticDoubleField.set(self.cls, value)

    @property
    def staticStringField(self):
        return self._staticStringField.get(self.cls)

    @staticStringField.setter
    def staticStringField(self, value):
        self._staticStringField.set(self.cls, value)

    def new(self, *args):
        if len(args) == 0:
            return self.cons()
        raise ArgumentError(self, args)


def setup_module():
    global _env
    _env = get_env(**JAVA_OPTS)


def test_custom():
    cls = _env.get('Custom')
    obj = cls.new()
    # fields
    for code, typ, old, new in FIELDS:
        attr = '{}Field'.format(typ)
        assert getattr(obj, attr) == old
        setattr(obj, attr, new)
        assert getattr(obj, attr) == new
        setattr(obj, attr, old)
        assert getattr(obj, attr) == old

    # # static fields
    for code, typ, old, new in STATIC_FIELDS:
        attr = 'static{}Field'.format(typ)
        assert getattr(cls, attr) == old
        setattr(cls, attr, new)
        assert getattr(cls, attr) == new
        setattr(cls, attr, old)
        assert getattr(cls, attr) == old

    # # methods
    cls.staticVoidMethod()
    assert cls.staticBooleanMethod() == JNI_FALSE
    assert cls.staticByteMethod() == 0x32
    assert cls.staticCharMethod() == six.unichr(0x0196)
    assert cls.staticShortMethod() == 0x1122
    assert cls.staticIntMethod() == 0x00112233
    assert cls.staticLongMethod() == 0x876543210
    assert cls.staticFloatMethod() == jfloat(98.6).value
    assert cls.staticDoubleMethod() == jdouble(777.665544).value
    assert cls.staticStringMethod() == 'hello world'
