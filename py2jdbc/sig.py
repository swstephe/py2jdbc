# -*- coding: utf8 -*-
import six
import py2jdbc.jni


class JSigType(type):
    """
    Metaclass for all signature objects which registers the class definition
    to a lookup on the signature characters.
    """
    registry = {}

    def __new__(mcs, clsname, bases, attrs):
        newclass = super(JSigType, mcs).__new__(mcs, clsname, bases, attrs)
        mcs.registry[getattr(newclass, 'code')] = newclass
        return newclass


class JSig(six.with_metaclass(JSigType)):
    """
    Base class for all signature types.

    Stores the local environment and defines a placeholder for releasing memory.

    Base classes map actual JNIEnv functions to call when the type is
    referenced.
    """
    code = None

    def __init__(self, env):
        self.env = env
        self._release = False

    @property
    def name(self):
        """
        Convenience property which returns the type name from the class name.
        This is so "JSigVoid" will return "Void", which can be used in
        constructing names like "CallVoidMethodA".

        :return: the signature type name derived from the class name.
        """
        return self.__class__.__name__[4:]

    def release(self, value):
        """
        Release memory from a bound value.

        :param value: the bound value
        """
        pass


class JSigVoid(JSig):
    """
    Signature Type for Void methods and static methods.
    """
    code = 'V'

    def __init__(self, env):
        super(JSigVoid, self).__init__(env)
        self._fn_call = env.CallVoidMethodA
        self._fn_call_static = env.CallStaticVoidMethodA

    def call(self, obj, mid, argtypes, *args):
        """
        Encapsulate CallVoidMethod

        :param obj: a Java object instance
        :param mid: the methodID of the method to call
        :param argtypes: a sequence of argument signature types
        :param args: the Python arguments to bind
        """
        _args = method_args(argtypes, *args)
        self._fn_call(obj, mid, _args)
        for _a, _at in zip(_args, argtypes):
            _at.release(_a.l)

    def call_static(self, cls, mid, argtypes, *args):
        """
        Encapsulate CallStaticVoidMethod

        :param cls: a Java class object
        :param mid: the methodID of the static method to call
        :param argtypes: a list of argument signature types
        :param args: the Python arguments to bind
        """
        _args = method_args(argtypes, *args)
        self._fn_call_static(cls, mid, _args)
        for _a, _at in zip(_args, argtypes):
            _at.release(_a.l)


