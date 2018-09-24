# -*- coding: utf8 -*-
import inspect
import logging
import sys
import threading
from . import jni
from . import sig


log = logging.getLogger(__name__)
tlocal = threading.local()


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
        throwable = env.classes['java.lang.Throwable'](e.throwable)
        ste = env.classes['java.lang.StackTraceElement']
        message = ['Exception in thread "main" {}'.format(throwable.getMessage())]
        log.info('message=%r', message)
        stack_trace = throwable.getStackTrace()
        for elem in stack_trace:
            name = ste(elem).getClassName()
            log.info("name=%r", name)
            message.append(name)
        raise cls('\n    at '.join(message))

    def __init__(self, message):
        self.message = message


def class_predicate(member):
    """
    Utility function to determine if a class defined in this module
    is a JClass wrapper subclass.

    :param member: a module item, (variable, function, class, etc.)
    :return: True if item is a subclass of JClass
    """
    return (
        inspect.isclass(member)
        and member.__module__ == __name__
        and issubclass(member, JClass)
        and member != JClass
    )


class ThreadEnv(object):
    """
    Wrapper for jni.JNIEnv for the current thread.
    """
    def __init__(self, **kwargs):
        """
        Automatically attach/create JNI environment, then run
        through module JClass subclasses, construct and register them.

        :param kwargs: jni.JNIEnv.get_env arguments, (like classpath, verbose, etc.)
        """
        self.env = jni.get_env(**kwargs)
        self.classes = {}
        for k, v in inspect.getmembers(sys.modules[__name__], class_predicate):
            cls = v(self)
            self.classes[cls.class_name] = cls

    @classmethod
    def instance(cls, **kwargs):
        """
        Make this a weak singleton.  Call this method to grab the current ThreadEnv
        object for the thread, or create one if the current thread doesn't have one.

        The instance will have all the JClass subclass wrappers already loaded
        against the current jni.JNIEnv.

        :param kwargs: jni.JNIEnv.get_env arguments, (like classpath, verbose, etc.)
        :return: the current thread's ThreadEnv object
        """
        global tlocal
        if not hasattr(tlocal, 'env'):
            tlocal.env = cls(**kwargs)
        return tlocal.env

    def check_exception(self):
        """
        Utility to check if an exception was thrown.  If so, it automatically
        wraps it in a wrap.JavaException object.

        :raises: JavaException if an exception occurred.
        """
        try:
            jni.check_exception(self.env)
        except jni.JavaException as e:
            JavaException.from_jni_exception(self.env, e)


def get_env(**kwargs):
    """
    Alias for singleton creator function, which attaches/creates a ThreadEnv
    for the current thread.

    :param kwargs: jni.JNIEnv.get_env arguments, (classpath, verbose, etc.)
    :return: the current thread's ThreadEnv instance.
    """
    return ThreadEnv.instance(**kwargs)


class JBase(object):
    """
    Common structure for fields and methods.
    """
    def __init__(self, cls, name, signature):
        """
        Construct a field or method instance.
        Basically just stores the arguments.

        :param cls: a JClass wrapper subclass
        :param name: the name of the field or method
        :param signature: the Java signature of the field or method
        """
        self.cls = cls
        self.name = name
        self.signature = signature

    @property
    def env(self):
        """
        A convenience link back to the jni.JNIEnv instance.
        :return: the current thread's jni.JNIEnv instance
        """
        return self.cls.env.env


class JField(JBase):
    """
    Wraps a java object instance field, which can be converted to a Python property.
    """
    def __init__(self, cls, name, signature):
        """
        Construct a JField instance.

        A JField is created when the class is loaded, then attached to instances
        as they are wrapped.

        :param cls: a JClass wrapper subclass
        :param name: the name of the field.
        :param signature: the Java signature of the field
        :raises: RuntimeError if the field was not found.
        """
        super(JField, self).__init__(cls, name, signature)
        self.fid = self.env.GetFieldID(cls.cls, name, signature)
        if self.fid is None:
            raise RuntimeError("Failed to find field id for {}.{}/{}".format(
                cls.class_name,
                name,
                signature
            ))
        self.restype = next(sig.type_signature(self.env, self.signature))
        self.cls.env.check_exception()

    def get(self, obj):
        """
        Retrieve the value of a field for the current object instance

        :param obj: the object instance
        :return: the field value, converted for Python
        """
        return self.restype.get(obj, self.fid)

    def set(self, obj, value):
        """
        Set the value of a field for the current object instance

        :param obj: the object instance
        :param value: the value to assign to the object field
        """
        self.restype.set(obj, self.fid, value)


