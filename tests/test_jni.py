# -*- coding: utf8 -*-
import random
from ctypes import byref, string_at
import logging
import pytest
from tests.config import (
    CLASSPATH, JAVA_OPTS, BOOLEANS,
    MIN_BYTE, MAX_BYTE,
    MIN_CHAR, MAX_CHAR,
    MIN_SHORT, MAX_SHORT,
    MIN_LONG, MAX_LONG,
    MIN_INT, MAX_INT,
    MIN_FLOAT, MAX_FLOAT,
    MIN_DOUBLE, MAX_DOUBLE
)
from py2jdbc import jni

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

_env = None


class TObject(object):
    class_name = 'java.lang.Object'
    cls = None

    def __init__(self, obj):
        if self.cls is None:
            self.cls = _env.FindClass(self.class_name)
        self._equals = _env.GetMethodID(self.cls, 'equals', '(Ljava/lang/Object;)Z')
        jni.check_exception(_env)
        self.obj = obj

    def __del__(self):
        if self.obj:
            _env.DeleteLocalRef(self.obj)
        self.obj = None
        if self.cls:
            _env.DeleteLocalRef(self.cls)
        self.cls = None

    def __eq__(self, obj):
        args = jni.jvalue.__mul__(1)()
        setattr(args[0], 'l', obj)
        value = _env.CallBooleanMethodA(obj, self._equals, args)
        jni.check_exception(_env)
        assert value is not None
        return value

    def __ne__(self, obj):
        return not self.__eq__(obj)


class TClass(TObject):
    class_name = 'java.lang.Class'

    def __init__(self, obj):
        super(TClass, self).__init__(obj)
        self._forName = _env.GetStaticMethodID(
            self.cls,
            'forName',
            '(Ljava/lang/String;)Ljava/lang/Class;'
        )
        jni.check_exception(_env)
        assert self._forName is not None
        self._getDeclaredField = _env.GetMethodID(
            self.cls,
            'getDeclaredField',
            '(Ljava/lang/String;)Ljava/lang/reflect/Field;'
        )
        jni.check_exception(_env)
        assert self._getDeclaredField is not None
        self._getDeclaredMethod = _env.GetMethodID(
            self.cls,
            'getDeclaredMethod',
            '(Ljava/lang/String;[Ljava/lang/Class;)Ljava/lang/reflect/Method;'
        )
        jni.check_exception(_env)
        assert self._getDeclaredMethod is not None
        self._getName = _env.GetMethodID(
            self.cls,
            'getName',
            '()Ljava/lang/String;'
        )
        jni.check_exception(_env)
        assert self._getName is not None

    def getDeclaredField(self, name):
        str_obj = _env.NewStringUTF(name)
        jni.check_exception(_env)
        assert str_obj is not None
        args = jni.jvalue.__mul__(1)()
        setattr(args[0], 'l', str_obj)
        field = _env.CallObjectMethodA(self.obj, self._getDeclaredField, args)
        jni.check_exception(_env)
        _env.DeleteLocalRef(str_obj)
        assert field is not None
        return TReflectField(field)

    def getDeclaredMethod(self, name, *classes):
        cls = _env.FindClass('java.lang.Class')
        jni.check_exception(_env)
        assert cls is not None
        str_obj = _env.NewStringUTF(name)
        jni.check_exception(_env)
        assert str_obj is not None
        _classes = _env.NewObjectArray(len(classes), cls, None)
        jni.check_exception(_env)
        assert _classes is not None
        for i, _cls in enumerate(classes):
            _env.SetObjectArrayElement(_classes, i, _cls)
            jni.check_exception(_env)
        args = jni.jvalue.__mul__(2)()
        setattr(args[0], 'l', str_obj)
        setattr(args[1], 'l', _classes)
        method = _env.CallObjectMethodA(self.obj, self._getDeclaredMethod, args)
        jni.check_exception(_env)
        assert method is not None
        _env.DeleteLocalRef(str_obj)
        _env.DeleteLocalRef(_classes)
        _env.DeleteLocalRef(cls)
        return TReflectMethod(method)

    def forName(self, name):
        str_obj = _env.NewStringUTF(name)
        jni.check_exception(_env)
        assert str_obj is not None
        args = jni.jvalue.__mul__(1)()
        setattr(args[0], 'l', str_obj)
        cls_obj = _env.CallStaticObjectMethodA(self.cls, self._forName, args)
        jni.check_exception(_env)
        assert cls_obj is not None
        return TClass(cls_obj)

    def getName(self):
        args = jni.jvalue.__mul__(0)()
        str_obj = _env.CallObjectMethodA(self.obj, self._getName, args)
        chars = _env.GetStringUTFChars(str_obj, None)
        _env.DeleteLocalRef(str_obj)
        return jni.decode(chars)


class TReflectField(TObject):
    class_name = 'java.lang.reflect.Field'

    def __init__(self, obj):
        super(TReflectField, self).__init__(obj)
        self._getName = _env.GetMethodID(self.cls, 'getName', '()Ljava/lang/String;')
        jni.check_exception(_env)
        assert self._getName is not None
        self._getType = _env.GetMethodID(self.cls, 'getType', '()Ljava/lang/Class;')
        jni.check_exception(_env)
        assert self._getType is not None
        self._hashCode = _env.GetMethodID(self.cls, 'hashCode', '()I')
        jni.check_exception(_env)
        assert self._hashCode is not None

    def getName(self):
        args = jni.jvalue.__mul__(0)()
        str_obj = _env.CallObjectMethodA(self.obj, self._getName, args)
        jni.check_exception(_env)
        assert str_obj is not None
        chars = _env.GetStringUTFChars(str_obj, None)
        jni.check_exception(_env)
        assert chars is not None
        _env.DeleteLocalRef(str_obj)
        return jni.decode(chars)

    def getType(self):
        args = jni.jvalue.__mul__(0)()
        cls_obj = _env.CallObjectMethodA(self.obj, self._getType, args)
        jni.check_exception(_env)
        assert cls_obj is not None
        return cls_obj

    def hashCode(self):
        args = jni.jvalue.__mul__(0)()
        value = _env.CallIntMethodA(self.obj, self._hashCode, args)
        jni.check_exception(_env)
        return value


