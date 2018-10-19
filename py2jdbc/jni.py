# -*- coding: utf8 -*-
import atexit
import codecs
import logging
import signal
import six

from ctypes import (
    c_void_p, c_char_p,
    c_int8, c_uint8, c_int16, c_uint16, c_int32, c_int64,
    c_float, c_double,
    Structure, Union,
    CDLL, CFUNCTYPE, POINTER,
    byref
)
from py2jdbc.jvm import CP_SEP, find_libjvm, get_classpath
import py2jdbc.mutf8

log = logging.getLogger(__name__)


JNI_FALSE = 0
JNI_TRUE = 1

JNI_OK = 0
JNI_ERR = -1
JNI_EDETACHED = -2
JNI_EVERSION = -3
JNI_ENOMEM = -4
JNI_EEXIST = -5
JNI_EINVAL = -6

JNI_COMMIT = 1
JNI_ABORT = 2

jboolean = c_uint8
jbyte = c_int8
jchar = c_uint16
jshort = c_int16
jint = c_int32
jlong = c_int64
jfloat = c_float
jdouble = c_double
jsize = jint


# noinspection PyPep8Naming
class _jobject(Structure):
    """
    Anonymous structure for target of jobject, jclass, etc...

    This allows me to maintain class hierarchies with other
    object pointers.
    """


_jclass = _jobject
_jthrowable = _jobject
_jstring = _jobject
_jarray = _jobject
_jbooleanArray = _jarray
_jbyteArray = _jarray
_jcharArray = _jarray
_jshortArray = _jarray
_jintArray = _jarray
_jlongArray = _jarray
_jfloatArray = _jarray
_jdoubleArray = _jarray
_jobjectArray = _jarray

jobject = POINTER(_jobject)
jclass = POINTER(_jclass)
jthrowable = POINTER(_jthrowable)
jstring = POINTER(_jstring)
jarray = POINTER(_jarray)
jbooleanArray = POINTER(_jbooleanArray)
jbyteArray = POINTER(_jbyteArray)
jcharArray = POINTER(_jcharArray)
jshortArray = POINTER(_jshortArray)
jintArray = POINTER(_jintArray)
jlongArray = POINTER(_jlongArray)
jfloatArray = POINTER(_jfloatArray)
jdoubleArray = POINTER(_jdoubleArray)
jobjectArray = POINTER(_jobjectArray)

jchar_p = POINTER(jchar)

jweak = jobject

type_codes = (
    ('z', 'boolean'),
    ('b', 'byte'),
    ('c', 'char'),
    ('s', 'short'),
    ('i', 'int'),
    ('j', 'long'),
    ('f', 'float'),
    ('d', 'double'),
    ('l', 'object')
)


# noinspection PyPep8Naming
class jvalue(Union):
    """
    JNI jvalue union type
    """
    _fields_ = tuple((a, globals()['j' + b]) for a, b in type_codes)


jvalue_p = POINTER(jvalue)


# noinspection PyPep8Naming
class _jfieldID(Structure):
    """
    Anonymous target for jfieldID pointers
    """
    pass


jfieldID = POINTER(_jfieldID)


# noinspection PyPep8Naming
class _jmethodID(Structure):
    """
    Anonymous target for jmethodID pointers
    """
    pass


jmethodID = POINTER(_jmethodID)


class JNINativeMethod(Structure):
    """
    Structure which describes a generic pointer to a native function.
    """
    _fields_ = (
        ('name', c_char_p),
        ('signature', c_char_p),
        ('fnPtr', c_void_p)
    )


# noinspection PyPep8Naming,PyClassHasNoInit
class jobjectType:
    """
    Simulate the JNI enum jobjectType.
    """
    JNIInvalidRefType = 0
    JNILocalRefType = 1
    JNIGlobalRefType = 2
    JNIWeakGlobalRefType = 3


def map_fields(*fields):
    """
    Generate `ctypes` type declarations based on a list of strings and function types.

    Entries can either be a string, in which case it is mapped to a simple "void*".
    Otherwise, it should be a 3-entry tuple:
    1. the return type
    2. the function name
    3. the function argument types.
    which will be mapped to a ctypes CFUNCTYPE declaration to enforce type-agreement.

    :param fields: a list of strings and function tuple descriptions
    :return: a generator which returns void* and CFUNCTYPE declarations.
    """
    for field in fields:
        if isinstance(field, six.string_types):
            yield field, c_void_p
        else:
            yield field[1], CFUNCTYPE(field[0], *field[2:])


# noinspection PyPep8Naming
class JNIInvokeInterface_(Structure):
    """
    Anonymous target for VM interface list of function pointers.
    The actual pointer definitions are created later.
    """
    pass


# noinspection PyPep8Naming
class JNINativeInterface_(Structure):
    """
    Anonymous target for JNIEnv interface list of function pointers.
    The actual pointer definitions are created later.
    """
    pass


class JavaException(Exception):
    """
    At this level, return the raw throwable parameters for an exception.
    Wait until "wrap" layer to unroll the exception details into a Python exception.
    """
    def __init__(self, env, throwable):
        self.env = env
        self.throwable = throwable


class NullResultException(Exception):
    """
    A JNI function returned NNULL
    """
    def __init__(self, env, *args):
        self.env = env
        super(NullResultException, self).__init__(*args)


class JavaVM(Structure):
    """
    Wrap VM functions with Python wrapper function calls.
    """
    _fields_ = [('functions', POINTER(JNIInvokeInterface_))]

    def DestroyJavaVM(self):
        """
        Unloads a Java VM and reclaims its resources.

        Any thread, whether attached or not, can invoke this function. If the current thread
        is attached, the VM waits until the current thread is the only non-daemon user-level
        Java thread. If the current thread is not attached, the VM attaches the current thread
        and then waits until the current thread is the only non-daemon user-level thread.

        :return: Returns JNI_OK on success; returns a suitable JNI error code
            (a negative number) on failure.
        """
        return self.functions[0].DestroyJavaVM(self)

    def AttachCurrentThread(self, penv, args):
        """
        Attaches the current thread to a Java VM. Returns a JNI interface pointer in the
        JNIEnv argument.

        Trying to attach a thread that is already attached is a no-op.

        A native thread cannot be attached simultaneously to two Java VMs.

        When a thread is attached to the VM, the context class loader is the bootstrap
        loader.

        :param penv: pointer to the location where the JNI interface pointer of the current
            thread will be placed.
        :param args: can be NULL or a pointer to a JavaVMAttachArgs structure to specify
            additional information:

            The second argument to AttachCurrentThread is always a pointer to JNIEnv. The
            third argument to AttachCurrentThread was reserved, and should be set to NULL.
        :return: Returns JNI_OK on success; returns a suitable JNI error code
            (a negative number) on failure.
        """
        return self.functions[0].AttachCurrentThread(self, penv, args)

    def DetachCurrentThread(self):
        """
        Detaches the current thread from a Java VM. All Java monitors held by this thread
        are released. All Java threads waiting for this thread to die are notified.

        The main thread can be detached from the VM.

        :return: Returns JNI_OK on success; returns a suitable JNI error code (a negative
            number) on failure.
        """
        return self.functions[0].DetachCurrentThread(self)

    def GetEnv(self, penv, version):
        """
        Get the JNIEnv for the current thread

        :param penv: a pointer to the location in which the JNIEnv interface pointer for
                    the current thread will be placed.
        :param version: The requested JNI version.
        :return: If the current thread is not attached to the VM, sets env to NULL, and
            returns JNI_EDETACHED. If the specified version is not supported, sets env
            to NULL, and returns JNI_EVERSION. Otherwise, sets env to the appropriate
            interface, and returns JNI_OK.
        """
        return self.functions[0].GetEnv(self, penv, version)

    def AttachCurrentThreadAsDaemon(self, penv, args):
        """
        Same semantics as AttachCurrentThread, but the newly-created java.lang.Thread
        instance is a daemon.

        If the thread has already been attached via either AttachCurrentThread or
        AttachCurrentThreadAsDaemon, this routine simply sets the value pointed to by
        penv to the JNIEnv of the current thread. In this case neither AttachCurrentThread
        nor this routine have any effect on the daemon status of the thread.

        :param penv: a pointer to the location in which the JNIEnv interface pointer for
                    the current thread will be placed.
        :param args: a pointer to a JavaVMAttachArgs structure.
        :return: Returns JNI_OK on success; returns a suitable JNI error code (a negative
                    number) on failure.
        """
        return self.functions[0].AttachCurrentThreadAsDaemon(self, penv, args)


JavaVM_p = POINTER(JavaVM)


