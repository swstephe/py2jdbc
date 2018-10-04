# -*- coding: utf8 -*-
import datetime
import logging
import six
import time

from py2jdbc import jni
from py2jdbc import wrap
from py2jdbc.lang import Date, Object, LangException


log = logging.getLogger(__name__)


class SQLException(LangException):
    """
    Wrapper for java.sql.SQLException
    """
    class Instance(LangException.Instance):
        def __init__(self, cls, obj):
            super(SQLException.Instance, self).__init__(cls, obj)
            self.getErrorCode = lambda o=obj: cls.getErrorCode(o)
            self.getNextException = lambda o=obj: cls.getNextException()
            self.getSQLState = lambda o=obj: cls.getSQLState(o)

    def __init__(self, env, class_name='java.sql.SQLException'):
        super(SQLException, self).__init__(env, class_name=class_name)
        self.getErrorCode = self.method('getErrorCode', '()I')
        self.getNextException = self.method('getNextException', '()Ljava/sql/SQLException;')
        self.getSQLState = self.method('getSQLState', '()Ljava/lang/String;')


class Connection(Object):
    """
    Wrapper for java.sql.Connection java class
    """
    class Instance(Object.Instance):
        def __init__(self, cls, obj):
            super(Connection.Instance, self).__init__(cls, obj)
            self.createStatement = lambda o=obj: cls.createStatement(o)
            self.close = lambda o=obj: cls.close(o)
            self.commit = lambda o=obj: cls.commit(o)
            self.getAutoCommit = lambda o=obj: cls.getAutoCommit(o)
            self.prepareStatement = lambda sql, o=obj: cls.prepareStatement(o, sql)
            self.rollback = lambda o=obj: cls.rollback(o)
            self.setAutoCommit = lambda v, o=obj: cls.setAutoCommit(o, v)

    def __init__(self, env, class_name='java.sql.Connection'):
        super(Connection, self).__init__(env, class_name=class_name)
        self.createStatement = self.method('createStatement', '()Ljava/sql/Statement;')
        self.close = self.method('close', '()V')
        self.commit = self.method('commit', '()V')
        self.getAutoCommit = self.method('getAutoCommit', '()Z')
        self.prepareStatement = self.method(
            'prepareStatement',
            '(Ljava/lang/String;)Ljava/sql/PreparedStatement;'
        )
        self.rollback = self.method('rollback', '()V')
        self.setAutoCommit = self.method('setAutoCommit', '(Z)V')

    def __call__(self, *args):
        return Connection.Instance(self, *args)


class DriverManager(Object):
    """
    Wrapper for java.sql.DriverManager java class
    """
    def __init__(self, env, class_name='java.sql.DriverManager'):
        super(DriverManager, self).__init__(env, class_name=class_name)
        self.getConnection1 = self.static_method(
            'getConnection',
            '(Ljava/lang/String;)Ljava/sql/Connection;'
        )
        self.getConnection3 = self.static_method(
            'getConnection',
            '(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/sql/Connection;'
        )
        self._getDrivers = self.static_method('getDrivers', '()Ljava/util/Enumeration;')

    def getConnection(self, *args):
        """
        Create a connection to a JDBC database.  This links to 2 overloaded
        forms, one with 1 argument and one with 3.  It checks the number of
        arguments given and calls the approprate Java method.

        :param args: 1 or 3 connection string arguments
        :return: a wrapped java.sql.Connection jobject
        """
        try:
            if len(args) == 1:
                conn = self.getConnection1(*args)
            elif len(args) == 3:
                conn = self.getConnection3(*args)
            else:
                raise RuntimeError("wrong number of arguments: %d" % len(args))
        except jni.JavaException as e:
            raise wrap.JavaException.from_jni_exception(self.env, e)
        return self.env.classes['java.sql.Connection'](conn)

    def getDrivers(self):
        """
        Fetch a list of drivers, automatically wrap
        in Enumeration and Driver wrappers.

        :return: a generator that produces a list of JDBC drivers
        """
        enumeration = self.env.classes['java.lang.Enumeration']
        driver = self.env.classes['java.sql.Driver']
        drivers = self.getDrivers()
        return (driver(obj) for obj in enumeration(drivers))