class TReflectMethod(TObject):
    class_name = 'java.lang.reflect.Method'

    def __init__(self, obj):
        super(TReflectMethod, self).__init__(obj)
        self._getName = _env.GetMethodID(
            self.cls,
            'getName',
            '()Ljava/lang/String;'
        )
        jni.check_exception(_env)
        assert self._getName is not None
        self._getReturnType = _env.GetMethodID(
            self.cls,
            'getReturnType',
            '()Ljava/lang/Class;'
        )
        jni.check_exception(_env)
        assert self._getReturnType is not None
        self._getParameterTypes = _env.GetMethodID(
            self.cls,
            'getParameterTypes',
            '()[Ljava/lang/Class;'
        )
        jni.check_exception(_env)
        assert self._getParameterTypes is not None
        self._hashCode = _env.GetMethodID(self.cls, 'hashCode', '()I')
        jni.check_exception(_env)
        assert self._hashCode is not None

    def getName(self):
        args = jni.jvalue.__mul__(0)()
        str_obj = _env.CallObjectMethodA(self.obj, self._getName, args)
        jni.check_exception(_env)
        chars = _env.GetStringUTFChars(str_obj, None)
        jni.check_exception(_env)
        assert chars is not None
        _env.DeleteLocalRef(str_obj)
        return jni.decode(chars)

    def getReturnType(self):
        args = jni.jvalue.__mul__(0)()
        cls_obj = _env.CallObjectMethodA(self.obj, self.getReturnType, args)
        jni.check_exception(_env)
        assert cls_obj is not None
        return cls_obj

    def getParameterTypes(self):
        args = jni.jvalue.__mul__(0)()
        _classes = _env.CallObjectMethodA(self.obj, self._getParameterTypes, args)
        jni.check_exception(_env)
        assert _classes is not None
        return [
            TClass(_env.GetObjectArrayElement(_classes, i))
            for i in range(_env.GetArrayLength(_classes))
        ]

    def hashCode(self):
        args = jni.jvalue.__mul__(0)()
        value = _env.CallIntMethodA(self.obj, self._hashCode, args)
        jni.check_exception(_env)
        return value


def setup_module():
    global _env
    _env = jni.get_env(**JAVA_OPTS)


def teardown_module():
    jni.destroy_vm()


def test_env():
    e2 = jni.JNIEnv_p()
    rc = jni.vm[0].GetEnv(byref(e2), jni.JNI_VERSION_1_2)
    assert rc == jni.JNI_OK
    rc = jni.vm[0].AttachCurrentThread(byref(e2), None)
    assert rc == jni.JNI_OK
    rc = jni.vm[0].AttachCurrentThreadAsDaemon(byref(e2), None)
    assert rc == jni.JNI_OK
    v2 = jni.JavaVM_p()
    rc = _env.GetJavaVM(byref(v2))
    assert rc == jni.JNI_OK


def test_version():
    version = _env.GetVersion()
    jni.check_exception(_env)
    assert isinstance(version, int)
    log.info('version=%s', _env.version)


def _string(src):
    c = jni.jchar.__mul__(len(src))()
    for i in range(len(src)):
        c[i] = ord(src[i])
    s = _env.NewString(c, len(src))
    assert s is not None
    jni.check_exception(_env)
    assert _env.GetStringLength(s) == len(src)
    jni.check_exception(_env)
    z = jni.jboolean()
    chars = _env.GetStringChars(s, byref(z))
    assert chars is not None
    jni.check_exception(_env)
    xxx = ''.join(chr(chars[i]) for i in range(len(src)))
    assert len(xxx) == len(src)
    _env.ReleaseStringChars(s, chars)
    _env.DeleteLocalRef(s)


def test_string():
    _string('')
    _string('abc\0foo')
    _string('testing')
    _string('夢fooÞbar印')


def _utf(src):
    s = _env.NewStringUTF(src)
    assert s is not None
    jni.check_exception(_env)
    assert _env.GetObjectRefType(s) == jni.jobjectType.JNILocalRefType
    assert _env.GetStringUTFLength(s) == len(jni.encode(src)) - 1
    jni.check_exception(_env)
    chars = _env.GetStringUTFChars(s, None)
    assert chars is not None
    jni.check_exception(_env)
    xxx = string_at(chars, len(src))
    assert len(xxx) == len(src)
    # _env.ReleaseStringUTFChars(s, chars)
    _env.DeleteLocalRef(s)


def test_utf():
    _utf('')
    _utf('abc\0foo')
    _utf('testing')
    _utf('夢fooÞbar印')