class JNIEnv(Structure):
    """
    Wrap JNIEnv function calls, including some Python symantics.
    See the JNI specifications for functions that don't add anything.
    """
    _fields_ = [('functions', POINTER(JNINativeInterface_))]

    def GetVersion(self):
        """
        Returns the version of the native method interface.

        :return: the major version number in the higher 16 bits and the minor version number
                in the lower 16 bits.
        """
        return self.functions[0].GetVersion(self)

    @property
    def version(self):
        """
        Python utility enhancement, return GetVersion as a "M.N" string.

        :return: A string with the version.
        """
        value = self.GetVersion()
        return '{}.{}'.format(value >> 32, value & 0xffff)

    def DefineClass(self, name, loader, buf, buflen):
        """
        Loads a class from a buffer of raw class data. The buffer containing the raw class
        data is not referenced by the VM after the DefineClass call returns, and it may be
        discarded if desired.

        :param name: the name of the class or interface to be defined.
        :param loader: a class loader assigned to the defined class.
        :param buf: buffer containing the .class file data.
        :param buflen: buffer length.
        :return: Returns a Java class object or NULL if an error occurs.
        """
        return self.functions[0].DefineClass(self, encode(name), loader, buf, buflen)

    def FindClass(self, name):
        """
        Loads a class from locations listed in the java.class.path property.

        Note that this wrapper accepts either java/lang/String or java.lang.String.

        :param name: The class name
        :return: the jclass object pointer
        """
        class_object = self.functions[0].FindClass(self, encode(name.replace('.', '/')))
        self.check_exception()
        if class_object is None:
            raise NullResultException(self, name)
        return class_object

    def FromReflectedMethod(self, method):
        """
        Converts a java.lang.reflect.Method or java.lang.reflect.Constructor object
        to a method ID.

        :param method: the java.lang.reflect.X object
        :return: the methodID
        """
        mid = self.functions[0].FromReflectedMethod(self, method)
        self.check_exception()
        if mid is None:
            raise NullResultException(self, method)
        return mid

    def FromReflectedField(self, field):
        """
        Converts a java.lang.reflect.Field to a field ID.

        :param field: the java.lang.reflect.Field object
        :return: the fieldID
        """
        fid = self.functions[0].FromReflectedField(self, field)
        self.check_exception()
        if fid is None:
            raise NullResultException(self, field)
        return fid

    def ToReflectedMethod(self, clazz, mid, is_static):
        """
        Converts a method ID derived from cls to a java.lang.reflect.Method
        or java.lang.reflect.Constructor object. isStatic must be set to JNI_TRUE
        if the method ID refers to a static field, and JNI_FALSE otherwise.

        :param clazz: the class of the method
        :param mid: the methodID of the method
        :param is_static: JNI_TRUE if the method is static
        :return: the java.lang.reflect.X method object
        """
        obj = self.functions[0].ToReflectedMethod(self, clazz, mid, is_static)
        self.check_exception()
        if obj is None:
            raise NullResultException(self, clazz, mid, is_static)
        return obj

    def GetSuperclass(self, clazz):
        """
        If clazz represents any class other than the class Object, then this function returns
        the object that represents the superclass of the class specified by clazz.

        If clazz specifies the class Object, or clazz represents an interface, this function
        returns NULL.

        :param clazz: a Java class object.
        :return: the superclass of the class represented by clazz, or NULL.
        """
        return self.functions[0].GetSuperclass(self, clazz)

    def IsAssignableFrom(self, clazz1, clazz2):
        """
        Determines whether an object of clazz1 can be safely cast to clazz2.

        :param clazz1: the first class argument.
        :param clazz2: the second class argument.
        :return: True if the class can be cast
        """
        return self.functions[0].IsAssignableFrom(self, clazz1, clazz2)

    def ToReflectedField(self, clazz, fid, is_static):
        """
        Converts a field ID derived from cls to a java.lang.reflect.Field object.
        isStatic must be set to JNI_TRUE if fieldID refers to a static field,
        and JNI_FALSE otherwise.

        :param clazz: the class that owns this field
        :param fid: the fieldID
        :param is_static: whether this field is static
        :return: a java.lang.reflect.Field object or 0 if it fails
        """
        return self.functions[0].ToReflectedField(self, clazz, fid, is_static)

    def Throw(self, obj):
        """
        Causes a java.lang.Throwable object to be thrown.

        :param obj: a java.lang.Throwable object.
        :return: 0 on success; a negative value on failure.
        :raises JavaException on exception
            RuntimeError if exception couldn't be thrown
        """
        result = self.functions[0].Throw(self, obj)
        self.check_exception()
        if result != 0:
            raise RuntimeError("couldn't throw exception")

    def ThrowNew(self, clazz, msg):
        """
        Constructs an exception object from the specified class with the message specified by
        message and causes that exception to be thrown.

        :param clazz: a subclass of java.lang.Throwable.
        :param msg:  the message used to construct the java.lang.Throwable object.
        :return: 0 on success; a negative value on failure.
        """
        return self.functions[0].ThrowNew(self, clazz, encode(msg))

    def ExceptionOccurred(self):
        """
        Determines if an exception is being thrown. The exception stays being thrown until
        either the native code calls ExceptionClear(), or the Java code handles the exception.

        :return: the exception object that is currently in the process of being thrown, or
            None if no exception is currently being thrown.
        """
        return self.functions[0].ExceptionOccurred(self)

    def ExceptionDescribe(self):
        """
        Prints an exception and a backtrace of the stack to a system error-reporting channel,
        such as stderr. This is a convenience routine provided for debugging.
        """
        self.functions[0].ExceptionDescribe(self)

    def ExceptionClear(self):
        """
        Clears any exception that is currently being thrown. If no exception is currently
        being thrown, this routine has no effect.
        """
        self.functions[0].ExceptionClear(self)

    def check_exception(self):
        """
        Utility for checking if an exception occurred, and if so, raise
        a Python exception containing the Throwable object.
        """
        throwable = self.ExceptionOccurred()
        if throwable:
            if log.getEffectiveLevel() == logging.DEBUG:
                self.ExceptionDescribe()
            self.ExceptionClear()
            raise JavaException(self, throwable)

    def FatalError(self, msg):
        """
        Raises a fatal error and does not expect the VM to recover. This function does not
        return.

        :param msg: an error message
        :return:
        """
        self.functions[0].FatalError(self, encode(msg))

    def PushLocalFrame(self, capacity):
        """
        Creates a new local reference frame, in which at least a given number of local
        references can be created.

        :param capacity:
        :return: 0 on success, a negative number
        :raises: OutOfMemoryError
        """
        return self.functions[0].PushLocalFrame(self, capacity)

    def PopLocalFrame(self, result=None):
        """
        Pops off the current local reference frame, frees all the local references.

        Pass None as result if you do not need to return a reference to the previous frame.

        :param result: look for reference from of result object
        :return: local reference in the previous local reference frame
        """
        return self.functions[0].PopLocalFrame(self, result)

    def NewGlobalRef(self, lobj):
        """
        Creates a new global reference to the object referred to by the obj argument. The obj
        argument may be a global or local reference. Global references must be explicitly
        disposed of by calling DeleteGlobalRef().

        :param lobj: a global or local reference.
        :return: Returns a global reference, or NULL if the system runs out of memory.
        """
        return self.functions[0].NewGlobalRef(self, lobj)

    def DeleteGlobalRef(self, gref):
        """
        Deletes the global reference pointed to by gref.

        :param gref: a global reference.
        :return:
        """
        self.functions[0].DeleteGlobalRef(self, gref)

    def DeleteLocalRef(self, obj):
        """
        Deletes the local reference pointed to by localRef.

        :param obj: a local reference.
        """
        self.functions[0].DeleteLocalRef(self, obj)

    def IsSameObject(self, obj1, obj2):
        """
        Tests whether two references refer to the same Java object.

        :param obj1: a Java object
        :param obj2: a Java object
        :return: True if references are to same object; otherwise False
        """
        return self.functions[0].IsSameObject(self, obj1, obj2) == JNI_TRUE

    def NewLocalRef(self, ref=None):
        """
        Creates a new local reference that refers to the same object as ref

        :param ref: a global or local reference
        :return: None if ref refers to None
        """
        return self.functions[0].NewLocalRef(self, ref)

    def EnsureLocalCapacity(self, capacity):
        """
        Ensures that at least a given number of local references can be created in the current
        thread.

        :param capacity: number of local references
        :return: 0 on success; otherwise a negative number
        :raises: OutOfMemoryError
        """
        return self.functions[0].EnsureLocalCapacity(self, capacity)

    def AllocObject(self, clazz):
        """
        Allocates a new Java object without invoking any of the constructors for the object.

        :param clazz: Any class except array classes.
        :return: a reference to the object.
        """
        obj = self.functions[0].AllocObject(self, clazz)
        self.check_exception()
        return obj

    def NewObjectA(self, clazz, mid, args):
        """
        Create a new object using the constructor.

        :param clazz: The class of the object
        :param mid: The MethodID of the constructor to use.
        :param args: a jvalue array of parameters
        :return: the created object.
        """
        obj = self.functions[0].NewObjectA(self, clazz, mid, args)
        self.check_exception()
        if obj is None:
            raise NullResultException(self, clazz, mid, args)
        return obj

    def GetObjectClass(self, obj):
        """
        Find the class for an object.
        :param obj: the object
        :return: the class for the given object
        """
        return self.functions[0].GetObjectClass(self, obj)

    def IsInstanceOf(self, obj, clazz):
        """
        Tests whether an object is an instance of a class.

        :param obj: the object
        :param clazz: the class
        :return: True if object is instance, otherwise False
        """
        return self.functions[0].IsInstanceOf(self, obj, clazz) == JNI_TRUE

    def GetMethodID(self, clazz, name, sig):
        """
        Returns the method ID for an instance (nonstatic) method of a class or interface.
        The method may be defined in one of the clazz’s superclasses and inherited by clazz.
        The method is determined by its name and signature.

        :param clazz: a Java class object
        :param name: the method name
        :param sig: the signature name
        :return: a method ID or None if the method can't be found
        """
        mid = self.functions[0].GetMethodID(self, clazz, encode(name), encode(sig))
        self.check_exception()
        if mid is None:
            raise NullResultException(self, clazz, name, sig)
        return mid

    def CallObjectMethodA(self, obj, mid, args):
        """
        Call an instance method which returns an Object.

        :param obj: the object instance
        :param mid: the method ID
        :param args: a jvalue array of method arguments
        :return: a jobject reference to the object returned by the method
        """
        result = self.functions[0].CallObjectMethodA(self, obj, mid, args)
        self.check_exception()
        return result

    def CallBooleanMethodA(self, obj, mid, args):
        """
        Call an instance method which returns a boolean.

        :param obj: the object instance
        :param mid: the method ID
        :param args: a jvalue array of method arguments
        :return: a jboolean returned by the method
        """
        result = self.functions[0].CallBooleanMethodA(self, obj, mid, args)
        self.check_exception()
        return result

    def CallByteMethodA(self, obj, mid, args):
        """
        Call an instance method which returns a byte.

        :param obj: the object instance
        :param mid: the method ID
        :param args: a jvalue array of method arguments
        :return: a jbyte returned by the method
        """
        result = self.functions[0].CallByteMethodA(self, obj, mid, args)
        self.check_exception()
        return result

    def CallCharMethodA(self, obj, mid, args):
        """
        Call an instance method which returns a char.

        :param obj: the object instance
        :param mid: the method ID
        :param args: a jvalue array of method arguments
        :return: a jchar returned by the method
        """
        result = self.functions[0].CallCharMethodA(self, obj, mid, args)
        self.check_exception()
        return result

    def CallShortMethodA(self, obj, mid, args):
        """
        Call an instance method which returns a short.

        :param obj: the object instance
        :param mid: the method ID
        :param args: a jvalue array of method arguments
        :return: a jshort returned by the method
        """
        result = self.functions[0].CallShortMethodA(self, obj, mid, args)
        self.check_exception()
        return result

    def CallIntMethodA(self, obj, mid, args):
        """
        Call an instance method which returns an int.

        :param obj: the object instance
        :param mid: the method ID
        :param args: a jvalue array of method arguments
        :return: a jint returned by the method
        """
        result = self.functions[0].CallIntMethodA(self, obj, mid, args)
        self.check_exception()
        return result

    def CallLongMethodA(self, obj, mid, args):
        """
        Call an instance method which returns a long.

        :param obj: the object instance
        :param mid: the method ID
        :param args: a jvalue array of method arguments
        :return: a jlong returned by the method
        """
        result = self.functions[0].CallLongMethodA(self, obj, mid, args)
        self.check_exception()
        return result

    def CallFloatMethodA(self, obj, mid, args):
        """
        Call an instance method which returns a float.

        :param obj: the object instance
        :param mid: the method ID
        :param args: a jvalue array of method arguments
        :return: a jfloat returned by the method
        """
        result = self.functions[0].CallFloatMethodA(self, obj, mid, args)
        self.check_exception()
        return result

    def CallDoubleMethodA(self, obj, mid, args):
        """
        Call an instance method which returns a double.

        :param obj: the object instance
        :param mid: the method ID
        :param args: a jvalue array of method arguments
        :return: a jdouble returned by the method
        """
        result = self.functions[0].CallDoubleMethodA(self, obj, mid, args)
        self.check_exception()
        return result

    def CallVoidMethodA(self, obj, mid, args):
        """
        Call an instance method which does not return a value.

        :param obj: the object instance
        :param mid: the method ID
        :param args: a jvalue array of method arguments
        """
        self.functions[0].CallVoidMethodA(self, obj, mid, args)
        self.check_exception()

    def CallNonvirtualObjectMethodA(self, obj, clazz, mid, args):
        """
        Call an instance method from a different class which returns an Object.

        :param obj: the object instance
        :param clazz: the class of the method
        :param mid: the method ID
        :param args: a jvalue array of method arguments
        :return: the Object return value
        """
        result = self.functions[0].CallNonvirtualObjectMethodA(self, obj, clazz, mid, args)
        self.check_exception()
        return result

    def CallNonvirtualBooleanMethodA(self, obj, clazz, mid, args):
        """
        Call an instance method from a different class which returns a boolean.

        :param obj: the object instance
        :param clazz: the class of the method
        :param mid: the method ID
        :param args: a jvalue array of method arguments
        :return: the jboolean return value
        """
        result = self.functions[0].CallNonvirtualBooleanMethodA(self, obj, clazz, mid, args)
        self.check_exception()
        return result

    def CallNonvirtualByteMethodA(self, obj, clazz, mid, args):
        """
        Call an instance method from a different class which returns a byte.

        :param obj: the object instance
        :param clazz: the class of the method
        :param mid: the method ID
        :param args: a jvalue array of method arguments
        :return: the byte return value
        """
        result = self.functions[0].CallNonvirtualByteMethodA(self, obj, clazz, mid, args)
        self.check_exception()
        return result

    def CallNonvirtualCharMethodA(self, obj, clazz, mid, args):
        """
        Call an instance method from a different class which returns a char.

        :param obj: the object instance
        :param clazz: the class of the method
        :param mid: the method ID
        :param args: a jvalue array of method arguments
        :return: the jchar return value
        """
        result = self.functions[0].CallNonvirtualCharMethodA(self, obj, clazz, mid, args)
        self.check_exception()
        return result

    def CallNonvirtualShortMethodA(self, obj, clazz, mid, args):
        """
        Call an instance method from a different class which returns a short.

        :param obj: the object instance
        :param clazz: the class of the method
        :param mid: the method ID
        :param args: a jvalue array of method arguments
        :return: the short return value
        """
        result = self.functions[0].CallNonvirtualShortMethodA(self, obj, clazz, mid, args)
        self.check_exception()
        return result

    def CallNonvirtualIntMethodA(self, obj, clazz, mid, args):
        """
        Call an instance method from a different class which returns an int.

        :param obj: the object instance
        :param clazz: the class of the method
        :param mid: the method ID
        :param args: a jvalue array of method arguments
        :return: the int return value
        """
        result = self.functions[0].CallNonvirtualIntMethodA(self, obj, clazz, mid, args)
        self.check_exception()
        return result

    def CallNonvirtualLongMethodA(self, obj, clazz, mid, args):
        """
        Call an instance method from a different class which returns a long.

        :param obj: the object instance
        :param clazz: the class of the method
        :param mid: the method ID
        :param args: a jvalue array of method arguments
        :return: the long return value
        """
        result = self.functions[0].CallNonvirtualLongMethodA(self, obj, clazz, mid, args)
        self.check_exception()
        return result

    def CallNonvirtualFloatMethodA(self, obj, clazz, mid, args):
        """
        Call an instance method from a different class which returns a float.

        :param obj: the object instance
        :param clazz: the class of the method
        :param mid: the method ID
        :param args: a jvalue array of method arguments
        :return: the float return value
        """
        result = self.functions[0].CallNonvirtualFloatMethodA(self, obj, clazz, mid, args)
        self.check_exception()
        return result

    def CallNonvirtualDoubleMethodA(self, obj, clazz, mid, args):
        """
        Call an instance method from a different class which returns a double.

        :param obj: the object instance
        :param clazz: the class of the method
        :param mid: the method ID
        :param args: a jvalue array of method arguments
        :return: the double return value
        """
        result = self.functions[0].CallNonvirtualDoubleMethodA(self, obj, clazz, mid, args)
        self.check_exception()
        return result

    def CallNonvirtualVoidMethodA(self, obj, clazz, mid, args):
        """
        Call an instance method from a different class which doesn't return a value.

        :param obj: the object instance
        :param clazz: the class of the method
        :param mid: the method ID
        :param args: a jvalue array of method arguments
        """
        self.functions[0].CallNonvirtualVoidMethodA(self, obj, clazz, mid, args)
        self.check_exception()

    def GetFieldID(self, clazz, name, sig):
        """
        Returns the field ID for an instance (nonstatic) field of a class.
        The field is specified by its name and signature.
        The Get<tyope>Field and Set<Type>Field families of accessor
        functions use this field ID to retrieve object fields.

        :param clazz: the class of the object
        :param name: the name of the field
        :param sig: the signature of the field
        :return: the fieldID object or None if the operation fails.
        """
        fid = self.functions[0].GetFieldID(self, clazz, encode(name), encode(sig))
        self.check_exception()
        if fid is None:
            raise NullResultException(clazz, name, sig)
        return fid

    def GetObjectField(self, obj, fid):
        """
        Retrieve the value of an Object field of an instance.

        :param obj: The object instance.
        :param fid: The fieldID from GetFieldID
        :return: the jobject reference to the field value.
        """
        return self.functions[0].GetObjectField(self, obj, fid)

    def GetBooleanField(self, obj, fid):
        """
        Retrieve the value of a boolean field of an instance.

        :param obj: The object instance.
        :param fid: The fieldID from GetFieldID
        :return: the boolean field value.
        """
        return self.functions[0].GetBooleanField(self, obj, fid)

    def GetByteField(self, obj, fid):
        """
        Retrieve the value of a byte field of an instance.

        :param obj: The object instance.
        :param fid: The fieldID from GetFieldID
        :return: the byte field value.
        """
        return self.functions[0].GetByteField(self, obj, fid)

    def GetCharField(self, obj, fid):
        """
        Retrieve the value of a char field of an instance.

        :param obj: The object instance.
        :param fid: The fieldID from GetFieldID
        :return: the char field value.
        """
        return self.functions[0].GetCharField(self, obj, fid)

    def GetShortField(self, obj, fid):
        """
        Retrieve the value of a short field of an instance.

        :param obj: The object instance.
        :param fid: The fieldID from GetFieldID
        :return: the short field value.
        """
        return self.functions[0].GetShortField(self, obj, fid)

    def GetIntField(self, obj, fid):
        """
        Retrieve the value of an int field of an instance.

        :param obj: The object instance.
        :param fid: The fieldID from GetFieldID
        :return: the int field value.
        """
        return self.functions[0].GetIntField(self, obj, fid)

    def GetLongField(self, obj, fid):
        """
        Retrieve the value of a long field of an instance.

        :param obj: The object instance.
        :param fid: The fieldID from GetFieldID
        :return: the long field value.
        """
        return self.functions[0].GetLongField(self, obj, fid)

    def GetFloatField(self, obj, fid):
        """
        Retrieve the value of a float field of an instance.

        :param obj: The object instance.
        :param fid: The fieldID from GetFieldID
        :return: the float field value.
        """
        return self.functions[0].GetFloatField(self, obj, fid)

    def GetDoubleField(self, obj, fid):
        """
        Retrieve the value of a double field of an instance.

        :param obj: The object instance.
        :param fid: The fieldID from GetFieldID
        :return: the double field value.
        """
        return self.functions[0].GetDoubleField(self, obj, fid)

    def SetObjectField(self, obj, fid, val):
        """
        Set the value of an Object field of an instance.

        :param obj: the object instance.
        :param fid: the fieldID from GetFieldID
        :param val: the object reference new value
        """
        self.functions[0].SetObjectField(self, obj, fid, val)

    def SetBooleanField(self, obj, fid, val):
        """
        Set the value of a boolean field of an instance.

        :param obj: the object instance.
        :param fid: the fieldID from GetFieldID
        :param val: the boolean new value
        """
        self.functions[0].SetBooleanField(self, obj, fid, val)

    def SetByteField(self, obj, fid, val):
        """
        Set the value of a byte field of an instance.

        :param obj: the object instance.
        :param fid: the fieldID from GetFieldID
        :param val: the byte new value
        """
        return self.functions[0].SetByteField(self, obj, fid, val)

    def SetCharField(self, obj, fid, val):
        """
        Set the value of an Object field of an instance.

        :param obj: the object instance.
        :param fid: the fieldID from GetFieldID
        :param val: the object reference of the field of an instance
        """
        return self.functions[0].SetCharField(self, obj, fid, val)

    def SetShortField(self, obj, fid, val):
        """
        Set the value of an Object field of an instance.

        :param obj: the object instance.
        :param fid: the fieldID from GetFieldID
        :param val: the object reference of the field of an instance
        """
        return self.functions[0].SetShortField(self, obj, fid, val)

    def SetIntField(self, obj, fid, val):
        """
        Set the value of an Object field of an instance.

        :param obj: the object instance.
        :param fid: the fieldID from GetFieldID
        :param val: the object reference of the field of an instance
        """
        return self.functions[0].SetIntField(self, obj, fid, val)

    def SetLongField(self, obj, fid, val):
        """
        Set the value of an Object field of an instance.

        :param obj: the object instance.
        :param fid: the fieldID from GetFieldID
        :param val: the object reference of the field of an instance
        """
        return self.functions[0].SetLongField(self, obj, fid, val)

    def SetFloatField(self, obj, fid, val):
        """
        Set the value of an Object field of an instance.

        :param obj: the object instance.
        :param fid: the fieldID from GetFieldID
        :param val: the object reference of the field of an instance
        """
        return self.functions[0].SetFloatField(self, obj, fid, val)

    def SetDoubleField(self, obj, fid, val):
        """
        Set the value of an Object field of an instance.

        :param obj: the object instance.
        :param fid: the fieldID from GetFieldID
        :param val: the object reference of the field of an instance
        """
        return self.functions[0].SetDoubleField(self, obj, fid, val)

    def GetStaticMethodID(self, clazz, name, signature):
        """
        Returns the method ID for a static method of a class.
        The method is specified by its name and signature.

        :param clazz: a Java class object
        :param name: the static method name
        :param signature: the static method signature
        :return: a method ID or None if operation fails
        """
        mid = self.functions[0].GetStaticMethodID(
            self,
            clazz,
            encode(name),
            encode(signature)
        )
        self.check_exception()
        if mid is None:
            raise NullResultException(self, clazz, name, signature)
        return mid

    def CallStaticObjectMethodA(self, clazz, mid, args):
        """
        Call a static method with arguments and return an Object reference.

        :param clazz: a Java class object
        :param mid: the static method ID from GetStaticMethodID
        :param args: an array of jvalue method arguments
        :return: an object reference
        """
        result = self.functions[0].CallStaticObjectMethodA(self, clazz, mid, args)
        self.check_exception()
        if result is None:
            raise NullResultException(self, clazz, mid, args)
        return result

    def CallStaticBooleanMethodA(self, clazz, mid, args):
        """
        Call a static method with arguments and return a boolean.

        :param clazz: a Java class object
        :param mid: the static method ID from GetStaticMethodID
        :param args: an array of jvalue method arguments
        :return: a jboolean
        """
        result = self.functions[0].CallStaticBooleanMethodA(self, clazz, mid, args)
        self.check_exception()
        return result

    def CallStaticByteMethodA(self, clazz, mid, args):
        """
        Call a static method with arguments and return a byte

        :param clazz: a Java class object
        :param mid: the static method ID from GetStaticMethodID
        :param args: an array of jvalue method arguments
        :return: a jbyte
        """
        result = self.functions[0].CallStaticByteMethodA(self, clazz, mid, args)
        self.check_exception()
        return result

    def CallStaticCharMethodA(self, clazz, mid, args):
        """
        Call a static method with arguments and return a char.

        :param clazz: a Java class object
        :param mid: the static method ID from GetStaticMethodID
        :param args: an array of jvalue method arguments
        :return: a jchar
        """
        result = self.functions[0].CallStaticCharMethodA(self, clazz, mid, args)
        self.check_exception()
        return result

    def CallStaticShortMethodA(self, clazz, mid, args):
        """
        Call a static method with arguments and return a short.

        :param clazz: a Java class object
        :param mid: the static method ID from GetStaticMethodID
        :param args: an array of jvalue method arguments
        :return: a jshort
        """
        result = self.functions[0].CallStaticShortMethodA(self, clazz, mid, args)
        self.check_exception()
        return result

    def CallStaticIntMethodA(self, clazz, mid, args):
        """
        Call a static method with arguments and return an int.

        :param clazz: a Java class object
        :param mid: the static method ID from GetStaticMethodID
        :param args: an array of jvalue method arguments
        :return: a jint
        """
        result = self.functions[0].CallStaticIntMethodA(self, clazz, mid, args)
        self.check_exception()
        return result

    def CallStaticLongMethodA(self, clazz, mid, args):
        """
        Call a static method with arguments and return a long.

        :param clazz: a Java class object
        :param mid: the static method ID from GetStaticMethodID
        :param args: an array of jvalue method arguments
        :return: a jlong
        """
        result = self.functions[0].CallStaticLongMethodA(self, clazz, mid, args)
        self.check_exception()
        return result

    def CallStaticFloatMethodA(self, clazz, mid, args):
        """
        Call a static method with arguments and return a float.

        :param clazz: a Java class object
        :param mid: the static method ID from GetStaticMethodID
        :param args: an array of jvalue method arguments
        :return: a jfloat
        """
        result = self.functions[0].CallStaticFloatMethodA(self, clazz, mid, args)
        self.check_exception()
        return result

    def CallStaticDoubleMethodA(self, clazz, mid, args):
        """
        Call a static method with arguments and return a double.

        :param clazz: a Java class object
        :param mid: the static method ID from GetStaticMethodID
        :param args: an array of jvalue method arguments
        :return: a jdouble
        """
        result = self.functions[0].CallStaticDoubleMethodA(self, clazz, mid, args)
        self.check_exception()
        return result

    def CallStaticVoidMethodA(self, clazz, mid, args):
        """
        Call a static method with arguments which doesn't return a value.

        :param clazz: a Java class object
        :param mid: the static method ID from GetStaticMethodID
        :param args: an array of jvalue method arguments
        """
        self.functions[0].CallStaticVoidMethodA(self, clazz, mid, args)
        self.check_exception()

    def GetStaticFieldID(self, clazz, name, sig):
        """
        Returns the field ID for a static field of a class. The field is specified by its
        name and signature.

        :param clazz: a Java class object
        :param name: the static field name
        :param sig: the static field signature
        :return: a field ID or None if the static field cannot be found.
        """
        fid = self.functions[0].GetStaticFieldID(self, clazz, encode(name), encode(sig))
        self.check_exception()
        if fid is None:
            raise NullResultException(self, clazz, name, sig)
        return fid

    def GetStaticObjectField(self, clazz, fid):
        """
        Retrieve the static value of an Object field of a class.

        :param clazz: a Java class reference.
        :param fid: the fieldID from GetStaticFieldID
        :return: the jobject reference to the field value.
        """
        return self.functions[0].GetStaticObjectField(self, clazz, fid)

    def GetStaticBooleanField(self, clazz, fid):
        """
        Retrieve the static value of a boolean field of a class.

        :param clazz: a Java class reference.
        :param fid: the fieldID from GetStaticFieldID
        :return: the jboolean field value.
        """
        return self.functions[0].GetStaticBooleanField(self, clazz, fid)

    def GetStaticByteField(self, clazz, fid):
        """
        Retrieve the static value of a byte field of a class.

        :param clazz: a Java class reference.
        :param fid: the fieldID from GetStaticFieldID
        :return: the jbyte field value.
        """
        return self.functions[0].GetStaticByteField(self, clazz, fid)

    def GetStaticCharField(self, clazz, fid):
        """
        Retrieve the static value of a char field of a class.

        :param clazz: a Java class reference.
        :param fid: the fieldID from GetStaticFieldID
        :return: the jchar field value.
        """
        return self.functions[0].GetStaticCharField(self, clazz, fid)

    def GetStaticShortField(self, clazz, fid):
        """
        Retrieve the static value of a short field of a class.

        :param clazz: a Java class reference.
        :param fid: the fieldID from GetStaticFieldID
        :return: the jshort field value.
        """
        return self.functions[0].GetStaticShortField(self, clazz, fid)

    def GetStaticIntField(self, clazz, fid):
        """
        Retrieve the static value of an int field of a class.

        :param clazz: a Java class reference.
        :param fid: the fieldID from GetStaticFieldID
        :return: the jint field value.
        """
        return self.functions[0].GetStaticIntField(self, clazz, fid)

    def GetStaticLongField(self, clazz, fid):
        """
        Retrieve the static value of a long field of a class.

        :param clazz: a Java class reference.
        :param fid: the fieldID from GetStaticFieldID
        :return: the jlong field value.
        """
        return self.functions[0].GetStaticLongField(self, clazz, fid)

    def GetStaticFloatField(self, clazz, fid):
        """
        Retrieve the static value of a float field of a class.

        :param clazz: a Java class reference.
        :param fid: the fieldID from GetStaticFieldID
        :return: the jfloat reference to the field value.
        """
        return self.functions[0].GetStaticFloatField(self, clazz, fid)

    def GetStaticDoubleField(self, clazz, fid):
        """
        Retrieve the static value of a double field of a class.

        :param clazz: a Java class reference.
        :param fid: the fieldID from GetStaticFieldID
        :return: the jdouble field value.
        """
        return self.functions[0].GetStaticDoubleField(self, clazz, fid)

    def SetStaticObjectField(self, clazz, fid, value):
        """
        Set the static value of an Object field of a class.

        :param clazz: a Java class object.
        :param fid: the static fieldID from GetStaticFieldID
        :param value: the new object reference value
        """
        self.functions[0].SetStaticObjectField(self, clazz, fid, value)

    def SetStaticBooleanField(self, clazz, fid, value):
        """
        Set the static value of a boolean field of a class.

        :param clazz: a Java class object.
        :param fid: the static fieldID from GetStaticFieldID
        :param value: the new jboolean value
        """
        self.functions[0].SetStaticBooleanField(self, clazz, fid, value)

    def SetStaticByteField(self, clazz, fid, value):
        """
        Set the static value of a byte field of a class.

        :param clazz: a Java class object.
        :param fid: the static fieldID from GetStaticFieldID
        :param value: the new jbyte value
        """
        self.functions[0].SetStaticByteField(self, clazz, fid, value)

    def SetStaticCharField(self, clazz, fid, value):
        """
        Set the static value of a char field of a class.

        :param clazz: a Java class object.
        :param fid: the static fieldID from GetStaticFieldID
        :param value: the new jchar value
        """
        self.functions[0].SetStaticCharField(self, clazz, fid, value)

    def SetStaticShortField(self, clazz, fid, value):
        """
        Set the static value of a short field of a class.

        :param clazz: a Java class object.
        :param fid: the static fieldID from GetStaticFieldID
        :param value: the new jshort value
        """
        self.functions[0].SetStaticShortField(self, clazz, fid, value)

    def SetStaticIntField(self, clazz, fid, value):
        """
        Set the static value of an int field of a class.

        :param clazz: a Java class object.
        :param fid: the static fieldID from GetStaticFieldID
        :param value: the new jint value
        """
        self.functions[0].SetStaticIntField(self, clazz, fid, value)

    def SetStaticLongField(self, clazz, fid, value):
        """
        Set the static value of a long field of a class.

        :param clazz: a Java class object.
        :param fid: the static fieldID from GetStaticFieldID
        :param value: the new jlong value
        """
        self.functions[0].SetStaticLongField(self, clazz, fid, value)

    def SetStaticFloatField(self, clazz, fid, value):
        """
        Set the static value of a float field of a class.

        :param clazz: a Java class object.
        :param fid: the static fieldID from GetStaticFieldID
        :param value: the new jfloat value
        """
        self.functions[0].SetStaticFloatField(self, clazz, fid, value)

    def SetStaticDoubleField(self, clazz, fid, value):
        """
        Set the static value of a double field of a class.

        :param clazz: a Java class object.
        :param fid: the static fieldID from GetStaticFieldID
        :param value: the new double value
        """
        return self.functions[0].SetStaticDoubleField(self, clazz, fid, value)

    def NewString(self, p_unicode, p_len):
        """
        Constructs a new java.lang.String object from an array of Unicode characters.

        :param p_unicode: an array of unicode characters.
        :param p_len: length of unicode string
        :return: a Java string object, or None if the string cannot be constructed.
        """
        obj = self.functions[0].NewString(self, p_unicode, p_len)
        self.check_exception()
        if obj is None:
            raise NullResultException(self, p_unicode, p_len)
        return obj

    def GetStringLength(self, p_str):
        """
        Returns the number of unicode characters in a Java string.

        :param p_str: a Java string object.
        :return:  the length in unicode characters.
        """
        return self.functions[0].GetStringLength(self, p_str)

    def GetStringChars(self, p_str, is_copy=None):
        """
        Returns a pointer to the array of Unicode characters of the string.
        This pointer is valid until ReleaseStringChars() is called.

        :param p_str: a Java string object
        :param is_copy: a pointer to a jboolean
        :return: a pointer to Unicode string or None if operation fails.
        """
        return self.functions[0].GetStringChars(self, p_str, is_copy)

    def ReleaseStringChars(self, p_str, chars):
        """
        Informs the VM that the native code no longer needs access to chars.

        :param p_str: a Java string object
        :param chars: the chars obtained from GetStringChars.
        """
        self.functions[0].ReleaseStringChars(self, p_str, chars)

    def NewStringUTF(self, utf):
        """
        Construct a new java.lang.String object from an array of characters in
        modified UTF-8 encoding.

        :param utf: string to encode, (these will automatically be encoded if unicode).
        :return: a reference to the new java.lang.String
        """
        return self.functions[0].NewStringUTF(self, encode(utf))

    def GetStringUTFLength(self, p_str):
        """
        Returns the number of bytes in a modified UTF-8 representation of a string
        :param p_str: a Java string object
        :return: the length in bytes
        """
        return self.functions[0].GetStringUTFLength(self, p_str)

    def GetStringUTFChars(self, p_str, is_copy=None):
        """
        Return a pointer to an array of bytes representing the string in modified
        UTF-8 encoding.  The array is valid until it is release by ReleaseStringUTFChars.

        :param p_str: a Jva string object
        :param is_copy: a pointer to a jboolean
        :return: a pointer to the modified UTF-8 string or None if the operation fails.
        """
        return self.functions[0].GetStringUTFChars(self, p_str, is_copy)

    def ReleaseStringUTFChars(self, p_str, chars):
        """
        Informs the VM that the native code no longer needs access to the chars allocated
        by GetStringUTFChars().

        :param p_str: a Java string object
        :param chars: a pointer to the modified UTF-8 bytes
        """
        self.functions[0].ReleaseStringUTFChars(self, p_str, chars)

    def GetArrayLength(self, array):
        """
        Return the length of an array.

        :param array: a Java array object.
        :return: the number of elements in the array.
        """
        return self.functions[0].GetArrayLength(self, array)

    def NewObjectArray(self, p_len, clazz, init):
        """
        Constructs an array holding objects.  all elements are initially set to init.

        :param p_len: array size
        :param clazz: array element class.
        :param init: initialization value
        :return: a Java array object or None if the array cannot be constructed.
        """
        return self.functions[0].NewObjectArray(self, p_len, clazz, init)

    def GetObjectArrayElement(self, array, index):
        """
        Return an element of an Object array.

        :param array: a Java array
        :param index: array index
        :return: a reference to the Object element.
        """
        return self.functions[0].GetObjectArrayElement(self, array, index)

    def SetObjectArrayElement(self, array, index, value):
        """
        Sets an element of an Object array.

        :param array: a Java array
        :param index: array index
        :param value: value of array element.
        :return:
        """
        self.functions[0].SetObjectArrayElement(self, array, index, value)

    def NewBooleanArray(self, p_len):
        """
        Create a Java array of booleans.

        :param p_len: the number of elements
        :return: a Java array of booleans
        """
        return self.functions[0].NewBooleanArray(self, p_len)

    def NewByteArray(self, p_len):
        """
        Create a Java array of bytes.

        :param p_len: the number of elements
        :return: a Java array of bytes
        """
        return self.functions[0].NewByteArray(self, p_len)

    def NewCharArray(self, p_len):
        """
        Create a Java array of chars.

        :param p_len: the number of elements
        :return: a Java array of chars
        """
        return self.functions[0].NewCharArray(self, p_len)

    def NewShortArray(self, p_len):
        """
        Create a Java array of shorts.

        :param p_len: the number of elements
        :return: a Java array of shorts
        """
        return self.functions[0].NewShortArray(self, p_len)

    def NewIntArray(self, p_len):
        """
        Create a Java array of ints.

        :param p_len: the number of elements
        :return: a Java array of ints
        """
        return self.functions[0].NewIntArray(self, p_len)

    def NewLongArray(self, p_len):
        """
        Create a Java array of longs.

        :param p_len: the number of elements
        :return: a Java array of longs
        """
        return self.functions[0].NewLongArray(self, p_len)

    def NewFloatArray(self, p_len):
        """
        Create a Java array of floats.

        :param p_len: the number of elements
        :return: a Java array of floats
        """
        return self.functions[0].NewFloatArray(self, p_len)

    def NewDoubleArray(self, p_len):
        """
        Create a Java array of doubles.

        :param p_len: the number of elements
        :return: a Java array of doubles
        """
        return self.functions[0].NewDoubleArray(self, p_len)

    def GetBooleanArrayElements(self, array, is_copy=None):
        """
        Returns the body of the boolean array.
        The result is valid until the corresponding ReleaseBooleanArrayElements() function
        is called. Since the returned array may be a copy of the Java array, changes made to
        the returned array will not necessarily be reflected in the original array until
        ReleaseBooleanArrayElements() is called.

        If isCopy is not NULL, then isCopy is set to JNI_TRUE if a copy is made;
        or it is set to JNI_FALSE if no copy is made.

        :param array: a jbooleanArray reference
        :param is_copy: a jboolean reference indicating pointer is to a copy or None
        :return: a pointer to jboolean buffer
        """
        return self.functions[0].GetBooleanArrayElements(self, array, is_copy)

    def GetByteArrayElements(self, array, is_copy=None):
        """
        Returns the body of the bte array.
        The result is valid until the corresponding ReleaseByteArrayElements() function
        is called. Since the returned array may be a copy of the Java array, changes made to
        the returned array will not necessarily be reflected in the original array until
        ReleaseByteArrayElements() is called.

        If isCopy is not NULL, then isCopy is set to JNI_TRUE if a copy is made;
        or it is set to JNI_FALSE if no copy is made.

        :param array: a jbyteArray reference
        :param is_copy: a jboolean reference indicating pointer is to a copy or None
        :return: a pointer to jbyte buffer
        """
        return self.functions[0].GetByteArrayElements(self, array, is_copy)

    def GetCharArrayElements(self, array, is_copy=None):
        """
        Returns the body of the char array.
        The result is valid until the corresponding ReleaseCharArrayElements() function
        is called. Since the returned array may be a copy of the Java array, changes made to
        the returned array will not necessarily be reflected in the original array until
        ReleaseCharArrayElements() is called.

        If isCopy is not NULL, then isCopy is set to JNI_TRUE if a copy is made;
        or it is set to JNI_FALSE if no copy is made.

        :param array: a jcharArray reference
        :param is_copy: a jboolean reference indicating pointer is to a copy or None
        :return: a pointer to jchar buffer
        """
        return self.functions[0].GetCharArrayElements(self, array, is_copy)

    def GetShortArrayElements(self, array, is_copy=None):
        """
        Returns the body of the short array.
        The result is valid until the corresponding ReleaseShortArrayElements() function
        is called. Since the returned array may be a copy of the Java array, changes made to
        the returned array will not necessarily be reflected in the original array until
        ReleaseShortArrayElements() is called.

        If isCopy is not NULL, then isCopy is set to JNI_TRUE if a copy is made;
        or it is set to JNI_FALSE if no copy is made.

        :param array: a jshortArray reference
        :param is_copy: a jboolean reference indicating pointer is to a copy or None
        :return: a pointer to jshort buffer
        """
        return self.functions[0].GetShortArrayElements(self, array, is_copy)

    def GetIntArrayElements(self, array, is_copy=None):
        """
        Returns the body of the int array.
        The result is valid until the corresponding ReleaseIntArrayElements() function
        is called. Since the returned array may be a copy of the Java array, changes made to
        the returned array will not necessarily be reflected in the original array until
        ReleaseIntArrayElements() is called.

        If isCopy is not NULL, then isCopy is set to JNI_TRUE if a copy is made;
        or it is set to JNI_FALSE if no copy is made.

        :param array: a jintArray reference
        :param is_copy: a jboolean reference indicating pointer is to a copy or None
        :return: a pointer to jint buffer
        """
        return self.functions[0].GetIntArrayElements(self, array, is_copy)

    def GetLongArrayElements(self, array, is_copy=None):
        """
        Returns the body of the long array.
        The result is valid until the corresponding ReleaseLongArrayElements() function
        is called. Since the returned array may be a copy of the Java array, changes made to
        the returned array will not necessarily be reflected in the original array until
        ReleaseLongArrayElements() is called.

        If isCopy is not NULL, then isCopy is set to JNI_TRUE if a copy is made;
        or it is set to JNI_FALSE if no copy is made.

        :param array: a jlongArray reference
        :param is_copy: a jboolean reference indicating pointer is to a copy or None
        :return: a pointer to jlong buffer
        """
        return self.functions[0].GetLongArrayElements(self, array, is_copy)

    def GetFloatArrayElements(self, array, is_copy=None):
        """
        Returns the body of the float array.
        The result is valid until the corresponding ReleaseFloatArrayElements() function
        is called. Since the returned array may be a copy of the Java array, changes made to
        the returned array will not necessarily be reflected in the original array until
        ReleaseFloatArrayElements() is called.

        If isCopy is not NULL, then isCopy is set to JNI_TRUE if a copy is made;
        or it is set to JNI_FALSE if no copy is made.

        :param array: a jfloatArray reference
        :param is_copy: a jboolean reference indicating pointer is to a copy or None
        :return: a pointer to jfloat buffer
        """
        return self.functions[0].GetFloatArrayElements(self, array, is_copy)

    def GetDoubleArrayElements(self, array, is_copy=None):
        """
        Returns the body of the double array.
        The result is valid until the corresponding ReleaseDoubleArrayElements() function
        is called. Since the returned array may be a copy of the Java array, changes made to
        the returned array will not necessarily be reflected in the original array until
        ReleaseDoubleArrayElements() is called.

        If isCopy is not NULL, then isCopy is set to JNI_TRUE if a copy is made;
        or it is set to JNI_FALSE if no copy is made.

        :param array: a jdoubleArray reference
        :param is_copy: a jboolean reference indicating pointer is to a copy or None
        :return: a pointer to jdouble buffer
        """
        return self.functions[0].GetDoubleArrayElements(self, array, is_copy)

    def ReleaseBooleanArrayElements(self, array, elems, mode):
        """
        Release a pointer to a primitive data type buffer after a call to
        GetBooleanArrayElements.

        :param array: a jbooleanArray reference
        :param elems: the pointer to the jboolean buffer
        :param mode:
            0: copy back the contents and free the buffer
            JNI_COMMIT: copy back the contents but do not free
            JNI_ABORT: free the buffer without copying back the changes
        """
        self.functions[0].ReleaseBooleanArrayElements(self, array, elems, mode)

    def ReleaseByteArrayElements(self, array, elems, mode):
        """
        Release a pointer to a primitive data type buffer after a call to
        GetByteArrayElements.

        :param array: a jbyteArray reference
        :param elems: the pointer to the jbyte buffer
        :param mode:
            0: copy back the contents and free the buffer
            JNI_COMMIT: copy back the contents but do not free
            JNI_ABORT: free the buffer without copying back the changes
        """
        self.functions[0].ReleaseByteArrayElements(self, array, elems, mode)

    def ReleaseCharArrayElements(self, array, elems, mode):
        """
        Release a pointer to a primitive data type buffer after a call to
        GetCharArrayElements.

        :param array: a jcharArray reference
        :param elems: the pointer to the jchar buffer
        :param mode:
            0: copy back the contents and free the buffer
            JNI_COMMIT: copy back the contents but do not free
            JNI_ABORT: free the buffer without copying back the changes
        """
        self.functions[0].ReleaseCharArrayElements(self, array, elems, mode)

    def ReleaseShortArrayElements(self, array, elems, mode):
        """
        Release a pointer to a primitive data type buffer after a call to
        GetShortArrayElements.

        :param array: a jshortArray reference
        :param elems: the pointer to the jshort buffer
        :param mode:
            0: copy back the contents and free the buffer
            JNI_COMMIT: copy back the contents but do not free
            JNI_ABORT: free the buffer without copying back the changes
        """
        self.functions[0].ReleaseShortArrayElements(self, array, elems, mode)

    def ReleaseIntArrayElements(self, array, elems, mode):
        """
        Release a pointer to a primitive data type buffer after a call to
        GetIntArrayElements.

        :param array: a jintArray reference
        :param elems: the pointer to the jint buffer
        :param mode:
            0: copy back the contents and free the buffer
            JNI_COMMIT: copy back the contents but do not free
            JNI_ABORT: free the buffer without copying back the changes
        """
        self.functions[0].ReleaseIntArrayElements(self, array, elems, mode)

    def ReleaseLongArrayElements(self, array, elems, mode):
        """
        Release a pointer to a primitive data type buffer after a call to
        GetLongArrayElements.

        :param array: a jlongArray reference
        :param elems: the pointer to the jlong buffer
        :param mode:
            0: copy back the contents and free the buffer
            JNI_COMMIT: copy back the contents but do not free
            JNI_ABORT: free the buffer without copying back the changes
        """
        self.functions[0].ReleaseLongArrayElements(self, array, elems, mode)

    def ReleaseFloatArrayElements(self, array, elems, mode):
        """
        Release a pointer to a primitive data type buffer after a call to
        GetFloatArrayElements.

        :param array: a jfloatArray reference
        :param elems: the pointer to the jfloat buffer
        :param mode:
            0: copy back the contents and free the buffer
            JNI_COMMIT: copy back the contents but do not free
            JNI_ABORT: free the buffer without copying back the changes
        """
        self.functions[0].ReleaseFloatArrayElements(self, array, elems, mode)

    def ReleaseDoubleArrayElements(self, array, elems, mode):
        """
        Release a pointer to a primitive data type buffer after a call to
        GetDoubleArrayElements.

        :param array: a jdoubleArray reference
        :param elems: the pointer to the jdouble buffer
        :param mode:
            0: copy back the contents and free the buffer
            JNI_COMMIT: copy back the contents but do not free
            JNI_ABORT: free the buffer without copying back the changes
        """
        self.functions[0].ReleaseDoubleArrayElements(self, array, elems, mode)

    def GetBooleanArrayRegion(self, array, start, p_len, buf):
        """
        Copies a region of a boolean array into a buffer.

        :param array: a jbooleanArray reference
        :param start: the starting index
        :param p_len: the number of elements to copy
        :param buf: the destination buffer
        """
        self.functions[0].GetBooleanArrayRegion(self, array, start, p_len, buf)

    def GetByteArrayRegion(self, array, start, p_len, buf):
        """
        Copies a region of a byte array into a buffer.

        :param array: a jbyteArray reference
        :param start: the starting index
        :param p_len: the number of elements to copy
        :param buf: the destination buffer
        """
        self.functions[0].GetByteArrayRegion(self, array, start, p_len, buf)

    def GetCharArrayRegion(self, array, start, p_len, buf):
        """
        Copies a region of a char array into a buffer.

        :param array: a jcharArray reference
        :param start: the starting index
        :param p_len: the number of elements to copy
        :param buf: the destination buffer
        """
        self.functions[0].GetCharArrayRegion(self, array, start, p_len, buf)

    def GetShortArrayRegion(self, array, start, p_len, buf):
        """
        Copies a region of a short array into a buffer.

        :param array: a jshortArray reference
        :param start: the starting index
        :param p_len: the number of elements to copy
        :param buf: the destination buffer
        """
        self.functions[0].GetShortArrayRegion(self, array, start, p_len, buf)

    def GetIntArrayRegion(self, array, start, p_len, buf):
        """
        Copies a region of a int array into a buffer.

        :param array: a jintArray reference
        :param start: the starting index
        :param p_len: the number of elements to copy
        :param buf: the destination buffer
        """
        self.functions[0].GetIntArrayRegion(self, array, start, p_len, buf)

    def GetLongArrayRegion(self, array, start, p_len, buf):
        """
        Copies a region of a long array into a buffer.

        :param array: a jlongArray reference
        :param start: the starting index
        :param p_len: the number of elements to copy
        :param buf: the destination buffer
        """
        self.functions[0].GetLongArrayRegion(self, array, start, p_len, buf)

    def GetFloatArrayRegion(self, array, start, p_len, buf):
        """
        Copies a region of a float array into a buffer.

        :param array: a jfloatArray reference
        :param start: the starting index
        :param p_len: the number of elements to copy
        :param buf: the destination buffer
        """
        self.functions[0].GetFloatArrayRegion(self, array, start, p_len, buf)

    def GetDoubleArrayRegion(self, array, start, p_len, buf):
        """
        Copies a region of a double array into a buffer.

        :param array: a jdoubleArray reference
        :param start: the starting index
        :param p_len: the number of elements to copy
        :param buf: the destination buffer
        """
        self.functions[0].GetDoubleArrayRegion(self, array, start, p_len, buf)

    def SetBooleanArrayRegion(self, array, start, p_len, buf):
        """
        Copies back a region of a primitive array from a buffer.

        :param array: a jbooleanArray reference
        :param start: the starting index
        :param p_len: the number of elements to copy
        :param buf: the source buffer
        """
        self.functions[0].SetBooleanArrayRegion(self, array, start, p_len, buf)

    def SetByteArrayRegion(self, array, start, p_len, buf):
        """
        Copies back a region of a primitive array from a buffer.

        :param array: a jbyteArray reference
        :param start: the starting index
        :param p_len: the number of elements to copy
        :param buf: the source buffer
        """
        self.functions[0].SetByteArrayRegion(self, array, start, p_len, buf)

    def SetCharArrayRegion(self, array, start, p_len, buf):
        """
        Copies back a region of a primitive array from a buffer.

        :param array: a jcharArray reference
        :param start: the starting index
        :param p_len: the number of elements to copy
        :param buf: the source buffer
        """
        self.functions[0].SetCharArrayRegion(self, array, start, p_len, buf)

    def SetShortArrayRegion(self, array, start, p_len, buf):
        """
        Copies back a region of a primitive array from a buffer.

        :param array: a jshortArray reference
        :param start: the starting index
        :param p_len: the number of elements to copy
        :param buf: the source buffer
        """
        self.functions[0].SetShortArrayRegion(self, array, start, p_len, buf)

    def SetIntArrayRegion(self, array, start, p_len, buf):
        """
        Copies back a region of a primitive array from a buffer.

        :param array: a jintArray reference
        :param start: the starting index
        :param p_len: the number of elements to copy
        :param buf: the source buffer
        """
        self.functions[0].SetIntArrayRegion(self, array, start, p_len, buf)

    def SetLongArrayRegion(self, array, start, p_len, buf):
        """
        Copies back a region of a primitive array from a buffer.

        :param array: a jlongArray reference
        :param start: the starting index
        :param p_len: the number of elements to copy
        :param buf: the source buffer
        """
        self.functions[0].SetLongArrayRegion(self, array, start, p_len, buf)

    def SetFloatArrayRegion(self, array, start, p_len, buf):
        """
        Copies back a region of a primitive array from a buffer.

        :param array: a jfloatArray reference
        :param start: the starting index
        :param p_len: the number of elements to copy
        :param buf: the source buffer
        """
        self.functions[0].SetFloatArrayRegion(self, array, start, p_len, buf)

    def SetDoubleArrayRegion(self, array, start, p_len, buf):
        """
        Copies back a region of a primitive array from a buffer.

        :param array: a jdoubleArray reference
        :param start: the starting index
        :param p_len: the number of elements to copy
        :param buf: the source buffer
        """
        self.functions[0].SetDoubleArrayRegion(self, array, start, p_len, buf)

    def RegisterNatives(self, clazz, methods, n_methods):
        """
        Registers native methods with the class specified by the clazz argument.
        The methods parameter specifies an array of JNINativeMethod structures that contain
        the names, signatures, and function pointers of the native methods. The name and
        signature fields of the JNINativeMethod structure are pointers to modified UTF-8
        strings. The nMethods parameter specifies the number of native methods in the array.

        :param clazz: a Java class object
        :param methods: the native methods in the class
        :param n_methods: the number of native methods in the class
        :return: 0 on success, a negative value on failure.
        """
        return self.functions[0].RegisterNatives(self, clazz, methods, n_methods)

    def UnregisterNatives(self, clazz):
        """
        Unregisters native methods of a class. The class goes back to the state before it
        was linked or registered with its native method functions.

        This function should not be used in normal native code. Instead, it provides
        special programs a way to reload and relink native libraries.

        :param clazz: a Java class object
        :return: 0 on success, a negative value on falure.
        """
        return self.functions[0].UnregisterNatives(self, clazz)

    def MonitorEnter(self, obj):
        """
        Enters the monitor associated with the underlying Java object referred to by obj.

        :param obj: a normal Java object or class object.
        :return: 0 on success, a negative value on failure
        """
        return self.functions[0].MonitorEnter(self, obj)

    def MonitorExit(self, obj):
        """
        The current thread must be the owner of the monitor associated with the underlying
        Java object referred to by obj. The thread decrements the counter indicating the
        number of times it has entered this monitor. If the value of the counter becomes zero,
        the current thread releases the monitor.

        :param obj: a normal Java ovject or class object
        :return: 0 on success, a negative value on failure.
        """
        return self.functions[0].MonitorExit(self, obj)

    def GetJavaVM(self, p_vm):
        """
        Returns the Java VM interface (used in the Invocation API) associated with
        the current thread. The result is placed at the location pointed to by
        the second argument, vm.

        :param p_vm: a pointer to where the result should be placed
        :return: 0 on success, a negative value n failure
        """
        return self.functions[0].GetJavaVM(self, p_vm)

    def GetStringRegion(self, p_str, start, p_len, buf):
        """
        Copies len number of Unicode characters beginning at offset start to the given
        buffer buf.

        :param p_str: a java string reference
        :param start: offset to start copying
        :param p_len: number of characters to copy
        :param buf: jchar buffer to receive copy of characters
        """
        self.functions[0].GetStringRegion(self, p_str, start, p_len, buf)

    def GetStringUTFRegion(self, p_str, start, p_len, buf):
        """
        Translate Unicode characters into modified UTF-8 encoding and
        place result in the given buffer.

        :param p_str: a Java string reference
        :param start: offset to start copying
        :param p_len: number of characters to copy
        :param buf: a char buffer to receive copy of translated characters
        """
        self.functions[0].GetStringUTFRegion(self, p_str, start, p_len, buf)

    def GetPrimitiveArrayCritical(self, array, is_copy=None):
        return self.functions[0].GetPrimitiveArrayCritical(self, array, is_copy)

    def ReleasePrimitiveArrayCritical(self, array, carray, is_copy=None):
        self.functions[0].ReleasePrimitiveArrayCritical(self, array, carray, is_copy)

    def GetStringCritical(self, string, is_copy=None):
        """
        If possible, the VM returns a pointer to string elements; otherwise, a copy is made.

        However, there are significant restrictions on how this functions can be used.
        In a code segment enclosed by Get/ReleaseStringCritical calls, the native code must
        not issue arbitrary JNI calls, or cause the current thread to block.

        :param string: a Java string reference
        :param is_copy: a pointer to a jboolean to indicate whether this is a copy
        :return: a pointer to the jchar buffer of the string
        """
        return self.functions[0].GetStringCritical(self, string, is_copy)

    def ReleaseStringCritical(self, string, cstring):
        """
        Release characters referenced by GetStringCritical.

        :param string: a Java string reference
        :param cstring: the jchar buffer pointer retrieved from GetStringCritical
        """
        self.functions[0].ReleaseStringCritical(self, string, cstring)

    def NewWeakGlobalRef(self, obj):
        """
        Creates a new weak global reference.

        :param obj: object to reference.
        :return: None if obj refers to None, or if the VM runs out of memory.
        :raises: OutOfMemoryError
        """
        return self.functions[0].NewWeakGlobalRef(self, obj)

    def DeleteWeakGlobalRef(self, ref):
        """
        Delete the VM resources needed for the given weak global reference.

        :param ref: the weak global reference
        """
        self.functions[0].DeleteWeakGlobalRef(self, ref)

    def ExceptionCheck(self):
        """
        Check for pending exceptions without creating a local reference to
        the exception object.

        :return: JNI_TRUE when there is a pending exception; otherwise, returns JNI_FALSE.
        """
        return self.functions[0].ExceptionCheck(self)

    def NewDirectByteBuffer(self, address, capacity):
        """
        Allocates and returns a direct java.nio.ByteBuffer referring to the block
        of memory starting at the memory address address and extending capacity bytes.

        :param address: the starting address of the memory region
        :param capacity: the size in bytes of the memory region
        :return:
        """
        return self.functions[0].NewDirectByteBuffer(self, address, capacity)

    def GetDirectBufferAddress(self, buf):
        """
        Fetches and returns the starting address of the memory region
        referenced by the given direct java.nio.Buffer.

        :param buf: a direct java.nio.Buffer object
        :return: the starting address of the memory region referened by the buffer.
            Returns None if the memory region is undfined.
        """
        return self.functions[0].GetDirectBufferAddress(self, buf)

    def GetDirectBufferCapacity(self, buf):
        return self.functions[0].GetDirectBufferCapacity(self, buf)

    def GetObjectRefType(self, obj):
        """
        Return the type of the object referred to by the obj argument.

        :param obj: the object to check, either global or weak global referenced.
        :return: the type of the object::
            JNIInvalidRefType = 0
            JNILocalRefType = 1
            JNIGlobalRefType = 2
            JNIWeakGlobalRefType = 3
        """
        return self.functions[0].GetObjectRefType(self, obj)

    def GetModule(self, clazz):
        """
        Returns the java.lang.Module object for the module that the class is a member of.
        If the class is not in a named module then the unnamed module of the class loader
        for the class is returned. If the class represents an array type then this function
        returns the Module object for the element type. If the class represents a primitive
        type or void, then the Module object for the java.base module is returned.

        :param clazz: a Java class object, must not be None
        :return: the module that the class or interface is a member of.
        """
        return self.functions[0].GetModule(self, clazz)


