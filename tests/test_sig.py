# -*- coding: utf8 -*-
import random
import six
from ctypes import c_float, c_double
import logging
from py2jdbc import jni
from py2jdbc import sig
from tests.config import (
    CLASSPATH, JAVA_OPTS, BOOLEANS,
    MIN_BYTE, MAX_BYTE,
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
    _env = jni.get_env(**JAVA_OPTS)


def test_void():
    v = next(sig.type_signature(_env, 'V'))
    assert isinstance(v, sig.JSigVoid)
    assert v.code == 'V'
    assert v.name == 'Void'


def test_boolean():
    z = next(sig.type_signature(_env, 'Z'))
    assert isinstance(z, sig.JSigBoolean)
    assert z.code == 'Z'
    assert z.name == 'Boolean'
    assert z.jtype == jni.jboolean
    assert z.j2py(jni.JNI_FALSE) is False
    assert z.j2py(jni.JNI_TRUE) is True
    assert z.py2j(False) == jni.JNI_FALSE
    assert z.py2j(True) == jni.JNI_TRUE
    val = jni.jvalue()
    assert val.z == jni.JNI_FALSE
    z.jval(val, jni.JNI_TRUE)
    assert val.z == jni.JNI_TRUE


def test_byte():
    b = next(sig.type_signature(_env, 'B'))
    assert isinstance(b, sig.JSigByte)
    assert b.code == 'B'
    assert b.name == 'Byte'
    assert b.jtype == jni.jbyte
    assert b.j2py(12) == 12
    assert b.j2py(-35) == -35
    assert b.py2j(46) == 46
    assert b.py2j(-79) == -79
    val = jni.jvalue()
    assert val.b == 0
    b.jval(val, 88)
    assert val.b == 88


def test_char():
    c = next(sig.type_signature(_env, 'C'))
    assert isinstance(c, sig.JSigChar)
    assert c.code == 'C'
    assert c.name == 'Char'
    assert c.jtype == jni.jchar
    assert c.j2py(12) == six.unichr(12)
    assert c.j2py(ord('#')) == '#'
    assert c.py2j('.') == ord('.')
    assert c.py2j('O') == ord('O')
    val = jni.jvalue()
    assert val.c == 0
    c.jval(val, 'X')
    assert val.c == ord('X')


def test_short():
    s = next(sig.type_signature(_env, 'S'))
    assert isinstance(s, sig.JSigShort)
    assert s.code == 'S'
    assert s.name == 'Short'
    assert s.jtype == jni.jshort
    assert s.j2py(1200) == 1200
    assert s.j2py(-3511) == -3511
    assert s.py2j(4622) == 4622
    assert s.py2j(-7933) == -7933
    val = jni.jvalue()
    assert val.s == 0
    s.jval(val, 8844)
    assert val.s == 8844


def test_int():
    i = next(sig.type_signature(_env, 'I'))
    assert isinstance(i, sig.JSigInt)
    assert i.code == 'I'
    assert i.name == 'Int'
    assert i.jtype == jni.jint
    assert i.j2py(120055) == 120055
    assert i.j2py(-351166) == -351166
    assert i.py2j(462277) == 462277
    assert i.py2j(-793388) == -793388
    val = jni.jvalue()
    assert val.i == 0
    i.jval(val, 884499)
    assert val.i == 884499


def test_long():
    j = next(sig.type_signature(_env, 'J'))
    assert isinstance(j, sig.JSigLong)
    assert j.code == 'J'
    assert j.name == 'Long'
    assert j.jtype == jni.jlong
    assert j.j2py(1200112233) == 1200112233
    assert j.j2py(-3511445566) == -3511445566
    assert j.py2j(4622778899) == 4622778899
    assert j.py2j(-7933223344) == -7933223344
    val = jni.jvalue()
    assert val.j == 0
    j.jval(val, 8844556677)
    assert val.j == 8844556677


def test_float():
    f = next(sig.type_signature(_env, 'F'))
    assert isinstance(f, sig.JSigFloat)
    assert f.code == 'F'
    assert f.name == 'Float'
    assert f.jtype == jni.jfloat
    assert f.j2py(1.2) == 1.2
    assert f.j2py(-3.5) == -3.5
    assert f.py2j(4.6) == 4.6
    assert f.py2j(-7.9) == -7.9
    val = jni.jvalue()
    assert val.f == 0
    f.jval(val, 8.4)
    assert abs(val.f - 8.4) < 1e-6


def test_double():
    d = next(sig.type_signature(_env, 'D'))
    assert isinstance(d, sig.JSigDouble)
    assert d.code == 'D'
    assert d.name == 'Double'
    assert d.jtype == jni.jdouble
    assert d.j2py(1.233) == 1.233
    assert d.j2py(-3.51122) == -3.51122
    assert d.py2j(46.2233) == 46.2233
    assert d.py2j(-79.3344) == -79.3344
    val = jni.jvalue()
    assert val.d == 0
    d.jval(val, 88.445566)
    assert abs(val.d - 88.445566) < 1e-30


def test_boolean_array():
    za = next(sig.type_signature(_env, '[Z'))
    assert isinstance(za, sig.JSigBooleanArray)
    assert za.code == '[Z'
    assert za.name == 'BooleanArray'
    assert za.jtype == jni.jboolean
    count = 10
    a = [random.choice(BOOLEANS) for _ in range(count)]
    a1 = jni.jboolean.__mul__(count)(*a)
    ja = _env.NewBooleanArray(count)
    _env.SetBooleanArrayRegion(ja, 0, count, a1)
    assert za.j2py(ja) == a
    j2 = za.py2j(a)
    a2 = _env.GetBooleanArrayElements(j2, None)
    for i in range(count):
        assert a2[i] == a1[i]
    _env.ReleaseBooleanArrayElements(j2, a2, jni.JNI_ABORT)
    _env.DeleteLocalRef(j2)
    _env.DeleteLocalRef(ja)


def test_byte_array():
    ba = next(sig.type_signature(_env, '[B'))
    assert isinstance(ba, sig.JSigByteArray)
    assert ba.code == '[B'
    assert ba.name == 'ByteArray'
    assert ba.jtype == jni.jbyte
    count = 10
    a = [random.randint(MIN_BYTE, MAX_BYTE) for _ in range(count)]
    a1 = jni.jbyte.__mul__(count)(*a)
    ja = _env.NewByteArray(count)
    _env.SetByteArrayRegion(ja, 0, count, a1)
    assert ba.j2py(ja) == a
    j2 = ba.py2j(a)
    a2 = _env.GetByteArrayElements(j2, None)
    for i in range(count):
        assert a2[i] == a1[i]
    _env.ReleaseByteArrayElements(j2, a2, jni.JNI_ABORT)
    _env.DeleteLocalRef(j2)
    _env.DeleteLocalRef(ja)


def test_char_array():
    ca = next(sig.type_signature(_env, '[C'))
    assert isinstance(ca, sig.JSigCharArray)
    assert ca.code == '[C'
    assert ca.name == 'CharArray'
    assert ca.jtype == jni.jchar
    count = 10
    a = list(six.unichr(random.randint(MIN_CHAR, MAX_CHAR)) for _ in range(count))
    a1 = jni.jchar.__mul__(count)(*(ord(x) for x in a))
    ja = _env.NewCharArray(count)
    _env.SetCharArrayRegion(ja, 0, count, a1)
    assert ca.j2py(ja) == a
    j2 = ca.py2j(a)
    a2 = _env.GetCharArrayElements(j2, None)
    for i in range(count):
        assert a2[i] == a1[i]
    _env.ReleaseCharArrayElements(j2, a2, jni.JNI_ABORT)
    _env.DeleteLocalRef(j2)
    _env.DeleteLocalRef(ja)


def test_short_array():
    sa = next(sig.type_signature(_env, '[S'))
    assert isinstance(sa, sig.JSigShortArray)
    assert sa.code == '[S'
    assert sa.name == 'ShortArray'
    assert sa.jtype == jni.jshort
    count = 10
    a = [random.randint(MIN_SHORT, MAX_SHORT) for _ in range(count)]
    a1 = jni.jshort.__mul__(count)(*a)
    ja = _env.NewShortArray(count)
    _env.SetShortArrayRegion(ja, 0, count, a1)
    assert sa.j2py(ja) == a
    j2 = sa.py2j(a)
    a2 = _env.GetShortArrayElements(j2, None)
    for i in range(count):
        assert a2[i] == a1[i]
    _env.ReleaseShortArrayElements(j2, a2, jni.JNI_ABORT)
    _env.DeleteLocalRef(j2)
    _env.DeleteLocalRef(ja)


def test_int_array():
    ia = next(sig.type_signature(_env, '[I'))
    assert isinstance(ia, sig.JSigIntArray)
    assert ia.code == '[I'
    assert ia.name == 'IntArray'
    assert ia.jtype == jni.jint
    count = 10
    a = [random.randint(MIN_INT, MAX_INT) for _ in range(count)]
    a1 = jni.jint.__mul__(count)(*a)
    ja = _env.NewIntArray(count)
    _env.SetIntArrayRegion(ja, 0, count, a1)
    assert ia.j2py(ja) == a
    j2 = ia.py2j(a)
    a2 = _env.GetIntArrayElements(j2, None)
    for i in range(count):
        assert a2[i] == a1[i]
    _env.ReleaseIntArrayElements(j2, a2, jni.JNI_ABORT)
    _env.DeleteLocalRef(j2)
    _env.DeleteLocalRef(ja)


def test_long_array():
    jj = next(sig.type_signature(_env, '[J'))
    assert isinstance(jj, sig.JSigLongArray)
    assert jj.code == '[J'
    assert jj.name == 'LongArray'
    assert jj.jtype == jni.jlong
    count = 10
    a = [random.randint(MIN_LONG, MAX_LONG) for _ in range(count)]
    a1 = jni.jlong.__mul__(count)(*a)
    ja = _env.NewLongArray(count)
    _env.SetLongArrayRegion(ja, 0, count, a1)
    assert jj.j2py(ja) == a
    j2 = jj.py2j(a)
    a2 = _env.GetLongArrayElements(j2, None)
    for i in range(count):
        assert a2[i] == a1[i]
    _env.ReleaseLongArrayElements(j2, a2, jni.JNI_ABORT)
    _env.DeleteLocalRef(j2)
    _env.DeleteLocalRef(ja)


def test_float_array():
    fa = next(sig.type_signature(_env, '[F'))
    assert isinstance(fa, sig.JSigFloatArray)
    assert fa.code == '[F'
    assert fa.name == 'FloatArray'
    assert fa.jtype == jni.jfloat
    count = 10
    a = [c_float(random.gauss(0, 1e10)).value for _ in range(count)]
    a1 = jni.jfloat.__mul__(count)(*a)
    ja = _env.NewFloatArray(count)
    _env.SetFloatArrayRegion(ja, 0, count, a1)
    j1 = fa.j2py(ja)
    assert sum(abs(j1[i] - a[i]) for i in range(count)) == 0
    j2 = fa.py2j(a)
    a2 = _env.GetFloatArrayElements(j2, None)
    assert sum(abs(a2[i] - a1[i]) for i in range(count)) == 0
    _env.ReleaseFloatArrayElements(j2, a2, jni.JNI_ABORT)
    _env.DeleteLocalRef(j2)
    _env.DeleteLocalRef(ja)


def test_double_array():
    da = next(sig.type_signature(_env, '[D'))
    assert isinstance(da, sig.JSigDoubleArray)
    assert da.code == '[D'
    assert da.name == 'DoubleArray'
    assert da.jtype == jni.jdouble
    count = 10
    a = [c_double(random.gauss(0, 1e10)).value for _ in range(count)]
    a1 = jni.jdouble.__mul__(count)(*a)
    ja = _env.NewDoubleArray(count)
    _env.SetDoubleArrayRegion(ja, 0, count, a1)
    j1 = da.j2py(ja)
    assert sum(abs(j1[i] - a[i]) for i in range(count)) == 0
    j2 = da.py2j(a)
    a2 = _env.GetDoubleArrayElements(j2, None)
    assert sum(abs(a2[i] - a1[i]) for i in range(count)) == 0
    _env.ReleaseDoubleArrayElements(j2, a2, jni.JNI_ABORT)
    _env.DeleteLocalRef(j2)
    _env.DeleteLocalRef(ja)


def test_system():
    cls = _env.FindClass('java.lang.System')
    jni.check_exception(_env)
    assert cls is not None
    signature = '(Ljava/lang/String;)Ljava/lang/String;'
    mid = _env.GetStaticMethodID(cls, 'getProperty', signature)
    jni.check_exception(_env)
    assert mid is not None
    argtypes, restype = sig.method_signature(_env, signature)
    result = restype.call_static(cls, mid, argtypes, 'java.class.path')
    assert result == CLASSPATH
    signature = 'Ljava/io/PrintStream;'
    fid = _env.GetStaticFieldID(cls, 'out', signature)
    t = next(sig.type_signature(_env, signature))
    jni.check_exception(_env)
    result2 = t.get_static(cls, fid)
    assert result2 is not None
    _env.DeleteLocalRef(result2)
    _env.DeleteLocalRef(cls)


def test_class():
    cls = _env.FindClass('java.lang.Class')
    jni.check_exception(_env)
    assert cls is not None
    signature = '(Ljava/lang/String;)Ljava/lang/Class;'
    mid1 = _env.GetStaticMethodID(cls, 'forName', signature)
    jni.check_exception(_env)
    assert mid1 is not None
    argtypes, restype = sig.method_signature(_env, signature)
    result = restype.call_static(cls, mid1, argtypes, 'java.lang.System')
    assert result is not None
    _env.DeleteLocalRef(result)
    signature = '()Ljava/lang/String;'
    mid2 = _env.GetMethodID(cls, 'getName', signature)
    jni.check_exception(_env)
    assert mid2 is not None
    argtypes, restype = sig.method_signature(_env, signature)
    result = restype.call(cls, mid2, argtypes)
    assert result == 'java.lang.Class'
    _env.DeleteLocalRef(cls)


def test_drivermanager():
    cls = _env.FindClass('java.sql.DriverManager')
    jni.check_exception(_env)
    assert cls is not None
    signature = '(Ljava/lang/String;)Ljava/sql/Connection;'
    mid1 = _env.GetStaticMethodID(cls, 'getConnection', signature)
    jni.check_exception(_env)
    assert mid1 is not None
    argtypes, restype = sig.method_signature(_env, signature)
    conn = restype.call_static(cls, mid1, argtypes, 'jdbc:sqlite::memory:')
    assert conn is not None
    _env.DeleteLocalRef(conn)
    _env.DeleteLocalRef(cls)


def _new(class_name, signature, *values):
    cls = _env.FindClass(class_name)
    jni.check_exception(_env)
    assert cls is not None
    argtypes, restype = sig.constructor_signature(_env, class_name, signature)
    mid = _env.GetMethodID(cls, '<init>', '({})V'.format(signature))
    jni.check_exception(_env)
    obj = restype.new(cls, mid, argtypes, *values)
    jni.check_exception(_env)
    assert obj is not None
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
