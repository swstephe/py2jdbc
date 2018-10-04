# -*- coding: utf8 -*-
from py2jdbc.lang import Object


class Calendar(Object):
    """
    Wrapper for java.util.Calendar java abstract class
    """
    class Instance(Object.Instance):
        def __init__(self, cls, obj):
            super(Calendar.Instance, self).__init__(cls, obj)
            self.get = lambda flag, o=obj: cls.get(o, flag)
            self.getTimeInMillis = lambda o=obj: cls.getTimeInMillis(o)
            self._set2 = lambda o=obj, *a: cls._set2(o, *a)
            self._set3 = lambda o=obj, *a: cls._set3(o, *a)
            self._set5 = lambda o=obj, *a: cls._set5(o, *a)
            self._set6 = lambda o=obj, *a: cls._set6(o, *a)
            self.setTimeInMillis = lambda millis, o=obj: cls.setTimeInMillis(o, millis)

        @property
        def AM_PM(self):
            return self.get(self.cls.AM_PM)

        @property
        def DAY_OF_MONTH(self):
            return self.get(self.cls.DAY_OF_MONTH)

        @property
        def DAY_OF_WEEK(self):
            return self.get(self.cls.DAY_OF_WEEK)

        @property
        def DAY_OF_WEEK_IN_MONTH(self):
            return self.get(self.cls.DAY_OF_WEEK_IN_MONTH)

        @property
        def DAY_OF_YEAR(self):
            return self.get(self.cls.DAY_OF_YEAR)

        @property
        def DST_OFFSET(self):
            return self.get(self.cls.DST_OFFSET)

        @property
        def ERA(self):
            return self.get(self.cls.ERA)

        @property
        def HOUR(self):
            return self.get(self.cls.HOUR)

        @property
        def HOUR_OF_DAY(self):
            return self.get(self.cls.HOUR_OF_DAY)

        @property
        def MILLISECOND(self):
            return self.get(self.cls.MILLISECOND)

        @property
        def MINUTE(self):
            return self.get(self.cls.MINUTE)

        @property
        def MONTH(self):
            return self.get(self.cls.MONTH)

        @property
        def SECOND(self):
            return self.get(self.cls.SECOND)

        @property
        def SHORT(self):
            return self.get(self.cls.SHORT)

        @property
        def WEEK_OF_MONTH(self):
            return self.get(self.cls.WEEK_OF_MONTH)

        @property
        def WEEK_OF_YEAR(self):
            return self.get(self.cls.WEEK_OF_YEAR)

        @property
        def YEAR(self):
            return self.get(self.cls.YEAR)

        @property
        def ZONE_OFFSET(self):
            return self.get(self.cls.ZONE_OFFSET)

        def set(self, *args):
            if len(args) == 2:
                return self._set2(self.obj, *args)
            if len(args) == 3:
                return self._set3(self.obj, *args)
            if len(args) == 5:
                return self._set5(self.obj, *args)
            if len(args) == 6:
                return self._set6(self.obj, *args)
            raise ValueError("incorrect number of arguments: %d" % len(args))

    def __init__(self, env, class_name='java.util.Calendar'):
        super(Calendar, self).__init__(env, class_name=class_name)
        self.ALL_STYLES = self.static_field('ALL_STYLES', 'I')
        self.AM = self.static_field('AM', 'I')
        self.AM_PM = self.static_field('AM_PM', 'I')
        self.APRIL = self.static_field('APRIL', 'I')
        self.AUGUST = self.static_field('AUGUST', 'I')
        self.DATE = self.static_field('DATE', 'I')
        self.DAY_OF_MONTH = self.static_field('DAY_OF_MONTH', 'I')
        self.DAY_OF_WEEK = self.static_field('DAY_OF_WEEK', 'I')
        self.DAY_OF_WEEK_IN_MONTH = self.static_field('DAY_OF_WEEK_IN_MONTH', 'I')
        self.DAY_OF_YEAR = self.static_field('DAY_OF_YEAR', 'I')
        self.DECEMBER = self.static_field('DECEMBER', 'I')
        self.DST_OFFSET = self.static_field('DST_OFFSET', 'I')
        self.ERA = self.static_field('ERA', 'I')
        self.FEBRUARY = self.static_field('FEBRUARY', 'I')
        self.FIELD_COUNT = self.static_field('FIELD_COUNT', 'I')
        self.FRIDAY = self.static_field('FRIDAY', 'I')
        self.HOUR = self.static_field('HOUR', 'I')
        self.HOUR_OF_DAY = self.static_field('HOUR_OF_DAY', 'I')
        self.JANUARY = self.static_field('JANUARY', 'I')
        self.JULY = self.static_field('JULY', 'I')
        self.JUNE = self.static_field('JUNE', 'I')
        self.LONG = self.static_field('LONG', 'I')
        self.MARCH = self.static_field('MARCH', 'I')
        self.MAY = self.static_field('MAY', 'I')
        self.MILLISECOND = self.static_field('MILLISECOND', 'I')
        self.MINUTE = self.static_field('MINUTE', 'I')
        self.MONDAY = self.static_field('MONDAY', 'I')
        self.MONTH = self.static_field('MONTH', 'I')
        self.NOVEMBER = self.static_field('NOVEMBER', 'I')
        self.OCTOBER = self.static_field('OCTOBER', 'I')
        self.PM = self.static_field('PM', 'I')
        self.SATURDAY = self.static_field('SATURDAY', 'I')
        self.SECOND = self.static_field('SECOND', 'I')
        self.SEPTEMBER = self.static_field('SEPTEMBER', 'I')
        self.SHORT = self.static_field('SHORT', 'I')
        self.SUNDAY = self.static_field('SUNDAY', 'I')
        self.THURSDAY = self.static_field('THURSDAY', 'I')
        self.TUESDAY = self.static_field('TUESDAY', 'I')
        self.UNDECIMBER = self.static_field('UNDECIMBER', 'I')
        self.WEDNESDAY = self.static_field('WEDNESDAY', 'I')
        self.WEEK_OF_MONTH = self.static_field('WEEK_OF_MONTH', 'I')
        self.WEEK_OF_YEAR = self.static_field('WEEK_OF_YEAR', 'I')
        self.YEAR = self.static_field('YEAR', 'I')
        self.ZONE_OFFSET = self.static_field('ZONE_OFFSET', 'I')
        self.get = self.method('get', '(I)I')
        self.getTimeInMillis = self.method('getTimeInMillis', '()J')
        self._set2 = self.method('set', '(II)V')
        self._set3 = self.method('set', '(III)V')
        self._set5 = self.method('set', '(IIIII)V')
        self._set6 = self.method('set', '(IIIIII)V')
        self.setTimeInMillis = self.method('setTimeInMillis', '(J)V')

    def __call__(self, *args):
        return Calendar.Instance(self, *args)


