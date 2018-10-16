# -*- coding: utf8 -*-
import logging
from py2jdbc.lang import Object


log = logging.getLogger(__name__)


class ReflectModifier(Object):
    class_name = 'java.lang.reflect.Modifier'

    def __init__(self, env):
        super(ReflectModifier, self).__init__(env)
        self._ABSTRACT = self.static_field('ABSTRACT', 'I')
        self._FINAL = self.static_field('FINAL', 'I')
        self._INTERFACE = self.static_field('INTERFACE', 'I')
        self._NATIVE = self.static_field('NATIVE', 'I')
        self._PRIVATE = self.static_field('PRIVATE', 'I')
        self._PROTECTED = self.static_field('PROTECTED', 'I')
        self._PUBLIC = self.static_field('PUBLIC', 'I')
        self._STATIC = self.static_field('STATIC', 'I')
        self._STRICT = self.static_field('STRICT', 'I')
        self._SYNCHRONIZED = self.static_field('SYNCHRONIZED', 'I')
        self._TRANSIENT = self.static_field('TRANSIENT', 'I')
        self._VOLATILE = self.static_field('VOLATILE', 'I')

        self.classModifiers = self.static_method('classModifiers', '()I')
        self.constructorModifiers = self.static_method('constructorModifiers', '()I')
        self.fieldModifiers = self.static_method('fieldModifiers', '()I')
        self.interfaceModifiers = self.static_method('interfaceModifiers', '()I')
        self.isAbstract = self.static_method('isAbstract', '(I)Z')
        self.isFinal = self.static_method('isFinal', '(I)Z')
        self.isInterface = self.static_method('isInterface', '(I)Z')
        self.isNative = self.static_method('isNative', '(I)Z')
        self.isPrivate = self.static_method('isPrivate', '(I)Z')
        self.isProtected = self.static_method('isProtected', '(I)Z')
        self.isPublic = self.static_method('isPublic', '(I)Z')
        self.isStatic = self.static_method('isStatic', '(I)Z')
        self.isStrict = self.static_method('isStrict', '(I)Z')
        self.isSynchronized = self.static_method('isSynchronized', '(I)Z')
        self.isTransient = self.static_method('isTransient', '(I)Z')
        self.isVolatile = self.static_method('isVolatile', '(I)Z')
        self.methodModifiers = self.static_method('methodModifiers', '()I')

    @property
    def ABSTRACT(self):
        return self._ABSTRACT.get(self.cls)

    @property
    def FINAL(self):
        return self._FINAL.get(self.cls)

    @property
    def INTERFACE(self):
        return self._INTERFACE.get(self.cls)

    @property
    def NATIVE(self):
        return self._NATIVE.get(self.cls)

    @property
    def PRIVATE(self):
        return self._PRIVATE.get(self.cls)

    @property
    def PROTECTED(self):
        return self._PROTECTED.get(self.cls)

    @property
    def PUBLIC(self):
        return self._PUBLIC.get(self.cls)

    @property
    def STATIC(self):
        return self._STATIC.get(self.cls)

    @property
    def STRICT(self):
        return self._STRICT.get(self.cls)

    @property
    def SYNCHRONIZED(self):
        return self._SYNCHRONIZED.get(self.cls)

    @property
    def TRANSIENT(self):
        return self._TRANSIENT.get(self.cls)

    @property
    def VOLATILE(self):
        return self._VOLATILE.get(self.cls)


class ReflectField(Object):
    class_name = 'java.lang.reflect.Field'

    class Instance(Object.Instance):
        def __init__(self, cls, obj):
            super(ReflectField.Instance, self).__init__(cls, obj)
            self.getModifiers = lambda o=obj: cls.getModifiers(o)
            self.getName = lambda o=obj: cls.getName(o)

        def getType(self):
            cls = self.env.get('java.lang.Class')
            return cls(self.cls.getType(self.obj))

    def __init__(self, env):
        super(ReflectField, self).__init__(env)
        self.getModifiers = self.method('getModifiers', '()I')
        self.getName = self.method('getName', '()Ljava/lang/String;')
        self.getType = self.method('getType', '()Ljava/lang/Class;')


class ReflectMethod(Object):
    class_name = 'java.lang.reflect.Method'

    class Instance(Object.Instance):
        def __init__(self, cls, obj):
            super(ReflectMethod.Instance, self).__init__(cls, obj)
            self.getModifiers = lambda o=obj: cls.getModifiers(o)
            self.getName = lambda o=obj: cls.getName(o)

        def getReturnType(self):
            cls = self.env.get('java.lang.Class')
            return cls(self.cls.getReturnType(self.obj))

        def getParameterTypes(self):
            cls = self.env.get('java.lang.Class')
            return list(cls(param) for param in self.cls.getParameterTypes(self.obj))

    def __init__(self, env):
        super(ReflectMethod, self).__init__(env)
        self.getModifiers = self.method('getModifiers', '()I')
        self.getName = self.method('getName', '()Ljava/lang/String;')
        self.getReturnType = self.method('getReturnType', '()Ljava/lang/Class;')
        self.getParameterTypes = self.method('getParameterTypes', '()[Ljava/lang/Class;')
