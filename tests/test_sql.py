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


def test_date():
    cls = _env.get('java.sql.Date')
    today = datetime.date.today()
    obj = cls.from_python(today)
    cal = _env.get('java.util.Calendar').getInstance()
    cal.setTime(obj.obj)
    assert cal.YEAR == today.year
    assert cal.MONTH == today.month
    assert cal.DAY_OF_MONTH == today.day


def test_time():
    cls = _env.get('java.sql.Time')
    now = datetime.datetime.now()
    t = datetime.time(now.hour, now.minute, now.second)
    obj = cls.from_python(t)
    t2 = obj.to_python()
    assert t.hour == t2.hour
    assert t.minute == t2.minute
    assert t.second == t2.second
    assert t == t2


def test_timestamp():
    # current time rounded to nearest millisecond
    cls = _env.get('java.sql.Timestamp')
    now = datetime.datetime.now()
    ts = datetime.datetime(
        now.year,
        now.month,
        now.day,
        now.hour,
        now.minute,
        now.second
    )
    obj = cls.from_python(ts)
    ts2 = obj.to_python()
    assert ts.year == ts2.year
    assert ts.month == ts2.month
    assert ts.day == ts2.day
    assert ts.hour == ts2.hour
    assert ts.minute == ts2.minute
    assert ts.second == ts2.second
    assert ts == ts2


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
