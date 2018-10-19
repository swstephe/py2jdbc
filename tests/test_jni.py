# -*- coding: utf8 -*-
import random
import six
from ctypes import byref, string_at
import logging
# noinspection PyPackageRequirements
import pytest
import py2jdbc.jni
from tests.config import (
    CLASSPATH, JAVA_OPTS, BOOLEANS,
    FIELDS, STATIC_FIELDS,
    MIN_BYTE, MAX_BYTE,
    MIN_CHAR, MAX_CHAR,
    MIN_SHORT, MAX_SHORT,
    MIN_LONG, MAX_LONG,
    MIN_INT, MAX_INT,
    MIN_FLOAT, MAX_FLOAT,
    MIN_DOUBLE, MAX_DOUBLE
)

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
        self.obj = obj

    def __del__(self):
        if self.obj:
            _env.DeleteLocalRef(self.obj)
        self.obj = None
        if self.cls:
            _env.DeleteLocalRef(self.cls)
        self.cls = None

    def __eq__(self, obj):
        args = py2jdbc.jni.jvalue.__mul__(1)()
        setattr(args[0], 'l', obj)
        return _env.CallBooleanMethodA(obj, self._equals, args)

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
        self._getDeclaredField = _env.GetMethodID(
            self.cls,
            'getDeclaredField',
            '(Ljava/lang/String;)Ljava/lang/reflect/Field;'
        )
        self._getDeclaredMethod = _env.GetMethodID(
            self.cls,
            'getDeclaredMethod',
            '(Ljava/lang/String;[Ljava/lang/Class;)Ljava/lang/reflect/Method;'
        )
        self._getName = _env.GetMethodID(
            self.cls,
            'getName',
            '()Ljava/lang/String;'
        )

    def getDeclaredField(self, name):
        str_obj = _env.NewStringUTF(name)
        args = py2jdbc.jni.jvalue.__mul__(1)()
        setattr(args[0], 'l', str_obj)
        field = _env.CallObjectMethodA(self.obj, self._getDeclaredField, args)
        _env.DeleteLocalRef(str_obj)
        return TReflectField(field)

    def getDeclaredMethod(self, name, *classes):
        cls = _env.FindClass('java.lang.Class')
        str_obj = _env.NewStringUTF(name)
        assert str_obj is not None
        _classes = _env.NewObjectArray(len(classes), cls, None)
        for i, _cls in enumerate(classes):
            _env.SetObjectArrayElement(_classes, i, _cls)
        args = py2jdbc.jni.jvalue.__mul__(2)()
        setattr(args[0], 'l', str_obj)
        setattr(args[1], 'l', _classes)
        method = _env.CallObjectMethodA(self.obj, self._getDeclaredMethod, args)
        _env.DeleteLocalRef(str_obj)
        _env.DeleteLocalRef(_classes)
        _env.DeleteLocalRef(cls)
        return TReflectMethod(method)

    def forName(self, name):
        str_obj = _env.NewStringUTF(name)
        args = py2jdbc.jni.jvalue.__mul__(1)()
        setattr(args[0], 'l', str_obj)
        cls_obj = _env.CallStaticObjectMethodA(self.cls, self._forName, args)
        return TClass(cls_obj)

    def getName(self):
        args = py2jdbc.jni.jvalue.__mul__(0)()
        str_obj = _env.CallObjectMethodA(self.obj, self._getName, args)
        chars = _env.GetStringUTFChars(str_obj, None)
        _env.DeleteLocalRef(str_obj)
        return py2jdbc.jni.decode(chars)


class TReflectField(TObject):
    class_name = 'java.lang.reflect.Field'

    def __init__(self, obj):
        super(TReflectField, self).__init__(obj)
        self._getName = _env.GetMethodID(self.cls, 'getName', '()Ljava/lang/String;')
        self._getType = _env.GetMethodID(self.cls, 'getType', '()Ljava/lang/Class;')
        self._hashCode = _env.GetMethodID(self.cls, 'hashCode', '()I')

    def getName(self):
        args = py2jdbc.jni.jvalue.__mul__(0)()
        str_obj = _env.CallObjectMethodA(self.obj, self._getName, args)
        chars = _env.GetStringUTFChars(str_obj, None)
        _env.DeleteLocalRef(str_obj)
        return py2jdbc.jni.decode(chars)

    def getType(self):
        args = py2jdbc.jni.jvalue.__mul__(0)()
        return _env.CallObjectMethodA(self.obj, self._getType, args)

    def hashCode(self):
        args = py2jdbc.jni.jvalue.__mul__(0)()
        return _env.CallIntMethodA(self.obj, self._hashCode, args)