class JSigScalar(JSig):
    """
    This is the base class for any singature type which returns
    a scalar primitive, (not arrays or objects).  It automatically maps
    the field and method calls based on the subclass name.
    """
    def __init__(self, env):
        super(JSigScalar, self).__init__(env)
        self._fn_call = getattr(env, 'Call{}MethodA'.format(self.name))
        self._fn_call_static = getattr(env, 'CallStatic{}MethodA'.format(self.name))
        self._fn_get = getattr(env, 'Get{}Field'.format(self.name))
        self._fn_set = getattr(env, 'Set{}Field'.format(self.name))
        self._fn_get_static = getattr(env, 'GetStatic{}Field'.format(self.name))
        self._fn_set_static = getattr(env, 'SetStatic{}Field'.format(self.name))

    def j2py(self, value):
        """
        In most cases, (byte, short, int, long, float, etc), the Java
        value is the same as the Python value.
        :param value: a Python value
        :return: the value for Java
        """
        return value

    def py2j(self, value):
        """
        In most cases, the Python value is the same as the Java value.

        :param value: a Java value
        :return: the value for Java
        """
        return value

    @property
    def jtype(self):
        """
        The JNI type that is being returned.
        So that: `JSigByte().jtype == jbyte`

        :return: a JNI primitive type
        """
        return getattr(py2jdbc.jni, 'j' + self.name[0].lower() + self.name[1:])

    def jval(self, jval, value):
        """
        Assign a jvalue union to a value using the matching tag.

        :param jval: a jvalue union
        :param value: a Python value
        """
        setattr(jval, self.code.lower(), self.py2j(value))

    def get(self, obj, fid):
        """
        Fetch a non-static field value

        :param obj: a Java object instance
        :param fid: the fieldID of the field
        :return: the value of the field, converted to Python
        """
        value = self._fn_get(obj, fid)
        return self.j2py(value)

    def set(self, obj, fid, value):
        """
        Set a non-static field value

        :param obj: a Java object instance
        :param fid: the fieldID of the field
        :param value: the Python value to assign to the field
        """
        self._fn_set(obj, fid, self.py2j(value))

    def get_static(self, cls, fid):
        """
        Fetch a static field value

        :param cls: a Java class object
        :param fid: the fieldID of the field
        :return: the value of the static field, converted to Python
        """
        value = self._fn_get_static(cls, fid)
        return self.j2py(value)

    def set_static(self, cls, fid, value):
        """
        Set a static field value

        :param cls: a Java class object
        :param fid: the fieldID of the field
        :param value: the Python value to assign to the field
        """
        self._fn_set_static(cls, fid, self.py2j(value))

    def call(self, obj, mid, argtypes, *args):
        """
        Call a non-static method

        :param obj: a Java object instance
        :param mid: the methodID of the method to call
        :param argtypes: a sequence of argument signature types
        :param args: the Python arguments to bind
        :return: the primitive value result of the method
        """
        _args = method_args(argtypes, *args)
        value = self._fn_call(obj, mid, _args)
        for _a, _at in zip(_args, argtypes):
            _at.release(_a.l)
        result = self.j2py(value)
        self.release(value)
        return result

    def call_static(self, cls, mid, argtypes, *args):
        """
        Call a static method

        :param cls: a Java class object
        :param mid: the methodID of the method
        :param argtypes: a sequence of argument signature types
        :param args: the Python arguments to the method
        :return: the primitive value result of the static method
        """
        _args = method_args(argtypes, *args)
        value = self._fn_call_static(cls, mid, _args)
        for _a, _at in zip(_args, argtypes):
            _at.release(_a.l)
        result = self.j2py(value)
        self.release(value)
        return result


class JSigBoolean(JSigScalar):
    """
    Singature type for Java booleans.

    The conversion functions convert JNI_TRUE/JNI_FALSE
    to and from Python booleans.
    """
    code = 'Z'

    def j2py(self, value):
        """
        Convert a Java jboolean to a Python boolean value
        :param value: the Java jboolean
        :return: the Python boolean value
        """
        assert value in (py2jdbc.jni.JNI_FALSE, py2jdbc.jni.JNI_TRUE)
        return value == py2jdbc.jni.JNI_TRUE

    def py2j(self, value):
        """
        Convert a Python boolean to a Java jboolean value

        :param value: the Python boolean value
        :return: a Java jboolean
        """
        return py2jdbc.jni.JNI_TRUE if value else py2jdbc.jni.JNI_FALSE


class JSigByte(JSigScalar):
    """
    Signature type for Java bytes.
    """
    code = 'B'

    def py2j(self, value):
        """
        Convert a Python value to a Java byte value.
        This implemenation converts to byte so you can say::

            py2j('123')
            py2j(123.45)

        :param value: a Python value
        :return: a jbyte value
        """
        return int(value)


class JSigChar(JSigScalar):
    """
    Signature type for Java char
    """
    code = 'C'

    def j2py(self, value):
        """
        Convert a Java char value to Python

        :param value: a jchar (short) value
        :return: a Python unicode character
        """
        # noinspection PyCompatibility
        return six.unichr(value)

    def py2j(self, value):
        """
        Convert a Python value to a Java jchar
        :param value: a Python value
        :return: a Java jchar value
        """
        return ord(value)


class JSigShort(JSigScalar):
    """
    Signature type for Java short
    """
    code = 'S'

    def py2j(self, value):
        """
        Convert a Python value to a Java jshort
        :param value: a Python value which can be converted to int
        :return: a Java jshort
        """
        return int(value)


