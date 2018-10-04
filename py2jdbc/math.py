# -*- coding: utf8 -*-
from py2jdbc.lang import Number


class BigDecimal(Number):
    """
    Wrapper for java.math.BigDecimal java class
    """
    class Instance(Number.Instance):
        def __init__(self, cls, obj):
            super(BigDecimal.Instance, self).__init__(cls, obj)
            self.abs = lambda o=obj: cls.abs(o)

        def __abs__(self):
            return self.abs()

        def __float__(self):
            return self.doubleValue()

    def __init__(self, env, class_name='java.math.BigDecimal'):
        super(BigDecimal, self).__init__(env, class_name=class_name)
        self._ONE = self.static_field('ONE', 'Ljava/math/BigDecimal;')
        self.ROUND_CEILING = self.static_field('ROUND_CEILING', 'I')
        self.ROUND_DOWN = self.static_field('ROUND_DOWN', 'I')
        self.ROUND_FLOOR = self.static_field('ROUND_FLOOR', 'I')
        self.ROUND_HALF_DOWN = self.static_field('ROUND_HALF_DOWN', 'I')
        self.ROUND_HALF_EVEN = self.static_field('ROUND_HALF_EVEN', 'I')
        self.ROUND_HALF_UP = self.static_field('ROUND_HALF_UP', 'I')
        self.ROUND_UNNECESSARY = self.static_field('ROUND_UNNECESSARY', 'I')
        self.ROUND_UP = self.static_field('ROUND_UP', 'I')
        self._TEN = self.static_field('TEN', 'Ljava/math/BigDecimal;')
        self._ZERO = self.static_field('ZERO', 'Ljava/math/BigDecimal;')
        self.cons_s = self.constructor('Ljava/lang/String;')
        self.abs = self.method('abs', '()Ljava/math/BigDecimal;')

    def __call__(self, *args):
        return BigDecimal.Instance(self, *args)

    @property
    def ONE(self):
        return self(self._ONE)

    @property
    def TEN(self):
        return self(self._TEN)

    @property
    def ZERO(self):
        return self(self._ZERO)

    def new(self, *args):
        if len(args) != 1:
            raise ValueError("expected one argument")
        return self.cons_s(*args)
