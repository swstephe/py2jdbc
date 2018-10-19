# -*- coding: utf8 -*-
import logging
import six
from py2jdbc.jni import JNI_TRUE
from py2jdbc.wrap import JClass


log = logging.getLogger(__name__)


class MsgException(Exception):
    def __init__(self, message):
        super(MsgException, self).__init__()
        self.message = message


class ArgumentError(MsgException):
    def __init__(self, cls, args):
        super(ArgumentError, self).__init__(
            "unexpected arguments to %r.new(): %r" % (
                cls.__class__.__name__,
                args
            )
        )


class Object(JClass):
    """
    Wrapper for java.lang.Object class
    """
    class_name = 'java.lang.Object'

    class Instance(object):
        """
        Wrapper for an instance of java.lang.Object
        """
        def __init__(self, cls, obj):
            self.cls = cls
            self.obj = obj
            self.clone = lambda o=obj: cls.clone(o)
            self.equals = lambda other, o=obj: cls.equals(o, other)
            self.getClass = lambda o=obj: cls.getClass(o)
            self.hashCode = lambda o=obj: cls.hashCode(o)
            self.notify = lambda o=obj: cls.notify(o)
            self.notifyAll = lambda o=obj: cls.notifyAll(o)
            self.toString = lambda o=obj: cls.toString(o)

        @property
        def env(self):
            return self.cls.env

        def __eq__(self, other):
            return self.equals(other.obj)

        def __hash__(self):
            return self.hashCode()

        def __str__(self):
            return self.toString()

        def wait(self, *args):
            if len(args) == 0:
                self.cls.wait0(self.obj)
            elif len(args) == 1:
                self.cls.wait1(self.obj, *args)
            elif len(args) == 2:
                self.cls.wait2(self.obj, *args)
            else:
                raise ValueError("invalid number of arguments: %r" % args)

    def __init__(self, env):
        super(Object, self).__init__(env)
        if self.class_name == Object.class_name:
            self.cons = self.constructor()
        self.clone = self.method('clone', '()Ljava/lang/Object;')
        self.equals = self.method('equals', '(Ljava/lang/Object;)Z')
        self.getClass = self.method('getClass', '()Ljava/lang/Class;')
        self.hashCode = self.method('hashCode', '()I')
        self.notify = self.method('notify', '()V')
        self.notifyAll = self.method('notifyAll', '()V')
        self.toString = self.method('toString', '()Ljava/lang/String;')
        self.wait0 = self.method('wait', '()V')
        self.wait1 = self.method('wait', '(J)V')
        self.wait2 = self.method('wait', '(JI)V')

    def __call__(self, obj):
        """
        Given an object instance (jni.jobject), wrap it in this
        class' wrapper class.

        :param obj: the object instance
        :return: this class' Instance object
        """
        return self.Instance(self, obj)

    def new(self, *args):
        if len(args) == 0:
            return self.cons()
        raise ArgumentError(self, args)


class Class(Object):
    """
    Wrapper for java.lang.Class class
    """
    class_name = 'java.lang.Class'

    class Instance(Object.Instance):
        """
        Wrapper for an instance of java.lang.Class
        """
        def __init__(self, cls, obj):
            super(Class.Instance, self).__init__(cls, obj)
            self.getName = lambda o=obj: cls.getName(o)

        def getDeclaredField(self, name):
            cls = self.env.get('java.lang.reflect.Field')
            return cls(self.cls.getDeclaredField(self.obj, name))

        def getDeclaredMethod(self, name, *classes):
            cls = self.env.get('java.lang.reflect.Method')
            return cls(self.cls.getDeclaredMethod(self.obj, name, classes))

    def __init__(self, env):
        super(Class, self).__init__(env)
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
    class_name = 'java.lang.StackTraceElement'

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

    def __init__(self, env):
        super(StackTraceElement, self).__init__(env)
        self.getClassName = self.method('getClassName', '()Ljava/lang/String;')
        self.getFileName = self.method('getFileName', '()Ljava/lang/String;')
        self.getLineNumber = self.method('getLineNumber', '()I')
        self.getMethodName = self.method('getMethodName', '()Ljava/lang/String;')