class TReflectMethod(TObject):
    class_name = 'java.lang.reflect.Method'

    def __init__(self, obj):
        super(TReflectMethod, self).__init__(obj)
        self._getName = _env.GetMethodID(
            self.cls,
            'getName',
            '()Ljava/lang/String;'
        )
        self._getReturnType = _env.GetMethodID(
            self.cls,
            'getReturnType',
            '()Ljava/lang/Class;'
        )
        self._getParameterTypes = _env.GetMethodID(
            self.cls,
            'getParameterTypes',
            '()[Ljava/lang/Class;'
        )
        self._hashCode = _env.GetMethodID(self.cls, 'hashCode', '()I')

    def getName(self):
        args = py2jdbc.jni.jvalue.__mul__(0)()
        str_obj = _env.CallObjectMethodA(self.obj, self._getName, args)
        chars = _env.GetStringUTFChars(str_obj, None)
        _env.DeleteLocalRef(str_obj)
        return py2jdbc.jni.decode(chars)

    def getReturnType(self):
        args = py2jdbc.jni.jvalue.__mul__(0)()
        return _env.CallObjectMethodA(self.obj, self.getReturnType, args)

    def getParameterTypes(self):
        args = py2jdbc.jni.jvalue.__mul__(0)()
        _classes = _env.CallObjectMethodA(self.obj, self._getParameterTypes, args)
        return [
            TClass(_env.GetObjectArrayElement(_classes, i))
            for i in range(_env.GetArrayLength(_classes))
        ]

    def hashCode(self):
        args = py2jdbc.jni.jvalue.__mul__(0)()
        return _env.CallIntMethodA(self.obj, self._hashCode, args)


def setup_module():
    global _env
    _env = py2jdbc.jni.get_env(**JAVA_OPTS)


def test_env():
    e2 = py2jdbc.jni.JNIEnv_p()
    rc = py2jdbc.jni.vm[0].GetEnv(byref(e2), py2jdbc.jni.JNI_VERSION_1_2)
    assert rc == py2jdbc.jni.JNI_OK
    rc = py2jdbc.jni.vm[0].AttachCurrentThread(byref(e2), None)
    assert rc == py2jdbc.jni.JNI_OK
    rc = py2jdbc.jni.vm[0].AttachCurrentThreadAsDaemon(byref(e2), None)
    assert rc == py2jdbc.jni.JNI_OK
    v2 = py2jdbc.jni.JavaVM_p()
    rc = _env.GetJavaVM(byref(v2))
    assert rc == py2jdbc.jni.JNI_OK


def test_version():
    version = _env.GetVersion()
    assert isinstance(version, int)
    log.info('version=%s', _env.version)


def _string(src):
    c = py2jdbc.jni.jchar.__mul__(len(src))()
    for i in range(len(src)):
        c[i] = ord(src[i])
    s = _env.NewString(c, len(src))
    assert _env.GetStringLength(s) == len(src)
    z = py2jdbc.jni.jboolean()
    chars = _env.GetStringChars(s, byref(z))
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
    src_utf = py2jdbc.jni.encode(six.u(src))
    s = _env.NewStringUTF(src_utf)
    assert _env.GetObjectRefType(s) == py2jdbc.jni.jobjectType.JNILocalRefType
    assert _env.GetStringUTFLength(s) == len(src_utf) - 1
    chars = _env.GetStringUTFChars(s, None)
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
    a0 = py2jdbc.jni.jboolean.__mul__(count)()
    for i in range(count):
        a0[i] = py2jdbc.jni.jboolean(BOOLEANS[data[i]])
    _env.SetBooleanArrayRegion(a, 0, count, a0)
    a1 = _env.GetBooleanArrayElements(a, None)
    assert all(a1[i] == a0[i] for i in range(count))
    _env.ReleaseBooleanArrayElements(a, a1, py2jdbc.jni.JNI_ABORT)
    a2 = py2jdbc.jni.jboolean.__mul__(count)()
    _env.GetBooleanArrayRegion(a, 0, count, a2)
    assert all(a2[i] == a0[i] for i in range(count))
    for i in range(count):
        a2[i] = py2jdbc.jni.JNI_FALSE
    _env.SetBooleanArrayRegion(a, 0, count, a2)
    a3 = py2jdbc.jni.jboolean.__mul__(count)()
    _env.GetBooleanArrayRegion(a, 0, count, a3)
    assert all(a3[i] == py2jdbc.jni.JNI_FALSE for i in range(count))
    _env.DeleteLocalRef(a)


