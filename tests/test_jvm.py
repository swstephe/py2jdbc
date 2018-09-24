# -*- coding: utf8 -*-
import os
from py2jdbc import jvm

CWD = os.path.dirname(os.path.realpath(__file__))
LIB = os.path.join(CWD, 'lib')


def test_find_libjvm():
    path = jvm.find_libjvm()
    assert path is not None
    assert os.path.exists(path)


def test_get_classpath():
    cp = jvm.get_classpath()
    assert cp is not None
    cp_env = os.getenv('CLASSPATH')
    if cp_env:
        assert cp_env == cp
    else:
        assert cp == ''

    cp = jvm.get_classpath(LIB)
    assert cp is not None
    assert LIB in cp