class JSigInt(JSigScalar):
    """
    A Signature type for Java int
    """
    code = 'I'

    def py2j(self, value):
        """
        Converts a Python value to a Java jint

        :param value: a Python value which can be converted to int
        :return: a Java jint
        """
        return int(value)


class JSigLong(JSigScalar):
    """
    A Signature type for Java long
    """
    code = 'J'

    def py2j(self, value):
        """
        Converts a Python value to a Java jlong

        :param value: a Python value which can be converted to int
        :return: a Java jlong
        """
        return int(value)


class JSigFloat(JSigScalar):
    """
    A Signature type for Java float
    """
    code = 'F'

    def py2j(self, value):
        """
        Converts a Python value to a Java jfloat

        :param value: a Python value which can be converted to float
        :return: a Java jfloat
        """
        return float(value)


class JSigDouble(JSigScalar):
    """
    A Signature type for Java double
    """
    code = 'D'

    def py2j(self, value):
        """
        Converts a Python value to a Java jdouble

        :param value: a Python value which can be converted to float
        :return: a Java jdouble
        """
        return float(value)


class JSigObject(JSigScalar):
    """
    A Signature type for Java objects
    """
    code = 'L'

    def __init__(self, env, class_name):
        super(JSigObject, self).__init__(env)
        self.classname = class_name.replace('.', '/')

    def j2py(self, value):
        """
        Try to convert a Java object instance to
        a Python object.  It automatically converts Java
        strings to Python strings, otherwise it passes
        the object for higher level wrapping.

        :param value: a Java object instance
        :return: a Java string or object instance.
        """
        if self.classname == 'java/lang/String':
            chars = self.env.GetStringUTFChars(value)
            self.env.DeleteLocalRef(value)
            return py2jdbc.jni.decode(chars)
        return super(JSigObject, self).j2py(value)

    def py2j(self, value):
        """
        Try to convert a Python value to a Java object.
        Supports automatic conversion of Python strings,
        otherwise it expects higher level wrappers will
        convert.

        :param value: a java object or Python string
        :return: a java object
        """
        if self.classname == 'java/lang/String':
            value = self.env.NewStringUTF(value)
            self._release = True
            return value
        return super(JSigObject, self).py2j(value)

    def new(self, cls, mid, argtypes, *args):
        """
        Call a construtor on an object instance

        :param cls: a Java class object
        :param mid: the methodID of the constructor
        :param argtypes: a sequence of argument signature types
        :param args: the Python arguments to the constructor
        :return: the created object
        """
        _args = method_args(argtypes, *args)
        obj = self.env.NewObjectA(cls, mid, _args)
        for _a, _at in zip(_args, argtypes):
            _at.release(_a.l)
        return obj

    def release(self, value):
        """
        Delete the local reference for java strings.
        :param value: the original java object
        """
        if self._release:
            self.env.DeleteLocalRef(value)
            self._release = False