class Throwable(Object):
    """
    Wrapper for java.lang.Throwable class
    """
    class_name = 'java.lang.Throwable'

    class Instance(Object.Instance, Exception):
        """
        Wrapper for java.lang.Throwable object instance
        """
        def __init__(self, cls, obj):
            super(Throwable.Instance, self).__init__(cls, obj)
            self.getMessage = lambda o=obj: cls.getMessage(o)
            self.getStackTrace = lambda o=obj: cls.getStackTrace(o)
            # gather exception message
            ste = cls.env.get('java.lang.StackTraceElement')
            message = [self.getMessage()]
            stack_trace = self.getStackTrace()
            for elem in stack_trace:
                name = ste(elem).getClassName()
                message.append(name)
            self.message = '\n    at '.join(message)

    def __init__(self, env):
        super(Throwable, self).__init__(env)
        self.getMessage = self.method('getMessage', '()Ljava/lang/String;')
        self.getStackTrace = self.method('getStackTrace', '()[Ljava/lang/StackTraceElement;')


class LangException(Throwable):
    """
    Wrapper for java.lang.Exception class
    """
    class_name = 'java.lang.Exception'

    class Instance(Throwable.Instance):
        """
        Wrapper for java.lang.Exception object instance
        """
        pass


class Boolean(Object):
    """
    Wrapper for java.lang.Boolean class
    """
    class_name = 'java.lang.Boolean'

    class Instance(Object.Instance):
        """
        Wrapper for java.lang.Boolean object instance
        """
        def __init__(self, cls, obj):
            super(Boolean.Instance, self).__init__(cls, obj)
            self.booleanValue = lambda o=obj: cls.booleanValue(o)

        def __bool__(self):
            return self.booleanValue() == JNI_TRUE

    def __init__(self, env):
        super(Boolean, self).__init__(env)
        self._FALSE = self.static_field('FALSE', 'Ljava/lang/Boolean;')
        self._TRUE = self.static_field('TRUE', 'Ljava/lang/Boolean;')
        if self.class_name == Boolean.class_name:
            self.cons_s = self.constructor('Ljava/lang/String;')
            self.cons_z = self.constructor('Z')
        self.booleanValue = self.method('booleanValue', '()Z')

    @property
    def FALSE(self):
        return self(self._FALSE.get(self.cls))

    @property
    def TRUE(self):
        return self(self._TRUE.get(self.cls))

    def new(self, *args):
        if len(args) == 1:
            if isinstance(args[0], six.string_types):
                return self.cons_s(*args)
            else:
                return self.cons_z(*args)
        return super(Boolean, self).new(*args)


class Character(Object):
    """
    Wrapper for java.lang.Character
    """
    class_name = 'java.lang.Character'

    class Instance(Object.Instance):
        def __init__(self, cls, obj):
            super(Character.Instance, self).__init__(cls, obj)
            self.charValue = lambda o=obj: cls.charValue(o)

    def __init__(self, env):
        super(Character, self).__init__(env)
        if self.class_name == Character.class_name:
            self.cons = self.constructor('C')
        self.charValue = self.method('charValue', '()C')
        self._MAX_VALUE = self.static_field('MAX_VALUE', 'C')

    @property
    def MAX_VALUE(self):
        return self._MAX_VALUE.get(self.cls)

    def new(self, *args):
        if len(args) == 1:
            return self.cons(args[0])
        return super(Character, self).new(*args)


class Number(Object):
    """
    Wrapper for java.lang.Number class
    """
    class_name = 'java.lang.Number'

    class Instance(Object.Instance):
        """
        Wrapper for java.lang.Number object instance
        """
        def __init__(self, cls, obj):
            super(Number.Instance, self).__init__(cls, obj)
            self.byteValue = lambda o=obj: cls.byteValue(o)
            self.doubleValue = lambda o=obj: cls.doubleValue(o)
            self.floatValue = lambda o=obj: cls.floatValue(o)
            self.intValue = lambda o=obj: cls.intValue(o)
            self.longValue = lambda o=obj: cls.longValue(o)
            self.shortValue = lambda o=obj: cls.shortValue(o)

        def __int__(self):
            return self.longValue()

        def __float__(self):
            return self.doubleValue()

    def __init__(self, env):
        super(Number, self).__init__(env)
        if self.class_name == Number.class_name:
            self.cons = self.constructor()
        self.byteValue = self.method('byteValue', '()B')
        self.doubleValue = self.method('doubleValue', '()D')
        self.floatValue = self.method('floatValue', '()F')
        self.intValue = self.method('intValue', '()I')
        self.longValue = self.method('longValue', '()J')
        self.shortValue = self.method('shortValue', '()S')

    def new(self, *args):
        if len(args) == 0:
            return self.cons()
        return super(Number, self).new(*args)