def test_byte_array():
    count = random.randint(0, 9)
    data = [random.randint(MIN_BYTE, MAX_BYTE) for _ in range(count)]
    a = _env.NewByteArray(count)
    a0 = py2jdbc.jni.jbyte.__mul__(count)()
    for i in range(count):
        a0[i] = data[i]
    _env.SetByteArrayRegion(a, 0, count, a0)
    a1 = _env.GetByteArrayElements(a, None)
    assert all(a1[i] == data[i] for i in range(count))
    _env.ReleaseByteArrayElements(a, a1, py2jdbc.jni.JNI_ABORT)
    a2 = py2jdbc.jni.jbyte.__mul__(count)()
    _env.GetByteArrayRegion(a, 0, count, a2)
    assert all(a2[i] == a0[i] for i in range(count))
    for i in range(count):
        a2[i] = 1
    _env.SetByteArrayRegion(a, 0, count, a2)
    a3 = py2jdbc.jni.jbyte.__mul__(count)()
    _env.GetByteArrayRegion(a, 0, count, a3)
    assert all(a3[i] == 1 for i in range(count))
    assert _env.GetArrayLength(a) == count
    _env.DeleteLocalRef(a)


def test_char_array():
    count = random.randint(0, 9)
    data = [random.randint(MIN_CHAR, MAX_CHAR) for _ in range(count)]
    a = _env.NewCharArray(count)
    a0 = py2jdbc.jni.jchar.__mul__(count)()
    for i in range(count):
        a0[i] = data[i]
    _env.SetCharArrayRegion(a, 0, count, a0)
    a1 = _env.GetCharArrayElements(a, None)
    assert all(a1[i] == data[i] for i in range(count))
    _env.ReleaseCharArrayElements(a, a1, py2jdbc.jni.JNI_ABORT)
    a2 = py2jdbc.jni.jchar.__mul__(count)()
    _env.GetCharArrayRegion(a, 0, count, a2)
    assert all(a2[i] == a0[i] for i in range(count))
    for i in range(count):
        a2[i] = 2
    _env.SetCharArrayRegion(a, 0, count, a2)
    a3 = py2jdbc.jni.jchar.__mul__(count)()
    _env.GetCharArrayRegion(a, 0, count, a3)
    assert all(a3[i] == 2 for i in range(count))
    assert _env.GetArrayLength(a) == count
    _env.DeleteLocalRef(a)


def test_short_array():
    count = random.randint(0, 9)
    data = [random.randint(MIN_SHORT, MAX_SHORT) for _ in range(count)]
    a = _env.NewShortArray(count)
    a0 = py2jdbc.jni.jshort.__mul__(count)()
    for i in range(count):
        a0[i] = data[i]
    _env.SetShortArrayRegion(a, 0, count, a0)
    a1 = _env.GetShortArrayElements(a, None)
    assert all(a1[i] == data[i] for i in range(count))
    _env.ReleaseShortArrayElements(a, a1, py2jdbc.jni.JNI_ABORT)
    a2 = py2jdbc.jni.jshort.__mul__(count)()
    _env.GetShortArrayRegion(a, 0, count, a2)
    assert all(a2[i] == a0[i] for i in range(count))
    for i in range(count):
        a2[i] = 3
    _env.SetShortArrayRegion(a, 0, count, a2)
    a3 = py2jdbc.jni.jshort.__mul__(count)()
    _env.GetShortArrayRegion(a, 0, count, a3)
    assert all(a3[i] == 3 for i in range(count))
    _env.DeleteLocalRef(a)


def test_int_array():
    count = random.randint(0, 9)
    data = [random.randint(MIN_INT, MAX_INT) for _ in range(count)]
    a = _env.NewIntArray(count)
    a0 = py2jdbc.jni.jint.__mul__(count)()
    for i in range(count):
        a0[i] = data[i]
    _env.SetIntArrayRegion(a, 0, count, a0)
    a1 = _env.GetIntArrayElements(a, None)
    assert all(a1[i] == data[i] for i in range(count))
    _env.ReleaseIntArrayElements(a, a1, py2jdbc.jni.JNI_ABORT)
    a2 = py2jdbc.jni.jint.__mul__(count)()
    _env.GetIntArrayRegion(a, 0, count, a2)
    assert all(a2[i] == a0[i] for i in range(count))
    for i in range(count):
        a2[i] = 4
    _env.SetIntArrayRegion(a, 0, count, a2)
    a3 = py2jdbc.jni.jint.__mul__(count)()
    _env.GetIntArrayRegion(a, 0, count, a3)
    assert all(a3[i] == 4 for i in range(count))
    assert _env.GetArrayLength(a) == count
    _env.DeleteLocalRef(a)


