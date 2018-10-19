# -*- coding: utf8 -*-
import os
import random
import six
from ctypes import c_float, c_double
import logging
import py2jdbc.jni
import py2jdbc.sig
from tests.config import (
    CLASSPATH, JAVA_OPTS, BOOLEANS,
    MIN_CHAR, MAX_CHAR,
    MIN_SHORT, MAX_SHORT,
    MIN_LONG, MAX_LONG,
    MIN_INT, MAX_INT
)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

_env = None


def setup_module():
    global _env
    _env = py2jdbc.jni.get_env(**JAVA_OPTS)


def test_void():
    v = next(py2jdbc.sig.type_signature(_env, 'V'))
    assert isinstance(v, py2jdbc.sig.JSigVoid)
    assert v.code == 'V'
    assert v.name == 'Void'


def test_boolean():
    z = next(py2jdbc.sig.type_signature(_env, 'Z'))
    assert isinstance(z, py2jdbc.sig.JSigBoolean)
    assert z.code == 'Z'
    assert z.name == 'Boolean'
    assert z.jtype == py2jdbc.jni.jboolean
    assert z.j2py(py2jdbc.jni.JNI_FALSE) is False
    assert z.j2py(py2jdbc.jni.JNI_TRUE) is True
    assert z.py2j(False) == py2jdbc.jni.JNI_FALSE
    assert z.py2j(True) == py2jdbc.jni.JNI_TRUE
    val = py2jdbc.jni.jvalue()
    assert val.z == py2jdbc.jni.JNI_FALSE
    z.jval(val, py2jdbc.jni.JNI_TRUE)
    assert val.z == py2jdbc.jni.JNI_TRUE


def test_byte():
    b = next(py2jdbc.sig.type_signature(_env, 'B'))
    assert isinstance(b, py2jdbc.sig.JSigByte)
    assert b.code == 'B'
    assert b.name == 'Byte'
    assert b.jtype == py2jdbc.jni.jbyte
    assert b.j2py(12) == 12
    assert b.j2py(-35) == -35
    assert b.py2j(46) == 46
    assert b.py2j(-79) == -79
    val = py2jdbc.jni.jvalue()
    assert val.b == 0
    b.jval(val, 88)
    assert val.b == 88


def test_char():
    c = next(py2jdbc.sig.type_signature(_env, 'C'))
    assert isinstance(c, py2jdbc.sig.JSigChar)
    assert c.code == 'C'
    assert c.name == 'Char'
    assert c.jtype == py2jdbc.jni.jchar
    assert c.j2py(12) == six.unichr(12)
    assert c.j2py(ord('#')) == '#'
    assert c.py2j('.') == ord('.')
    assert c.py2j('O') == ord('O')
    val = py2jdbc.jni.jvalue()
    assert val.c == 0
    c.jval(val, 'X')
    assert val.c == ord('X')


def test_short():
    s = next(py2jdbc.sig.type_signature(_env, 'S'))
    assert isinstance(s, py2jdbc.sig.JSigShort)
    assert s.code == 'S'
    assert s.name == 'Short'
    assert s.jtype == py2jdbc.jni.jshort
    assert s.j2py(1200) == 1200
    assert s.j2py(-3511) == -3511
    assert s.py2j(4622) == 4622
    assert s.py2j(-7933) == -7933
    val = py2jdbc.jni.jvalue()
    assert val.s == 0
    s.jval(val, 8844)
    assert val.s == 8844


def test_int():
    i = next(py2jdbc.sig.type_signature(_env, 'I'))
    assert isinstance(i, py2jdbc.sig.JSigInt)
    assert i.code == 'I'
    assert i.name == 'Int'
    assert i.jtype == py2jdbc.jni.jint
    assert i.j2py(120055) == 120055
    assert i.j2py(-351166) == -351166
    assert i.py2j(462277) == 462277
    assert i.py2j(-793388) == -793388
    val = py2jdbc.jni.jvalue()
    assert val.i == 0
    i.jval(val, 884499)
    assert val.i == 884499


def test_long():
    j = next(py2jdbc.sig.type_signature(_env, 'J'))
    assert isinstance(j, py2jdbc.sig.JSigLong)
    assert j.code == 'J'
    assert j.name == 'Long'
    assert j.jtype == py2jdbc.jni.jlong
    assert j.j2py(1200112233) == 1200112233
    assert j.j2py(-3511445566) == -3511445566
    assert j.py2j(4622778899) == 4622778899
    assert j.py2j(-7933223344) == -7933223344
    val = py2jdbc.jni.jvalue()
    assert val.j == 0
    j.jval(val, 8844556677)
    assert val.j == 8844556677


