# -*- coding: utf8 -*-
import os
from py2jdbc.jni import JNI_FALSE, JNI_TRUE

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

CWD = os.path.dirname(os.path.realpath(__file__))
LIB = os.path.join(CWD, 'lib')
SRC = os.path.join(CWD, 'src')
CLASSPATH = ':'.join([
    os.path.join(SRC),
    os.path.join(LIB, 'sqlite-jdbc-3.23.1.jar'),
])
DRIVER = 'org.sqlite.JDBC'
JAVA_OPTS = dict(classpath=CLASSPATH, verbose=('memory', 'gc'), check='jni')