def test_boolean_array():
    count = random.randint(0, 9)
    data = [random.choice((False, True)) for _ in range(count)]
    a = _env.NewBooleanArray(count)
    assert a is not None
    jni.check_exception(_env)
    a0 = jni.jboolean.__mul__(count)()
    for i in range(count):
        a0[i] = jni.jboolean(BOOLEANS[data[i]])
    _env.SetBooleanArrayRegion(a, 0, count, a0)
    jni.check_exception(_env)
    a1 = _env.GetBooleanArrayElements(a, None)
    assert all(a1[i] == a0[i] for i in range(count))
    _env.ReleaseBooleanArrayElements(a, a1, jni.JNI_ABORT)
    a2 = jni.jboolean.__mul__(count)()
    _env.GetBooleanArrayRegion(a, 0, count, a2)
    jni.check_exception(_env)
    assert all(a2[i] == a0[i] for i in range(count))
    for i in range(count):
        a2[i] = jni.JNI_FALSE
    _env.SetBooleanArrayRegion(a, 0, count, a2)
    a3 = jni.jboolean.__mul__(count)()
    _env.GetBooleanArrayRegion(a, 0, count, a3)
    jni.check_exception(_env)
    assert all(a3[i] == jni.JNI_FALSE for i in range(count))
    _env.DeleteLocalRef(a)


def test_byte_array():
    count = random.randint(0, 9)
    data = [random.randint(MIN_BYTE, MAX_BYTE) for _ in range(count)]
    a = _env.NewByteArray(count)
    assert a is not None
    jni.check_exception(_env)
    a0 = jni.jbyte.__mul__(count)()
    for i in range(count):
        a0[i] = data[i]
    _env.SetByteArrayRegion(a, 0, count, a0)
    jni.check_exception(_env)
    a1 = _env.GetByteArrayElements(a, None)
    assert all(a1[i] == data[i] for i in range(count))
    _env.ReleaseByteArrayElements(a, a1, jni.JNI_ABORT)
    a2 = jni.jbyte.__mul__(count)()
    _env.GetByteArrayRegion(a, 0, count, a2)
    jni.check_exception(_env)
    assert all(a2[i] == a0[i] for i in range(count))
    for i in range(count):
        a2[i] = 1
    _env.SetByteArrayRegion(a, 0, count, a2)
    a3 = jni.jbyte.__mul__(count)()
    _env.GetByteArrayRegion(a, 0, count, a3)
    jni.check_exception(_env)
    assert all(a3[i] == 1 for i in range(count))
    assert _env.GetArrayLength(a) == count
    _env.DeleteLocalRef(a)


def test_char_array():
    count = random.randint(0, 9)
    data = [random.randint(MIN_CHAR, MAX_CHAR) for _ in range(count)]
    a = _env.NewCharArray(count)
    assert a is not None
    jni.check_exception(_env)
    a0 = jni.jchar.__mul__(count)()
    for i in range(count):
        a0[i] = data[i]
    _env.SetCharArrayRegion(a, 0, count, a0)
    jni.check_exception(_env)
    a1 = _env.GetCharArrayElements(a, None)
    assert all(a1[i] == data[i] for i in range(count))
    _env.ReleaseCharArrayElements(a, a1, jni.JNI_ABORT)
    a2 = jni.jchar.__mul__(count)()
    _env.GetCharArrayRegion(a, 0, count, a2)
    jni.check_exception(_env)
    assert all(a2[i] == a0[i] for i in range(count))
    for i in range(count):
        a2[i] = 2
    _env.SetCharArrayRegion(a, 0, count, a2)
    a3 = jni.jchar.__mul__(count)()
    _env.GetCharArrayRegion(a, 0, count, a3)
    jni.check_exception(_env)
    assert all(a3[i] == 2 for i in range(count))
    assert _env.GetArrayLength(a) == count
    _env.DeleteLocalRef(a)


def test_short_array():
    count = random.randint(0, 9)
    data = [random.randint(MIN_SHORT, MAX_SHORT) for _ in range(count)]
    a = _env.NewShortArray(count)
    assert a is not None
    jni.check_exception(_env)
    a0 = jni.jshort.__mul__(count)()
    for i in range(count):
        a0[i] = data[i]
    _env.SetShortArrayRegion(a, 0, count, a0)
    jni.check_exception(_env)
    a1 = _env.GetShortArrayElements(a, None)
    assert all(a1[i] == data[i] for i in range(count))
    _env.ReleaseShortArrayElements(a, a1, jni.JNI_ABORT)
    a2 = jni.jshort.__mul__(count)()
    _env.GetShortArrayRegion(a, 0, count, a2)
    jni.check_exception(_env)
    assert all(a2[i] == a0[i] for i in range(count))
    for i in range(count):
        a2[i] = 3
    _env.SetShortArrayRegion(a, 0, count, a2)
    a3 = jni.jshort.__mul__(count)()
    _env.GetShortArrayRegion(a, 0, count, a3)
    jni.check_exception(_env)
    assert all(a3[i] == 3 for i in range(count))
    _env.DeleteLocalRef(a)


def test_int_array():
    count = random.randint(0, 9)
    data = [random.randint(MIN_INT, MAX_INT) for _ in range(count)]
    a = _env.NewIntArray(count)
    assert a is not None
    jni.check_exception(_env)
    a0 = jni.jint.__mul__(count)()
    for i in range(count):
        a0[i] = data[i]
    _env.SetIntArrayRegion(a, 0, count, a0)
    jni.check_exception(_env)
    a1 = _env.GetIntArrayElements(a, None)
    assert all(a1[i] == data[i] for i in range(count))
    _env.ReleaseIntArrayElements(a, a1, jni.JNI_ABORT)
    a2 = jni.jint.__mul__(count)()
    _env.GetIntArrayRegion(a, 0, count, a2)
    jni.check_exception(_env)
    assert all(a2[i] == a0[i] for i in range(count))
    for i in range(count):
        a2[i] = 4
    _env.SetIntArrayRegion(a, 0, count, a2)
    a3 = jni.jint.__mul__(count)()
    _env.GetIntArrayRegion(a, 0, count, a3)
    jni.check_exception(_env)
    assert all(a3[i] == 4 for i in range(count))
    assert _env.GetArrayLength(a) == count
    _env.DeleteLocalRef(a)