def test_long_array():
    count = random.randint(0, 9)
    data = [random.randint(MIN_LONG, MAX_LONG) for _ in range(count)]
    a = _env.NewLongArray(count)
    a0 = py2jdbc.jni.jlong.__mul__(count)()
    for i in range(count):
        a0[i] = data[i]
    _env.SetLongArrayRegion(a, 0, count, a0)
    a1 = _env.GetLongArrayElements(a, None)
    assert all(a1[i] == a0[i] for i in range(count))
    _env.ReleaseLongArrayElements(a, a1, py2jdbc.jni.JNI_ABORT)
    a2 = py2jdbc.jni.jlong.__mul__(count)()
    _env.GetLongArrayRegion(a, 0, count, a2)
    assert all(a2[i] == a0[i] for i in range(count))
    for i in range(count):
        a2[i] = 5
    _env.SetLongArrayRegion(a, 0, count, a2)
    a3 = py2jdbc.jni.jlong.__mul__(count)()
    _env.GetLongArrayRegion(a, 0, count, a3)
    assert all(a3[i] == 5 for i in range(count))
    assert _env.GetArrayLength(a) == count
    _env.DeleteLocalRef(a)


def test_float_array():
    count = random.randint(0, 9)
    data = [
        py2jdbc.jni.jfloat(random.uniform(MIN_FLOAT, MAX_FLOAT)).value
        for _ in range(count)
    ]
    a = _env.NewFloatArray(count)
    a0 = py2jdbc.jni.jfloat.__mul__(count)()
    for i in range(count):
        a0[i] = data[i]
    _env.SetFloatArrayRegion(a, 0, count, a0)
    a1 = _env.GetFloatArrayElements(a, None)
    assert all(a1[i] == a0[i] for i in range(count))
    _env.ReleaseFloatArrayElements(a, a1, py2jdbc.jni.JNI_ABORT)
    a2 = py2jdbc.jni.jfloat.__mul__(count)()
    _env.GetFloatArrayRegion(a, 0, count, a2)
    assert all(a2[i] == a0[i] for i in range(count))
    value = py2jdbc.jni.jfloat(6.5).value
    for i in range(count):
        a2[i] = value
    _env.SetFloatArrayRegion(a, 0, count, a2)
    a3 = py2jdbc.jni.jfloat.__mul__(count)()
    _env.GetFloatArrayRegion(a, 0, count, a3)
    assert all(a3[i] == value for i in range(count))
    assert _env.GetArrayLength(a) == count
    _env.DeleteLocalRef(a)


def test_double_array():
    count = random.randint(0, 9)
    data = [
        py2jdbc.jni.jdouble(random.uniform(MIN_DOUBLE, MAX_DOUBLE)).value
        for _ in range(count)
    ]
    a = _env.NewDoubleArray(count)
    a0 = py2jdbc.jni.jdouble.__mul__(count)()
    for i in range(count):
        a0[i] = data[i]
    _env.SetDoubleArrayRegion(a, 0, count, a0)
    a1 = _env.GetDoubleArrayElements(a, None)
    assert all(a1[i] == a0[i] for i in range(count))
    _env.ReleaseDoubleArrayElements(a, a1, py2jdbc.jni.JNI_ABORT)
    a2 = py2jdbc.jni.jdouble.__mul__(count)()
    _env.GetDoubleArrayRegion(a, 0, count, a2)
    assert all(a2[i] == a0[i] for i in range(count))
    value = py2jdbc.jni.jdouble(8.901234567).value
    for i in range(count):
        a2[i] = value
    _env.SetDoubleArrayRegion(a, 0, count, a2)
    a3 = py2jdbc.jni.jdouble.__mul__(count)()
    _env.GetDoubleArrayRegion(a, 0, count, a3)
    assert all(a3[i] == value for i in range(count))
    assert _env.GetArrayLength(a) == count
    _env.DeleteLocalRef(a)


