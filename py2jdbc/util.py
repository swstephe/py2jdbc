# -*- coding: utf8 -*-
import datetime
from py2jdbc.lang import Object


class Calendar(Object):
    """
    Wrapper for java.util.Calendar java abstract class
    """
    class_name = 'java.util.Calendar'

    class Instance(Object.Instance):
        def __init__(self, cls, obj):
            super(Calendar.Instance, self).__init__(cls, obj)
            self.get = lambda flag, o=obj: cls.get(o, flag)
            self.getTimeInMillis = lambda o=obj: cls.getTimeInMillis(o)
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

        def getTime(self):
            cls = self.env.get('java.util.Date')
            return cls(self.cls.getTime(self.obj))

        def set(self, *args):
            if len(args) == 2:
                return self.cls.set2(self.obj, *args)
            if len(args) == 3:
                return self.cls.set3(self.obj, *args)
            if len(args) == 5:
                return self.cls.set5(self.obj, *args)
            if len(args) == 6:
                return self.cls.set6(self.obj, *args)
            raise ValueError("incorrect number of arguments: %d" % len(args))

        def setTime(self, date_instance):
            return self.cls.setTime(self.obj, date_instance)

    def __init__(self, env):
        super(Calendar, self).__init__(env)
        self._ALL_STYLES = self.static_field('ALL_STYLES', 'I')
        self._AM = self.static_field('AM', 'I')
        self._AM_PM = self.static_field('AM_PM', 'I')
        self._APRIL = self.static_field('APRIL', 'I')
        self._AUGUST = self.static_field('AUGUST', 'I')
        self._DATE = self.static_field('DATE', 'I')
        self._DAY_OF_MONTH = self.static_field('DAY_OF_MONTH', 'I')
        self._DAY_OF_WEEK = self.static_field('DAY_OF_WEEK', 'I')
        self._DAY_OF_WEEK_IN_MONTH = self.static_field('DAY_OF_WEEK_IN_MONTH', 'I')
        self._DAY_OF_YEAR = self.static_field('DAY_OF_YEAR', 'I')
        self._DECEMBER = self.static_field('DECEMBER', 'I')
        self._DST_OFFSET = self.static_field('DST_OFFSET', 'I')
        self._ERA = self.static_field('ERA', 'I')
        self._FEBRUARY = self.static_field('FEBRUARY', 'I')
        self._FIELD_COUNT = self.static_field('FIELD_COUNT', 'I')
        self._FRIDAY = self.static_field('FRIDAY', 'I')
        self._HOUR = self.static_field('HOUR', 'I')
        self._HOUR_OF_DAY = self.static_field('HOUR_OF_DAY', 'I')
        self._JANUARY = self.static_field('JANUARY', 'I')
        self._JULY = self.static_field('JULY', 'I')
        self._JUNE = self.static_field('JUNE', 'I')
        self._LONG = self.static_field('LONG', 'I')
        self._MARCH = self.static_field('MARCH', 'I')
        self._MAY = self.static_field('MAY', 'I')
        self._MILLISECOND = self.static_field('MILLISECOND', 'I')
        self._MINUTE = self.static_field('MINUTE', 'I')
        self._MONDAY = self.static_field('MONDAY', 'I')
        self._MONTH = self.static_field('MONTH', 'I')
        self._NOVEMBER = self.static_field('NOVEMBER', 'I')
        self._OCTOBER = self.static_field('OCTOBER', 'I')
        self._PM = self.static_field('PM', 'I')
        self._SATURDAY = self.static_field('SATURDAY', 'I')
        self._SECOND = self.static_field('SECOND', 'I')
        self._SEPTEMBER = self.static_field('SEPTEMBER', 'I')
        self._SHORT = self.static_field('SHORT', 'I')
        self._SUNDAY = self.static_field('SUNDAY', 'I')
        self._THURSDAY = self.static_field('THURSDAY', 'I')
        self._TUESDAY = self.static_field('TUESDAY', 'I')
        self._UNDECIMBER = self.static_field('UNDECIMBER', 'I')
        self._WEDNESDAY = self.static_field('WEDNESDAY', 'I')
        self._WEEK_OF_MONTH = self.static_field('WEEK_OF_MONTH', 'I')
        self._WEEK_OF_YEAR = self.static_field('WEEK_OF_YEAR', 'I')
        self._YEAR = self.static_field('YEAR', 'I')
        self._ZONE_OFFSET = self.static_field('ZONE_OFFSET', 'I')
        self._getInstance0 = self.static_method('getInstance', '()Ljava/util/Calendar;')
        self.get = self.method('get', '(I)I')
        self.getTime = self.method('getTime', '()Ljava/util/Date;')
        self.getTimeInMillis = self.method('getTimeInMillis', '()J')
        self.set2 = self.method('set', '(II)V')
        self.set3 = self.method('set', '(III)V')
        self.set5 = self.method('set', '(IIIII)V')
        self.set6 = self.method('set', '(IIIIII)V')
        self.setTime = self.method('setTime', '(Ljava/util/Date;)V')
        self.setTimeInMillis = self.method('setTimeInMillis', '(J)V')

    @property
    def ALL_STYLES(self):
        return self._ALL_STYLES.get(self.cls)

    @property
    def AM(self):
        return self._AM.get(self.cls)

    @property
    def AM_PM(self):
        return self._AM_PM.get(self.cls)

    @property
    def APRIL(self):
        return self._APRIL.get(self.cls)

    @property
    def AUGUST(self):
        return self._AUGUST.get(self.cls)

    @property
    def DATE(self):
        return self._DATE.get(self.cls)

    @property
    def DAY_OF_MONTH(self):
        return self._DAY_OF_MONTH.get(self.cls)

    @property
    def DAY_OF_WEEK(self):
        return self._DAY_OF_WEEK.get(self.cls)

    @property
    def DAY_OF_WEEK_IN_MONTH(self):
        return self._DAY_OF_WEEK_IN_MONTH.get(self.cls)

    @property
    def DAY_OF_YEAR(self):
        return self._DAY_OF_YEAR.get(self.cls)

    @property
    def DECEMBER(self):
        return self._DECEMBER.get(self.cls)

    @property
    def DST_OFFSET(self):
        return self._DST_OFFSET.get(self.cls)

    @property
    def ERA(self):
        return self._ERA.get(self.cls)

    @property
    def FEBRUARY(self):
        return self._FEBRUARY.get(self.cls)

    @property
    def FIELD_COUNT(self):
        return self._FIELD_COUNT.get(self.cls)

    @property
    def FRIDAY(self):
        return self._FRIDAY.get(self.cls)

    @property
    def HOUR(self):
        return self._HOUR.get(self.cls)

    @property
    def HOUR_OF_DAY(self):
        return self._HOUR_OF_DAY.get(self.cls)

    @property
    def JANUARY(self):
        return self._JANUARY.get(self.cls)

    @property
    def JULY(self):
        return self._JULY.get(self.cls)

    @property
    def JUNE(self):
        return self._JUNE.get(self.cls)

    @property
    def LONG(self):
        return self._LONG.get(self.cls)

    @property
    def MARCH(self):
        return self._MARCH.get(self.cls)

    @property
    def MAY(self):
        return self._MAY.get(self.cls)

    @property
    def MILLISECOND(self):
        return self._MILLISECOND.get(self.cls)

    @property
    def MINUTE(self):
        return self._MINUTE.get(self.cls)

    @property
    def MONDAY(self):
        return self._MONDAY.get(self.cls)

    @property
    def MONTH(self):
        return self._MONTH.get(self.cls)

    @property
    def NOVEMBER(self):
        return self._NOVEMBER.get(self.cls)

    @property
    def OCTOBER(self):
        return self._OCTOBER.get(self.cls)

    @property
    def PM(self):
        return self._PM.get(self.cls)

    @property
    def SATURDAY(self):
        return self._SATURDAY.get(self.cls)

    @property
    def SECOND(self):
        return self._SECOND.get(self.cls)

    @property
    def SEPTEMBER(self):
        return self._SEPTEMBER.get(self.cls)

    @property
    def SHORT(self):
        return self._SHORT.get(self.cls)

    @property
    def SUNDAY(self):
        return self._SUNDAY.get(self.cls)

    @property
    def THURSDAY(self):
        return self._THURSDAY.get(self.cls)

    @property
    def TUESDAY(self):
        return self._TUESDAY.get(self.cls)

    @property
    def UNDECIMBER(self):
        return self._UNDECIMBER.get(self.cls)

    @property
    def WEDNESDAY(self):
        return self._WEDNESDAY.get(self.cls)

    @property
    def WEEK_OF_MONTH(self):
        return self._WEEK_OF_MONTH.get(self.cls)

    @property
    def WEEK_OF_YEAR(self):
        return self._WEEK_OF_YEAR.get(self.cls)

    @property
    def YEAR(self):
        return self._YEAR.get(self.cls)

    @property
    def ZONE_OFFSET(self):
        return self._ZONE_OFFSET.get(self.cls)

    def getInstance(self, *args):
        if len(args) == 0:
            return self(self._getInstance0(self.cls))
        raise RuntimeError("unexpected arguments: %r" % args)