def test_long_array():
    count = random.randint(0, 9)
    data = [random.randint(MIN_LONG, MAX_LONG) for _ in range(count)]
    a = _env.NewLongArray(count)
    assert a is not None
    jni.check_exception(_env)
    a0 = jni.jlong.__mul__(count)()
    for i in range(count):
        a0[i] = data[i]
    _env.SetLongArrayRegion(a, 0, count, a0)
    jni.check_exception(_env)
    a1 = _env.GetLongArrayElements(a, None)
    assert all(a1[i] == a0[i] for i in range(count))
    _env.ReleaseLongArrayElements(a, a1, jni.JNI_ABORT)
    a2 = jni.jlong.__mul__(count)()
    _env.GetLongArrayRegion(a, 0, count, a2)
    jni.check_exception(_env)
    assert all(a2[i] == a0[i] for i in range(count))
    for i in range(count):
        a2[i] = 5
    _env.SetLongArrayRegion(a, 0, count, a2)
    a3 = jni.jlong.__mul__(count)()
    _env.GetLongArrayRegion(a, 0, count, a3)
    jni.check_exception(_env)
    assert all(a3[i] == 5 for i in range(count))
    assert _env.GetArrayLength(a) == count
    _env.DeleteLocalRef(a)


def test_float_array():
    count = random.randint(0, 9)
    data = [
        jni.jfloat(random.uniform(MIN_FLOAT, MAX_FLOAT)).value
        for _ in range(count)
    ]
    a = _env.NewFloatArray(count)
    assert a is not None
    jni.check_exception(_env)
    a0 = jni.jfloat.__mul__(count)()
    for i in range(count):
        a0[i] = data[i]
    _env.SetFloatArrayRegion(a, 0, count, a0)
    jni.check_exception(_env)
    a1 = _env.GetFloatArrayElements(a, None)
    assert all(a1[i] == a0[i] for i in range(count))
    _env.ReleaseFloatArrayElements(a, a1, jni.JNI_ABORT)
    a2 = jni.jfloat.__mul__(count)()
    _env.GetFloatArrayRegion(a, 0, count, a2)
    jni.check_exception(_env)
    assert all(a2[i] == a0[i] for i in range(count))
    value = jni.jfloat(6.5).value
    for i in range(count):
        a2[i] = value
    _env.SetFloatArrayRegion(a, 0, count, a2)
    a3 = jni.jfloat.__mul__(count)()
    _env.GetFloatArrayRegion(a, 0, count, a3)
    jni.check_exception(_env)
    assert all(a3[i] == value for i in range(count))
    assert _env.GetArrayLength(a) == count
    _env.DeleteLocalRef(a)


def test_double_array():
    count = random.randint(0, 9)
    data = [
        jni.jdouble(random.uniform(MIN_DOUBLE, MAX_DOUBLE)).value
        for _ in range(count)
    ]
    a = _env.NewDoubleArray(count)
    assert a is not None
    jni.check_exception(_env)
    a0 = jni.jdouble.__mul__(count)()
    for i in range(count):
        a0[i] = data[i]
    _env.SetDoubleArrayRegion(a, 0, count, a0)
    jni.check_exception(_env)
    a1 = _env.GetDoubleArrayElements(a, None)
    assert all(a1[i] == a0[i] for i in range(count))
    _env.ReleaseDoubleArrayElements(a, a1, jni.JNI_ABORT)
    a2 = jni.jdouble.__mul__(count)()
    _env.GetDoubleArrayRegion(a, 0, count, a2)
    jni.check_exception(_env)
    assert all(a2[i] == a0[i] for i in range(count))
    value = jni.jdouble(8.901234567).value
    for i in range(count):
        a2[i] = value
    _env.SetDoubleArrayRegion(a, 0, count, a2)
    a3 = jni.jdouble.__mul__(count)()
    _env.GetDoubleArrayRegion(a, 0, count, a3)
    jni.check_exception(_env)
    assert all(a3[i] == value for i in range(count))
    assert _env.GetArrayLength(a) == count
    _env.DeleteLocalRef(a)


def test_object_array():
    cls = _env.FindClass('java.lang.String')
    count = random.randint(0, 9)
    a = _env.NewObjectArray(count, cls, None)
    assert a is not None
    jni.check_exception(_env)
    data = [hex(i) for i in range(count)]
    for i in range(count):
        s = _env.NewStringUTF(data[i])
        _env.SetObjectArrayElement(a, i, s)
        _env.DeleteLocalRef(s)
        jni.check_exception(_env)
    for i in range(count):
        value = _env.GetObjectArrayElement(a, i)
        jni.check_exception(_env)
        chars = _env.GetStringUTFChars(value, None)
        _env.DeleteLocalRef(value)
        jni.check_exception(_env)
        assert jni.decode(chars) == data[i]
    assert _env.GetArrayLength(a) == count
    _env.DeleteLocalRef(a)
    _env.DeleteLocalRef(cls)


