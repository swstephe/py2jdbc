# -*- coding: utf8 -*-
import logging
import six
import py2jdbc.jni
import py2jdbc.sig

log = logging.getLogger(__name__)


class Register(type):
    """
    Metaclass to register classes for loading when ThreadEnv is created.
    """
    registry = []

    def __new__(mcs, clsname, bases, attrs):
        newclass = super(Register, mcs).__new__(mcs, clsname, bases, attrs)
        class_name = getattr(newclass, 'class_name')
        if class_name:
            mcs.registry.append(newclass)
        return newclass


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
        self.env = py2jdbc.jni.get_env(**kwargs)
        self.classes = {}
        self.exceptions = (
            'java.sql.SQLException',
            'java.lang.Exception',
            'java.lang.Throwable'
        )
        for cls in JClass.registry:
            cls(self)

    @classmethod
    def instance(cls, **kwargs):
        """
        Make this a weak singleton.  Call this method to grab the current ThreadEnv
        object for the thread, or create one if the current thread doesn't have one.

        The instance will have all the JClass subclass wrappers already loaded
        against the current py2jdbc.jni.JNIEnv.

        :param kwargs: py2jdbc.jni.JNIEnv.get_env arguments, (like classpath, verbose, etc.)
        :return: the current thread's ThreadEnv object
        """
        return cls(**kwargs)

    def exception(self, e):
        """
        Utility to check if an exception was thrown.  If so, it automatically
        wraps it in a wrap.JavaException object.

        :raises: JavaException if an exception occurred.
        """
        for ec in self.exceptions:
            e_class = self.classes.get(ec)
            if e_class and self.env.IsInstanceOf(e.throwable, e_class.cls):
                return e_class(e.throwable)
        return e

    def get(self, arg):
        return self.classes[arg]


def get_env(**kwargs):
    """
    Alias for singleton creator function, which attaches/creates a ThreadEnv
    for the current thread.

    :param kwargs: py2jdbc.jni.JNIEnv.get_env arguments, (classpath, verbose, etc.)
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
        A convenience link back to the py2jdbc.jni.JNIEnv instance.
        :return: the current thread's py2jdbc.jni.JNIEnv instance
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
        try:
            self.fid = self.env.GetFieldID(cls.cls, name, signature)
            self.restype = next(py2jdbc.sig.type_signature(self.env, signature))
        except py2jdbc.jni.JavaException as e:
            raise self.cls.env.exception(e)

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

        A JMethod is created when the class is loaded, then attached to instances
        as they are wrapped.

        :param cls: a JClass wrapper subclass
        :param name: the name of the method.
        :param signature: the Java signature of the method
        :raises: RuntimeError if the method was not found.
        """
        super(JMethod, self).__init__(cls, name, signature)
        try:
            self.mid = self.env.GetMethodID(cls.cls, name, signature)
            self.argtypes, self.restype = self.get_signature(signature)
        except py2jdbc.jni.JavaException as e:
            raise self.cls.env.exception(e)

    def get_signature(self, signature):
        """
        Overridable function that returns handlers for result and argument
        types for this method.

        :param signature: method signature
        :return: argtypes and restype from signature
        """
        return py2jdbc.sig.method_signature(self.env, signature)

    def __call__(self, obj, *args):
        """
        Call the method on the object instance with Python arguments.

        :param obj: the object instance
        :param args: Python value arguments
        :return: the result value, or None for Void methods.
        """
        try:
            return self.restype.call(obj, self.mid, self.argtypes, *args)
        except py2jdbc.jni.JavaException as e:
            raise self.cls.env.exception(e)


class JConstructor(JMethod):
    """
    Wraps a java object constructor method
    """
    def __init__(self, cls, signature):
        """
        Create an instance of a constructor.
        When called, it will craeate an object of the class.

        :param cls: a JClass wrapper subclass
        :param signature: the Java signature of the constructor, (just the arguments)
        :raises: RuntimeError if no matching constructor was found
        """
        super(JConstructor, self).__init__(cls, '<init>', '({})V'.format(signature))

    def get_signature(self, signature):
        """
        Function that returns handlers for result and argument
        types for this constructor.

        :param signature: the full singature
        :return: argtypes and restype
        """
        return py2jdbc.sig.constructor_signature(
            self.env,
            self.cls.class_name,
            signature[1:-2]
        )

    def __call__(self, *args):
        """
        Call the constructor and create an object instance with Python arguments.

        :param args: Python value arguments
        :return: the resulting object instance handle
        """
        try:
            obj = self.restype.new(self.cls.cls, self.mid, self.argtypes, *args)
            return self.cls(obj)
        except py2jdbc.jni.JavaException as e:
            raise self.cls.env.exception(e)


class JStaticField(JBase):
    """
    Wraps a java class static field
    """
    def __init__(self, cls, name, signature):
        super(JStaticField, self).__init__(cls, name, signature)
        try:
            self.fid = self.env.GetStaticFieldID(cls.cls, name, signature)
            self.restype = next(py2jdbc.sig.type_signature(self.env, signature))
        except py2jdbc.jni.JavaException as e:
            raise self.cls.env.exception(e)

    def get(self, cls):
        try:
            return self.restype.get_static(cls, self.fid)
        except py2jdbc.jni.JavaException as e:
            raise self.cls.env.exception(e)

    def set(self, cls, value):
        try:
            self.restype.set_static(cls, self.fid, value)
        except py2jdbc.jni.JavaException as e:
            raise self.cls.env.exception(e)


class JStaticMethod(JBase):
    """
    Wraps a java class static method
    """
    def __init__(self, cls, name, signature):
        """
        Construct a JMethod instance.

        A JStaticMethod is created when the class is loaded, then attached to instances
        as they are wrapped.

        :param cls: a JClass wrapper subclass
        :param name: the name of the method.
        :param signature: the Java signature of the method
        :raises: RuntimeError if the method was not found.
        """
        super(JStaticMethod, self).__init__(cls, name, signature)
        self.mid = self.env.GetStaticMethodID(self.cls.cls, name, signature)
        self.argtypes, self.restype = py2jdbc.sig.method_signature(self.env, signature)

    def __call__(self, *args):
        """
        Call the static method on the class with Python arguments.

        :param args: Python value arguments
        :return: the result value, or None for Void static methods.
        """
        try:
            value = self.restype.call_static(self.cls.cls, self.mid, self.argtypes, *args)
            self.restype.release(value)
            return value
        except py2jdbc.jni.JavaException as e:
            raise self.cls.env.exception(e)


class JClass(six.with_metaclass(Register)):
    """
    Wraps a Java class.

    This is the main base class for all other wrapper classes.
    Wrapper classes should call 'field', 'static_field', 'method', 'static_method',
    to describe the desired items that you want to access.
    """
    class_name = None

    def __init__(self, env):
        """
        Create base of Java class instance for the current thread's local environment.

        :param env: the current thread's local environment
        """
        self.env = env
        try:
            self.cls = env.env.FindClass(self.class_name)
            self.env.classes[self.class_name] = self
        except py2jdbc.jni.JavaException as e:
            raise self.env.exception(e)

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
        Link a JStaticField declaration to the current class

        :param name: the static field name
        :param signature: the static field signature
        :return: the static field's value
        """
        return JStaticField(self, name, signature)

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

    def constructor(self, signature=''):
        """
        Link a JConstructor declaration to the current class.

        :param signature: the constructor signature (just args)
        :return: the constructor handler wrapper
        """
        return JConstructor(self, signature)