class JSigArray(JSig):
    """
    The base class for arrays of primitive types or objects.

    Instances can map a jarray to a Python list of ints,
    or convert back from a Python sequence of ints back into a jbyteArray,
    for example.
    """
    def __init__(self, env):
        super(JSigArray, self).__init__(env)
        self._fn_get_elements = getattr(env, 'Get{}Elements'.format(self.name))
        self._fn_release_elements = getattr(env, 'Release{}Elements'.format(self.name))
        self._fn_new = getattr(env, 'New{}'.format(self.name))
        self._fn_set_region = getattr(env, 'Set{}Region'.format(self.name))
        self._fn_call = env.CallObjectMethodA
        self._fn_call_static = env.CallStaticObjectMethodA

    @property
    def jtype(self):
        """
        Maps in function calls by looking at the class name.

        JSigBooleanArray => jbooleanArray
        :return: the jni module array type.
        """
        return getattr(py2jdbc.jni, 'j' + self.name[0].lower() + self.name[1:-5])

    def jval(self, jval, value):
        """
        Assign a jvalue union to a value using the matching tag.

        :param jval: a jvalue union
        :param value: a Python value
        """
        setattr(jval, 'l', self.py2j(value))

    def elem_j2py(self, value):
        """
        Each element is, by default, itself.
        :param value:  the Java primitive value
        :return: a Python value
        """
        return value

    def j2py(self, value):
        """
        Convert a Java array to a Python list by applying `elem_j2py`
        to each element.

        :param value: a Java array object
        :return: a Python list of values
        """
        _len = self.env.GetArrayLength(value)
        _values = self._fn_get_elements(value, None)
        result = [self.elem_j2py(_values[i]) for i in range(_len)]
        self._fn_release_elements(value, _values, py2jdbc.jni.JNI_ABORT)
        return result

    def elem_py2j(self, value):
        """
        Convert a python element value to a Java primitive value.
        By default, the values are the same

        :param value: the Python value
        :return: a Java primitive value
        """
        return value

    def py2j(self, value):
        """
        Convert a Python sequence of values to a Java array type.

        :param value: a Python sequence, (list, tuple, generator, etc).
        :return: a Java array value
        """
        _len = len(value)
        result = self._fn_new(_len)
        _values = self.jtype.__mul__(_len)(*(self.elem_py2j(v) for v in value))
        self._fn_set_region(result, 0, _len, _values)
        return result

    def call(self, obj, mid, argtypes, *args):
        """
        Call a non-static method and return a Python list of values
        representing the Java array return value.

        :param obj: a Java object instance
        :param mid: the methodId of the method
        :param argtypes: a sequence of argument signature objects
        :param args: Python value arguments to method
        :return: a Python list of values
        """
        _args = method_args(argtypes, *args)
        value = self._fn_call(obj, mid, _args)
        for _a, _at in zip(_args, argtypes):
            _at.release(_a.l)
        result = self.j2py(value)
        self.release(value)
        return result

    def call_static(self, cls, mid, argtypes, *args):
        """
        Call a static method and return a Python list of values
        representing the Java array return value.

        :param cls: a Java class object
        :param mid: the methodId of the static method
        :param argtypes: a sequence of argument signature objects
        :param args: Python value arguments to method
        :return: a Python list of values
        """
        _args = method_args(argtypes, *args)
        value = self._fn_call_static(cls, mid, _args)
        for _a, _at in zip(_args, argtypes):
            _at.release(_a.l)
        result = self.j2py(value)
        self.release(value)
        return result

    def release(self, value):
        """
        Free memory from the allocated array values.
        :param value: a Java array value
        """
        self.env.DeleteLocalRef(value)


class JSigBooleanArray(JSigArray):
    """
    A Signature type for boolean arrays.
    """
    code = '[Z'

    def elem_j2py(self, value):
        """
        Convert each element of a jbooleanArray to a Python boolean

        :param value: a jboolean element
        :return: a Python boolean
        """
        return value == py2jdbc.jni.JNI_TRUE

    def elem_py2j(self, value):
        """
        Convert each element of a Python list to a jboolean

        :param value: a Python boolean
        :return: a jboolean value
        """
        return py2jdbc.jni.JNI_TRUE if value else py2jdbc.jni.JNI_FALSE


class JSigByteArray(JSigArray):
    """
    A Signature Type for byte arrays.
    """
    code = '[B'

    def j2py(self, value):
        """
        Convert a Java byte array into a Python binary sequence.
        That would be `bytes` in Python 3 or `str` in Python 2.

        :param value: a Java byteArray object
        :return: a Python single-byte string
        """
        _len = self.env.GetArrayLength(value)
        _values = self._fn_get_elements(value, None)
        result = b''.join(six.int2byte(_values[i] & 0xff) for i in range(_len))
        self._fn_release_elements(value, _values, py2jdbc.jni.JNI_ABORT)
        return result

    def py2j(self, value):
        """
        Convert a Python binary string to a Java byteArray

        :param value: a Python byte string
        :return: a Java byteArray
        """
        _len = len(value)
        result = self._fn_new(_len)
        _values = self.jtype.__mul__(_len)(*value)
        self._fn_set_region(result, 0, _len, _values)
        return result