def test_is_same_object():
    cls1 = _env.FindClass('java.lang.String')
    jni.check_exception(_env)
    assert cls1 is not None
    cls2 = _env.NewGlobalRef(cls1)
    jni.check_exception(_env)
    assert _env.IsSameObject(cls1, cls2) is True
    jni.check_exception(_env)
    _env.DeleteGlobalRef(cls2)
    _env.DeleteLocalRef(cls1)


def test_boolean():
    cls = _env.FindClass('java.lang.Boolean')
    jni.check_exception(_env)
    assert cls is not None
    fid = _env.GetStaticFieldID(cls, 'TRUE', 'Ljava/lang/Boolean;')
    jni.check_exception(_env)
    assert fid is not None
    obj0 = _env.GetStaticObjectField(cls, fid)
    jni.check_exception(_env)
    assert obj0 is not None
    cons = _env.GetMethodID(cls, '<init>', '(Z)V')
    jni.check_exception(_env)
    args = jni.jvalue.__mul__(1)()
    args[0].z = jni.JNI_TRUE
    obj = _env.NewObjectA(cls, cons, args)
    jni.check_exception(_env)
    assert obj is not None
    mid = _env.GetMethodID(cls, 'booleanValue', '()Z')
    jni.check_exception(_env)
    assert mid is not None
    assert _env.CallBooleanMethodA(obj, mid, args) == jni.JNI_TRUE
    jni.check_exception(_env)
    assert _env.CallBooleanMethodA(obj0, mid, args) == jni.JNI_TRUE
    jni.check_exception(_env)
    _env.DeleteLocalRef(obj0)
    _env.DeleteLocalRef(obj)
    _env.DeleteLocalRef(cls)


def test_byte():
    cls = _env.FindClass('java.lang.Byte')
    jni.check_exception(_env)
    assert cls is not None
    fid = _env.GetStaticFieldID(cls, 'MAX_VALUE', 'B')
    jni.check_exception(_env)
    assert fid is not None
    assert _env.GetStaticByteField(cls, fid) == MAX_BYTE
    jni.check_exception(_env)
    cons = _env.GetMethodID(cls, '<init>', '(B)V')
    jni.check_exception(_env)
    args = jni.jvalue.__mul__(1)()
    args[0].b = 42
    obj = _env.NewObjectA(cls, cons, args)
    jni.check_exception(_env)
    assert obj is not None
    mid = _env.GetMethodID(cls, 'byteValue', '()B')
    jni.check_exception(_env)
    assert mid is not None
    assert _env.CallByteMethodA(obj, mid, args) == 42
    jni.check_exception(_env)
    _env.DeleteLocalRef(obj)
    _env.DeleteLocalRef(cls)


def test_char():
    cls = _env.FindClass('java.lang.Character')
    jni.check_exception(_env)
    assert cls is not None
    fid = _env.GetStaticFieldID(cls, 'MAX_VALUE', 'C')
    jni.check_exception(_env)
    assert _env.GetStaticCharField(cls, fid) == MAX_CHAR
    jni.check_exception(_env)
    cons = _env.GetMethodID(cls, '<init>', '(C)V')
    jni.check_exception(_env)
    args = jni.jvalue.__mul__(1)()
    args[0].c = 0xbeef
    obj = _env.NewObjectA(cls, cons, args)
    jni.check_exception(_env)
    assert obj is not None
    mid = _env.GetMethodID(cls, 'charValue', '()C')
    jni.check_exception(_env)
    assert mid is not None
    assert _env.CallCharMethodA(obj, mid, args) == 0xbeef
    jni.check_exception(_env)
    _env.DeleteLocalRef(obj)
    _env.DeleteLocalRef(cls)


def test_short():
    cls = _env.FindClass('java.lang.Short')
    jni.check_exception(_env)
    assert cls is not None
    fid = _env.GetStaticFieldID(cls, 'MAX_VALUE', 'S')
    jni.check_exception(_env)
    assert _env.GetStaticShortField(cls, fid) == MAX_SHORT
    jni.check_exception(_env)
    cons = _env.GetMethodID(cls, '<init>', '(S)V')
    jni.check_exception(_env)
    args = jni.jvalue.__mul__(1)()
    args[0].s = 420
    obj = _env.NewObjectA(cls, cons, args)
    jni.check_exception(_env)
    assert obj is not None
    mid = _env.GetMethodID(cls, 'shortValue', '()S')
    jni.check_exception(_env)
    assert mid is not None
    assert _env.CallShortMethodA(obj, mid, args) == 420
    jni.check_exception(_env)
    _env.DeleteLocalRef(obj)
    _env.DeleteLocalRef(cls)


def test_int():
    cls = _env.FindClass('java.lang.Integer')
    jni.check_exception(_env)
    assert cls is not None
    fid = _env.GetStaticFieldID(cls, 'MAX_VALUE', 'I')
    jni.check_exception(_env)
    assert _env.GetStaticIntField(cls, fid) == MAX_INT
    jni.check_exception(_env)
    cons = _env.GetMethodID(cls, '<init>', '(I)V')
    jni.check_exception(_env)
    args = jni.jvalue.__mul__(1)()
    args[0].i = 0x12345678
    obj = _env.NewObjectA(cls, cons, args)
    jni.check_exception(_env)
    assert obj is not None
    mid = _env.GetMethodID(cls, 'intValue', '()I')
    jni.check_exception(_env)
    assert mid is not None
    assert _env.CallIntMethodA(obj, mid, args) == 0x12345678
    jni.check_exception(_env)
    _env.DeleteLocalRef(obj)
    _env.DeleteLocalRef(cls)