JNIEnv_p = POINTER(JNIEnv)

JNIInvokeInterface_._fields_ = tuple(map_fields(
    'reserved0',
    'reserved1',
    'reserved2',
    (jint, 'DestroyJavaVM', JavaVM_p),
    (jint, 'AttachCurrentThread', JavaVM_p, POINTER(JNIEnv_p), c_void_p),
    (jint, 'DetachCurrentThread', JavaVM_p),
    (jint, 'GetEnv', JavaVM_p, POINTER(JNIEnv_p), jint),
    (jint, 'AttachCurrentThreadAsDaemon', JavaVM_p, POINTER(JNIEnv_p), c_void_p),
))

JNINativeInterface_._fields_ = tuple(map_fields(
    'reserved0',
    'reserved1',
    'reserved2',
    'reserved3',
    (jint, 'GetVersion', JNIEnv_p),

    (jclass, 'DefineClass', JNIEnv_p, c_char_p, jobject, POINTER(jbyte), jsize),
    (jclass, 'FindClass', JNIEnv_p, c_char_p),

    (jmethodID, 'FromReflectedMethod', JNIEnv_p, jobject),
    (jfieldID, 'FromReflectedField', JNIEnv_p, jobject),

    (jobject, 'ToReflectedMethod', JNIEnv_p, jclass, jmethodID, jboolean),

    (jclass, 'GetSuperclass', JNIEnv_p, jclass),
    (jboolean, 'IsAssignableFrom', JNIEnv_p, jclass, jclass),

    (jobject, 'ToReflectedField', JNIEnv_p, jclass, jfieldID, jboolean),

    (jint, 'Throw', JNIEnv_p, jthrowable),
    (jint, 'ThrowNew', JNIEnv_p, jclass, c_char_p),
    (jthrowable, 'ExceptionOccurred', JNIEnv_p),
    (None, 'ExceptionDescribe', JNIEnv_p),
    (None, 'ExceptionClear', JNIEnv_p),
    (None, 'FatalError', JNIEnv_p, c_char_p),

    (jint, 'PushLocalFrame', JNIEnv_p, jint),
    (jobject, 'PopLocalFrame', JNIEnv_p, jobject),

    (jobject, 'NewGlobalRef', JNIEnv_p, jobject),
    (None, 'DeleteGlobalRef', JNIEnv_p, jobject),
    (None, 'DeleteLocalRef', JNIEnv_p, jobject),
    (jboolean, 'IsSameObject', JNIEnv_p, jobject, jobject),
    (jobject, 'NewLocalRef', JNIEnv_p, jobject),
    (jint, 'EnsureLocalCapacity', JNIEnv_p, jint),

    (jobject, 'AllocObject', JNIEnv_p, jclass),
    'NewObject',
    'NewObjectV',
    (jobject, 'NewObjectA', JNIEnv_p, jclass, jmethodID, jvalue_p),

    (jclass, 'GetObjectClass', JNIEnv_p, jobject),
    (jboolean, 'IsInstanceOf', JNIEnv_p, jobject, jclass),

    (jmethodID, 'GetMethodID', JNIEnv_p, jclass, c_char_p, c_char_p),

    'CallObjectMethod',
    'CallObjectMethodV',
    (jobject, 'CallObjectMethodA', JNIEnv_p, jobject, jmethodID, jvalue_p),

    'CallBooleanMethod',
    'CallBooleanMethodV',
    (jboolean, 'CallBooleanMethodA', JNIEnv_p, jobject, jmethodID, jvalue_p),

    'CallByteMethod',
    'CallByteMethodV',
    (jbyte, 'CallByteMethodA', JNIEnv_p, jobject, jmethodID, jvalue_p),

    'CallCharMethod',
    'CallCharMethodV',
    (jchar, 'CallCharMethodA', JNIEnv_p, jobject, jmethodID, jvalue_p),

    'CallShortMethod',
    'CallShortMethodV',
    (jshort, 'CallShortMethodA', JNIEnv_p, jobject, jmethodID, jvalue_p),

    'CallIntMethod',
    'CallIntMethodV',
    (jint, 'CallIntMethodA', JNIEnv_p, jobject, jmethodID, jvalue_p),

    'CallLongMethod',
    'CallLongMethodV',
    (jlong, 'CallLongMethodA', JNIEnv_p, jobject, jmethodID, jvalue_p),

    'CallFloatMethod',
    'CallFloatMethodV',
    (jfloat, 'CallFloatMethodA', JNIEnv_p, jobject, jmethodID, jvalue_p),

    'CallDoubleMethod',
    'CallDoubleMethodV',
    (jdouble, 'CallDoubleMethodA', JNIEnv_p, jobject, jmethodID, jvalue_p),

    'CallVoidMethod',
    'CallVoidMethodV',
    (None, 'CallVoidMethodA', JNIEnv_p, jobject, jmethodID, jvalue_p),

    'CallNonvirtualObjectMethod',
    'CallNonvirtualObjectMethodV',
    (jobject, 'CallNonvirtualObjectMethodA', JNIEnv_p, jobject, jclass, jmethodID, jvalue_p),

    'CallNonvirtualBooleanMethod',
    'CallNonvirtualBooleanMethodV',
    (jboolean, 'CallNonvirtualBooleanMethodA', JNIEnv_p, jobject, jclass, jmethodID, jvalue_p),

    'CallNonvirtualByteMethod',
    'CallNonvirtualByteMethodV',
    (jbyte, 'CallNonvirtualByteMethodA', JNIEnv_p, jobject, jclass, jmethodID, jvalue_p),

    'CallNonvirtualCharMethod',
    'CallNonvirtualCharMethodV',
    (jchar, 'CallNonvirtualCharMethodA', JNIEnv_p, jobject, jclass, jmethodID, jvalue_p),

    'CallNonvirtualShortMethod',
    'CallNonvirtualShortMethodV',
    (jshort, 'CallNonvirtualShortMethodA', JNIEnv_p, jobject, jclass, jmethodID, jvalue_p),

    'CallNonvirtualIntMethod',
    'CallNonvirtualIntMethodV',
    (jint, 'CallNonvirtualIntMethodA', JNIEnv_p, jobject, jclass, jmethodID, jvalue_p),

    'CallNonvirtualLongMethod',
    'CallNonvirtualLongMethodV',
    (jlong, 'CallNonvirtualLongMethodA', JNIEnv_p, jobject, jclass, jmethodID, jvalue_p),

    'CallNonvirtualFloatMethod',
    'CallNonvirtualFloatMethodV',
    (jfloat, 'CallNonvirtualFloatMethodA', JNIEnv_p, jobject, jclass, jmethodID, jvalue_p),

    'CallNonvirtualDoubleMethod',
    'CallNonvirtualDoubleMethodV',
    (jdouble, 'CallNonvirtualDoubleMethodA', JNIEnv_p, jobject, jclass, jmethodID, jvalue_p),

    'CallNonvirtualVoidMethod',
    'CallNonvirtualVoidMethodV',
    (None, 'CallNonvirtualVoidMethodA', JNIEnv_p, jobject, jclass, jmethodID, jvalue_p),

    (jfieldID, 'GetFieldID', JNIEnv_p, jclass, c_char_p, c_char_p),

    (jobject, 'GetObjectField', JNIEnv_p, jobject, jfieldID),
    (jboolean, 'GetBooleanField', JNIEnv_p, jobject, jfieldID),
    (jbyte, 'GetByteField', JNIEnv_p, jobject, jfieldID),
    (jchar, 'GetCharField', JNIEnv_p, jobject, jfieldID),
    (jshort, 'GetShortField', JNIEnv_p, jobject, jfieldID),
    (jint, 'GetIntField', JNIEnv_p, jobject, jfieldID),
    (jlong, 'GetLongField', JNIEnv_p, jobject, jfieldID),
    (jfloat, 'GetFloatField', JNIEnv_p, jobject, jfieldID),
    (jdouble, 'GetDoubleField', JNIEnv_p, jobject, jfieldID),

    (None, 'SetObjectField', JNIEnv_p, jobject, jfieldID, jobject),
    (None, 'SetBooleanField', JNIEnv_p, jobject, jfieldID, jboolean),
    (None, 'SetByteField', JNIEnv_p, jobject, jfieldID, jbyte),
    (None, 'SetCharField', JNIEnv_p, jobject, jfieldID, jchar),
    (None, 'SetShortField', JNIEnv_p, jobject, jfieldID, jshort),
    (None, 'SetIntField', JNIEnv_p, jobject, jfieldID, jint),
    (None, 'SetLongField', JNIEnv_p, jobject, jfieldID, jlong),
    (None, 'SetFloatField', JNIEnv_p, jobject, jfieldID, jfloat),
    (None, 'SetDoubleField', JNIEnv_p, jobject, jfieldID, jdouble),

    (jmethodID, 'GetStaticMethodID', JNIEnv_p, jclass, c_char_p, c_char_p),

    'CallStaticObjectMethod',
    'CallStaticObjectMethodV',
    (jobject, 'CallStaticObjectMethodA', JNIEnv_p, jclass, jmethodID, jvalue_p),

    'CallStaticBooleanMethod',
    'CallStaticBooleanMethodV',
    (jboolean, 'CallStaticBooleanMethodA', JNIEnv_p, jclass, jmethodID, jvalue_p),

    'CallStaticByteMethod',
    'CallStaticByteMethodV',
    (jbyte, 'CallStaticByteMethodA', JNIEnv_p, jclass, jmethodID, jvalue_p),

    'CallStaticCharMethod',
    'CallStaticCharMethodV',
    (jchar, 'CallStaticCharMethodA', JNIEnv_p, jclass, jmethodID, jvalue_p),

    'CallStaticShortMethod',
    'CallStaticShortMethodV',
    (jshort, 'CallStaticShortMethodA', JNIEnv_p, jclass, jmethodID, jvalue_p),

    'CallStaticIntMethod',
    'CallStaticIntMethodV',
    (jint, 'CallStaticIntMethodA', JNIEnv_p, jclass, jmethodID, jvalue_p),

    'CallStaticLongMethod',
    'CallStaticLongMethodV',
    (jlong, 'CallStaticLongMethodA', JNIEnv_p, jclass, jmethodID, jvalue_p),

    'CallStaticFloatMethod',
    'CallStaticFloatMethodV',
    (jfloat, 'CallStaticFloatMethodA', JNIEnv_p, jclass, jmethodID, jvalue_p),

    'CallStaticDoubleMethod',
    'CallStaticDoubleMethodV',
    (jdouble, 'CallStaticDoubleMethodA', JNIEnv_p, jclass, jmethodID, jvalue_p),

    'CallStaticVoidMethod',
    'CallStaticVoidMethodV',
    (None, 'CallStaticVoidMethodA', JNIEnv_p, jclass, jmethodID, jvalue_p),

    (jfieldID, 'GetStaticFieldID', JNIEnv_p, jclass, c_char_p, c_char_p),
    (jobject, 'GetStaticObjectField', JNIEnv_p, jclass, jfieldID),
    (jboolean, 'GetStaticBooleanField', JNIEnv_p, jclass, jfieldID),
    (jbyte, 'GetStaticByteField', JNIEnv_p, jclass, jfieldID),
    (jchar, 'GetStaticCharField', JNIEnv_p, jclass, jfieldID),
    (jshort, 'GetStaticShortField', JNIEnv_p, jclass, jfieldID),
    (jint, 'GetStaticIntField', JNIEnv_p, jclass, jfieldID),
    (jlong, 'GetStaticLongField', JNIEnv_p, jclass, jfieldID),
    (jfloat, 'GetStaticFloatField', JNIEnv_p, jclass, jfieldID),
    (jdouble, 'GetStaticDoubleField', JNIEnv_p, jclass, jfieldID),

    (None, 'SetStaticObjectField', JNIEnv_p, jclass, jfieldID, jobject),
    (None, 'SetStaticBooleanField', JNIEnv_p, jclass, jfieldID, jboolean),
    (None, 'SetStaticByteField', JNIEnv_p, jclass, jfieldID, jbyte),
    (None, 'SetStaticCharField', JNIEnv_p, jclass, jfieldID, jchar),
    (None, 'SetStaticShortField', JNIEnv_p, jclass, jfieldID, jshort),
    (None, 'SetStaticIntField', JNIEnv_p, jclass, jfieldID, jint),
    (None, 'SetStaticLongField', JNIEnv_p, jclass, jfieldID, jlong),
    (None, 'SetStaticFloatField', JNIEnv_p, jclass, jfieldID, jfloat),
    (None, 'SetStaticDoubleField', JNIEnv_p, jclass, jfieldID, jdouble),

    (jstring, 'NewString', JNIEnv_p, jchar_p, jsize),
    (jsize, 'GetStringLength', JNIEnv_p, jstring),
    (jchar_p, 'GetStringChars', JNIEnv_p, jstring, POINTER(jboolean)),
    (None, 'ReleaseStringChars', JNIEnv_p, jstring, jchar_p),

    (jstring, 'NewStringUTF', JNIEnv_p, c_char_p),
    (jsize, 'GetStringUTFLength', JNIEnv_p, jstring),
    (c_char_p, 'GetStringUTFChars', JNIEnv_p, jstring, POINTER(jboolean)),
    (None, 'ReleaseStringUTFChars', JNIEnv_p, jstring, c_char_p),

    (jsize, 'GetArrayLength', JNIEnv_p, jarray),

    (jobjectArray, 'NewObjectArray', JNIEnv_p, jsize, jclass, jobject),
    (jobject, 'GetObjectArrayElement', JNIEnv_p, jobjectArray, jsize),
    (None, 'SetObjectArrayElement', JNIEnv_p, jobjectArray, jsize, jobject),

    (jbooleanArray, 'NewBooleanArray', JNIEnv_p, jsize),
    (jbyteArray, 'NewByteArray', JNIEnv_p, jsize),
    (jcharArray, 'NewCharArray', JNIEnv_p, jsize),
    (jshortArray, 'NewShortArray', JNIEnv_p, jsize),
    (jintArray, 'NewIntArray', JNIEnv_p, jsize),
    (jlongArray, 'NewLongArray', JNIEnv_p, jsize),
    (jfloatArray, 'NewFloatArray', JNIEnv_p, jsize),
    (jdoubleArray, 'NewDoubleArray', JNIEnv_p, jsize),

    (POINTER(jboolean), 'GetBooleanArrayElements', JNIEnv_p, jbooleanArray, POINTER(jboolean)),
    (POINTER(jbyte), 'GetByteArrayElements', JNIEnv_p, jbyteArray, POINTER(jboolean)),
    (POINTER(jchar), 'GetCharArrayElements', JNIEnv_p, jcharArray, POINTER(jboolean)),
    (POINTER(jshort), 'GetShortArrayElements', JNIEnv_p, jshortArray, POINTER(jboolean)),
    (POINTER(jint), 'GetIntArrayElements', JNIEnv_p, jintArray, POINTER(jboolean)),
    (POINTER(jlong), 'GetLongArrayElements', JNIEnv_p, jlongArray, POINTER(jboolean)),
    (POINTER(jfloat), 'GetFloatArrayElements', JNIEnv_p, jfloatArray, POINTER(jboolean)),
    (POINTER(jdouble), 'GetDoubleArrayElements', JNIEnv_p, jdoubleArray, POINTER(jboolean)),

    (None, 'ReleaseBooleanArrayElements', JNIEnv_p, jbooleanArray, POINTER(jboolean), jint),
    (None, 'ReleaseByteArrayElements', JNIEnv_p, jbyteArray, POINTER(jbyte), jint),
    (None, 'ReleaseCharArrayElements', JNIEnv_p, jcharArray, POINTER(jchar), jint),
    (None, 'ReleaseShortArrayElements', JNIEnv_p, jshortArray, POINTER(jshort), jint),
    (None, 'ReleaseIntArrayElements', JNIEnv_p, jintArray, POINTER(jint), jint),
    (None, 'ReleaseLongArrayElements', JNIEnv_p, jlongArray, POINTER(jlong), jint),
    (None, 'ReleaseFloatArrayElements', JNIEnv_p, jfloatArray, POINTER(jfloat), jint),
    (None, 'ReleaseDoubleArrayElements', JNIEnv_p, jdoubleArray, POINTER(jdouble), jint),

    (None, 'GetBooleanArrayRegion', JNIEnv_p, jbooleanArray, jsize, jsize, POINTER(jboolean)),
    (None, 'GetByteArrayRegion', JNIEnv_p, jbyteArray, jsize, jsize, POINTER(jbyte)),
    (None, 'GetCharArrayRegion', JNIEnv_p, jcharArray, jsize, jsize, POINTER(jchar)),
    (None, 'GetShortArrayRegion', JNIEnv_p, jshortArray, jsize, jsize, POINTER(jshort)),
    (None, 'GetIntArrayRegion', JNIEnv_p, jintArray, jsize, jsize, POINTER(jint)),
    (None, 'GetLongArrayRegion', JNIEnv_p, jlongArray, jsize, jsize, POINTER(jlong)),
    (None, 'GetFloatArrayRegion', JNIEnv_p, jfloatArray, jsize, jsize, POINTER(jfloat)),
    (None, 'GetDoubleArrayRegion', JNIEnv_p, jdoubleArray, jsize, jsize, POINTER(jdouble)),

    (None, 'SetBooleanArrayRegion', JNIEnv_p, jbooleanArray, jsize, jsize, POINTER(jboolean)),
    (None, 'SetByteArrayRegion', JNIEnv_p, jbyteArray, jsize, jsize, POINTER(jbyte)),
    (None, 'SetCharArrayRegion', JNIEnv_p, jcharArray, jsize, jsize, POINTER(jchar)),
    (None, 'SetShortArrayRegion', JNIEnv_p, jshortArray, jsize, jsize, POINTER(jshort)),
    (None, 'SetIntArrayRegion', JNIEnv_p, jintArray, jsize, jsize, POINTER(jint)),
    (None, 'SetLongArrayRegion', JNIEnv_p, jlongArray, jsize, jsize, POINTER(jlong)),
    (None, 'SetFloatArrayRegion', JNIEnv_p, jfloatArray, jsize, jsize, POINTER(jfloat)),
    (None, 'SetDoubleArrayRegion', JNIEnv_p, jdoubleArray, jsize, jsize, POINTER(jdouble)),

    (jint, 'RegisterNatives', JNIEnv_p, jclass, POINTER(JNINativeMethod), jint),
    (jint, 'UnregisterNatives', JNIEnv_p, jclass),

    (jint, 'MonitorEnter', JNIEnv_p, jobject),
    (jint, 'MonitorExit', JNIEnv_p, jobject),

    (jint, 'GetJavaVM', JNIEnv_p, POINTER(JavaVM_p)),

    (None, 'GetStringRegion', JNIEnv_p, jstring, jsize, jsize, jchar_p),
    (None, 'GetStringUTFRegion', JNIEnv_p, jstring, jsize, jsize, c_char_p),

    (c_void_p, 'GetPrimitiveArrayCritical', JNIEnv_p, jarray, POINTER(jboolean)),
    (None, 'ReleasePrimitiveArrayCritical', JNIEnv_p, jarray, c_void_p, jint),

    (jchar_p, 'GetStringCritical', JNIEnv_p, jstring, POINTER(jboolean)),
    (None, 'ReleaseStringCritical', JNIEnv_p, jstring, jchar_p),

    (jweak, 'NewWeakGlobalRef', JNIEnv_p, jobject),
    (None, 'DeleteWeakGlobalRef', JNIEnv_p, jweak),

    (jboolean, 'ExceptionCheck', JNIEnv_p),

    (jobject, 'NewDirectByteBuffer', JNIEnv_p, c_void_p, jlong),
    (c_void_p, 'GetDirectBufferAddress', JNIEnv_p, jobject),
    (jlong, 'GetDirectBufferCapacity', JNIEnv_p, jobject),

    (int, 'GetObjectRefType', JNIEnv_p, jobject),
    (jobject, 'GetModule', JNIEnv_p, jclass),
))