class JSigCharArray(JSigArray):
    """
    A Signature Type for char arrays.
    """
    code = '[C'

    def elem_j2py(self, value):
        """
        Convert each element of a jcharArray to a Python unicode char

        :param value: a jchar (short) element
        :return: a Python unicode char
        """
        # noinspection PyCompatibility
        return six.unichr(value)

    def elem_py2j(self, value):
        """
        Convert each element of a Python unicode sequence to a jchar

        :param value: a Python char element
        :return: a jchar (short)
        """
        return ord(value)


class JSigShortArray(JSigArray):
    """
    A Signature type for a short array
    """
    code = '[S'

    def elem_py2j(self, value):
        """
        Convert each Python value to a jshort value

        :param value: a Python value which can be converted to int
        :return: a Java jshort value
        """
        return int(value)


class JSigIntArray(JSigArray):
    """
    A Signature type for an int array
    """
    code = '[I'

    def elem_py2j(self, value):
        """
        Convert each Python value to a jint value

        :param value: a Python value which can be converted to int
        :return: a Java jint value
        """
        return int(value)


class JSigLongArray(JSigArray):
    """
    A Signature type for a long array
    """
    code = '[J'

    def elem_py2j(self, value):
        """
        Convert each Python value to a jlong value

        :param value: a Python value which can be converted to int
        :return: a Java jlong value
        """
        return int(value)


class JSigFloatArray(JSigArray):
    """
    A Signature type for a float array
    """
    code = '[F'

    def elem_py2j(self, value):
        """
        Convert each Python value to a jfloat value

        :param value: a Python value which can be converted to float
        :return: a Java jfloat value
        """
        return float(value)


class JSigDoubleArray(JSigArray):
    """
    A Signature type for a double array
    """
    code = '[D'

    def elem_py2j(self, value):
        """
        Convert each Python value to a jdouble value

        :param value: a Python value which can be converted to a float
        :return:  a Java jdouble value
        """
        return float(value)


class JSigObjectArray(JSig):
    """
    A Signature type for object arrays.
    """
    code = '[L'

    def __init__(self, env, class_name):
        super(JSigObjectArray, self).__init__(env)
        self.class_name = class_name
        self.cls = self.env.FindClass(self.class_name)
        self._fn_get_element = env.GetObjectArrayElement
        self._fn_new = env.NewObjectArray
        self._fn_set_element = env.SetObjectArrayElement

    @property
    def jtype(self):
        return py2jdbc.jni.jobjectArray

    def jval(self, jval, value):
        """
        Assign a jvalue union to a value using the matching tag.

        :param jval: a jvalue union
        :param value: a Python value
        """
        setattr(jval, 'l', self.py2j(value))

    def elem_j2py(self, value):
        """
        Convert each element of an objct array to a string
        if element type is java/lang/String.

        :param value:
        :return:
        """
        if self.class_name == 'java/lang/String':
            value = self.env.GetStringUTFChars(value)
            return py2jdbc.jni.decode(value)
        return value

    def j2py(self, value):
        """
        Convert a Java objectArray into a list of Python objects.

        :param value: a Java objectarray
        :return: a list of Python objects.
        """
        _len = self.env.GetArrayLength(value)
        return [
            self.elem_j2py(self.env.GetObjectArrayElement(value, i))
            for i in range(_len)
        ]

    def elem_py2j(self, value):
        """
        Convert each element of a Python sequence to a Java object
        :param value: a Python value
        :return: a Java jobject
        """
        if isinstance(value, six.string_types):
            value = self.env.NewStringUTF(value.encode('utf8'))
            self._release = True
        return value

    def py2j(self, value):
        """
        Convert a Python sequence of values to a Java objectArray.

        :param value: a Python sequence of values
        :return: a Java objectArray
        """
        _len = len(value)
        result = self.env.NewObjectArray(_len, self.cls, None)
        for i, v in enumerate(value):
            self.env.SetObjectArrayElement(result, i, self.elem_py2j(v))
        return result

    def call(self, obj, mid, argtypes, *args):
        """
        Call a method on an object instance.

        :param obj: a Java object instance
        :param mid: the class methodID
        :param argtypes: a sequence of Signature argument types
        :param args: a sequence of python arguments
        :return: a Python list of object or string elements
        """
        _args = method_args(argtypes, *args)
        value = self.env.CallObjectMethodA(obj, mid, _args)
        for _a, _at in zip(_args, argtypes):
            _at.release(_a.l)
        result = self.j2py(value)
        self.release(value)
        return result

    def call_static(self, cls, mid, argtypes, *args):
        """
        Call a static method on a Java class object

        :param cls: a Java class object
        :param mid: the class methodID
        :param argtypes: a sequence of Signature argument types
        :param args: a sequence of python arguments
        :return: a Python list of object or string elements
        """
        _args = method_args(argtypes, *args)
        value = self.env.CallStaticObjectMethodA(cls, mid, _args)
        for _a, _at in zip(_args, argtypes):
            _at.release(_a.l)
        result = self.j2py(value)
        self.release(value)
        return result

    def release(self, value):
        """
        Release memory allocated while constructing objectArray values.

        :param value: the original jobjectArray value
        """
        if self._release:
            _len = self.env.GetArrayLength(value)
            for i in range(_len):
                v = self.env.GetObjectArrayElement(value, i)
                self.env.DeleteLocalRef(v)
        self.env.DeleteLocalRef(value)