class Driver(Object):
    """
    Wrapper for java.sql.Driver java class
    """
    class Instance(Object.Instance):
        """
        Wrapper for java.sql.Driver object instance
        """
        def __init__(self, cls, obj):
            super(Driver.Instance, self).__init__(cls, obj)
            self.acceptsURL = lambda url, o=obj: cls.acceptsURL(o, url)

    def __init__(self, env, class_name='java.sql.Driver'):
        super(Driver, self).__init__(env, class_name=class_name)
        self.acceptsURL = self.method('acceptsURL', '(Ljava/lang/String;)Z')

    def __call__(self, obj):
        return Driver.Instance(self, obj)


class ParameterMetaData(Object):
    """
    Wrapper for java.sql.ParameterMetaData interface.
    """
    class Instance(Object.Instance):
        """
        Wrapper for java.sql.ParameterMetaData object instance
        """
        def __init__(self, cls, obj):
            super(ParameterMetaData.Instance, self).__init__(cls, obj)
            self.getParameterClassName = lambda i, o=obj: cls.getParameterClassName(o, i)
            self.getParameterCount = lambda o=obj: cls.getParameterCount(o)
            self.getParameterMode = lambda i, o=obj: cls.getParameterMode(o, i)
            self.getParameterType = lambda i, o=obj: cls.getParameterType(o, i)
            self.getParameterTypeName = lambda i, o=obj: cls.getParameterTypeName(o, i)
            self.getPrecision = lambda i, o=obj: cls.getPrecision(o, i)
            self.getScale = lambda i, o=obj: cls.getScale(o, i)
            self.isNullable = lambda i, o=obj: cls.isNullable(o, i)
            self.isSigned = lambda i, o=obj: cls.isSigned(o, i)

    def __init__(self, env, class_name='java.sql.ParameterMetaData'):
        super(ParameterMetaData, self).__init__(env, class_name=class_name)
        self.getParameterClassName = self.method(
            'getParameterClassName',
            '(I)Ljava/lang/String;'
        )
        self.getParameterCount = self.method('getParameterCount', '()I')
        self.getParameterMode = self.method('getParameterMode', '(I)I')
        self.getParameterType = self.method('getParameterType', '(I)I')
        self.getParameterTypeName = self.method(
            'getParameterTypeName',
            '(I)Ljava/lang/String;'
        )
        self.getPrecision = self.method('getPrecision', '(I)I')
        self.getScale = self.method('getScale', '(I)I')
        self.isNullable = self.method('isNullable', '(I)I')
        self.isSigned = self.method('isSigned', '(I)Z')
        self.parameterModeIn = self.static_field('parameterModeIn', 'I')
        self.parameterModeInOut = self.static_field('parameterModeInOut', 'I')
        self.parameterModeOut = self.static_field('parameterModeOut', 'I')
        self.parameterModeUnknown = self.static_field('parameterModeUnknown', 'I')
        self.parameterNoNulls = self.static_field('parameterNoNulls', 'I')
        self.parameterNullable = self.static_field('parameterNullable', 'I')
        self.parameterNullableUnknown = self.static_field('parameterNullableUnknown', 'I')

    def __call__(self, obj):
        return ParameterMetaData.Instance(self, obj)