def test_long():
    cls = _env.FindClass('java.lang.Long')
    jni.check_exception(_env)
    assert cls is not None
    fid = _env.GetStaticFieldID(cls, 'MAX_VALUE', 'J')
    jni.check_exception(_env)
    assert _env.GetStaticLongField(cls, fid) == MAX_LONG
    jni.check_exception(_env)
    cons = _env.GetMethodID(cls, '<init>', '(J)V')
    jni.check_exception(_env)
    args = jni.jvalue.__mul__(1)()
    args[0].j = 0x123456789abc
    obj = _env.NewObjectA(cls, cons, args)
    jni.check_exception(_env)
    assert obj is not None
    mid = _env.GetMethodID(cls, 'longValue', '()J')
    jni.check_exception(_env)
    assert mid is not None
    assert _env.CallLongMethodA(obj, mid, args) == 0x123456789abc
    jni.check_exception(_env)
    _env.DeleteLocalRef(obj)
    _env.DeleteLocalRef(cls)


def test_float():
    cls = _env.FindClass('java.lang.Float')
    jni.check_exception(_env)
    assert cls is not None
    fid = _env.GetStaticFieldID(cls, 'MAX_VALUE', 'F')
    jni.check_exception(_env)
    assert _env.GetStaticFloatField(cls, fid) == MAX_FLOAT
    jni.check_exception(_env)
    cons = _env.GetMethodID(cls, '<init>', '(F)V')
    jni.check_exception(_env)
    args = jni.jvalue.__mul__(1)()
    value = jni.jfloat(1234.567).value
    args[0].f = value
    obj = _env.NewObjectA(cls, cons, args)
    jni.check_exception(_env)
    assert obj is not None
    mid = _env.GetMethodID(cls, 'floatValue', '()F')
    jni.check_exception(_env)
    assert mid is not None
    assert _env.CallFloatMethodA(obj, mid, args) == value
    jni.check_exception(_env)
    _env.DeleteLocalRef(obj)
    _env.DeleteLocalRef(cls)


def test_double():
    cls = _env.FindClass('java.lang.Double')
    jni.check_exception(_env)
    assert cls is not None
    fid = _env.GetStaticFieldID(cls, 'MAX_VALUE', 'D')
    jni.check_exception(_env)
    assert _env.GetStaticDoubleField(cls, fid) == MAX_DOUBLE
    jni.check_exception(_env)
    cons = _env.GetMethodID(cls, '<init>', '(D)V')
    jni.check_exception(_env)
    args = jni.jvalue.__mul__(1)()
    value = jni.jdouble(1234.5678901234).value
    args[0].d = value
    obj = _env.NewObjectA(cls, cons, args)
    jni.check_exception(_env)
    assert obj is not None
    mid = _env.GetMethodID(cls, 'doubleValue', '()D')
    jni.check_exception(_env)
    assert mid is not None
    assert _env.CallDoubleMethodA(obj, mid, args) == value
    jni.check_exception(_env)
    _env.DeleteLocalRef(obj)
    _env.DeleteLocalRef(cls)


def test_system():
    cls = _env.FindClass('java.lang.System')
    jni.check_exception(_env)
    assert cls is not None
    mid = _env.GetStaticMethodID(
        cls,
        'getProperty',
        '(Ljava/lang/String;)Ljava/lang/String;'
    )
    jni.check_exception(_env)
    assert mid is not None
    s = _env.NewStringUTF('java.class.path')
    jni.check_exception(_env)
    args = jni.jvalue.__mul__(1)()
    setattr(args[0], 'l', s)
    result = _env.CallStaticObjectMethodA(cls, mid, args)
    jni.check_exception(_env)
    assert result is not None
    _env.DeleteLocalRef(s)
    jni.check_exception(_env)
    chars = _env.GetStringUTFChars(result, None)
    _env.DeleteLocalRef(result)
    jni.check_exception(_env)
    assert jni.decode(chars) == CLASSPATH
    fid = _env.GetStaticFieldID(cls, 'out', 'Ljava/io/PrintStream;')
    jni.check_exception(_env)
    result2 = _env.GetStaticObjectField(cls, fid)
    jni.check_exception(_env)
    assert result2 is not None
    _env.DeleteLocalRef(result2)
    _env.DeleteLocalRef(cls)


def test_class():
    cls = _env.FindClass('java.lang.Class')
    assert cls is not None
    jni.check_exception(_env)
    mid1 = _env.GetStaticMethodID(
        cls,
        'forName',
        '(Ljava/lang/String;)Ljava/lang/Class;'
    )
    jni.check_exception(_env)
    assert mid1 is not None
    s = _env.NewStringUTF('java.lang.System')
    jni.check_exception(_env)
    args = jni.jvalue.__mul__(1)()
    setattr(args[0], 'l', s)
    result = _env.CallStaticObjectMethodA(cls, mid1, args)
    _env.DeleteLocalRef(s)
    jni.check_exception(_env)
    assert result is not None
    _env.DeleteLocalRef(result)
    mid2 = _env.GetMethodID(
        cls,
        'getName',
        '()Ljava/lang/String;'
    )
    jni.check_exception(_env)
    assert mid2 is not None
    args = jni.jvalue.__mul__(0)()
    result = _env.CallObjectMethodA(
        cls,
        mid2,
        args
    )
    jni.check_exception(_env)
    assert result is not None
    chars = _env.GetStringUTFChars(result, None)
    _env.DeleteLocalRef(result)
    jni.check_exception(_env)
    assert jni.decode(chars) == 'java.lang.Class'
    _env.DeleteLocalRef(cls)


