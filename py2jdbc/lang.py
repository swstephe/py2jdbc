# -*- coding: utf8 -*-
import logging
import six

from py2jdbc.wrap import JClass, ThreadEnv
from py2jdbc.reflect import ReflectField, ReflectMethod


log = logging.getLogger(__name__)


class JavaException(Exception):
    """
    Wrapper for jni.JavaException.

    Takes a jthrowable object and expands the stack trace into
    a strng message.
    """
    @classmethod
    def from_jni_exception(cls, env, e):
        """
        Extract messages from top-level stack trace.

        :param env: `ThreadEnv` instance
        :param e: jthrowable
        :return: JavaException with message initialized to stack trace strings.
        """
        for cn in ((
            'java.sql.SQLException',
            'java.lang.Exception',
            'java.lang.Throwable',
        )):
            if cn in env.classes:
                base_class = env.classes[cn]
                if env.env.IsInstanceOf(e.throwable, base_class.cls):
                    throwable = base_class(e.throwable)
                    break
        else:
            raise RuntimeError(
                "exception raised with %s class"
                % jni.get_class_name(env, e.throwable)
            )
        ste = env.classes['java.lang.StackTraceElement']
        message = ['Exception in thread "main" {}'.format(throwable.getMessage())]
        log.info('message=%r', message)
        stack_trace = throwable.getStackTrace()
        for elem in stack_trace:
            name = ste(elem).getClassName()
            log.info("name=%r", name)
            message.append(name)
        message = '\n    at '.join(message)
        raise cls(message)

    def __init__(self, message):
        self.message = message


class Object(JClass):
    """
    Wrapper for java.lang.Object class
    """
    class Instance(object):
        """
        Wrapper for an instance of java.lang.Object
        """
        def __init__(self, cls, obj):
            self.cls = cls
            self.obj = obj
            self.equals = lambda other, o=obj: cls.equals(o, other)
            self.hashCode = lambda o=obj: cls.hashCode(o)
            self.toString = lambda o=obj: cls.toString(o)
            self.getClass = lambda o=obj: cls.getClass(o)

        @property
        def env(self):
            return self.cls.env

        def __eq__(self, other):
            return self.equals(other.obj)

    def __init__(self, env, class_name='java.lang.Object'):
        super(Object, self).__init__(env, class_name=class_name)
        self.equals = self.method('equals', '(Ljava/lang/Object;)Z')
        self.getClass = self.method('getClass', '()Ljava/lang/Class;')
        self.toString = self.method('toString', '()Ljava/lang/String;')
        self.hashCode = self.method('hashCode', '()I')

    def __call__(self, *args):
        """
        Given an object instance (jni.jobject), wrap it in this
        class' wrapper class.

        :param obj: the object instance
        :return: this class' Instance object
        """
        return Object.Instance(self, *args)

    def new(self, *args):
        raise RuntimeError("unexpected arguments to %r(): %r" % (
            self.__class__.__name__,
            args
        ))


class Class(Object):
    """
    Wrapper for java.lang.Class class
    """
    class Instance(Object.Instance):
        """
        Wrapper for an instance of java.lang.Class
        """
        def __init__(self, cls, obj):
            super(Class.Instance, self).__init__(cls, obj)
            self.getName = lambda o=obj: cls.getName(o)

        def getDeclaredField(self, name):
            return ReflectField(self.cls.getDeclaredField(self.obj, name))

        def getDeclaredMethod(self, name, *classes):
            _classes = classes
            return ReflectMethod(self.cls.getDeclaredMethod(self.obj, name, _classes))

    def __init__(self, env, class_name='java.lang.Class'):
        super(Class, self).__init__(env, class_name=class_name)
        self._forName = self.static_method('forName', '(Ljava/lang/String;)Ljava/lang/Class;')
        self.getDeclaredField = self.method(
            'getDeclaredField',
            '(Ljava/lang/String;)Ljava/lang/reflect/Field;'
        )
        self.getDeclaredMethod = self.method(
            'getDeclaredMethod',
            '(Ljava/lang/String;[Ljava/lang/Class;)Ljava/lang/reflect/Method;'
        )
        self.getName = self.method('getName', '()Ljava/lang/String;')

    def __call__(self, *args):
        return Class.Instance(self, *args)

    def forName(self, name):
        """
        :param name:
        :return: a Class.Instance wrapper for the result of forName
        """
        return self(self._forName(name))