class PreparedStatement(Object):
    """
    Wrapper for java.sql.PreparedStatement java class.
    """
    class Instance(Object.Instance):
        """
        Wrapper for java.sql.PreparedStatement object instance
        """
        def __init__(self, cls, obj):
            super(PreparedStatement.Instance, self).__init__(cls, obj)
            self.addBatch = lambda o=obj: cls.addBatch(o)
            self.clearParameters = lambda o=obj: cls.clearParameters(o)
            self.close = lambda o=obj: cls.close(o)
            self.execute = lambda o=obj: cls.execute(o)
            self.executeBatch = lambda o=obj: cls.executeBatch(o)
            self.getParameterMetaData = lambda o=obj: cls.getParameterMetaData(o)
            self.getResultSet = lambda o=obj: cls.getResultSet(o)
            self.getUpdateCount = lambda o=obj: cls.getUpdateCount(o)
            self.setBoolean = lambda i, v, o=obj: cls.setBoolean(o, i, v)
            self.setByte = lambda i, v, o=obj: cls.setByte(o, i, v)
            self.setDate = lambda i, v, o=obj: cls.setDate(o, i, v)
            self.setDouble = lambda i, v, o=obj: cls.setDouble(o, i, v)
            self.setFloat = lambda i, v, o=obj: cls.setFloat(o, i, v)
            self.setShort = lambda i, v, o=obj: cls.setShort(o, i, v)
            self.setInt = lambda i, v, o=obj: cls.setInt(o, i, v)
            self.setLong = lambda i, v, o=obj: cls.setLong(o, i, v)
            self.setNull = lambda i, v, o=obj: cls.setNull(o, i, v)
            self.setString = lambda i, v, o=obj: cls.setString(o, i, v)
            self.setTimestamp = lambda i, v, o=obj: cls.setTimestamp(o, i, v)
            if cls.Date is None:
                cls.Date = self.env.classes['java.sql.Date']
            if cls.Timestamp is None:
                cls.Timestamp = self.env.classes['java.sql.Timestamp']
            if cls.TypesNull is None:
                cls.TypesNull = self.env.classes['java.sql.Types'].NULL

        def set(self, i, arg):
            if arg is None:
                self.setNull(i, self.cls.TypesNull)
            elif isinstance(arg, bool):
                self.setBoolean(i, arg)
            elif isinstance(arg, int):
                self.setLong(i, arg)
            elif isinstance(arg, float):
                self.setDouble(i, arg)
            elif isinstance(arg, six.string_types):
                self.setString(i, arg)
            elif isinstance(arg, datetime.datetime):
                self.setTimestamp(i, self.cls.Timestamp(time.mktime(arg.timetuple()) * 1000))
            elif isinstance(arg, datetime.date):
                self.setDate(i, self.cls.Date(time.mktime(arg.timetuple()) * 1000))
            else:
                raise RuntimeError("can't bind to python value %r(%r)", arg, type(arg))

    def __init__(self, env, class_name='java.sql.PreparedStatement'):
        super(PreparedStatement, self).__init__(env, class_name=class_name)
        self.addBatch = self.method('addBatch', '()V')
        self.clearParameters = self.method('clearParameters', '()V')
        self.close = self.method('close', '()V')
        self.execute = self.method('execute', '()Z')
        self.executeBatch = self.method('executeBatch', '()[I')
        self.getParameterMetaData = self.method(
            'getParameterMetaData',
            '()Ljava/sql/ParameterMetaData;'
        )
        self.getResultSet = self.method('getResultSet', '()Ljava/sql/ResultSet;')
        self.getUpdateCount = self.method('getUpdateCount', '()I')
        self.setBoolean = self.method('setBoolean', '(IZ)V')
        self.setByte = self.method('setByte', '(IB)V')
        self.setDate = self.method('setDate', '(ILjava/sql/Date;)V')
        self.setDouble = self.method('setDouble', '(ID)V')
        self.setFloat = self.method('setFloat', '(IF)V')
        self.setShort = self.method('setShort', '(IS)V')
        self.setInt = self.method('setInt', '(II)V')
        self.setLong = self.method('setLong', '(IJ)V')
        self.setNull = self.method('setNull', '(II)V')
        self.setString = self.method('setString', '(ILjava/lang/String;)V')
        self.setTimestamp = self.method('setTimestamp', '(ILjava/sql/Timestamp;)V')
        self.Date = None
        self.Timestamp = None
        self.TypesNull = None

    def __call__(self, obj):
        return PreparedStatement.Instance(self, obj)