class GregorianCalendar(Calendar):
    """
    Wrapper for java.util.GregorianCalendar java class
    """
    class Instance(Calendar.Instance):
        def __init__(self, cls, obj):
            super(GregorianCalendar.Instance, self).__init__(cls, obj)

    def __init__(self, env, class_name='java.util.GregorianCalendar'):
        super(GregorianCalendar, self).__init__(env, class_name=class_name)
        self.AD = self.static_field('AD', 'I')
        self.BC = self.static_field('BC', 'I')
        self.cons0 = self.constructor()
        self.cons3 = self.constructor('III')
        self.cons5 = self.constructor('IIIII')
        self.cons6 = self.constructor('IIIIII')

    def __call__(self, *args):
        return GregorianCalendar.Instance(self, *args)

    def new(self, *args):
        if len(args) == 0:
            return self.cons0(*args)
        elif len(args) == 3:
            return self.cons3(*args)
        elif len(args) == 5:
            return self.cons5(*args)
        elif len(args) == 6:
            return self.cons6(*args)
        return super(GregorianCalendar, self).new(*args)


class Date(Object):
    """
    Wrapper for java.util.Date java class
    """
    class Instance(Object.Instance):
        """
        Wrapper for java.util.Date object instance
        """
        def __init__(self, cls, obj):
            super(Date.Instance, self).__init__(cls, obj)

    def __init__(self, env, class_name='java.util.Date'):
        super(Date, self).__init__(env, class_name=class_name)
        self.cons_j = self.constructor('J')

    def __call__(self, *args):
        return Date.Instance(self, *args)

    def new(self, *args):
        if len(args) == 1 and isinstance(args[0], int):
            return self.cons_j(*args)
        return super(Date, self).new(*args)