class JavaVMOption(Structure):
    _fields_ = (
        ('optionString', c_char_p),
        ('extraInfo', c_void_p),
    )


class JavaVMInitArgs(Structure):
    _fields_ = (
        ('version', jint),
        ('nOptions', jint),
        ('options', POINTER(JavaVMOption)),
        ('ignoreUnrecognized', jboolean),
    )


class JavaVMAttachArgs(Structure):
    _fields_ = (
        ('version', jint),
        ('name', c_char_p),
        ('group', jobject),
    )


libjvm = CDLL(find_libjvm())

libjvm.JNI_GetDefaultJavaVMInitArgs.retval = jint
libjvm.JNI_GetDefaultJavaVMInitArgs.argstype = [POINTER(JavaVMInitArgs)]

libjvm.JNI_CreateJavaVM.retval = jint
libjvm.JNI_CreateJavaVM.argstype = [POINTER(JavaVM_p), POINTER(c_void_p), c_void_p]

libjvm.JNI_GetCreatedJavaVMs.retval = jint
libjvm.JNI_GetCreatedJavaVMs.argstype = [POINTER(JavaVM_p), jsize, POINTER(jsize)]

JNI_VERSION_1_1 = 0x00010001
JNI_VERSION_1_2 = 0x00010002
JNI_VERSION_1_4 = 0x00010004
JNI_VERSION_1_6 = 0x00010006
JNI_VERSION_1_8 = 0x00010008
JNI_VERSION_9 = 0x00090000
JNI_VERSION_10 = 0x000a0000