class ResultSet(Object):
    """
    Wrapper for java.sql.ResultSet java class
    """
    class Instance(Object.Instance):
        """
        Wrapper for java.sql.ResultSet object instance.

        It implements a Python iterator for iteration over rows.
        """
        def __init__(self, cls, obj):
            super(ResultSet.Instance, self).__init__(cls, obj)
            self.close = lambda o=obj: cls.close(o)
            self.getDouble = lambda i, o=obj: cls.getDouble(o, i)
            self.getInt = lambda i, o=obj: cls.getInt(o, i)
            self.getMetaData = lambda o=obj: cls.getMetaData(o)
            self.getString = lambda i, o=obj: cls.getString(o, i)
            self._next = lambda o=obj: cls.next(o)
            self.wasNull = lambda o=obj: cls.wasNull(o)

        def __iter__(self):
            return self

        def next(self):
            row = self._next()
            if not row:
                raise StopIteration()
            return row

    def __init__(self, env, class_name='java.sql.ResultSet'):
        super(ResultSet, self).__init__(env, class_name=class_name)
        self.close = self.method('close', '()V')
        self.getDouble = self.method('getDouble', '(I)D')
        self.getInt = self.method('getInt', '(I)I')
        self.getMetaData = self.method('getMetaData', '()Ljava/sql/ResultSetMetaData;')
        self.getString = self.method('getString', '(I)Ljava/lang/String;')
        self.next = self.method('next', '()Z')
        self.wasNull = self.method('wasNull', '()Z')

    def __call__(self, obj):
        return ResultSet.Instance(self, obj)


class ResultSetMetaData(Object):
    """
    Wrapper for java.sql.ResultSetMetaData java class
    """
    class Instance(Object.Instance):
        """
        Wrapper for java.sql.ResultSetMetaData object instance
        """
        def __init__(self, cls, obj):
            super(ResultSetMetaData.Instance, self).__init__(cls, obj)
            self.getColumnCount = lambda o=obj: cls.getColumnCount(o)
            self.getColumnDisplaySize = lambda i, o=obj: cls.getColumnDisplaySize(o, i)
            self.getColumnName = lambda i, o=obj: cls.getColumnName(o, i)
            self.getColumnType = lambda i, o=obj: cls.getColumnType(o, i)
            self.getColumnTypeName = lambda i, o=obj: cls.getColumnTypeName(o, i)
            self.getPrecision = lambda i, o=obj: cls.getPrecision(o, i)
            self.getScale = lambda i, o=obj: cls.getScale(o, i)
            self.isNullable = lambda i, o=obj: cls.isNullable(o, i)

    def __init__(self, env, class_name='java.sql.ResultSetMetaData'):
        super(ResultSetMetaData, self).__init__(env, class_name=class_name)
        self.getColumnCount = self.method('getColumnCount', '()I')
        self.getColumnDisplaySize = self.method('getColumnDisplaySize', '(I)I')
        self.getColumnName = self.method('getColumnName', '(I)Ljava/lang/String;')
        self.getColumnType = self.method('getColumnType', '(I)I')
        self.getColumnTypeName = self.method('getColumnTypeName', '(I)Ljava/lang/String;')
        self.getPrecision = self.method('getPrecision', '(I)I')
        self.getScale = self.method('getScale', '(I)I')
        self.isNullable = self.method('isNullable', '(I)I')

    def __call__(self, obj):
        return ResultSetMetaData.Instance(self, obj)


class SQLDate(Date):
    """
    Wrapper for java.util.Date java class
    """
    class Instance(Date.Instance):
        """
        Wrapper for java.util.Date object instance
        """
        def __init__(self, cls, obj):
            super(SQLDate.Instance, self).__init__(cls, obj)
            self.setTime = lambda value, o=obj: cls.settime(o, value)

    def __init__(self, env, class_name='java.sql.Date'):
        super(SQLDate, self).__init__(env, class_name=class_name)
        self.cons_j = self.constructor('J')
        self.setTime = self.method('setTime', '(J)V')
        self.valueOf = self.static_method(
            'valueOf',
            '(Ljava/lang/String;)Ljava/sql/Date;'
        )

    def __call__(self, *args):
        return SQLDate.Instance(*args)

    def new(self, *args):
        if len(args) == 1 and isinstance(args[0], int):
            return self.cons_j(*args)
        return super(SQLDate, self).new(*args)


