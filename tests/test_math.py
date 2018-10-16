# -*- coding: utf8 -*-
import logging
from py2jdbc.wrap import get_env
from py2jdbc.math import BigDecimal
from tests.config import JAVA_OPTS

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

_env = None


def setup_module():
    global _env
    _env = get_env(**JAVA_OPTS)


def test_big_decimal():
    cls = _env.get('java.math.BigDecimal')
    assert isinstance(cls.ONE, BigDecimal.Instance)
    assert isinstance(cls.ROUND_CEILING, int)
    assert isinstance(cls.TEN, BigDecimal.Instance)
    assert isinstance(cls.ZERO, BigDecimal.Instance)
    obj = cls.new('123.567')
    assert isinstance(obj, BigDecimal.Instance)
    assert int(obj) == 123
    assert float(obj) == 123.567
    assert cls.new('-123').abs() == cls.new(123)