class StackTraceElement(Object):
    """
    Wrapper for java.lang.StackTraceElement Java class
    """
    class Instance(Object.Instance):
        """
        Wrapper for an instance of java.lang.StackTraceElement
        """
        def __init__(self, cls, obj):
            super(StackTraceElement.Instance, self).__init__(cls, obj)
            self.getClassName = lambda o=obj, *a: cls.getClassName(o, *a)
            self.getFileName = lambda o=obj, *a: cls.getFileName(o, *a)
            self.getLineNumber = lambda o=obj, *a: cls.getLineNumber(o, *a)
            self.getMethodName = lambda o=obj, *a: cls.getMethodName(o, *a)

    def __init__(self, env, class_name='java.lang.StackTraceElement'):
        super(StackTraceElement, self).__init__(env, class_name=class_name)
        self.getClassName = self.method('getClassName', '()Ljava/lang/String;')
        self.getFileName = self.method('getFileName', '()Ljava/lang/String;')
        self.getLineNumber = self.method('getLineNumber', '()I')
        self.getMethodName = self.method('getMethodName', '()Ljava/lang/String;')

    def __call__(self, *args):
        return StackTraceElement.Instance(self, *args)


class System(Object):
    """
    Wrapper for java.lang.System.

    This is useful for testing and checking Java system properties.
    """
    def __init__(self, env, class_name='java.lang.System'):
        super(System, self).__init__(env, class_name=class_name)
        self.getProperty = self.static_method(
            'getProperty',
            '(Ljava/lang/String;)Ljava/lang/String;'
        )
        self.out = self.static_field('out', 'Ljava/io/PrintStream;')


class Throwable(Object):
    """
    Wrapper for java.lang.Throwable class
    """
    class Instance(Object.Instance):
        """
        Wrapper for java.lang.Throwable object instance
        """
        def __init__(self, cls, obj):
            super(Throwable.Instance, self).__init__(cls, obj)
            self.getMessage = lambda o=obj: cls.getMessage(o)
            self.getStackTrace = lambda o=obj: cls.getStackTrace(o)

    def __init__(self, env, class_name='java.lang.Throwable'):
        super(Throwable, self).__init__(env, class_name=class_name)
        self.getMessage = self.method('getMessage', '()Ljava/lang/String;')
        self.getStackTrace = self.method('getStackTrace', '()[Ljava/lang/StackTraceElement;')

    def __call__(self, *args):
        return Throwable.Instance(self, *args)


class LangException(Throwable):
    """
    Wrapper for java.lang.Exception class
    """
    class Instance(Throwable.Instance):
        """
        Wrapper for java.lang.Exception object instance
        """
        def __init__(self, cls, obj):
            super(LangException.Instance, self).__init__(cls, obj)

    def __init__(self, env, class_name='java.lang.Exception'):
        super(LangException, self).__init__(env, class_name=class_name)

    def __call__(self, *args):
        return LangException.Instance(self, *args)


class Boolean(Object):
    """
    Wrapper for java.lang.Boolean class
    """
    class Instance(Object.Instance):
        """
        Wrapper for java.lang.Boolean object instance
        """
        def __init__(self, cls, obj):
            super(Boolean.Instance, self).__init__(cls, obj)
            self.booleanValue = lambda o=obj: cls.booleanValue(o)

        def __bool__(self):
            return self.booleanValue()

    def __init__(self, env, class_name='java.lang.Boolean'):
        assert isinstance(env, ThreadEnv)
        super(Boolean, self).__init__(env, class_name=class_name)
        self.FALSE = self(self.static_field('FALSE', 'Ljava/lang/Boolean;'))
        self.TRUE = self(self.static_field('TRUE', 'Ljava/lang/Boolean;'))
        self.cons_s = self.constructor('Ljava/lang/String;')
        self.cons_z = self.constructor('Z')
        self.booleanValue = self.method('booleanValue', '()Z')

    def __call__(self, *args):
        return Boolean.Instance(self, *args)

    def new(self, *args):
        if len(args) != 1:
            raise ValueError("expected only one argument")
        if isinstance(args[0], six.string_types):
            return self.cons_s(*args)
        else:
            return self.cons_z(*args)


class Character(Object):
    """
    Wrapper for java.lang.Character
    """
    class Instance(Object.Instance):
        def __init__(self, cls, obj):
            super(Character.Instance, self).__init__(cls, obj)
            self.charValue = lambda o=obj: cls.charValue(o)

    def __init__(self, env, class_name='java.lang.Character'):
        super(Character, self).__init__(env, class_name=class_name)
        self.cons = self.constructor('C')
        self.charValue = self.method('charValue', '()C')

    def __call__(self, *args):
        return Character.Instance(self, *args)

    def new(self, *args):
        if len(args) != 1:
            raise ValueError("expected only one argument")
        return self.cons(*args)