class JMethod(JBase):
    """
    Wraps a java object instance method
    """
    def __init__(self, cls, name, signature):
        """
        Construct a JMethod instance.

        A JField is created when the class is loaded, then attached to instances
        as they are wrapped.

        :param cls: a JClass wrapper subclass
        :param name: the name of the method.
        :param signature: the Java signature of the method
        :raises: RuntimeError if the method was not found.
        """
        super(JMethod, self).__init__(cls, name, signature)
        self.mid = self.env.GetMethodID(cls.cls, name, signature)
        self.cls.env.check_exception()
        if self.mid is None:
            raise RuntimeError("Failed to find method id for {}.{}/{}".format(
                cls.name,
                name,
                signature
            ))
        self.argtypes, self.restype = sig.method_signature(self.env, signature)

    def __call__(self, obj, *args):
        """
        Call the method on the object instance with Python arguments.

        :param obj: the object instance
        :param args: Python value arguments
        :return: the result value, or None for Void methods.
        """
        try:
            value = self.restype.call(obj, self.mid, self.argtypes, *args)
            self.cls.env.check_exception()
        except jni.JavaException as e:
            raise JavaException.from_jni_exception(self.cls.env, e)
        return value


class JStaticMethod(JBase):
    """
    Wraps a java class static method
    """
    def __init__(self, cls, name, signature):
        """
        Construct a JMethod instance.

        A JField is created when the class is loaded, then attached to instances
        as they are wrapped.

        :param cls: a JClass wrapper subclass
        :param name: the name of the method.
        :param signature: the Java signature of the method
        :raises: RuntimeError if the method was not found.
        """
        super(JStaticMethod, self).__init__(cls, name, signature)
        self.mid = self.env.GetStaticMethodID(self.cls.cls, name, signature)
        if self.mid is None:
            raise RuntimeError("Failed to find static method id for {}.{}/{}".format(
                self.cls.name, name, signature))
        self.argtypes, self.restype = sig.method_signature(self.env, signature)

    def __call__(self, *args):
        """
        Call the static method on the class with Python arguments.

        :param args: Python value arguments
        :return: the result value, or None for Void static methods.
        """
        try:
            value = self.restype.call_static(self.cls.cls, self.mid, self.argtypes, *args)
            self.restype.release(value)
        except jni.JavaException as e:
            raise JavaException.from_jni_exception(self.cls.env, e)
        return value


class JClass(object):
    """
    Wraps a Java class.

    This is the main base class for all other wrapper classes.
    Wrapper classes should call 'field', 'static_field', 'method', 'static_method',
    to describe the desired items that you want to access.
    """
    def __init__(self, env, class_name):
        """
        Create base of Java class instance for the current thread's local environment.

        :param env: the current thread's local environment
        :param class_name: the Java class name, either java.lang.String or java/lang/String
        """
        self.env = env
        self.class_name = class_name
        self.cls = env.env.FindClass(self.class_name)
        self.env.check_exception()

    def field(self, name, signature):
        """
        Link a JField declaration to the current class.

        :param name: the field name
        :param signature: the field signature
        :return: the field handler wrapper
        """
        return JField(self, name, signature)

    def static_field(self, name, signature):
        """
        Assuming static fields are final, return the current value of the static field.

        :param name: the static field name
        :param signature: the static field signature
        :return: the static field's value
        """
        fid = self.env.env.GetStaticFieldID(self.cls, name, signature)
        if fid is None:
            raise RuntimeError("Failed to find static field id for {}.{}/{}".format(
                self.cls.class_name,
                name,
                signature
            ))
        restype = next(sig.type_signature(self.env.env, signature))
        self.env.check_exception()
        return restype.get_static(self.cls, fid)

    def method(self, name, signature):
        """
        Link a JMethod declaration to the current class.

        :param name: the method name
        :param signature: the method signature
        :return: the method handler wrapper
        """
        return JMethod(self, name, signature)

    def static_method(self, name, signature):
        """
        Link a JStaticMethod declaration to the current class.

        :param name: the static method name
        :param signature: the static method signature
        :return: the static method handler wrapper
        """
        return JStaticMethod(self, name, signature)

    def __call__(self, obj):
        """
        By convention, we create instances of classes by calling the
        class wrapper.  So something like this:

        Connection = ThreadEnv.classes['java.sql.Connection']
        obj = ... something that returns a jobject
        wrapped = Connection(obj)

        :param obj: first argument is the jobject value
        :return: an object instance from the jobject value
        """
        return Object.Instance(self, obj)


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
            self.toString = lambda o=obj: cls.toString(o)

        @property
        def env(self):
            return self.cls.env

    def __init__(self, env, class_name='java.lang.Object'):
        super(Object, self).__init__(env, class_name=class_name)
        self.toString = self.method('toString', '()Ljava/lang/String;')

    def __call__(self, *args):
        """
        Given an object instance (jni.jobject), wrap it in this
        class' wrapper class.

        :param obj: the object instance
        :return: this class' Instance object
        """
        return Object.Instance(self, *args)


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

    def __init__(self, env, class_name='java.lang.Class'):
        super(Class, self).__init__(env, class_name=class_name)
        self._forName = self.static_method('forName', '(Ljava/lang/String;)Ljava/lang/Class;')
        self.getName = self.method('getName', '()Ljava/lang/String;')

    def __call__(self, *args):
        return Class.Instance(self, *args)

    def forName(self, name):
        """
        :param name:
        :return: a Class.Instance wrapper for the result of forName
        """
        return self(self._forName(name))