def type_signature(env, signature):
    """
    Create a generator which parses a signature and returns
    a sequence of signature types.  This can be used with
    either a return type or a sequence of argument types.

    :param env: the current JNI environment
    :param signature: the Java signature
    :return: a generator which produces a sequence of matching signature types
    """
    is_array = False
    i = 0
    while i < len(signature):
        if signature[i] == ')':
            break
        if signature[i] == 'V':
            yield JSigVoid(env)
        elif signature[i] == 'L':
            j = signature.find(';', i)
            if j < 0:
                raise RuntimeError("couldn't find ';' in class id")
            class_name = signature[i + 1:j]
            i = j
            if is_array:
                yield JSigObjectArray(env, class_name)
                is_array = False
            else:
                yield JSigObject(env, class_name)
        elif signature[i] == '[':
            is_array = True
        else:
            if is_array:
                yield JSigType.registry['[' + signature[i]](env)
                is_array = False
            else:
                yield JSigType.registry[signature[i]](env)
        i += 1


def method_signature(env, signature):
    """
    Given a signature for a method, parse and return a tuple
    of argument signature types and a result type.

    The returned values can be used to filter Python values
    into method arguments, call the appropriate method
    function, then convert the result type back to a Python type.

    :param env: the current JNI environment
    :param signature: the Java method signature
    :return: a tuple of argument types and a result type
    """
    assert signature[0] == '('
    argtypes = tuple(type_signature(env, signature[1:]))
    restype = next(type_signature(env, signature[signature.index(')') + 1:]))
    return argtypes, restype


def constructor_signature(env, class_name, signature):
    """
    Given a signature for a method, (just the arguments),
    parse and return a tuple of argument signature types and a result type.

    The returned values can be used to filter Python values into
    constructor arguments and call the NewObject function.
    :param env: the current JNI environment
    :param class_name: the name of the class of the object to create
    :param signature: the Java constructor argument signature
    :return: a tuple of argument types and a result type
    """
    argtypes = tuple(type_signature(env, signature))
    restype = JSigObject(env, class_name)
    return argtypes, restype


def method_args(argtypes, *args):
    """
    Given a tuple of argument types, (see `method_signature`),
    process the subsequent Python values, converting them
    to the appropriate Java types and returns an array of
    jvalue objects, (for calling MethodA functions).

    :param argtypes: a tuple of argument signature types created by `method_signature`.
    :param args: subsequent Python values
    :return: the converted
    """
    _args = py2jdbc.jni.jvalue.__mul__(len(argtypes))()
    for i in range(len(argtypes)):
        argtypes[i].jval(_args[i], args[i])
    return _args