def test_float():
    f = next(py2jdbc.sig.type_signature(_env, 'F'))
    assert isinstance(f, py2jdbc.sig.JSigFloat)
    assert f.code == 'F'
    assert f.name == 'Float'
    assert f.jtype == py2jdbc.jni.jfloat
    assert f.j2py(1.2) == 1.2
    assert f.j2py(-3.5) == -3.5
    assert f.py2j(4.6) == 4.6
    assert f.py2j(-7.9) == -7.9
    val = py2jdbc.jni.jvalue()
    assert val.f == 0
    f.jval(val, 8.4)
    assert abs(val.f - 8.4) < 1e-6


def test_double():
    d = next(py2jdbc.sig.type_signature(_env, 'D'))
    assert isinstance(d, py2jdbc.sig.JSigDouble)
    assert d.code == 'D'
    assert d.name == 'Double'
    assert d.jtype == py2jdbc.jni.jdouble
    assert d.j2py(1.233) == 1.233
    assert d.j2py(-3.51122) == -3.51122
    assert d.py2j(46.2233) == 46.2233
    assert d.py2j(-79.3344) == -79.3344
    val = py2jdbc.jni.jvalue()
    assert val.d == 0
    d.jval(val, 88.445566)
    assert abs(val.d - 88.445566) < 1e-30


def test_boolean_array():
    za = next(py2jdbc.sig.type_signature(_env, '[Z'))
    assert isinstance(za, py2jdbc.sig.JSigBooleanArray)
    assert za.code == '[Z'
    assert za.name == 'BooleanArray'
    assert za.jtype == py2jdbc.jni.jboolean
    count = 10
    a = [random.choice(BOOLEANS) for _ in range(count)]
    a1 = py2jdbc.jni.jboolean.__mul__(count)(*a)
    ja = _env.NewBooleanArray(count)
    _env.SetBooleanArrayRegion(ja, 0, count, a1)
    assert za.j2py(ja) == a
    j2 = za.py2j(a)
    a2 = _env.GetBooleanArrayElements(j2, None)
    for i in range(count):
        assert a2[i] == a1[i]
    _env.ReleaseBooleanArrayElements(j2, a2, py2jdbc.jni.JNI_ABORT)
    _env.DeleteLocalRef(j2)
    _env.DeleteLocalRef(ja)


def test_byte_array():
    ba = next(py2jdbc.sig.type_signature(_env, '[B'))
    assert isinstance(ba, py2jdbc.sig.JSigByteArray)
    assert ba.code == '[B'
    assert ba.name == 'ByteArray'
    assert ba.jtype == py2jdbc.jni.jbyte
    count = 10
    a = os.urandom(count)
    a1 = py2jdbc.jni.jbyte.__mul__(count)(*a)
    ja = _env.NewByteArray(count)
    _env.SetByteArrayRegion(ja, 0, count, a1)
    assert ba.j2py(ja) == a
    j2 = ba.py2j(a)
    a2 = _env.GetByteArrayElements(j2, None)
    for i in range(count):
        assert a2[i] == a1[i]
    _env.ReleaseByteArrayElements(j2, a2, py2jdbc.jni.JNI_ABORT)
    _env.DeleteLocalRef(j2)
    _env.DeleteLocalRef(ja)


def test_char_array():
    ca = next(py2jdbc.sig.type_signature(_env, '[C'))
    assert isinstance(ca, py2jdbc.sig.JSigCharArray)
    assert ca.code == '[C'
    assert ca.name == 'CharArray'
    assert ca.jtype == py2jdbc.jni.jchar
    count = 10
    a = list(six.unichr(random.randint(MIN_CHAR, MAX_CHAR)) for _ in range(count))
    a1 = py2jdbc.jni.jchar.__mul__(count)(*(ord(x) for x in a))
    ja = _env.NewCharArray(count)
    _env.SetCharArrayRegion(ja, 0, count, a1)
    assert ca.j2py(ja) == a
    j2 = ca.py2j(a)
    a2 = _env.GetCharArrayElements(j2, None)
    for i in range(count):
        assert a2[i] == a1[i]
    _env.ReleaseCharArrayElements(j2, a2, py2jdbc.jni.JNI_ABORT)
    _env.DeleteLocalRef(j2)
    _env.DeleteLocalRef(ja)


