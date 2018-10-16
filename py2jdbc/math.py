# -*- coding: utf8 -*-
import six
from py2jdbc.lang import Number


class BigDecimal(Number):
    """
    Wrapper for java.math.BigDecimal java class
    """
    class_name = 'java.math.BigDecimal'

    class Instance(Number.Instance):
        def __init__(self, cls, obj):
            super(BigDecimal.Instance, self).__init__(cls, obj)
            self._abs = lambda o=obj: cls.abs(o)

        def abs(self):
            return self.cls(self._abs())

        def __abs__(self):
            return self.abs()

        def __float__(self):
            return self.doubleValue()

    def __init__(self, env):
        super(BigDecimal, self).__init__(env)
        if self.class_name == BigDecimal.class_name:
            self.cons_s = self.constructor('Ljava/lang/String;')
            self.cons_j = self.constructor('J')
        self._ONE = self.static_field('ONE', 'Ljava/math/BigDecimal;')
        self._ROUND_CEILING = self.static_field('ROUND_CEILING', 'I')
        self._ROUND_DOWN = self.static_field('ROUND_DOWN', 'I')
        self._ROUND_FLOOR = self.static_field('ROUND_FLOOR', 'I')
        self._ROUND_HALF_DOWN = self.static_field('ROUND_HALF_DOWN', 'I')
        self._ROUND_HALF_EVEN = self.static_field('ROUND_HALF_EVEN', 'I')
        self._ROUND_HALF_UP = self.static_field('ROUND_HALF_UP', 'I')
        self._ROUND_UNNECESSARY = self.static_field('ROUND_UNNECESSARY', 'I')
        self._ROUND_UP = self.static_field('ROUND_UP', 'I')
        self._TEN = self.static_field('TEN', 'Ljava/math/BigDecimal;')
        self._ZERO = self.static_field('ZERO', 'Ljava/math/BigDecimal;')
        self.abs = self.method('abs', '()Ljava/math/BigDecimal;')

    @property
    def ONE(self):
        return self(self._ONE.get(self.cls))

    @property
    def ROUND_CEILING(self):
        return self._ROUND_CEILING.get(self.cls)

    @property
    def ROUND_DOWN(self):
        return self._ROUND_DOWN.get(self.cls)

    @property
    def ROUND_FLOOR(self):
        return self._ROUND_FLOOR.get(self.cls)

    @property
    def ROUND_HALF_DOWN(self):
        return self._ROUND_HALF_DOWN.get(self.cls)

    @property
    def ROUND_HALF_EVEN(self):
        return self._ROUND_HALF_EVEN.get(self.cls)

    @property
    def ROUND_HALF_UP(self):
        return self._ROUND_HALF_UP.get(self.cls)

    @property
    def ROUND_UNNECESSARY(self):
        return self._ROUND_UNNECESSARY.get(self.cls)

    @property
    def ROUND_UP(self):
        return self._ROUND_UP.get(self.cls)

    @property
    def TEN(self):
        return self(self._TEN.get(self.cls))

    @property
    def ZERO(self):
        return self(self._ZERO.get(self.cls))

    def new(self, *args):
        if len(args) == 1:
            if isinstance(args[0], six.string_types):
                return self.cons_s(args[0])
            else:
                return self.cons_j(args[0])
        return super(BigDecimal, self).new(*args)