def test_object_array():
    cls = _env.FindClass('java.lang.String')
    count = random.randint(0, 9)
    a = _env.NewObjectArray(count, cls, None)
    data = [hex(i) for i in range(count)]
    for i in range(count):
        s = _env.NewStringUTF(data[i])
        _env.SetObjectArrayElement(a, i, s)
        _env.DeleteLocalRef(s)
    for i in range(count):
        value = _env.GetObjectArrayElement(a, i)
        chars = _env.GetStringUTFChars(value, None)
        _env.DeleteLocalRef(value)
        assert py2jdbc.jni.decode(chars) == data[i]
    assert _env.GetArrayLength(a) == count
    _env.DeleteLocalRef(a)
    _env.DeleteLocalRef(cls)


def test_is_same_object():
    cls1 = _env.FindClass('java.lang.String')
    cls2 = _env.NewGlobalRef(cls1)
    assert _env.IsSameObject(cls1, cls2) is True
    _env.DeleteGlobalRef(cls2)
    _env.DeleteLocalRef(cls1)


def test_boolean():
    cls = _env.FindClass('java.lang.Boolean')
    fid = _env.GetStaticFieldID(cls, 'TRUE', 'Ljava/lang/Boolean;')
    obj0 = _env.GetStaticObjectField(cls, fid)
    cons = _env.GetMethodID(cls, '<init>', '(Z)V')
    args = py2jdbc.jni.jvalue.__mul__(1)()
    args[0].z = py2jdbc.jni.JNI_TRUE
    obj = _env.NewObjectA(cls, cons, args)
    mid = _env.GetMethodID(cls, 'booleanValue', '()Z')
    assert _env.CallBooleanMethodA(obj, mid, args) == py2jdbc.jni.JNI_TRUE
    assert _env.CallBooleanMethodA(obj0, mid, args) == py2jdbc.jni.JNI_TRUE
    _env.DeleteLocalRef(obj0)
    _env.DeleteLocalRef(obj)
    _env.DeleteLocalRef(cls)


def test_byte():
    cls = _env.FindClass('java.lang.Byte')
    fid = _env.GetStaticFieldID(cls, 'MAX_VALUE', 'B')
    assert _env.GetStaticByteField(cls, fid) == MAX_BYTE
    cons = _env.GetMethodID(cls, '<init>', '(B)V')
    args = py2jdbc.jni.jvalue.__mul__(1)()
    args[0].b = 42
    obj = _env.NewObjectA(cls, cons, args)
    assert obj is not None
    mid = _env.GetMethodID(cls, 'byteValue', '()B')
    assert _env.CallByteMethodA(obj, mid, args) == 42
    _env.DeleteLocalRef(obj)
    _env.DeleteLocalRef(cls)


def test_char():
    cls = _env.FindClass('java.lang.Character')
    fid = _env.GetStaticFieldID(cls, 'MAX_VALUE', 'C')
    assert _env.GetStaticCharField(cls, fid) == MAX_CHAR
    cons = _env.GetMethodID(cls, '<init>', '(C)V')
    args = py2jdbc.jni.jvalue.__mul__(1)()
    args[0].c = 0xbeef
    obj = _env.NewObjectA(cls, cons, args)
    mid = _env.GetMethodID(cls, 'charValue', '()C')
    assert _env.CallCharMethodA(obj, mid, args) == 0xbeef
    _env.DeleteLocalRef(obj)
    _env.DeleteLocalRef(cls)


def test_short():
    cls = _env.FindClass('java.lang.Short')
    fid = _env.GetStaticFieldID(cls, 'MAX_VALUE', 'S')
    assert _env.GetStaticShortField(cls, fid) == MAX_SHORT
    cons = _env.GetMethodID(cls, '<init>', '(S)V')
    args = py2jdbc.jni.jvalue.__mul__(1)()
    args[0].s = 420
    obj = _env.NewObjectA(cls, cons, args)
    mid = _env.GetMethodID(cls, 'shortValue', '()S')
    assert _env.CallShortMethodA(obj, mid, args) == 420
    _env.DeleteLocalRef(obj)
    _env.DeleteLocalRef(cls)


def test_int():
    cls = _env.FindClass('java.lang.Integer')
    fid = _env.GetStaticFieldID(cls, 'MAX_VALUE', 'I')
    assert _env.GetStaticIntField(cls, fid) == MAX_INT
    cons = _env.GetMethodID(cls, '<init>', '(I)V')
    args = py2jdbc.jni.jvalue.__mul__(1)()
    args[0].i = 0x12345678
    obj = _env.NewObjectA(cls, cons, args)
    mid = _env.GetMethodID(cls, 'intValue', '()I')
    assert _env.CallIntMethodA(obj, mid, args) == 0x12345678
    _env.DeleteLocalRef(obj)
    _env.DeleteLocalRef(cls)


