# -*- coding: utf8 -*-
import logging

from py2jdbc.lang import Object


log = logging.getLogger(__name__)


class ReflectField(Object):
    class Instance(Object.Instance):
        def __init__(self, cls, obj):
            super(ReflectField.Instance, self).__init__(cls, obj)
            self.getName = lambda o=obj: cls.getName(o)
            self.getType = lambda o=obj: cls.getType(o)

    def __init__(self, env, class_name='java.lang.reflect.Field'):
        super(ReflectField, self).__init__(env, class_name=class_name)
        self.getName = self.method('getName', '()Ljava/lang/String;')
        self.getType = self.method('getType', '()Ljava/lang/Class;')


class ReflectMethod(Object):
    class Instance(Object.Instance):
        def __init__(self, cls, obj):
            self.getName = lambda o=obj: cls.getName(o)
            self.getReturnType = lambda o=obj: cls.getReturnType(o)
            self.getParameterTypes = lambda o=obj: cls.getParameterTypes(o)

    def __init__(self, env, class_name='java.lang.reflect.Method'):
        super(ReflectMethod, self).__init__(env, class_name=class_name)
        self.getName = self.method('getName', '()Ljava/lang/String;')
        self.getReturnType = self.method('getReturnType', '()Ljava/lang/Class;')
        self.getParameterTypes = self.method('getParameterTypes', '()[Ljava/lang/Class;')