class Number(Object):
    """
    Wrapper for java.lang.Number class
    """
    class Instance(Object.Instance):
        """
        Wrapper for java.lang.Number object instance
        """
        def __init__(self, cls, obj):
            super(Number.Instance, self).__init__(cls, obj)
            self.intValue = lambda o=obj: cls.intValue(o)
            self.longValue = lambda o=obj: cls.longValue(o)
            self.floatValue = lambda o=obj: cls.floatValue(o)
            self.doubleValue = lambda o=obj: cls.doubleValue(o)
            self.byteValue = lambda o=obj: cls.byteValue(o)
            self.shortValue = lambda o=obj: cls.shortValue(o)

        def __int__(self):
            return self.longValue()

        def __float__(self):
            return self.doubleValue()

    def __init__(self, env, class_name='java.lang.Number'):
        super(Number, self).__init__(env, class_name=class_name)
        self.intValue = self.method('intValue', '()I')
        self.longValue = self.method('longValue', '()J')
        self.floatValue = self.method('floatValue', '()F')
        self.doubleValue = self.method('doubleValue', '()D')
        self.byteValue = self.method('byteValue', '()B')
        self.shortValue = self.method('shortValue', '()S')

    def __call__(self, *args):
        return Number.Instance(self, *args)


class Byte(Number):
    """
    Wrapper for java.lang.Byte class
    """
    class Instance(Number.Instance):
        """
        Wrapper for java.lang.Byte object instance
        """
        def __init__(self, cls, obj):
            super(Byte.Instance, self).__init__(cls, obj)

        def __int__(self):
            return self.byteValue()

    def __init__(self, env, class_name='java.lang.Byte'):
        super(Byte, self).__init__(env, class_name=class_name)
        self.MAX_VALUE = self.static_field('MAX_VALUE', 'B')
        self.MIN_VALUE = self.static_field('MIN_VALUE', 'B')
        self.SIZE = self.static_field('SIZE', 'I')
        self.cons_s = self.constructor('Ljava/lang/String;')
        self.cons_b = self.constructor('B')
        self.compare = self.static_method('compare', '(BB)I')

    def __call__(self, *args):
        return Byte.Instance(self, *args)

    def new(self, *args):
        if len(args) != 1:
            raise ValueError("expected only one argument")
        if isinstance(args[0], six.string_types):
            return self.cons_s(*args)
        else:
            return self.cons_b(*args)


class Short(Number):
    """
    Wrapper for java.lang.Short class
    """
    class Instance(Number.Instance):
        """
        Wrapper for java.lang.Short object instance
        """
        def __init__(self, cls, obj):
            super(Short.Instance, self).__init__(cls, obj)

        def __int__(self):
            return self.shortValue()

    def __init__(self, env, class_name='java.lang.Short'):
        super(Short, self).__init__(env, class_name=class_name)
        self.MAX_VALUE = self.static_field('MAX_VALUE', 'S')
        self.MIN_VALUE = self.static_field('MIN_VALUE', 'S')
        self.SIZE = self.static_field('SIZE', 'I')
        self.cons_str = self.constructor('Ljava/lang/String;')
        self.cons_s = self.constructor('S')

    def __call__(self, *args):
        return Short.Instance(self, *args)

    def new(self, *args):
        if len(args) != 1:
            raise ValueError("expected only one argument")
        if isinstance(args[0], six.string_types):
            return self.cons_str(*args)
        else:
            return self.cons_s(*args)


class Integer(Number):
    """
    Wrapper for java.lang.Integer class
    """
    class Instance(Number.Instance):
        """
        Wrapper for java.lang.Integer object instance
        """
        def __init__(self, cls, obj):
            super(Integer.Instance, self).__init__(cls, obj)

        def __int__(self):
            return self.intValue()

    def __init__(self, env, class_name='java.lang.Integer'):
        super(Integer, self).__init__(env, class_name=class_name)
        self.MAX_VALUE = self.static_field('MAX_VALUE', 'I')
        self.MIN_VALUE = self.static_field('MIN_VALUE', 'I')
        self.SIZE = self.static_field('SIZE', 'I')
        self.cons_s = self.constructor('Ljava/lang/String;')
        self.cons_i = self.constructor('I')

    def __call__(self, *args):
        return Integer.Instance(self, *args)

    def new(self, *args):
        if len(args) != 1:
            raise ValueError("expected only one argument")
        if isinstance(args[0], six.string_types):
            return self.cons_s(*args)
        else:
            return self.cons_i(*args)


class Long(Number):
    """
    Wrapper for java.lang.Long class
    """
    class Instance(Number.Instance):
        """
        Wrapper for java.lang.Integer object instance
        """
        def __init__(self, cls, obj):
            super(Long.Instance, self).__init__(cls, obj)

        def __int__(self):
            return self.longValue()

    def __init__(self, env, class_name='java.lang.Long'):
        super(Long, self).__init__(env, class_name=class_name)
        self.MAX_VALUE = self.static_field('MAX_VALUE', 'J')
        self.MIN_VALUE = self.static_field('MIN_VALUE', 'J')
        self.SIZE = self.static_field('SIZE', 'I')
        self.cons_s = self.constructor('Ljava/lang/String;')
        self.cons_j = self.constructor('J')

    def __call__(self, *args):
        return Long.Instance(self, *args)

    def new(self, *args):
        if len(args) != 1:
            raise ValueError("expected only one argument")
        if isinstance(args[0], six.string_types):
            return self.cons_s(*args)
        else:
            return self.cons_j(*args)