def test_long():
    cls = _env.FindClass('java.lang.Long')
    fid = _env.GetStaticFieldID(cls, 'MAX_VALUE', 'J')
    assert _env.GetStaticLongField(cls, fid) == MAX_LONG
    cons = _env.GetMethodID(cls, '<init>', '(J)V')
    args = py2jdbc.jni.jvalue.__mul__(1)()
    args[0].j = 0x123456789abc
    obj = _env.NewObjectA(cls, cons, args)
    assert obj is not None
    mid = _env.GetMethodID(cls, 'longValue', '()J')
    assert _env.CallLongMethodA(obj, mid, args) == 0x123456789abc
    _env.DeleteLocalRef(obj)
    _env.DeleteLocalRef(cls)


def test_float():
    cls = _env.FindClass('java.lang.Float')
    fid = _env.GetStaticFieldID(cls, 'MAX_VALUE', 'F')
    assert _env.GetStaticFloatField(cls, fid) == MAX_FLOAT
    cons = _env.GetMethodID(cls, '<init>', '(F)V')
    args = py2jdbc.jni.jvalue.__mul__(1)()
    value = py2jdbc.jni.jfloat(1234.567).value
    args[0].f = value
    obj = _env.NewObjectA(cls, cons, args)
    mid = _env.GetMethodID(cls, 'floatValue', '()F')
    assert _env.CallFloatMethodA(obj, mid, args) == value
    _env.DeleteLocalRef(obj)
    _env.DeleteLocalRef(cls)


def test_double():
    cls = _env.FindClass('java.lang.Double')
    fid = _env.GetStaticFieldID(cls, 'MAX_VALUE', 'D')
    assert _env.GetStaticDoubleField(cls, fid) == MAX_DOUBLE
    cons = _env.GetMethodID(cls, '<init>', '(D)V')
    args = py2jdbc.jni.jvalue.__mul__(1)()
    value = py2jdbc.jni.jdouble(1234.5678901234).value
    args[0].d = value
    obj = _env.NewObjectA(cls, cons, args)
    mid = _env.GetMethodID(cls, 'doubleValue', '()D')
    assert _env.CallDoubleMethodA(obj, mid, args) == value
    _env.DeleteLocalRef(obj)
    _env.DeleteLocalRef(cls)


def test_system():
    cls = _env.FindClass('java.lang.System')
    mid = _env.GetStaticMethodID(
        cls,
        'getProperty',
        '(Ljava/lang/String;)Ljava/lang/String;'
    )
    s = _env.NewStringUTF('java.class.path')
    args = py2jdbc.jni.jvalue.__mul__(1)()
    setattr(args[0], 'l', s)
    result = _env.CallStaticObjectMethodA(cls, mid, args)
    _env.DeleteLocalRef(s)
    chars = _env.GetStringUTFChars(result, None)
    _env.DeleteLocalRef(result)
    assert py2jdbc.jni.decode(chars) == CLASSPATH
    fid = _env.GetStaticFieldID(cls, 'out', 'Ljava/io/PrintStream;')
    result2 = _env.GetStaticObjectField(cls, fid)
    _env.DeleteLocalRef(result2)
    _env.DeleteLocalRef(cls)


def test_class():
    cls = _env.FindClass('java.lang.Class')
    mid1 = _env.GetStaticMethodID(
        cls,
        'forName',
        '(Ljava/lang/String;)Ljava/lang/Class;'
    )
    s = _env.NewStringUTF('java.lang.System')
    args = py2jdbc.jni.jvalue.__mul__(1)()
    setattr(args[0], 'l', s)
    result = _env.CallStaticObjectMethodA(cls, mid1, args)
    _env.DeleteLocalRef(s)
    _env.DeleteLocalRef(result)
    mid2 = _env.GetMethodID(
        cls,
        'getName',
        '()Ljava/lang/String;'
    )
    args = py2jdbc.jni.jvalue.__mul__(0)()
    result = _env.CallObjectMethodA(
        cls,
        mid2,
        args
    )
    chars = _env.GetStringUTFChars(result, None)
    _env.DeleteLocalRef(result)
    assert py2jdbc.jni.decode(chars) == 'java.lang.Class'
    _env.DeleteLocalRef(cls)