class Number(Object):
    """
    Wrapper for java.lang.Number
    """
    def __init__(self, env, class_name='java.lang.Number'):
        super(Number, self).__init__(env, class_name=class_name)


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


class BigDecimal(Number):
    """
    Wrapper for java.lang.BigDecimal java class
    """
    def __init__(self, env, class_name='java.math.BigDecimal'):
        super(BigDecimal, self).__init__(env, class_name=class_name)


class Calendar(Object):
    """
    Wrapper for java.util.Calendar java class
    """
    class Instance(Object.Instance):
        def __init__(self, cls, obj):
            super(Calendar.Instance, self).__init__(cls, obj)
            # self.get = lambda o=obj, *a: cls.get(o, *a)
            # self.getTimeInMillis = lambda o=obj: cls.getTimeInMillis(o)
            # self._set2 = lambda o=obj, *a: cls._set2(o, *a)
            # self._set3 = lambda o=obj, *a: cls._set3(o, *a)
            # self._set5 = lambda o=obj, *a: cls._set5(o, *a)
            # self._set6 = lambda o=obj, *a: cls._set6(o, *a)

        def set(self, *args):
            if len(args) == 2:
                return self._set2(*args)
            if len(args) == 3:
                return self._set3(*args)
            if len(args) == 5:
                return self._set5(*args)
            if len(args) == 6:
                return self._set6(*args)
            raise ValueError("incorrect number of arguments: %d" % len(args))

    def __init__(self, env, class_name='java.util.Calendar'):
        super(Calendar, self).__init__(env, class_name=class_name)
        self.ALL_STYLES = self.static_field('ALL_STYLES', 'I')
        self.AM = self.static_field('AM', 'I')
        self.AM_PM = self.static_field('AM_PM', 'I')
        self.APRIL = self.static_field('APRIL', 'I')
        self.AUGUST = self.static_field('AUGUST', 'I')
        self.DATE = self.static_field('DATE', 'I')
        self.DAY_OF_MONTH = self.static_field('DAY_OF_MONTH', 'I')
        self.DAY_OF_WEEK = self.static_field('DAY_OF_WEEK', 'I')
        self.DAY_OF_WEEK_IN_MONTH = self.static_field('DAY_OF_WEEK_IN_MONTH', 'I')
        self.DAY_OF_YEAR = self.static_field('DAY_OF_YEAR', 'I')
        self.DECEMBER = self.static_field('DECEMBER', 'I')
        self.DST_OFFSET = self.static_field('DST_OFFSET', 'I')
        self.ERA = self.static_field('ERA', 'I')
        self.FEBRUARY = self.static_field('FEBRUARY', 'I')
        self.FIELD_COUNT = self.static_field('FIELD_COUNT', 'I')
        self.FRIDAY = self.static_field('FRIDAY', 'I')
        self.HOUR = self.static_field('HOUR', 'I')
        self.HOUR_OF_DAY = self.static_field('HOUR_OF_DAY', 'I')
        self.JANUARY = self.static_field('JANUARY', 'I')
        self.JULY = self.static_field('JULY', 'I')
        self.JUNE = self.static_field('JUNE', 'I')
        self.LONG = self.static_field('LONG', 'I')
        self.MARCH = self.static_field('MARCH', 'I')
        self.MAY = self.static_field('MAY', 'I')
        self.MILLISECOND = self.static_field('MILLISECOND', 'I')
        self.MINUTE = self.static_field('MINUTE', 'I')
        self.MONDAY = self.static_field('MONDAY', 'I')
        self.MONTH = self.static_field('MONTH', 'I')
        self.NOVEMBER = self.static_field('NOVEMBER', 'I')
        self.OCTOBER = self.static_field('OCTOBER', 'I')
        self.PM = self.static_field('PM', 'I')
        self.SATURDAY = self.static_field('SATURDAY', 'I')
        self.SEPTEMBER = self.static_field('SEPTEMBER', 'I')
        self.SHORT = self.static_field('SHORT', 'I')
        self.SUNDAY = self.static_field('SUNDAY', 'I')
        self.THURSDAY = self.static_field('THURSDAY', 'I')
        self.TUESDAY = self.static_field('TUESDAY', 'I')
        self.UNDECIMBER = self.static_field('UNDECIMBER', 'I')
        self.WEDNESDAY = self.static_field('WEDNESDAY', 'I')
        self.WEEK_OF_MONTH = self.static_field('WEEK_OF_MONTH', 'I')
        self.WEEK_OF_YEAR = self.static_field('WEEK_OF_YEAR', 'I')
        self.YEAR = self.static_field('YEAR', 'I')
        self.ZONE_OFFSET = self.static_field('ZONE_OFFSET', 'I')
        # self.get = self.method('get', '(I)I')
        # self.getTimeInMillis = self.method('getTimeInMillis', '()L')
        # self._set2 = self.method('set', '(II)V')
        # self._set3 = self.method('set', '(III)V')
        # self._set5 = self.method('set', '(IIIII)V')
        # self._set6 = self.method('set', '(IIIIII)V')
        # self.setTimeInMillis = self.method('setTimeInMillis', '(L)V')

    def __call__(self, *args):
        return Calendar.Instance(self, *args)