vm = JavaVM_p()
ENCODING = py2jdbc.mutf8.NAME


def encode(s):
    """
    Encode a unicode string using Java's modified UTF-8 with a trailing zero byte.

    :param s: unicode string to encode
    :return: the encoded bytes
    """
    return (codecs.encode(s, ENCODING) if isinstance(s, six.text_type) else s) + six.b('\0')


def decode(s):
    """
    Decode a sequence of byte/characters into a Python unicode string.

    :param s: a sequence of bytes
    :return: the decoded unicode string
    """
    return (
        codecs.decode(s.rstrip(six.b('\0')), ENCODING)
        if isinstance(s, six.binary_type)
        else s
    )


def get_env(**kwargs):
    """
    Create or Fetch the JNIEnv pointer for this thread.

    :param kwargs: a dictionary of options to pass to the JVM.
        version: the requested JNI version
        classpath: a string or list of strings to use for the classpath.
        verbose: a string or list of strings for '-verbose:' options
        check: a string or list of strings for '-check:' options
    :return: the local JNIEnv pointer.
    """
    global vm

    kwargs.setdefault('classpath', get_classpath('./lib'))
    kwargs.setdefault('version', JNI_VERSION_1_2)
    _env = JNIEnv_p()
    if vm:
        ret = vm[0].AttachCurrentThread(byref(_env), None)
        if ret != JNI_OK:
            raise RuntimeError("unable to attach to JVM")
    else:
        vm_args = JavaVMInitArgs()
        vm_args.version = kwargs['version']
        ret = libjvm.JNI_GetDefaultJavaVMInitArgs(byref(vm_args))
        if ret != JNI_OK:
            raise RuntimeError("unable to get default JVM arguments")
        opts = []
        for k, v in six.iteritems(kwargs):
            if k == 'classpath':
                if isinstance(v, six.string_types):
                    opts.append('-Djava.class.path={}'.format(v))
                else:
                    opts.append('-Djava.class.path={}'.format(CP_SEP.join(v)))
            elif k == 'verbose':
                if isinstance(v, six.string_types):
                    opts.append('-verbose:{}'.format(v))
                else:
                    opts += ['-verbose:{}'.format(x) for x in v]
            elif k == 'check':
                if isinstance(v, six.string_types):
                    opts.append('-Xcheck:{}'.format(v))
                else:
                    opts += ['-Xcheck:{}'.format(x) for x in v]
        if opts:
            options = JavaVMOption.__mul__(len(opts))()
            for i, opt in enumerate(opts):
                # noinspection PyPep8Naming
                options[i].optionString = encode(opt)
                # noinspection PyPep8Naming
                options[i].extraInfo = None
        else:
            options = None
        vm_args.nOptions = len(opts)
        vm_args.options = options
        vm_args.ignoreUnrecognized = JNI_FALSE
        ret = libjvm.JNI_CreateJavaVM(byref(vm), byref(_env), byref(vm_args))
        if ret != JNI_OK:
            raise RuntimeError("unable to Launch JVM")
    return _env[0]