def test_driver_manager():
    cls = _env.FindClass('java.sql.DriverManager')
    mid1 = _env.GetStaticMethodID(
        cls,
        'getConnection',
        '(Ljava/lang/String;)Ljava/sql/Connection;'
    )
    s = _env.NewStringUTF('jdbc:sqlite::memory:')
    args = py2jdbc.jni.jvalue.__mul__(1)()
    setattr(args[0], 'l', s)
    conn = _env.CallStaticObjectMethodA(cls, mid1, args)
    _env.DeleteLocalRef(s)
    _env.DeleteLocalRef(conn)
    _env.DeleteLocalRef(cls)


def test_exceptions():
    with pytest.raises(py2jdbc.jni.JavaException) as e:
        _env.FindClass('foo.bar.baz')
    _env.DeleteLocalRef(e.value.throwable)
    cls = _env.FindClass('java.sql.SQLException')
    cons = _env.GetMethodID(cls, '<init>', '()V')
    obj = _env.NewObjectA(cls, cons, None)
    with pytest.raises(py2jdbc.jni.JavaException) as e:
        _env.Throw(obj)
    _env.DeleteLocalRef(e.value.throwable)
    _env.DeleteLocalRef(obj)
    _env.DeleteLocalRef(cls)


def test_reflect_field():
    integer_cls = _env.FindClass('java.lang.Integer')
    tclass = TClass(integer_cls)
    field = tclass.getDeclaredField('MAX_VALUE')
    assert field.getName() == 'MAX_VALUE'
    fid = _env.FromReflectedField(field.obj)
    is_static = py2jdbc.jni.jboolean(py2jdbc.jni.JNI_TRUE)
    fld2 = _env.ToReflectedField(integer_cls, fid, is_static)
    assert py2jdbc.jni.get_class_name(_env, fld2) == 'java.lang.reflect.Field'
    field2 = TReflectField(fld2)
    assert field2.getName() == 'MAX_VALUE'
    assert field.hashCode() == field2.hashCode()
    del field2
    del field
    del tclass


def test_reflect_method():
    integer_cls = _env.FindClass('java.lang.Integer')
    tclass = TClass(integer_cls)
    method = tclass.getDeclaredMethod('intValue')
    assert method.getName() == 'intValue'
    mid = _env.FromReflectedMethod(method.obj)
    is_static = py2jdbc.jni.jboolean(py2jdbc.jni.JNI_FALSE)
    mth2 = _env.ToReflectedMethod(integer_cls, mid, is_static)
    method2 = TReflectMethod(mth2)
    assert method2.getName() == 'intValue'
    assert method.hashCode() == method2.hashCode()
    del method2
    del method
    del tclass