class Connection(Object):
    """
    Wrapper for java.sql.Connection java class
    """
    class Instance(Object.Instance):
        def __init__(self, cls, obj):
            super(Connection.Instance, self).__init__(cls, obj)
            self.createStatement = lambda o=obj: cls.createStatement(o)
            self.close = lambda o=obj: cls.close(o)
            self.commit = lambda o=obj: cls.commit(o)
            self.getAutoCommit = lambda o=obj: cls.getAutoCommit(o)
            self.prepareStatement = lambda sql, o=obj: cls.prepareStatement(o, sql)
            self.rollback = lambda o=obj: cls.rollback(o)
            self.setAutoCommit = lambda v, o=obj: cls.setAutoCommit(o, v)

    def __init__(self, env, class_name='java.sql.Connection'):
        super(Connection, self).__init__(env, class_name=class_name)
        self.createStatement = self.method('createStatement', '()Ljava/sql/Statement;')
        self.close = self.method('close', '()V')
        self.commit = self.method('commit', '()V')
        self.getAutoCommit = self.method('getAutoCommit', '()Z')
        self.prepareStatement = self.method(
            'prepareStatement',
            '(Ljava/lang/String;)Ljava/sql/PreparedStatement;'
        )
        self.rollback = self.method('rollback', '()V')
        self.setAutoCommit = self.method('setAutoCommit', '(Z)V')

    def __call__(self, *args):
        return Connection.Instance(self, *args)


class Date(Object):
    """
    Wrapper for java.util.Date java class
    """
    def __init__(self, env, class_name='java.util.Date'):
        super(Date, self).__init__(env, class_name=class_name)