class Byte(Number):
    """
    Wrapper for java.lang.Byte class
    """
    class_name = 'java.lang.Byte'

    class Instance(Number.Instance):
        """
        Wrapper for java.lang.Byte object instance
        """
        def __init__(self, cls, obj):
            super(Byte.Instance, self).__init__(cls, obj)

        def __int__(self):
            return self.byteValue()

    def __init__(self, env):
        super(Byte, self).__init__(env)
        if self.class_name == Byte.class_name:
            self.cons_s = self.constructor('Ljava/lang/String;')
            self.cons_b = self.constructor('B')
        self._MAX_VALUE = self.static_field('MAX_VALUE', 'B')
        self._MIN_VALUE = self.static_field('MIN_VALUE', 'B')
        self._SIZE = self.static_field('SIZE', 'I')
        self.compare = self.static_method('compare', '(BB)I')

    @property
    def MAX_VALUE(self):
        return self._MAX_VALUE.get(self.cls)

    @property
    def MIN_VALUE(self):
        return self._MIN_VALUE.get(self.cls)

    @property
    def SIZE(self):
        return self._SIZE.get(self.cls)

    def new(self, *args):
        if len(args) == 1:
            if isinstance(args[0], six.string_types):
                return self.cons_s(args[0])
            else:
                return self.cons_b(args[0])
        return super(Byte, self).new(*args)


class Short(Number):
    """
    Wrapper for java.lang.Short class
    """
    class_name = 'java.lang.Short'

    class Instance(Number.Instance):
        """
        Wrapper for java.lang.Short object instance
        """
        def __init__(self, cls, obj):
            super(Short.Instance, self).__init__(cls, obj)

        def __int__(self):
            return self.shortValue()

    def __init__(self, env):
        super(Short, self).__init__(env)
        if self.class_name == Short.class_name:
            self.cons_str = self.constructor('Ljava/lang/String;')
            self.cons_s = self.constructor('S')
        self._MAX_VALUE = self.static_field('MAX_VALUE', 'S')
        self._MIN_VALUE = self.static_field('MIN_VALUE', 'S')
        self._SIZE = self.static_field('SIZE', 'I')

    @property
    def MAX_VALUE(self):
        return self._MAX_VALUE.get(self.cls)

    @property
    def MIN_VALUE(self):
        return self._MIN_VALUE.get(self.cls)

    @property
    def SIZE(self):
        return self._SIZE.get(self.cls)

    def new(self, *args):
        if len(args) == 1:
            if isinstance(args[0], six.string_types):
                return self.cons_str(args[0])
            else:
                return self.cons_s(args[0])
        return super(Short, self).new(*args)


class Integer(Number):
    """
    Wrapper for java.lang.Integer class
    """
    class_name = 'java.lang.Integer'

    class Instance(Number.Instance):
        """
        Wrapper for java.lang.Integer object instance
        """
        def __init__(self, cls, obj):
            super(Integer.Instance, self).__init__(cls, obj)

        def __int__(self):
            return self.intValue()

    def __init__(self, env):
        super(Integer, self).__init__(env)
        if self.class_name == Integer.class_name:
            self.cons_s = self.constructor('Ljava/lang/String;')
            self.cons_i = self.constructor('I')
        self._MAX_VALUE = self.static_field('MAX_VALUE', 'I')
        self._MIN_VALUE = self.static_field('MIN_VALUE', 'I')
        self._SIZE = self.static_field('SIZE', 'I')
        self._valueOf = self.static_method(
            'valueOf',
            '(Ljava/lang/String;)Ljava/lang/Integer;'
        )

    @property
    def MAX_VALUE(self):
        return self._MAX_VALUE.get(self.cls)

    @property
    def MIN_VALUE(self):
        return self._MIN_VALUE.get(self.cls)

    @property
    def SIZE(self):
        return self._SIZE.get(self.cls)

    def valueOf(self, s):
        return self(self._valueOf(s))

    def new(self, *args):
        if len(args) == 1:
            if isinstance(args[0], six.string_types):
                return self.cons_s(*args)
            else:
                return self.cons_i(*args)
        return super(Integer, self).new(*args)