def test_custom():
    # class
    custom_cls = _env.FindClass('Custom')
    # constructors
    cons = _env.GetMethodID(custom_cls, '<init>', '()V')
    args = py2jdbc.jni.jvalue.__mul__(0)()
    obj = _env.NewObjectA(custom_cls, cons, args)
    # fields
    for code, typ, old, new in FIELDS:
        fid = _env.GetFieldID(custom_cls, '{}Field'.format(typ), code)
        if typ == 'string':
            str_obj = _env.GetObjectField(obj, fid)
            chars = _env.GetStringUTFChars(str_obj, None)
            assert py2jdbc.jni.decode(chars) == old
            _env.DeleteLocalRef(str_obj)
            str_obj = _env.NewStringUTF(new)
            _env.SetObjectField(obj, fid, str_obj)
            _env.DeleteLocalRef(str_obj)
            str_obj = _env.GetObjectField(obj, fid)
            chars = _env.GetStringUTFChars(str_obj, None)
            assert py2jdbc.jni.decode(chars) == new
            _env.DeleteLocalRef(str_obj)
            str_obj = _env.NewStringUTF(old)
            _env.SetObjectField(obj, fid, str_obj)
            _env.DeleteLocalRef(str_obj)
            str_obj = _env.GetObjectField(obj, fid)
            chars = _env.GetStringUTFChars(str_obj, None)
            assert py2jdbc.jni.decode(chars) == old
            _env.DeleteLocalRef(str_obj)
        else:
            if typ == 'char':
                old, new = ord(old), ord(new)
            getter = getattr(_env, 'Get{}Field'.format(typ.title()))
            setter = getattr(_env, 'Set{}Field'.format(typ.title()))
            fid = _env.GetFieldID(custom_cls, '{}Field'.format(typ), code)
            assert getter(obj, fid) == old
            setter(obj, fid, new)
            assert getter(obj, fid) == new
            setter(obj, fid, old)
            assert getter(obj, fid) == old

    # static fields
    for code, typ, old, new in STATIC_FIELDS:
        fid = _env.GetStaticFieldID(custom_cls, 'static{}Field'.format(typ), code)
        if typ == 'String':
            str_obj = _env.GetStaticObjectField(custom_cls, fid)
            chars = _env.GetStringUTFChars(str_obj, None)
            _env.DeleteLocalRef(str_obj)
            assert py2jdbc.jni.decode(chars) == old
            str_obj = _env.NewStringUTF(new)
            _env.SetStaticObjectField(custom_cls, fid, str_obj)
            _env.DeleteLocalRef(str_obj)
            str_obj = _env.GetStaticObjectField(custom_cls, fid)
            chars = _env.GetStringUTFChars(str_obj, None)
            _env.DeleteLocalRef(str_obj)
            assert py2jdbc.jni.decode(chars) == new
            str_obj = _env.NewStringUTF(old)
            _env.SetStaticObjectField(custom_cls, fid, str_obj)
            _env.DeleteLocalRef(str_obj)
            str_obj = _env.GetStaticObjectField(custom_cls, fid)
            chars = _env.GetStringUTFChars(str_obj, None)
            _env.DeleteLocalRef(str_obj)
            assert py2jdbc.jni.decode(chars) == old
        else:
            if typ == 'Char':
                old, new = ord(old), ord(new)
            getter = getattr(_env, 'GetStatic{}Field'.format(typ))
            setter = getattr(_env, 'SetStatic{}Field'.format(typ))
            assert getter(custom_cls, fid) == old
            setter(custom_cls, fid, new)
            assert getter(custom_cls, fid) == new
            setter(custom_cls, fid, old)
            assert getter(custom_cls, fid) == old

    # methods
    args = py2jdbc.jni.jvalue.__mul__(0)()
    mid = _env.GetStaticMethodID(custom_cls, 'staticVoidMethod', '()V')
    _env.CallStaticVoidMethodA(custom_cls, mid, args)
    mid = _env.GetStaticMethodID(custom_cls, 'staticBooleanMethod', '()Z')
    assert _env.CallStaticBooleanMethodA(custom_cls, mid, args) == py2jdbc.jni.JNI_FALSE
    mid = _env.GetStaticMethodID(custom_cls, 'staticByteMethod', '()B')
    assert _env.CallStaticByteMethodA(custom_cls, mid, args) == 0x32
    mid = _env.GetStaticMethodID(custom_cls, 'staticCharMethod', '()C')
    assert _env.CallStaticCharMethodA(custom_cls, mid, args) == 0x0196
    mid = _env.GetStaticMethodID(custom_cls, 'staticShortMethod', '()S')
    assert _env.CallStaticShortMethodA(custom_cls, mid, args) == 0x1122
    mid = _env.GetStaticMethodID(custom_cls, 'staticIntMethod', '()I')
    assert _env.CallStaticIntMethodA(custom_cls, mid, args) == 0x00112233
    mid = _env.GetStaticMethodID(custom_cls, 'staticLongMethod', '()J')
    assert _env.CallStaticLongMethodA(custom_cls, mid, args) == 0x876543210
    mid = _env.GetStaticMethodID(custom_cls, 'staticFloatMethod', '()F')
    assert _env.CallStaticFloatMethodA(custom_cls, mid, args) == py2jdbc.jni.jfloat(98.6).value
    mid = _env.GetStaticMethodID(custom_cls, 'staticDoubleMethod', '()D')
    assert (
        _env.CallStaticDoubleMethodA(custom_cls, mid, args) ==
        py2jdbc.jni.jdouble(777.665544).value
    )
    mid = _env.GetStaticMethodID(custom_cls, 'staticStringMethod', '()Ljava/lang/String;')
    str_obj = _env.CallStaticObjectMethodA(custom_cls, mid, args)
    chars = _env.GetStringUTFChars(str_obj, None)
    _env.DeleteLocalRef(str_obj)
    assert py2jdbc.jni.decode(chars) == 'hello world'
    _env.DeleteLocalRef(obj)
    _env.DeleteLocalRef(custom_cls)


def test_get_class_name():
    cls = _env.FindClass('java.lang.Integer')
    cons = _env.GetMethodID(cls, '<init>', '(I)V')
    args = py2jdbc.jni.jvalue.__mul__(1)()
    args[0].i = 0x12345678
    obj = _env.NewObjectA(cls, cons, args)
    assert py2jdbc.jni.get_class_name(_env, obj) == 'java.lang.Integer'
    _env.DeleteLocalRef(obj)
    _env.DeleteLocalRef(cls)