class DriverManager(Object):
    """
    Wrapper for java.sql.DriverManager java class
    """
    def __init__(self, env, class_name='java.sql.DriverManager'):
        super(DriverManager, self).__init__(env, class_name=class_name)
        self.getConnection1 = self.static_method(
            'getConnection',
            '(Ljava/lang/String;)Ljava/sql/Connection;'
        )
        self.getConnection3 = self.static_method(
            'getConnection',
            '(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/sql/Connection;'
        )
        self._getDrivers = self.static_method('getDrivers', '()Ljava/util/Enumeration;')

    def getConnection(self, *args):
        """
        Create a connection to a JDBC database.  This links to 2 overloaded
        forms, one with 1 argument and one with 3.  It checks the number of
        arguments given and calls the approprate Java method.

        :param args: 1 or 3 connection string arguments
        :return: a wrapped java.sql.Connection jobject
        """
        try:
            if len(args) == 1:
                conn = self.getConnection1(*args)
            elif len(args) == 3:
                conn = self.getConnection3(*args)
            else:
                raise RuntimeError("wrong number of arguments: %d" % len(args))
        except jni.JavaException as e:
            raise JavaException.from_jni_exception(self.env, e)
        return self.env.classes['java.sql.Connection'](conn)

    def getDrivers(self):
        """
        Fetch a list of drivers, automatically wrap
        in Enumeration and Driver wrappers.

        :return: a generator that produces a list of JDBC drivers
        """
        enumeration = self.env.classes['java.lang.Enumeration']
        driver = self.env.classes['java.sql.Driver']
        drivers = self.getDrivers()
        return (driver(obj) for obj in enumeration(drivers))



class Driver(Object):
    """
    Wrapper for java.sql.Driver java class
    """
    class Instance(Object.Instance):
        """
        Wrapper for java.sql.Driver object instance
        """
        def __init__(self, cls, obj):
            super(Driver.Instance, self).__init__(cls, obj)
            self.acceptsURL = lambda url, o=obj: cls.acceptsURL(o, url)

    def __init__(self, env, class_name='java.sql.Driver'):
        super(Driver, self).__init__(env, class_name=class_name)
        self.acceptsURL = self.method('acceptsURL', '(Ljava/lang/String;)Z')

    def __call__(self, obj):
        return Driver.Instance(self, obj)


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


class PreparedStatement(Object):
    """
    Wrapper for java.sql.PreparedStatement java class.
    """
    class Instance(Object.Instance):
        """
        Wrapper for java.sql.PreparedStatement object instance
        """
        def __init__(self, cls, obj):
            super(PreparedStatement.Instance, self).__init__(cls, obj)
            self.addBatch = lambda o=obj: cls.addBatch(o)
            self.clearParameters = lambda o=obj: cls.clearParameters(o)
            self.close = lambda o=obj: cls.close(o)
            self.execute = lambda o=obj: cls.execute(o)
            self.executeBatch = lambda o=obj: cls.executeBatch(o)
            self.getResultSet = lambda o=obj: cls.getResultSet(o)
            self.getUpdateCount = lambda o=obj: cls.getUpdateCount(o)
            self.setByte = lambda i, v, o=obj: cls.setByte(o, i, v)
            self.setDouble = lambda i, v, o=obj: cls.setDouble(o, i, v)
            self.setFloat = lambda i, v, o=obj: cls.setFloat(o, i, v)
            self.setShort = lambda i, v, o=obj: cls.setShort(o, i, v)
            self.setInt = lambda i, v, o=obj: cls.setInt(o, i, v)
            self.setNull = lambda i, v, o=obj: cls.setNull(o, i, v)
            self.setString = lambda i, v, o=obj: cls.setString(o, i, v)

    def __init__(self, env, class_name='java.sql.PreparedStatement'):
        super(PreparedStatement, self).__init__(env, class_name=class_name)
        self.addBatch = self.method('addBatch', '()V')
        self.clearParameters = self.method('clearParameters', '()V')
        self.close = self.method('close', '()V')
        self.execute = self.method('execute', '()Z')
        self.executeBatch = self.method('executeBatch', '()[I')
        self.getResultSet = self.method('getResultSet', '()Ljava/sql/ResultSet;')
        self.getUpdateCount = self.method('getUpdateCount', '()I')
        self.setByte = self.method('setByte', '(IB)V')
        self.setDouble = self.method('setDouble', '(ID)V')
        self.setFloat = self.method('setFloat', '(IF)V')
        self.setShort = self.method('setShort', '(IS)V')
        self.setInt = self.method('setInt', '(II)V')
        self.setNull = self.method('setNull', '(II)V')
        self.setString = self.method('setString', '(ILjava/lang/String;)V')

    def __call__(self, obj):
        return PreparedStatement.Instance(self, obj)