class Long(Number):
    """
    Wrapper for java.lang.Long class
    """
    class_name = 'java.lang.Long'

    class Instance(Number.Instance):
        """
        Wrapper for java.lang.Integer object instance
        """
        def __init__(self, cls, obj):
            super(Long.Instance, self).__init__(cls, obj)

        def __int__(self):
            return self.longValue()

    def __init__(self, env):
        super(Long, self).__init__(env)
        if self.class_name == Long.class_name:
            self.cons_s = self.constructor('Ljava/lang/String;')
            self.cons_j = self.constructor('J')
        self._MAX_VALUE = self.static_field('MAX_VALUE', 'J')
        self._MIN_VALUE = self.static_field('MIN_VALUE', 'J')
        self._SIZE = self.static_field('SIZE', 'I')

    @property
    def MAX_VALUE(self):
        return self._MAX_VALUE.get(self.cls)

    @property
    def MIN_VALUE(self):
        return self._MIN_VALUE.get(self.cls)

    @property
    def SIZE(self):
        return self._SIZE.get(self.cls)

    def new(self, *args):
        if len(args) == 1:
            if isinstance(args[0], six.string_types):
                return self.cons_s(args[0])
            else:
                return self.cons_j(args[0])
        return super(Long, self).new(*args)


class Float(Number):
    """
    Wrapper for java.lang.Float class
    """
    class_name = 'java.lang.Float'

    class Instance(Number.Instance):
        """
        Wrapper for java.lang.Float object instance
        """
        def __init__(self, cls, obj):
            super(Float.Instance, self).__init__(cls, obj)

        def __float__(self):
            return self.floatValue()

    def __init__(self, env):
        super(Float, self).__init__(env)
        if self.class_name == Float.class_name:
            self.cons_d = self.constructor('D')
            self.cons_s = self.constructor('Ljava/lang/String;')
        self._MAX_EXPONENT = self.static_field('MAX_EXPONENT', 'I')
        self._MAX_VALUE = self.static_field('MAX_VALUE', 'F')
        self._MIN_EXPONENT = self.static_field('MIN_EXPONENT', 'I')
        self._MIN_NORMAL = self.static_field('MIN_NORMAL', 'F')
        self._MIN_VALUE = self.static_field('MIN_VALUE', 'F')
        self._NaN = self.static_field('NaN', 'F')
        self._NEGATIVE_INFINITY = self.static_field('NEGATIVE_INFINITY', 'F')
        self._POSITIVE_INFINITY = self.static_field('POSITIVE_INFINITY', 'F')
        self._SIZE = self.static_field('SIZE', 'I')

    @property
    def MAX_EXPONENT(self):
        return self._MAX_EXPONENT.get(self.cls)

    @property
    def MAX_VALUE(self):
        return self._MAX_VALUE.get(self.cls)

    @property
    def MIN_EXPONENT(self):
        return self._MIN_EXPONENT.get(self.cls)

    @property
    def MIN_NORMAL(self):
        return self._MIN_NORMAL.get(self.cls)

    @property
    def MIN_VALUE(self):
        return self._MIN_VALUE.get(self.cls)

    @property
    def NaN(self):
        return self._NaN.get(self.cls)

    @property
    def NEGATIVE_INFINITY(self):
        return self._NEGATIVE_INFINITY.get(self.cls)

    @property
    def POSITIVE_INFINITY(self):
        return self._POSITIVE_INFINITY.get(self.cls)

    @property
    def SIZE(self):
        return self._SIZE.get(self.cls)

    def new(self, *args):
        if len(args) == 1:
            if isinstance(args[0], six.string_types):
                return self.cons_s(args[0])
            else:
                return self.cons_d(args[0])
        return super(Float, self).new(*args)