def destroy_vm():
    global vm
    if vm:
        vm[0].DetachCurrentThread()
        vm[0].DestroyJavaVM()
        vm.values = None


def get_class_name(env, obj):
    """
    Return the class name of an object.

    :param env: the JNIEnv environment
    :param obj: a Java object instance
    :return: a Python string name of the Java object class
    """
    class1 = env.GetObjectClass(obj)
    mid_get_class = env.GetMethodID(class1, 'getClass', '()Ljava/lang/Class;')
    args = jvalue.__mul__(0)()
    obj2 = env.CallObjectMethodA(obj, mid_get_class, args)
    class2 = env.GetObjectClass(obj2)
    mid_get_name = env.GetMethodID(class2, 'getName', '()Ljava/lang/String;')
    s = env.CallObjectMethodA(class1, mid_get_name, args)
    chars = env.GetStringUTFChars(s, None)
    env.DeleteLocalRef(class1)
    env.DeleteLocalRef(obj2)
    env.DeleteLocalRef(class2)
    env.DeleteLocalRef(s)
    return decode(chars)


atexit.register(destroy_vm)


# noinspection PyUnusedLocal
def signal_handler(sig, frame):
    raise RuntimeError("encountered signal")


signal.signal(signal.SIGHUP, signal_handler)
