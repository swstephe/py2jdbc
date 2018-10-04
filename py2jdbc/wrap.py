# -*- coding: utf8 -*-
import logging
import threading
from py2jdbc import jni
from py2jdbc import sig


log = logging.getLogger(__name__)
tlocal = threading.local()


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

    def __del__(self):
        for cls in self.classes:
            del cls

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
        jni.check_exception(self.env)


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

        A JMethod is created when the class is loaded, then attached to instances
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
        self.argtypes, self.restype = self.get_signature(signature)

    def get_signature(self, signature):
        """
        Overridable function that returns handlers for result and argument
        types for this method.

        :param signature: method signature
        :return: argtypes and restype from signature
        """
        return sig.method_signature(self.env, signature)

    def __call__(self, obj, *args):
        """
        Call the method on the object instance with Python arguments.

        :param obj: the object instance
        :param args: Python value arguments
        :return: the result value, or None for Void methods.
        """
        value = self.restype.call(obj, self.mid, self.argtypes, *args)
        self.cls.env.check_exception()
        return value


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
        return sig.constructor_signature(
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
        obj = self.restype.new(self.cls.cls, self.mid, self.argtypes, *args)
        self.cls.env.check_exception()
        return self.cls(obj)


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
        value = self.restype.call_static(self.cls.cls, self.mid, self.argtypes, *args)
        self.restype.release(value)
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
        self.env.classes[class_name] = self

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

    def constructor(self, signature=''):
        """
        Link a JConstructor declaration to the current class.

        :param signature: the constructor signature (just args)
        :return: the constructor handler wrapper
        """
        return JConstructor(self, signature)