def test_short_array():
    sa = next(py2jdbc.sig.type_signature(_env, '[S'))
    assert isinstance(sa, py2jdbc.sig.JSigShortArray)
    assert sa.code == '[S'
    assert sa.name == 'ShortArray'
    assert sa.jtype == py2jdbc.jni.jshort
    count = 10
    a = [random.randint(MIN_SHORT, MAX_SHORT) for _ in range(count)]
    a1 = py2jdbc.jni.jshort.__mul__(count)(*a)
    ja = _env.NewShortArray(count)
    _env.SetShortArrayRegion(ja, 0, count, a1)
    assert sa.j2py(ja) == a
    j2 = sa.py2j(a)
    a2 = _env.GetShortArrayElements(j2, None)
    for i in range(count):
        assert a2[i] == a1[i]
    _env.ReleaseShortArrayElements(j2, a2, py2jdbc.jni.JNI_ABORT)
    _env.DeleteLocalRef(j2)
    _env.DeleteLocalRef(ja)


def test_int_array():
    ia = next(py2jdbc.sig.type_signature(_env, '[I'))
    assert isinstance(ia, py2jdbc.sig.JSigIntArray)
    assert ia.code == '[I'
    assert ia.name == 'IntArray'
    assert ia.jtype == py2jdbc.jni.jint
    count = 10
    a = [random.randint(MIN_INT, MAX_INT) for _ in range(count)]
    a1 = py2jdbc.jni.jint.__mul__(count)(*a)
    ja = _env.NewIntArray(count)
    _env.SetIntArrayRegion(ja, 0, count, a1)
    assert ia.j2py(ja) == a
    j2 = ia.py2j(a)
    a2 = _env.GetIntArrayElements(j2, None)
    for i in range(count):
        assert a2[i] == a1[i]
    _env.ReleaseIntArrayElements(j2, a2, py2jdbc.jni.JNI_ABORT)
    _env.DeleteLocalRef(j2)
    _env.DeleteLocalRef(ja)


def test_long_array():
    jj = next(py2jdbc.sig.type_signature(_env, '[J'))
    assert isinstance(jj, py2jdbc.sig.JSigLongArray)
    assert jj.code == '[J'
    assert jj.name == 'LongArray'
    assert jj.jtype == py2jdbc.jni.jlong
    count = 10
    a = [random.randint(MIN_LONG, MAX_LONG) for _ in range(count)]
    a1 = py2jdbc.jni.jlong.__mul__(count)(*a)
    ja = _env.NewLongArray(count)
    _env.SetLongArrayRegion(ja, 0, count, a1)
    assert jj.j2py(ja) == a
    j2 = jj.py2j(a)
    a2 = _env.GetLongArrayElements(j2, None)
    for i in range(count):
        assert a2[i] == a1[i]
    _env.ReleaseLongArrayElements(j2, a2, py2jdbc.jni.JNI_ABORT)
    _env.DeleteLocalRef(j2)
    _env.DeleteLocalRef(ja)


def test_float_array():
    fa = next(py2jdbc.sig.type_signature(_env, '[F'))
    assert isinstance(fa, py2jdbc.sig.JSigFloatArray)
    assert fa.code == '[F'
    assert fa.name == 'FloatArray'
    assert fa.jtype == py2jdbc.jni.jfloat
    count = 10
    a = [c_float(random.gauss(0, 1e10)).value for _ in range(count)]
    a1 = py2jdbc.jni.jfloat.__mul__(count)(*a)
    ja = _env.NewFloatArray(count)
    _env.SetFloatArrayRegion(ja, 0, count, a1)
    j1 = fa.j2py(ja)
    assert sum(abs(j1[i] - a[i]) for i in range(count)) == 0
    j2 = fa.py2j(a)
    a2 = _env.GetFloatArrayElements(j2, None)
    assert sum(abs(a2[i] - a1[i]) for i in range(count)) == 0
    _env.ReleaseFloatArrayElements(j2, a2, py2jdbc.jni.JNI_ABORT)
    _env.DeleteLocalRef(j2)
    _env.DeleteLocalRef(ja)