class Double(Number):
    """
    Wrapper for java.lang.Double class
    """
    class_name = 'java.lang.Double'

    class Instance(Number.Instance):
        """
        Wrapper for java.lang.Double object instance
        """
        def __init__(self, cls, obj):
            super(Double.Instance, self).__init__(cls, obj)

        def __float__(self):
            return self.doubleValue()

    def __init__(self, env):
        super(Double, self).__init__(env)
        if self.class_name == Double.class_name:
            self.cons_d = self.constructor('D')
            self.cons_s = self.constructor('Ljava/lang/String;')
        self._MAX_EXPONENT = self.static_field('MAX_EXPONENT', 'I')
        self._MAX_VALUE = self.static_field('MAX_VALUE', 'D')
        self._MIN_EXPONENT = self.static_field('MIN_EXPONENT', 'I')
        self._MIN_NORMAL = self.static_field('MIN_NORMAL', 'D')
        self._MIN_VALUE = self.static_field('MIN_VALUE', 'D')
        self._NaN = self.static_field('NaN', 'D')
        self._NEGATIVE_INFINITY = self.static_field('NEGATIVE_INFINITY', 'D')
        self._POSITIVE_INFINITY = self.static_field('POSITIVE_INFINITY', 'D')
        self._SIZE = self.static_field('SIZE', 'I')

    @property
    def MAX_EXPONENT(self):
        return self._MAX_EXPONENT.get(self.cls)

    @property
    def MAX_VALUE(self):
        return self._MAX_VALUE.get(self.cls)

    @property
    def MIN_EXPONENT(self):
        return self._MIN_EXPONENT.get(self.cls)

    @property
    def MIN_NORMAL(self):
        return self._MIN_NORMAL.get(self.cls)

    @property
    def MIN_VALUE(self):
        return self._MIN_VALUE.get(self.cls)

    @property
    def NaN(self):
        return self._NaN.get(self.cls)

    @property
    def NEGATIVE_INFINITY(self):
        return self._NEGATIVE_INFINITY.get(self.cls)

    @property
    def POSITIVE_INFINITY(self):
        return self._POSITIVE_INFINITY.get(self.cls)

    @property
    def SIZE(self):
        return self._SIZE.get(self.cls)

    def new(self, *args):
        if len(args) == 1:
            if isinstance(args[0], six.string_types):
                return self.cons_s(args[0])
            else:
                return self.cons_d(args[0])
        return super(Double, self).new(*args)


class String(Object):
    class_name = 'java.lang.String'

    class Instance(Object.Instance):
        def __init__(self, cls, obj):
            super(String.Instance, self).__init__(cls, obj)
            self.charAt = lambda i, o=obj: cls.charAt(o, i)
            self.compareTo = lambda s, o=obj: cls.compareTo(o, s)
            self.compareToIgnoreCase = lambda s, o=obj: cls.compareToIgnoreCase(o, s)
            self.concat = lambda s, o=obj: cls.concat(o, s)
            self.endsWith = lambda s, o=obj: cls.endsWith(o, s)
            self.length = lambda o=obj: cls.length(o)

        def __len__(self):
            return self.length()

        def __cmp__(self, other):
            return self.compareTo(other.obj)

        def __getitem__(self, i):
            return self.charAt(i)

    def __init__(self, env):
        super(String, self).__init__(env)
        if self.class_name == String.class_name:
            self.cons = self.constructor()
            self.cons_ba = self.constructor('[B')
            self.cons_ca = self.constructor('[C')
            self.cons_s = self.constructor('Ljava/lang/String;')
        self.charAt = self.method('charAt', '(I)C')
        self.compareTo = self.method('compareTo', '(Ljava/lang/String;)I')
        self.compareToIgnoreCase = self.method('compareToIgnoreCase', '(Ljava/lang/String;)I')
        self.concat = self.method('concat', '(Ljava/lang/String;)Ljava/lang/String;')
        self.endsWith = self.method('endsWith', '(Ljava/lang/String;)Z')
        self.length = self.method('length', '()I')

    def new(self, *args):
        return super(String, self).new(*args)


class System(Object):
    """
    Wrapper for java.lang.System.

    This is useful for testing and checking Java system properties.
    """
    class_name = 'java.lang.System'

    def __init__(self, env):
        super(System, self).__init__(env)
        self.getProperty = self.static_method(
            'getProperty',
            '(Ljava/lang/String;)Ljava/lang/String;'
        )
        self._out = self.static_field('out', 'Ljava/io/PrintStream;')

    @property
    def out(self):
        return self._out.get(self.cls)

    @out.setter
    def out(self, value):
        self._out.set(self.cls, value)
