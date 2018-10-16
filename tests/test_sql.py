# -*- coding: utf8 -*-
import datetime
import logging
from py2jdbc.wrap import get_env
import py2jdbc.sql
from tests.config import JAVA_OPTS

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

_env = None


def setup_module():
    global _env
    _env = get_env(**JAVA_OPTS)


def test_time():
    cls = _env.get('java.sql.Time')
    now = datetime.datetime.fromtimestamp(
        round(datetime.datetime.now().timestamp()*1000.) / 1000.
    )
    obj = cls.from_time(now.time())
    now2 = obj.to_time()
    assert now.hour == now2.hour
    assert now.minute == now2.minute
    assert now.second == now2.second
    assert now.microsecond == now2.microsecond


def test_timestamp():
    # current time rounded to nearest millisecond
    cls = _env.get('java.sql.Timestamp')
    now = datetime.datetime.fromtimestamp(
        round(datetime.datetime.now().timestamp()*1000.) / 1000.
    )
    obj = cls.from_datetime(now)
    now2 = obj.to_datetime()
    assert now.year == now2.year
    assert now.month == now2.month
    assert now.day == now2.day
    assert now.hour == now2.hour
    assert now.minute == now2.minute
    assert now.second == now2.second
    assert now.microsecond == now2.microsecond


def test_drivermanager():
    cls = _env.get('java.sql.DriverManager')
    conn = cls.getConnection('jdbc:sqlite::memory:')
    assert conn is not None
    value = conn.getAutoCommit()
    assert value in (True, False)
    conn.setAutoCommit(value)
    conn.close()


def test_types():
    cls = _env.get('java.sql.Types')
    assert cls.VARCHAR == 12