class ResultSet(Object):
    """
    Wrapper for java.sql.ResultSet java class
    """
    class Instance(Object.Instance):
        """
        Wrapper for java.sql.ResultSet object instance.

        It implements a Python iterator for iteration over rows.
        """
        def __init__(self, cls, obj):
            super(ResultSet.Instance, self).__init__(cls, obj)
            self.close = lambda o=obj: cls.close(o)
            self.getInt = lambda i, o=obj: cls.getInt(o, i)
            self.getMetaData = lambda o=obj: cls.getMetaData(o)
            self.getString = lambda i, o=obj: cls.getString(o, i)
            self._next = lambda o=obj: cls.next(o)
            self.wasNull = lambda o=obj: cls.wasNull(o)

        def __iter__(self):
            return self

        def next(self):
            row = self._next()
            if not row:
                raise StopIteration()
            return row

    def __init__(self, env, class_name='java.sql.ResultSet'):
        super(ResultSet, self).__init__(env, class_name=class_name)
        self.close = self.method('close', '()V')
        self.getInt = self.method('getInt', '(I)I')
        self.getMetaData = self.method('getMetaData', '()Ljava/sql/ResultSetMetaData;')
        self.getString = self.method('getString', '(I)Ljava/lang/String;')
        self.next = self.method('next', '()Z')
        self.wasNull = self.method('wasNull', '()Z')

    def __call__(self, obj):
        return ResultSet.Instance(self, obj)


class ResultSetMetaData(Object):
    """
    Wrapper for java.sql.ResultSetMetaData java class
    """
    class Instance(Object.Instance):
        """
        Wrapper for java.sql.ResultSetMetaData object instance
        """
        def __init__(self, cls, obj):
            super(ResultSetMetaData.Instance, self).__init__(cls, obj)
            self.getColumnCount = lambda o=obj: cls.getColumnCount(o)
            self.getColumnDisplaySize = lambda i, o=obj: cls.getColumnDisplaySize(o, i)
            self.getColumnName = lambda i, o=obj: cls.getColumnName(o, i)
            self.getColumnType = lambda i, o=obj: cls.getColumnType(o, i)
            self.getColumnTypeName = lambda i, o=obj: cls.getColumnTypeName(o, i)
            self.getPrecision = lambda i, o=obj: cls.getPrecision(o, i)
            self.getScale = lambda i, o=obj: cls.getScale(o, i)
            self.isNullable = lambda i, o=obj: cls.isNullable(o, i)

    def __init__(self, env, class_name='java.sql.ResultSetMetaData'):
        super(ResultSetMetaData, self).__init__(env, class_name=class_name)
        self.getColumnCount = self.method('getColumnCount', '()I')
        self.getColumnDisplaySize = self.method('getColumnDisplaySize', '(I)I')
        self.getColumnName = self.method('getColumnName', '(I)Ljava/lang/String;')
        self.getColumnType = self.method('getColumnType', '(I)I')
        self.getColumnTypeName = self.method('getColumnTypeName', '(I)Ljava/lang/String;')
        self.getPrecision = self.method('getPrecision', '(I)I')
        self.getScale = self.method('getScale', '(I)I')
        self.isNullable = self.method('isNullable', '(I)I')

    def __call__(self, obj):
        return ResultSetMetaData.Instance(self, obj)


class SQLDate(Date):
    """
    Wrapper for java.util.Date java class
    """
    class Instance(Object.Instance):
        def __init__(self, cls, obj):
            super(SQLDate.Instance, self).__init__(cls, obj)

    def __init__(self, env, class_name='java.util.Date'):
        super(SQLDate, self).__init__(env, class_name=class_name)
        self._init = self.method('<init>', '(III)V')
        # self.valueOf = self.static_method('valueOf', '(Ljava/lang/String;)Ljava/sql/Date;')

    def __call__(self, year, month, day):
        return SQLDate.Instance(self._init(year, month, day))


