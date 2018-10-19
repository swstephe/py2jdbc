# -*- coding: utf8 -*-
import os
import six
from py2jdbc.jni import JNI_FALSE, JNI_TRUE, jfloat, jdouble
from py2jdbc.jvm import CP_SEP

BOOLEANS = JNI_FALSE, JNI_TRUE
MIN_BYTE = -0x80
MAX_BYTE = 0x7f
MIN_CHAR = 0x0000
MAX_CHAR = 0xffff
MIN_SHORT = -0x8000
MAX_SHORT = 0x7fff
MIN_INT = -0x80000000
MAX_INT = 0x7fffffff
MIN_LONG = -0x8000000000000000
MAX_LONG = 0x7fffffffffffffff
MIN_FLOAT = -3.4028234663852887e+38
MAX_FLOAT = 3.4028234663852886e+38
ERR_FLOAT = 1e-06
MIN_DOUBLE = -1.7976931348623157e+308
MAX_DOUBLE = 1.7976931348623157e+308
ERR_DOUBLE = 1e-30

FIELDS = (
    ('Z', 'boolean', JNI_TRUE, JNI_FALSE),
    ('B', 'byte', 0x01, 0x23),
    ('C', 'char', six.unichr(2), six.unichr(0x0161)),
    ('S', 'short', 0x0123, 0x0567),
    ('I', 'int', 0x0123456, 0x0abecafe),
    ('J', 'long', 0x0123456789, 0xbeefcafe),
    ('F', 'float', jfloat(123.456).value, jfloat(3.14).value),
    ('D', 'double', jdouble(123456.789789).value, jdouble(3.14159265).value),
    (
        'Ljava/lang/String;',
        'string',
        'abcdef',
        'one two three'
    )
)

STATIC_FIELDS = (
    ('Z', 'Boolean', JNI_FALSE, JNI_TRUE),
    ('B', 'Byte', 0x04, 0x26),
    ('C', 'Char', six.unichr(8), six.unichr(33)),
    ('S', 'Short', 0x0456, 0x6540),
    ('I', 'Int', 0x07890123, 0x11122233),
    ('J', 'Long', 0x56789abc, 0x1111222233334444),
    ('F', 'Float', jfloat(987.453).value, jfloat(0.000123).value),
    ('D', 'Double', jdouble(789.1234567).value, jdouble(-1.456e13).value),
    (
        'Ljava/lang/String;',
        'String',
        'Sell your cleverness and buy bewilderment.',
        'Let silence take you to the core of life.'
    )
)

CWD = os.path.dirname(os.path.realpath(__file__))
LIB = os.path.join(CWD, 'lib')
SRC = os.path.join(CWD, 'src')
CLASSPATH = CP_SEP.join([
    os.path.join(SRC),
    os.path.join(LIB, 'sqlite-jdbc-3.23.1.jar'),
    os.path.join(LIB, 'mysql-connector-java-8.0.12.jar'),
])
DRIVER = 'org.sqlite.JDBC'
JAVA_OPTS = dict(classpath=CLASSPATH, verbose=('memory', 'gc'), check='jni')
