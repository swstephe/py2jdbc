# -*- coding: utf8 -*-
import logging
from py2jdbc.wrap import get_env
from py2jdbc.util import GregorianCalendar
from tests.config import JAVA_OPTS

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

_env = None


def setup_module():
    global _env
    _env = get_env(**JAVA_OPTS)


def test_calendar():
    cls = _env.get('java.util.GregorianCalendar')
    assert cls is not None
    cal = cls.new(2018, 9, 26)
    assert cal.ERA == cls.AD
    assert cal.YEAR == 2018
    assert cal.MONTH == 9
    assert cal.DAY_OF_MONTH == 26
    cal.set(2018, 9, 26, 12, 34, 56)
    assert cal.ERA == cls.AD
    assert cal.YEAR == 2018
    assert cal.MONTH == 9
    assert cal.DAY_OF_MONTH == 26
    assert cal.HOUR == 0
    assert cal.HOUR_OF_DAY == 12
    assert cal.AM_PM == cls.PM
    assert cal.MINUTE == 34
    assert cal.SECOND == 56
    assert cal.MILLISECOND == 0