def test_double_array():
    da = next(py2jdbc.sig.type_signature(_env, '[D'))
    assert isinstance(da, py2jdbc.sig.JSigDoubleArray)
    assert da.code == '[D'
    assert da.name == 'DoubleArray'
    assert da.jtype == py2jdbc.jni.jdouble
    count = 10
    a = [c_double(random.gauss(0, 1e10)).value for _ in range(count)]
    a1 = py2jdbc.jni.jdouble.__mul__(count)(*a)
    ja = _env.NewDoubleArray(count)
    _env.SetDoubleArrayRegion(ja, 0, count, a1)
    j1 = da.j2py(ja)
    assert sum(abs(j1[i] - a[i]) for i in range(count)) == 0
    j2 = da.py2j(a)
    a2 = _env.GetDoubleArrayElements(j2, None)
    assert sum(abs(a2[i] - a1[i]) for i in range(count)) == 0
    _env.ReleaseDoubleArrayElements(j2, a2, py2jdbc.jni.JNI_ABORT)
    _env.DeleteLocalRef(j2)
    _env.DeleteLocalRef(ja)


def test_system():
    cls = _env.FindClass('java.lang.System')
    signature = '(Ljava/lang/String;)Ljava/lang/String;'
    mid = _env.GetStaticMethodID(cls, 'getProperty', signature)
    argtypes, restype = py2jdbc.sig.method_signature(_env, signature)
    result = restype.call_static(cls, mid, argtypes, 'java.class.path')
    assert result == CLASSPATH
    signature = 'Ljava/io/PrintStream;'
    fid = _env.GetStaticFieldID(cls, 'out', signature)
    t = next(py2jdbc.sig.type_signature(_env, signature))
    result2 = t.get_static(cls, fid)
    assert result2 is not None
    _env.DeleteLocalRef(result2)
    _env.DeleteLocalRef(cls)


def test_class():
    cls = _env.FindClass('java.lang.Class')
    signature = '(Ljava/lang/String;)Ljava/lang/Class;'
    mid1 = _env.GetStaticMethodID(cls, 'forName', signature)
    argtypes, restype = py2jdbc.sig.method_signature(_env, signature)
    result = restype.call_static(cls, mid1, argtypes, 'java.lang.System')
    assert result is not None
    _env.DeleteLocalRef(result)
    signature = '()Ljava/lang/String;'
    mid2 = _env.GetMethodID(cls, 'getName', signature)
    argtypes, restype = py2jdbc.sig.method_signature(_env, signature)
    result = restype.call(cls, mid2, argtypes)
    assert result == 'java.lang.Class'
    _env.DeleteLocalRef(cls)


def test_drivermanager():
    cls = _env.FindClass('java.sql.DriverManager')
    signature = '(Ljava/lang/String;)Ljava/sql/Connection;'
    mid1 = _env.GetStaticMethodID(cls, 'getConnection', signature)
    argtypes, restype = py2jdbc.sig.method_signature(_env, signature)
    conn = restype.call_static(cls, mid1, argtypes, 'jdbc:sqlite::memory:')
    assert conn is not None
    _env.DeleteLocalRef(conn)
    _env.DeleteLocalRef(cls)


def _new(class_name, signature, *values):
    cls = _env.FindClass(class_name)
    argtypes, restype = py2jdbc.sig.constructor_signature(_env, class_name, signature)
    mid = _env.GetMethodID(cls, '<init>', '({})V'.format(signature))
    obj = restype.new(cls, mid, argtypes, *values)
    _env.DeleteLocalRef(obj)
    _env.DeleteLocalRef(cls)


def test_new_boolean():
    _new('java.lang.Boolean', 'Ljava/lang/String;', 'true')
    _new('java.lang.Boolean', 'Z', True)


def test_new_byte():
    _new('java.lang.Byte', 'Ljava/lang/String;', '123')
    _new('java.lang.Byte', 'B', 123)


def test_new_char():
    _new('java.lang.Character', 'C', six.unichr(123))


def test_new_short():
    _new('java.lang.Short', 'Ljava/lang/String;', '12345')
    _new('java.lang.Short', 'S', 12345)


def test_new_int():
    _new('java.lang.Integer', 'Ljava/lang/String;', '654321')
    _new('java.lang.Integer', 'I', 654321)


def test_new_long():
    _new('java.lang.Long', 'Ljava/lang/String;', '789654321')
    _new('java.lang.Long', 'J', 789654321)


def test_new_float():
    _new('java.lang.Float', 'Ljava/lang/String;', '3.1415')
    _new('java.lang.Float', 'F', 3.1415)
    _new('java.lang.Float', 'D', 3.1415)


def test_new_double():
    _new('java.lang.Double', 'Ljava/lang/String;', '3.14159265')
    _new('java.lang.Double', 'D', 3.14159265)
