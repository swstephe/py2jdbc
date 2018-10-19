# -*- coding: utf8 -*-
import os
import py2jdbc.jvm

CWD = os.path.dirname(os.path.realpath(__file__))
LIB = os.path.join(CWD, 'lib')


def test_find_libjvm():
    path = py2jdbc.jvm.find_libjvm()
    assert path is not None
    assert os.path.exists(path)


def test_get_classpath():
    cp = py2jdbc.jvm.get_classpath()
    assert cp is not None
    cp_env = os.getenv('CLASSPATH')
    if cp_env:
        assert cp_env == cp
    else:
        assert cp == ''

    cp = py2jdbc.jvm.get_classpath(LIB)
    assert cp is not None
    assert LIB in cp