def test_drivermanager():
    cls = _env.FindClass('java.sql.DriverManager')
    jni.check_exception(_env)
    assert cls is not None
    mid1 = _env.GetStaticMethodID(
        cls,
        'getConnection',
        '(Ljava/lang/String;)Ljava/sql/Connection;'
    )
    jni.check_exception(_env)
    assert mid1 is not None
    s = _env.NewStringUTF('jdbc:sqlite::memory:')
    jni.check_exception(_env)
    args = jni.jvalue.__mul__(1)()
    setattr(args[0], 'l', s)
    conn = _env.CallStaticObjectMethodA(cls, mid1, args)
    jni.check_exception(_env)
    assert conn is not None
    _env.DeleteLocalRef(s)
    _env.DeleteLocalRef(conn)
    _env.DeleteLocalRef(cls)


def test_exceptions():
    cls = _env.FindClass('foo.bar.baz')
    with pytest.raises(jni.JavaException) as e:
        jni.check_exception(_env)
    _env.DeleteLocalRef(e.value.throwable)
    _env.DeleteLocalRef(cls)
    cls = _env.FindClass('java.sql.SQLException')
    jni.check_exception(_env)
    assert cls is not None
    cons = _env.GetMethodID(cls, '<init>', '()V')
    jni.check_exception(_env)
    assert cons is not None
    obj = _env.NewObjectA(cls, cons, None)
    jni.check_exception(_env)
    assert obj is not None
    _env.Throw(obj)
    with pytest.raises(jni.JavaException) as e:
        jni.check_exception(_env)
    _env.DeleteLocalRef(e.value.throwable)
    _env.DeleteLocalRef(obj)
    _env.DeleteLocalRef(cls)


def test_reflect_field():
    integer_cls = _env.FindClass('java.lang.Integer')
    jni.check_exception(_env)
    assert integer_cls is not None
    tclass = TClass(integer_cls)
    field = tclass.getDeclaredField('MAX_VALUE')
    assert field.getName() == 'MAX_VALUE'
    fid = _env.FromReflectedField(field.obj)
    jni.check_exception(_env)
    assert fid is not None
    is_static = jni.jboolean(jni.JNI_TRUE)
    fld2 = _env.ToReflectedField(integer_cls, fid, is_static)
    jni.check_exception(_env)
    assert fld2 is not None
    assert jni.get_class_name(_env, fld2) == 'java.lang.reflect.Field'
    field2 = TReflectField(fld2)
    assert field2.getName() == 'MAX_VALUE'
    assert field.hashCode() == field2.hashCode()
    del field2
    del field
    del tclass


def test_reflect_method():
    integer_cls = _env.FindClass('java.lang.Integer')
    jni.check_exception(_env)
    assert integer_cls is not None
    tclass = TClass(integer_cls)
    method = tclass.getDeclaredMethod('intValue')
    jni.check_exception(_env)
    assert method.getName() == 'intValue'
    mid = _env.FromReflectedMethod(method.obj)
    jni.check_exception(_env)
    assert mid is not None
    is_static = jni.jboolean(jni.JNI_FALSE)
    mth2 = _env.ToReflectedMethod(integer_cls, mid, is_static)
    jni.check_exception(_env)
    assert mth2 is not None
    method2 = TReflectMethod(mth2)
    assert method2.getName() == 'intValue'
    assert method.hashCode() == method2.hashCode()
    del method2
    del method
    del tclass


