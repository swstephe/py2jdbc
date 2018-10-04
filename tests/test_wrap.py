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

