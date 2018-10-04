# -*- coding: utf8 -*-
import logging
from py2jdbc import wrap
from tests.config import JAVA_OPTS

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

_env = None


def setup_module():
    global _env
    _env = wrap.get_env(**JAVA_OPTS)


def test_drivermanager():
    cls = _env.classes['java.sql.DriverManager']
    conn = cls.getConnection('jdbc:sqlite::memory:')
    assert conn is not None
    value = conn.getAutoCommit()
    assert value in (True, False)
    conn.setAutoCommit(value)
    conn.close()


def test_types():
    cls = _env.classes['java.sql.Types']
    assert cls.VARCHAR == 12