class Float(Number):
    """
    Wrapper for java.lang.Float class
    """
    class Instance(Number.Instance):
        """
        Wrapper for java.lang.Float object instance
        """
        def __init__(self, cls, obj):
            super(Float.Instance, self).__init__(cls, obj)

        def __float__(self):
            return self.floatValue()

    def __init__(self, env, class_name='java.lang.Float'):
        super(Float, self).__init__(env, class_name=class_name)
        self.MAX_EXPONENT = self.static_field('MAX_EXPONENT', 'I')
        self.MAX_VALUE = self.static_field('MAX_VALUE', 'F')
        self.MIN_EXPONENT = self.static_field('MIN_EXPONENT', 'I')
        self.MIN_NORMAL = self.static_field('MIN_NORMAL', 'F')
        self.MIN_VALUE = self.static_field('MIN_VALUE', 'F')
        self.NaN = self.static_field('NaN', 'F')
        self.NEGATIVE_INFINITY = self.static_field('NEGATIVE_INFINITY', 'F')
        self.POSITIVE_INFINITY = self.static_field('POSITIVE_INFINITY', 'F')
        self.SIZE = self.static_field('SIZE', 'I')
        self.cons_d = self.constructor('D')
        self.cons_s = self.constructor('Ljava/lang/String;')

    def __call__(self, *args):
        return Float.Instance(self, *args)

    def new(self, *args):
        if len(args) != 1:
            raise ValueError("expected only one argument")
        if isinstance(args[0], six.string_types):
            return self.cons_s(*args)
        else:
            return self.cons_d(*args)


class Double(Number):
    """
    Wrapper for java.lang.Double class
    """
    class Instance(Number.Instance):
        """
        Wrapper for java.lang.Double object instance
        """
        def __init__(self, cls, obj):
            super(Double.Instance, self).__init__(cls, obj)

        def __float__(self):
            return self.doubleValue()

    def __init__(self, env, class_name='java.lang.Double'):
        super(Double, self).__init__(env, class_name=class_name)
        self.MAX_EXPONENT = self.static_field('MAX_EXPONENT', 'I')
        self.MAX_VALUE = self.static_field('MAX_VALUE', 'D')
        self.MIN_EXPONENT = self.static_field('MIN_EXPONENT', 'I')
        self.MIN_NORMAL = self.static_field('MIN_NORMAL', 'D')
        self.MIN_VALUE = self.static_field('MIN_VALUE', 'D')
        self.NaN = self.static_field('NaN', 'D')
        self.NEGATIVE_INFINITY = self.static_field('NEGATIVE_INFINITY', 'D')
        self.POSITIVE_INFINITY = self.static_field('POSITIVE_INFINITY', 'D')
        self.SIZE = self.static_field('SIZE', 'I')
        self.cons_d = self.constructor('D')
        self.cons_s = self.constructor('Ljava/lang/String;')

    def __call__(self, *args):
        return Double.Instance(self, *args)

    def new(self, *args):
        if len(args) != 1:
            raise ValueError("expected only one argument")
        if isinstance(args[0], six.string_types):
            return self.cons_s(*args)
        else:
            return self.cons_d(*args)


class Enumeration(Object):
    """
    Wrapper for java.util.Enumeration java class.

    This is used to wrap things returning an Enumeration<T> object.
    It is up to the programmer to wrap the return values in the appropriate
    wrapper object.
    """
    class Instance(Object.Instance):
        """
        Wrapper for java.util.Enumeration object instance.

        Implements Python iterator symantics.
        """
        def __init__(self, cls, obj):
            super(Enumeration.Instance, self).__init__(cls, obj)
            self.hasMoreElements = lambda o=obj: cls.hasMoreElements(o)
            self.nextElement = lambda o=obj: cls.nextElement(o)

        def __iter__(self):
            return self

        def next(self):
            if not self.hasMoreElements():
                raise StopIteration()
            return self.nextElement()

    def __init__(self, env, class_name='java.util.Enumeration'):
        super(Enumeration, self).__init__(env, class_name=class_name)
        self.hasMoreElements = self.method('hasMoreElements', '()Z')
        self.nextElement = self.method('nextElement', '()Ljava/lang/Object;')

    def __call__(self, obj):
        return Enumeration.Instance(self, obj)