class Statement(Object):
    """
    Wrapper for java.sql.Statement java class
    """
    class Instance(Object.Instance):
        """
        Wrapper for java.sql.Statement object instance
        """
        def __init__(self, cls, obj):
            super(Statement.Instance, self).__init__(cls, obj)
            self.addBatch = lambda s, o=obj: cls.addBatch(o, s)
            self.executeQuery = lambda s, o=obj: cls.executeQuery(o, s)
            self.executeUpdate = lambda s, o=obj: cls.executeUpdate(o, s)
            self.setQueryTimeout = lambda v, o=obj: cls.setQueryTimeout(o, v)

    def __init__(self, env, class_name='java.sql.Statement'):
        super(Statement, self).__init__(env, class_name=class_name)
        self.addBatch = self.method('addBatch', '(Ljava/lang/String;)V')
        self.executeQuery = self.method(
            'executeQuery',
            '(Ljava/lang/String;)Ljava/sql/ResultSet;'
        )
        self.executeUpdate = self.method('executeUpdate', '(Ljava/lang/String;)I')
        self.setQueryTimeout = self.method('setQueryTimeout', '(I)V')

    def __call__(self, obj):
        return Statement.Instance(self, obj)


class Time(Object):
    """
    Wrapper for java.sql.Time java class
    """
    def __init__(self, env, class_name='java.sql.Time'):
        super(Time, self).__init__(env, class_name=class_name)


class Timestamp(Object):
    """
    Wrapper for java.sql.Timestamp java class
    """
    def __init__(self, env, class_name='java.sql.Timestamp'):
        super(Timestamp, self).__init__(env, class_name=class_name)


class Types(Object):
    """
    Wrapper for java.sql.Types java class.

    This is basically just a set of static fields, so it
    really just loads the values for each static field.
    """
    def __init__(self, env, class_name='java.sql.Types'):
        super(Types, self).__init__(env, class_name=class_name)
        self.ARRAY = self.static_field('ARRAY', 'I')
        self.BIGINT = self.static_field('BIGINT', 'I')
        self.BINARY = self.static_field('BINARY', 'I')
        self.BIT = self.static_field('BIT', 'I')
        self.BLOB = self.static_field('BLOB', 'I')
        self.BOOLEAN = self.static_field('BOOLEAN', 'I')
        self.CHAR = self.static_field('CHAR', 'I')
        self.CLOB = self.static_field('CLOB', 'I')
        self.DATALINK = self.static_field('DATALINK', 'I')
        self.DATE = self.static_field('DATE', 'I')
        self.DECIMAL = self.static_field('DECIMAL', 'I')
        self.DISTINCT = self.static_field('DISTINCT', 'I')
        self.DOUBLE = self.static_field('DOUBLE', 'I')
        self.FLOAT = self.static_field('FLOAT', 'I')
        self.INTEGER = self.static_field('INTEGER', 'I')
        self.JAVA_OBJECT = self.static_field('JAVA_OBJECT', 'I')
        self.LONGVARCHAR = self.static_field('LONGNVARCHAR', 'I')
        self.LONGVARBINARY = self.static_field('LONGVARBINARY', 'I')
        self.LONGVARCHAR = self.static_field('LONGVARCHAR', 'I')
        self.NCHAR = self.static_field('NCHAR', 'I')
        self.NCLOB = self.static_field('NCLOB', 'I')
        self.NULL = self.static_field('NULL', 'I')
        self.NUMERIC = self.static_field('NUMERIC', 'I')
        self.NVARCHAR = self.static_field('NVARCHAR', 'I')
        self.OTHER = self.static_field('OTHER', 'I')
        self.REAL = self.static_field('REAL', 'I')
        self.REF = self.static_field('REF', 'I')
        self.REF_CURSOR = self.static_field('REF_CURSOR', 'I')
        self.ROWID = self.static_field('ROWID', 'I')
        self.SMALLINT = self.static_field('SMALLINT', 'I')
        self.SQLXML = self.static_field('SQLXML', 'I')
        self.STRUCT = self.static_field('STRUCT', 'I')
        self.TIME = self.static_field('TIME', 'I')
        self.TIME_WITH_TIMEZONE = self.static_field('TIME_WITH_TIMEZONE', 'I')
        self.TIMESTAMP = self.static_field('TIMESTAMP', 'I')
        self.TIMESTAMP_WITH_TIMEZONE = self.static_field('TIMESTAMP_WITH_TIMEZONE', 'I')
        self.TINYINT = self.static_field('TINYINT', 'I')
        self.VARBINARY = self.static_field('VARBINARY', 'I')
        self.VARCHAR = self.static_field('VARCHAR', 'I')