def test_custom():
    custom_cls = _env.FindClass('Custom')
    jni.check_exception(_env)
    assert custom_cls is not None
    cons = _env.GetMethodID(custom_cls, '<init>', '()V')
    jni.check_exception(_env)
    assert cons is not None
    args = jni.jvalue.__mul__(0)()
    obj = _env.NewObjectA(custom_cls, cons, args)
    jni.check_exception(_env)
    assert obj is not None
    fid = _env.GetFieldID(custom_cls, 'booleanField', 'Z')
    jni.check_exception(_env)
    assert _env.GetBooleanField(obj, fid) == jni.JNI_TRUE
    _env.SetBooleanField(obj, fid, jni.JNI_FALSE)
    assert _env.GetBooleanField(obj, fid) == jni.JNI_FALSE
    fid = _env.GetFieldID(custom_cls, 'byteField', 'B')
    jni.check_exception(_env)
    assert _env.GetByteField(obj, fid) == 0x01
    _env.SetByteField(obj, fid, 0x23)
    assert _env.GetByteField(obj, fid) == 0x23
    fid = _env.GetFieldID(custom_cls, 'charField', 'C')
    jni.check_exception(_env)
    assert _env.GetCharField(obj, fid) == 0x0002
    _env.SetCharField(obj, fid, 0x0161)
    assert _env.GetCharField(obj, fid) == 0x0161
    fid = _env.GetFieldID(custom_cls, 'shortField', 'S')
    jni.check_exception(_env)
    assert _env.GetShortField(obj, fid) == 0x0123
    _env.SetShortField(obj, fid, 0x0567)
    assert _env.GetShortField(obj, fid) == 0x0567
    fid = _env.GetFieldID(custom_cls, 'intField', 'I')
    jni.check_exception(_env)
    assert _env.GetIntField(obj, fid) == 0x0123456
    _env.SetIntField(obj, fid, 0x0abecafe)
    assert _env.GetIntField(obj, fid) == 0x0abecafe
    fid = _env.GetFieldID(custom_cls, 'longField', 'J')
    jni.check_exception(_env)
    assert _env.GetLongField(obj, fid) == 0x0123456789
    _env.SetLongField(obj, fid, 0xbeefcafe)
    assert _env.GetLongField(obj, fid) == 0xbeefcafe
    fid = _env.GetFieldID(custom_cls, 'floatField', 'F')
    jni.check_exception(_env)
    assert _env.GetFloatField(obj, fid) == jni.jfloat(123.456).value
    _env.SetFloatField(obj, fid, jni.jfloat(3.14).value)
    assert _env.GetFloatField(obj, fid) == jni.jfloat(3.14).value
    fid = _env.GetFieldID(custom_cls, 'doubleField', 'D')
    jni.check_exception(_env)
    assert _env.GetDoubleField(obj, fid) == jni.jdouble(123456.789789).value
    _env.SetDoubleField(obj, fid, jni.jdouble(3.14159265).value)
    assert _env.GetDoubleField(obj, fid) == jni.jdouble(3.14159265).value
    fid = _env.GetFieldID(custom_cls, 'stringField', 'Ljava/lang/String;')
    jni.check_exception(_env)
    str_obj = _env.GetObjectField(obj, fid)
    chars = _env.GetStringUTFChars(str_obj, None)
    _env.DeleteLocalRef(str_obj)
    assert jni.decode(chars) == 'abcdef'
    str_obj = _env.NewStringUTF('one two three')
    _env.SetObjectField(obj, fid, str_obj)
    _env.DeleteLocalRef(str_obj)
    str2 = _env.GetObjectField(obj, fid)
    chars = _env.GetStringUTFChars(str2, None)
    _env.DeleteLocalRef(str2)
    assert jni.decode(chars) == 'one two three'
    args = jni.jvalue.__mul__(0)()
    mid = _env.GetStaticMethodID(custom_cls, 'staticVoidMethod', '()V')
    jni.check_exception(_env)
    assert mid is not None
    _env.CallStaticVoidMethodA(custom_cls, mid, args)
    jni.check_exception(_env)
    mid = _env.GetStaticMethodID(custom_cls, 'staticBooleanMethod', '()Z')
    jni.check_exception(_env)
    assert mid is not None
    assert _env.CallStaticBooleanMethodA(custom_cls, mid, args) == jni.JNI_FALSE
    jni.check_exception(_env)
    mid = _env.GetStaticMethodID(custom_cls, 'staticByteMethod', '()B')
    jni.check_exception(_env)
    assert mid is not None
    assert _env.CallStaticByteMethodA(custom_cls, mid, args) == 0x32
    jni.check_exception(_env)
    mid = _env.GetStaticMethodID(custom_cls, 'staticCharMethod', '()C')
    jni.check_exception(_env)
    assert mid is not None
    assert _env.CallStaticCharMethodA(custom_cls, mid, args) == 0x0196
    jni.check_exception(_env)
    mid = _env.GetStaticMethodID(custom_cls, 'staticShortMethod', '()S')
    jni.check_exception(_env)
    assert mid is not None
    assert _env.CallStaticShortMethodA(custom_cls, mid, args) == 0x1122
    jni.check_exception(_env)
    mid = _env.GetStaticMethodID(custom_cls, 'staticIntMethod', '()I')
    jni.check_exception(_env)
    assert mid is not None
    assert _env.CallStaticIntMethodA(custom_cls, mid, args) == 0x00112233
    jni.check_exception(_env)
    mid = _env.GetStaticMethodID(custom_cls, 'staticLongMethod', '()J')
    jni.check_exception(_env)
    assert mid is not None
    assert _env.CallStaticLongMethodA(custom_cls, mid, args) == 0x876543210
    jni.check_exception(_env)
    mid = _env.GetStaticMethodID(custom_cls, 'staticFloatMethod', '()F')
    jni.check_exception(_env)
    assert mid is not None
    assert _env.CallStaticFloatMethodA(custom_cls, mid, args) == jni.jfloat(98.6).value
    jni.check_exception(_env)
    mid = _env.GetStaticMethodID(custom_cls, 'staticDoubleMethod', '()D')
    jni.check_exception(_env)
    assert mid is not None
    assert _env.CallStaticDoubleMethodA(custom_cls, mid, args) == jni.jdouble(777.665544).value
    jni.check_exception(_env)
    mid = _env.GetStaticMethodID(custom_cls, 'staticStringMethod', '()Ljava/lang/String;')
    jni.check_exception(_env)
    assert mid is not None
    str_obj = _env.CallStaticObjectMethodA(custom_cls, mid, args)
    jni.check_exception(_env)
    chars = _env.GetStringUTFChars(str_obj, None)
    _env.DeleteLocalRef(str_obj)
    assert jni.decode(chars) == 'hello world'
    _env.DeleteLocalRef(obj)
    _env.DeleteLocalRef(custom_cls)


def test_get_class_name():
    cls = _env.FindClass('java.lang.Integer')
    jni.check_exception(_env)
    assert cls is not None
    cons = _env.GetMethodID(cls, '<init>', '(I)V')
    jni.check_exception(_env)
    args = jni.jvalue.__mul__(1)()
    args[0].i = 0x12345678
    obj = _env.NewObjectA(cls, cons, args)
    jni.check_exception(_env)
    assert obj is not None
    assert jni.get_class_name(_env, obj) == 'java.lang.Integer'
    _env.DeleteLocalRef(obj)
    _env.DeleteLocalRef(cls)