class Statement(Object):
    """
    Wrapper for java.sql.Statement java class
    """
    class Instance(Object.Instance):
        """
        Wrapper for java.sql.Statement object instance
        """
        def __init__(self, cls, obj):
            super(Statement.Instance, self).__init__(cls, obj)
            self.addBatch = lambda s, o=obj: cls.addBatch(o, s)
            self.executeQuery = lambda s, o=obj: cls.executeQuery(o, s)
            self.executeUpdate = lambda s, o=obj: cls.executeUpdate(o, s)
            self.setQueryTimeout = lambda v, o=obj: cls.setQueryTimeout(o, v)

    def __init__(self, env, class_name='java.sql.Statement'):
        super(Statement, self).__init__(env, class_name=class_name)
        self.addBatch = self.method('addBatch', '(Ljava/lang/String;)V')
        self.executeQuery = self.method(
            'executeQuery',
            '(Ljava/lang/String;)Ljava/sql/ResultSet;'
        )
        self.executeUpdate = self.method('executeUpdate', '(Ljava/lang/String;)I')
        self.setQueryTimeout = self.method('setQueryTimeout', '(I)V')

    def __call__(self, obj):
        return Statement.Instance(self, obj)


class Time(Object):
    """
    Wrapper for java.sql.Time java class
    """
    def __init__(self, env, class_name='java.sql.Time'):
        super(Time, self).__init__(env, class_name=class_name)


class Timestamp(Object):
    """
    Wrapper for java.sql.Timestamp java class
    """
    def __init__(self, env, class_name='java.sql.Timestamp'):
        super(Timestamp, self).__init__(env, class_name=class_name)


class Types(Object):
    """
    Wrapper for java.sql.Types java class.

    This is basically just a set of static fields, so it
    really just loads the values for each static field.
    """
    def __init__(self, env, class_name='java.sql.Types'):
        super(Types, self).__init__(env, class_name=class_name)
        self.ARRAY = self.static_field('ARRAY', 'I')
        self.BIGINT = self.static_field('BIGINT', 'I')
        self.BINARY = self.static_field('BINARY', 'I')
        self.BIT = self.static_field('BIT', 'I')
        self.BLOB = self.static_field('BLOB', 'I')
        self.BOOLEAN = self.static_field('BOOLEAN', 'I')
        self.CHAR = self.static_field('CHAR', 'I')
        self.CLOB = self.static_field('CLOB', 'I')
        self.DATALINK = self.static_field('DATALINK', 'I')
        self.DATE = self.static_field('DATE', 'I')
        self.DECIMAL = self.static_field('DECIMAL', 'I')
        self.DISTINCT = self.static_field('DISTINCT', 'I')
        self.DOUBLE = self.static_field('DOUBLE', 'I')
        self.FLOAT = self.static_field('FLOAT', 'I')
        self.INTEGER = self.static_field('INTEGER', 'I')
        self.JAVA_OBJECT = self.static_field('JAVA_OBJECT', 'I')
        self.LONGNVARCHAR = self.static_field('LONGNVARCHAR', 'I')
        self.LONGVARBINARY = self.static_field('LONGVARBINARY', 'I')
        self.LONGVARCHAR = self.static_field('LONGVARCHAR', 'I')
        self.NCHAR = self.static_field('NCHAR', 'I')
        self.NCLOB = self.static_field('NCLOB', 'I')
        self.NULL = self.static_field('NULL', 'I')
        self.NUMERIC = self.static_field('NUMERIC', 'I')
        self.NVARCHAR = self.static_field('NVARCHAR', 'I')
        self.OTHER = self.static_field('OTHER', 'I')
        self.REAL = self.static_field('REAL', 'I')
        self.REF = self.static_field('REF', 'I')
        self.REF_CURSOR = self.static_field('REF_CURSOR', 'I')
        self.ROWID = self.static_field('ROWID', 'I')
        self.SMALLINT = self.static_field('SMALLINT', 'I')
        self.SQLXML = self.static_field('SQLXML', 'I')
        self.STRUCT = self.static_field('STRUCT', 'I')
        self.TIME = self.static_field('TIME', 'I')
        self.TIME_WITH_TIMEZONE = self.static_field('TIME_WITH_TIMEZONE', 'I')
        self.TIMESTAMP = self.static_field('TIMESTAMP', 'I')
        self.TIMESTAMP_WITH_TIMEZONE = self.static_field('TIMESTAMP_WITH_TIMEZONE', 'I')
        self.TINYINT = self.static_field('TINYINT', 'I')
        self.VARBINARY = self.static_field('VARBINARY', 'I')
        self.VARCHAR = self.static_field('VARCHAR', 'I')