class GregorianCalendar(Calendar):
    """
    Wrapper for java.util.GregorianCalendar java class
    """
    class_name = 'java.util.GregorianCalendar'

    class Instance(Calendar.Instance):
        def __init__(self, cls, obj):
            super(GregorianCalendar.Instance, self).__init__(cls, obj)

    def __init__(self, env):
        super(GregorianCalendar, self).__init__(env)
        if self.class_name == GregorianCalendar.class_name:
            self.cons0 = self.constructor()
            self.cons3 = self.constructor('III')
            self.cons5 = self.constructor('IIIII')
            self.cons6 = self.constructor('IIIIII')
        self._AD = self.static_field('AD', 'I')
        self._BC = self.static_field('BC', 'I')

    @property
    def AD(self):
        return self._AD.get(self.cls)

    @property
    def BC(self):
        return self._BC.get(self.cls)

    def new(self, *args):
        if len(args) == 0:
            return self.cons0()
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
    class_name = 'java.util.Date'

    class Instance(Object.Instance):
        """
        Wrapper for java.util.Date object instance
        """
        def __init__(self, cls, obj):
            super(Date.Instance, self).__init__(cls, obj)

        def to_python(self):
            cal = self.cls.cal.new()
            cal.setTime(self.obj)
            return datetime.date(cal.YEAR, cal.MONTH, cal.DAY_OF_MONTH)

    def __init__(self, env):
        super(Date, self).__init__(env)
        self.cal = self.env.get('java.util.GregorianCalendar')
        if self.class_name == Date.class_name:
            self.cons_j = self.constructor('J')

    def new(self, *args):
        if len(args) == 1:
            if isinstance(args[0], int):
                return self.cons_j(args[0])
        return super(Date, self).new(*args)

    def from_python(self, value):
        if isinstance(value, datetime.date):
            cal = self.cal.new(value.year, value.month, value.day)
            return cal.getTime()
        return self.new(value)


class Enumeration(Object):
    """
    Wrapper for java.util.Enumeration java class.

    This is used to wrap things returning an Enumeration<T> object.
    It is up to the programmer to wrap the return values in the appropriate
    wrapper object.
    """
    class_name = 'java.util.Enumeration'

    class Instance(Object.Instance):
        """
        Wrapper for java.util.Enumeration object instance.

        Implements Python iterator symantics.
        """
        def __init__(self, cls, obj):
            super(Enumeration.Instance, self).__init__(cls, obj)
            self.hasMoreElements = lambda o=obj: cls.hasMoreElements(o)
            self.nextElement = lambda o=obj: cls.nextElement(o)

        def __iter__(self):
            return self

        def next(self):
            if not self.hasMoreElements():
                raise StopIteration()
            return self.nextElement()

    def __init__(self, env):
        super(Enumeration, self).__init__(env)
        self.hasMoreElements = self.method('hasMoreElements', '()Z')
        self.nextElement = self.method('nextElement', '()Ljava/lang/Object;')
