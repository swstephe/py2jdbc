# -*- coding: utf8 -*-
import datetime
import logging
import six

from py2jdbc.lang import LangException, Object, ArgumentError
from py2jdbc.util import Date


log = logging.getLogger(__name__)


class SQLException(LangException):
    """
    Wrapper for java.sql.SQLException
    """
    class_name = 'java.sql.SQLException'

    class Instance(LangException.Instance):
        def __init__(self, cls, obj):
            super(SQLException.Instance, self).__init__(cls, obj)
            self.getErrorCode = lambda o=obj: cls.getErrorCode(o)
            self.getNextException = lambda o=obj: cls.getNextException()
            self.getSQLState = lambda o=obj: cls.getSQLState(o)

    def __init__(self, env):
        super(SQLException, self).__init__(env)
        self.getErrorCode = self.method('getErrorCode', '()I')
        self.getNextException = self.method('getNextException', '()Ljava/sql/SQLException;')
        self.getSQLState = self.method('getSQLState', '()Ljava/lang/String;')


class Connection(Object):
    """
    Wrapper for java.sql.Connection java class
    """
    class_name = 'java.sql.Connection'

    class Instance(Object.Instance):
        def __init__(self, cls, obj):
            super(Connection.Instance, self).__init__(cls, obj)
            self.close = lambda o=obj: cls.close(o)
            self.commit = lambda o=obj: cls.commit(o)
            self.getAutoCommit = lambda o=obj: cls.getAutoCommit(o)
            self.rollback = lambda o=obj: cls.rollback(o)
            self.setAutoCommit = lambda v, o=obj: cls.setAutoCommit(o, v)

        def createStatement(self):
            cls = self.env.get('java.sql.Statement')
            return cls(self.cls.createStatement(self.obj))

        def getMetaData(self):
            cls = self.env.get('java.sql.DatabaseMetaData')
            return cls(self.cls.getMetaData(self.obj))

        def prepareCall(self, sql):
            cls = self.env.get('java.sql.CallableStatement')
            return cls(self.cls.prepareCall(self.obj, sql))

        def prepareStatement(self, sql):
            cls = self.env.get('java.sql.PreparedStatement')
            return cls(self.cls.prepareStatement(self.obj, sql))

    def __init__(self, env):
        super(Connection, self).__init__(env)
        self.createStatement = self.method('createStatement', '()Ljava/sql/Statement;')
        self.close = self.method('close', '()V')
        self.commit = self.method('commit', '()V')
        self.getAutoCommit = self.method('getAutoCommit', '()Z')
        self.getMetaData = self.method('getMetaData', '()Ljava/sql/DatabaseMetaData;')
        self.prepareCall = self.method(
            'prepareCall',
            '(Ljava/lang/String;)Ljava/sql/CallableStatement;'
        )
        self.prepareStatement = self.method(
            'prepareStatement',
            '(Ljava/lang/String;)Ljava/sql/PreparedStatement;'
        )
        self.rollback = self.method('rollback', '()V')
        self.setAutoCommit = self.method('setAutoCommit', '(Z)V')


class DatabaseMetaData(Object):
    """
    Wrapper for java.sql.DatabaseMetaData java interface
    """
    class_name = 'java.sql.DatabaseMetaData'

    class Instance(Object.Instance):
        def __init__(self, cls, obj):
            super(DatabaseMetaData.Instance, self).__init__(cls, obj)
            if self.cls.ResultSet is None:
                self.cls.ResultSet = self.env.get('java.sql.ResultSet')

        def getCatalogs(self):
            return self.cls.ResultSet(self.cls.getCatalogs(self.obj))

        def getFunctionColumns(self, catalog, schema, functions, columns):
            return self.cls.ResultSet(self.cls.getFunctionColumns(
                self.obj,
                catalog,
                schema,
                functions,
                columns
            ))

        def getFunctions(self, catalog, schemas, functions):
            return self.cls.ResultSet(self.cls.getFunctions(
                self.obj,
                catalog,
                schemas,
                functions
            ))


        def getProcedureColumns(self, catalog, schemas, procedures, columns):
            return self.cls.ResultSet(self.cls.getProcedureColumns(
                self.obj,
                catalog,
                schemas,
                procedures,
                columns
            ))

        def getProcedures(self, catalog, schemas, procedures):
            return self.cls.ResultSet(self.cls.getProcedures(
                self.obj,
                catalog,
                schemas,
                procedures
            ))

        def getSchemas(self, catalog, schemas):
            return self.cls.ResultSet(self.cls.getSchemas(
                self.obj,
                catalog,
                schemas
            ))

        def getTables(self, catalog, schemas, tables, types):
            return self.cls.ResultSet(self.cls.getTables(
                self.obj,
                catalog,
                schemas,
                tables,
                types
            ))

    def __init__(self, env):
        super(DatabaseMetaData, self).__init__(env)
        self.ResultSet = None
        self._attributeNoNulls = self.static_field('attributeNoNulls', 'S')
        self._attributeNullable = self.static_field('attributeNullable', 'S')
        self._attributeNullableUnknown = self.static_field('attributeNullableUnknown', 'S')
        self._bestRowNotPseudo = self.static_field('bestRowNotPseudo', 'I')
        self._bestRowPseudo = self.static_field('bestRowPseudo', 'I')
        self._bestRowSession = self.static_field('bestRowSession', 'I')
        self._bestRowTemporary = self.static_field('bestRowTemporary', 'I')
        self._bestRowTransaction = self.static_field('bestRowTransaction', 'I')
        self._bestRowUnknown = self.static_field('bestRowUnknown', 'I')
        self._columnNoNulls = self.static_field('columnNoNulls', 'I')
        self._columnNullable = self.static_field('columnNullable', 'I')
        self._columnNullableUnknown = self.static_field('columnNullableUnknown', 'I')
        self._functionColumnIn = self.static_field('functionColumnIn', 'I')
        self._functionColumnInOut = self.static_field('functionColumnInOut', 'I')
        self._functionColumnOut = self.static_field('functionColumnOut', 'I')
        self._functionColumnResult = self.static_field('functionColumnResult', 'I')
        self._functionColumnUnknown = self.static_field('functionColumnUnknown', 'I')
        self._functionNoNulls = self.static_field('functionNoNulls', 'I')
        self._functionNoTable = self.static_field('functionNoTable', 'I')
        self._functionNullable = self.static_field('functionNullable', 'I')
        self._functionNullableUnknown = self.static_field('functionNullableUnknown', 'I')
        self._functionResultUnknown = self.static_field('functionResultUnknown', 'I')
        self._functionReturn = self.static_field('functionReturn', 'I')
        self._functionReturnsTable = self.static_field('functionReturnsTable', 'I')
        self._importedKeyCascade = self.static_field('importedKeyCascade', 'I')
        self._importedKeyInitiallyDeferred = self.static_field(
            'importedKeyInitiallyDeferred', 'I')
        self._importedKeyInitiallyImmediate = self.static_field(
            'importedKeyInitiallyImmediate', 'I')
        self._importedKeyNoAction = self.static_field('importedKeyNoAction', 'I')
        self._importedKeyNotDeferrable = self.static_field('importedKeyNotDeferrable', 'I')
        self._importedKeyRestrict = self.static_field('importedKeyRestrict', 'I')
        self._importedKeySetDefault = self.static_field('importedKeySetDefault', 'I')
        self._importedKeySetNull = self.static_field('importedKeySetNull', 'I')
        self._procedureColumnIn = self.static_field('procedureColumnIn', 'I')
        self._procedureColumnInOut = self.static_field('procedureColumnInOut', 'I')
        self._procedureColumnOut = self.static_field('procedureColumnOut', 'I')
        self._procedureColumnResult = self.static_field('procedureColumnResult', 'I')
        self._procedureColumnReturn = self.static_field('procedureColumnReturn', 'I')
        self._procedureColumnUnknown = self.static_field('procedureColumnUnknown', 'I')
        self._procedureNoNulls = self.static_field('procedureNoNulls', 'I')
        self._procedureNoResult = self.static_field('procedureNoResult', 'I')
        self._procedureNullable = self.static_field('procedureNullable', 'I')
        self._procedureNullableUnknown = self.static_field('procedureNullableUnknown', 'I')
        self._procedureResultUnknown = self.static_field('procedureResultUnknown', 'I')
        self._procedureReturnsResult = self.static_field('procedureReturnsResult', 'I')
        self._sqlStateSQL = self.static_field('sqlStateSQL', 'I')
        self._sqlStateSQL99 = self.static_field('sqlStateSQL99', 'I')
        self._sqlStateXOpen = self.static_field('sqlStateXOpen', 'I')
        self._tableIndexClustered = self.static_field('tableIndexClustered', 'S')
        self._tableIndexHashed = self.static_field('tableIndexHashed', 'S')
        self._tableIndexOther = self.static_field('tableIndexOther', 'S')
        self._tableIndexStatistic = self.static_field('tableIndexStatistic', 'S')
        self._typeNoNulls = self.static_field('typeNoNulls', 'I')
        self._typeNullable = self.static_field('typeNullable', 'I')
        self._typeNullableUnknown = self.static_field('typeNullableUnknown', 'I')
        self._typePredBasic = self.static_field('typePredBasic', 'I')
        self._typePredChar = self.static_field('typePredChar', 'I')
        self._typePredNone = self.static_field('typePredNone', 'I')
        self._typeSearchable = self.static_field('typeSearchable', 'I')
        self._versionColumnNotPseudo = self.static_field('versionColumnNotPseudo', 'I')
        self._versionColumnPseudo = self.static_field('versionColumnPseudo', 'I')
        self._versionColumnUnknown = self.static_field('versionColumnUnknown', 'I')
        self.getCatalogs = self.method('getCatalogs', '()Ljava/sql/ResultSet;')
        self.getFunctionColumns = self.method(
            'getFunctionColumns', '({0}{0}{0}{0}){1}'.format(
                'Ljava/lang/String;',
                'Ljava/sql/ResultSet;'
            )
        )
        self.getFunctions = self.method(
            'getFunctions', '({0}{0}{0}){1}'.format(
                'Ljava/lang/String;',
                'Ljava/sql/ResultSet;'
            )
        )
        self.getProcedureColumns = self.method(
            'getProcedureColumns', '({0}{0}{0}{0}){1}'.format(
                'Ljava/lang/String;',
                'Ljava/sql/ResultSet;'
            )
        )
        self.getProcedures = self.method(
            'getProcedures', '({0}{0}{0}){1}'.format(
                'Ljava/lang/String;',
                'Ljava/sql/ResultSet;'
            )
        )
        self.getSchemas = self.method('getSchemas', '({0}{0}){1}'.format(
            'Ljava/lang/String;',
            'Ljava/sql/ResultSet;'
        ))
        self.getTables = self.method('getTables', '({0}{0}{0}[{0}){1}'.format(
            'Ljava/lang/String;',
            'Ljava/sql/ResultSet;'
        ))

    @property
    def attributeNoNulls(self):
        return self._attributeNoNulls.get(self.cls)

    @property
    def attributeNullable(self):
        return self._attributeNullable.get(self.cls)

    @property
    def attributeNullableUnknown(self):
        return self._attributeNullableUnknown.get(self.cls)

    @property
    def bestRowNotPseudo(self):
        return self._bestRowNotPseudo.get(self.cls)

    @property
    def bestRowPseudo(self):
        return self._bestRowPseudo.get(self.cls)

    @property
    def bestRowSession(self):
        return self._bestRowSession.get(self.cls)

    @property
    def bestRowTemporary(self):
        return self._bestRowTemporary.get(self.cls)

    @property
    def bestRowTransaction(self):
        return self._bestRowTransaction.get(self.cls)

    @property
    def bestRowUnknown(self):
        return self._bestRowUnknown.get(self.cls)

    @property
    def columnNoNulls(self):
        return self._columnNoNulls.get(self.cls)

    @property
    def columnNullable(self):
        return self._columnNullable.get(self.cls)

    @property
    def columnNullableUnknown(self):
        return self._columnNullableUnknown.get(self.cls)

    @property
    def functionColumnIn(self):
        return self._functionColumnIn.get(self.cls)

    @property
    def functionColumnInOut(self):
        return self._functionColumnInOut.get(self.cls)

    @property
    def functionColumnOut(self):
        return self._functionColumnOut.get(self.cls)

    @property
    def functionColumnResult(self):
        return self._functionColumnResult.get(self.cls)

    @property
    def functionColumnUnknown(self):
        return self._functionColumnUnknown.get(self.cls)

    @property
    def functionNoNulls(self):
        return self._functionNoNulls.get(self.cls)

    @property
    def functionNoTable(self):
        return self._functionNoTable.get(self.cls)

    @property
    def functionNullable(self):
        return self._functionNullable.get(self.cls)

    @property
    def functionNullableUnknown(self):
        return self._functionNullableUnknown.get(self.cls)

    @property
    def functionResultUnknown(self):
        return self._functionResultUnknown.get(self.cls)

    @property
    def functionReturn(self):
        return self._functionReturn.get(self.cls)

    @property
    def functionReturnsTable(self):
        return self._functionReturnsTable.get(self.cls)

    @property
    def importedKeyCascade(self):
        return self._importedKeyCascade.get(self.cls)

    @property
    def importedKeyInitiallyDeferred(self):
        return self._importedKeyInitiallyDeferred.get(self.cls)

    @property
    def importedKeyInitiallyImmediate(self):
        return self._importedKeyInitiallyImmediate.get(self.cls)

    @property
    def importedKeyNoAction(self):
        return self._importedKeyNoAction.get(self.cls)

    @property
    def importedKeyNotDeferrable(self):
        return self._importedKeyNotDeferrable.get(self.cls)

    @property
    def importedKeyRestrict(self):
        return self._importedKeyRestrict.get(self.cls)

    @property
    def importedKeySetDefault(self):
        return self._importedKeySetDefault.get(self.cls)

    @property
    def importedKeySetNull(self):
        return self._importedKeySetNull.get(self.cls)

    @property
    def procedureColumnIn(self):
        return self._procedureColumnIn.get(self.cls)

    @property
    def procedureColumnInOut(self):
        return self._procedureColumnInOut.get(self.cls)

    @property
    def procedureColumnOut(self):
        return self._procedureColumnOut.get(self.cls)

    @property
    def procedureColumnResult(self):
        return self._procedureColumnResult.get(self.cls)

    @property
    def procedureColumnReturn(self):
        return self._procedureColumnReturn.get(self.cls)

    @property
    def procedureColumnUnknown(self):
        return self._procedureColumnUnknown.get(self.cls)

    @property
    def procedureNoNulls(self):
        return self._procedureNoNulls.get(self.cls)

    @property
    def procedureNoResult(self):
        return self._procedureNoResult.get(self.cls)

    @property
    def procedureNullable(self):
        return self._procedureNullable.get(self.cls)

    @property
    def procedureNullableUnknown(self):
        return self._procedureNullableUnknown.get(self.cls)

    @property
    def procedureResultUnknown(self):
        return self._procedureResultUnknown.get(self.cls)

    @property
    def procedureReturnsResult(self):
        return self._procedureReturnsResult.get(self.cls)

    @property
    def sqlStateSQL(self):
        return self._sqlStateSQL.get(self.cls)

    @property
    def sqlStateSQL99(self):
        return self._sqlStateSQL99.get(self.cls)

    @property
    def sqlStateXOpen(self):
        return self._sqlStateXOpen.get(self.cls)

    @property
    def tableIndexClustered(self):
        return self._tableIndexClustered.get(self.cls)

    @property
    def tableIndexHashed(self):
        return self._tableIndexHashed.get(self.cls)

    @property
    def tableIndexOther(self):
        return self._tableIndexOther.get(self.cls)

    @property
    def tableIndexStatistic(self):
        return self._tableIndexStatistic.get(self.cls)

    @property
    def typeNoNulls(self):
        return self._typeNoNulls.get(self.cls)

    @property
    def typeNullable(self):
        return self._typeNullable.get(self.cls)

    @property
    def typeNullableUnknown(self):
        return self._typeNullableUnknown.get(self.cls)

    @property
    def typePredBasic(self):
        return self._typePredBasic.get(self.cls)

    @property
    def typePredChar(self):
        return self._typePredChar.get(self.cls)

    @property
    def typePredNone(self):
        return self._typePredNone.get(self.cls)

    @property
    def typeSearchable(self):
        return self._typeSearchable.get(self.cls)

    @property
    def versionColumnNotPseudo(self):
        return self._versionColumnNotPseudo.get(self.cls)

    @property
    def versionColumnPseudo(self):
        return self._versionColumnPseudo.get(self.cls)

    @property
    def versionColumnUnknown(self):
        return self._versionColumnUnknown.get(self.cls)


class DriverManager(Object):
    """
    Wrapper for java.sql.DriverManager java class
    """
    class_name = 'java.sql.DriverManager'

    def __init__(self, env):
        super(DriverManager, self).__init__(env)
        self._getConnection1 = self.static_method(
            'getConnection',
            '(Ljava/lang/String;)Ljava/sql/Connection;'
        )
        self._getConnection3 = self.static_method(
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
        if len(args) == 1:
            conn = self._getConnection1(*args)
        elif len(args) == 3:
            conn = self._getConnection3(*args)
        else:
            raise ArgumentError(self, args)
        return self.env.get('java.sql.Connection')(conn)

    def getDrivers(self):
        """
        Fetch a list of drivers, automatically wrap
        in Enumeration and Driver wrappers.

        :return: a generator that produces a list of JDBC drivers
        """
        enumeration = self.env.get('java.util.Enumeration')
        driver = self.env.get('java.sql.Driver')
        return (driver(obj) for obj in enumeration(self._getDrivers()))


class Driver(Object):
    """
    Wrapper for java.sql.Driver java class
    """
    class_name = 'java.sql.Driver'

    class Instance(Object.Instance):
        """
        Wrapper for java.sql.Driver object instance
        """
        def __init__(self, cls, obj):
            super(Driver.Instance, self).__init__(cls, obj)
            self.acceptsURL = lambda url, o=obj: cls.acceptsURL(o, url)

    def __init__(self, env):
        super(Driver, self).__init__(env)
        self.acceptsURL = self.method('acceptsURL', '(Ljava/lang/String;)Z')


class ParameterMetaData(Object):
    """
    Wrapper for java.sql.ParameterMetaData interface.
    """
    class_name = 'java.sql.ParameterMetaData'

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

    def __init__(self, env):
        super(ParameterMetaData, self).__init__(env)
        self._parameterModeIn = self.static_field('parameterModeIn', 'I')
        self._parameterModeInOut = self.static_field('parameterModeInOut', 'I')
        self._parameterModeOut = self.static_field('parameterModeOut', 'I')
        self._parameterModeUnknown = self.static_field('parameterModeUnknown', 'I')
        self._parameterNoNulls = self.static_field('parameterNoNulls', 'I')
        self._parameterNullable = self.static_field('parameterNullable', 'I')
        self._parameterNullableUnknown = self.static_field('parameterNullableUnknown', 'I')
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

    @property
    def parameterModeIn(self):
        return self._parameterModeIn.get(self.cls)

    @property
    def parameterModeInOut(self):
        return self._parameterModeInOut.get(self.cls)

    @property
    def parameterModeOut(self):
        return self._parameterModeOut.get(self.cls)

    @property
    def parameterModeUnknown(self):
        return self._parameterModeUnknown.get(self.cls)

    @property
    def parameterNoNulls(self):
        return self._parameterNoNulls.get(self.cls)

    @property
    def parameterNullable(self):
        return self._parameterNullable.get(self.cls)

    @property
    def parameterNullableUnknown(self):
        return self._parameterNullableUnknown.get(self.cls)


class PreparedStatement(Object):
    """
    Wrapper for java.sql.PreparedStatement java class.
    """
    class_name = 'java.sql.PreparedStatement'

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
            self.getUpdateCount = lambda o=obj: cls.getUpdateCount(o)
            self.setBoolean = lambda i, v, o=obj: cls.setBoolean(o, i, v)
            self.setByte = lambda i, v, o=obj: cls.setByte(o, i, v)
            self.setDouble = lambda i, v, o=obj: cls.setDouble(o, i, v)
            self.setFloat = lambda i, v, o=obj: cls.setFloat(o, i, v)
            self.setShort = lambda i, v, o=obj: cls.setShort(o, i, v)
            self.setInt = lambda i, v, o=obj: cls.setInt(o, i, v)
            self.setLong = lambda i, v, o=obj: cls.setLong(o, i, v)
            self.setNull = lambda i, v, o=obj: cls.setNull(o, i, v)
            self.setString = lambda i, v, o=obj: cls.setString(o, i, v)
            if cls.Date is None:
                cls.Date = self.env.get('java.sql.Date')
            if cls.ParameterMetaData is None:
                cls.ParameterMetaData = self.env.get('java.sql.ParameterMetaData')
            if cls.ResultSet is None:
                cls.ResultSet = self.env.get('java.sql.ResultSet')
            if cls.Time is None:
                cls.Time = self.env.get('java.sql.Time')
            if cls.Timestamp is None:
                cls.Timestamp = self.env.get('java.sql.Timestamp')
            if cls.TypesNull is None:
                cls.TypesNull = self.env.get('java.sql.Types').NULL

        def getParameterMetaData(self):
            return self.cls.ParameterMetaData(self.cls.getParameterMetaData(self.obj))

        def getResultSet(self):
            return self.cls.ResultSet(self.cls.getResultSet(self.obj))

        def set(self, i, arg):
            if arg is None:
                self.setNull(i, self.cls.TypesNull)
            elif isinstance(arg, bool):
                self.setBoolean(i, arg)
            elif isinstance(arg, int) or type(arg).__name__ == 'long':
                self.setLong(i, arg)
            elif isinstance(arg, float):
                self.setDouble(i, arg)
            elif isinstance(arg, six.string_types):
                self.setString(i, arg)
            elif isinstance(arg, six.binary_type):
                self.setBytes(i, arg)
            elif hasattr(arg, '__getitem__') and isinstance(arg[0], int):
                self.setBytes(i, arg)
            elif isinstance(arg, (datetime.datetime, self.cls.Timestamp.Instance)):
                self.setTimestamp(i, arg)
            elif isinstance(arg, (datetime.date, self.cls.Date.Instance)):
                self.setDate(i, arg)
            elif isinstance(arg, (datetime.time, self.cls.Time.Instance)):
                self.setTime(i, arg)
            else:
                raise RuntimeError("can't bind to python value %r(%r)", arg, type(arg))

        def setBytes(self, i, value):
            self.cls.setBytes(self.obj, i, value)

        def setDate(self, i, value):
            if not isinstance(value, self.cls.Date.Instance):
                value = self.cls.Date.from_python(value)
            self.cls.setDate(self.obj, i, value.obj)

        def setTime(self, i, value):
            if not isinstance(value, self.cls.Time.Instance):
                value = self.cls.Time.from_python(value)
            self.cls.setTime(self.obj, i, value.obj)

        def setTimestamp(self, i, value):
            if not isinstance(value, self.cls.Timestamp.Instance):
                value = self.cls.Timestamp.from_python(value)
            self.cls.setTimestamp(self.obj, i, value.obj)

    def __init__(self, env):
        super(PreparedStatement, self).__init__(env)
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
        self.setBytes = self.method('setBytes', '(I[B)V')
        self.setDate = self.method('setDate', '(ILjava/sql/Date;)V')
        self.setDouble = self.method('setDouble', '(ID)V')
        self.setFloat = self.method('setFloat', '(IF)V')
        self.setShort = self.method('setShort', '(IS)V')
        self.setInt = self.method('setInt', '(II)V')
        self.setLong = self.method('setLong', '(IJ)V')
        self.setNull = self.method('setNull', '(II)V')
        self.setString = self.method('setString', '(ILjava/lang/String;)V')
        self.setTime = self.method('setTime', '(ILjava/sql/Time;)V')
        self.setTimestamp = self.method('setTimestamp', '(ILjava/sql/Timestamp;)V')
        self.Date = None
        self.ParameterMetaData = None
        self.ResultSet = None
        self.Time = None
        self.Timestamp = None
        self.TypesNull = None




class CallableStatement(PreparedStatement):
    """
    Wrapper for java.sql.CallableStatement java interface
    """
    class_name = 'java.sql.CallableStatement'

    class Instance(PreparedStatement.Instance):
        """
        Wrapper for java.sql.CallableStatement object instance
        """
        def __init__(self, cls, obj):
            super(CallableStatement.Instance, self).__init__(cls, obj)
            self.getBoolean = lambda i, o=obj: cls.getBoolean(o, i)
            self.getBytes = lambda i, o=obj: cls.getBytes(o, i)
            self.getDouble = lambda i, o=obj: cls.getDouble(o, i)
            self.getFloat = lambda i, o=obj: cls.getFloat(o, i)
            self.getInt = lambda i, o=obj: cls.getInt(o, i)
            self.getLong = lambda i, o=obj: cls.getLong(o, i)
            self.getString = lambda i, o=obj: cls.getString(o, i)
            self.registerOutParameter = lambda i, t, o=obj: cls.registerOutParameter(o, i, t)
            self.setBoolean = lambda n, v, o=obj: cls.setBoolean(o, n, v)
            self.setBytes = lambda n, v, o=obj: cls.setBytes(o, n, v)
            self.setDate = lambda n, v, o=obj: cls.setDate(o, n, v)
            self.setDouble = lambda n, v, o=obj: cls.setDouble(o, n, v)
            self.setLong = lambda n, v, o=obj: cls.setLong(o, n, v)
            self.setNull = lambda n, t, o=obj: cls.setNull(o, n, t)
            self.setString = lambda n, v, o=obj: cls.setString(o, n, v)
            self.setTime = lambda n, v, o=obj: cls.setTime(o, n, v)
            self.setTimestamp = lambda n, v, o=obj: cls.setTimestamp(o, n, v)
            self.wasNull = lambda o=obj: cls.wasNull(o)

        def getDate(self, i):
            cls = self.env.get('java.sql.Date')
            return cls(self.cls.getDate(self.obj, i))

        def getMetaData(self):
            cls = self.env.get('java.sql.ResultSetMetaData')
            return cls(self.cls.getMetaData(self.obj))

        def getTime(self, i):
            cls = self.env.get('java.sql.Time')
            return cls(self.cls.getTime(self.obj, i))

        def getTimestamp(self, i):
            cls = self.env.get('java.sql.Timestamp')
            return cls(self.cls.getTimestamp(self.obj, i))

        def set(self, name, arg):
            if arg is None:
                self.setNull(name, self.cls.TypesNull)
            elif isinstance(arg, bool):
                self.setBoolean(name, arg)
            elif isinstance(arg, int):
                self.setLong(name, arg)
            elif isinstance(arg, float):
                self.setDouble(name, arg)
            elif isinstance(arg, six.string_types):
                self.setString(name, arg)
            elif isinstance(arg, six.binary_type):
                self.setBytes(name, arg)
            elif isinstance(arg, datetime.datetime):
                self.setTimestamp(name, arg)
            elif isinstance(arg, datetime.date):
                self.setDate(name, arg)
            elif isinstance(arg, datetime.time):
                self.setTime(name, arg)
            else:
                raise RuntimeError("can't set parameter %r to python value %r(%r)", name, arg, type(arg))


    def __init__(self, env):
        super(CallableStatement, self).__init__(env)
        self.getBoolean = self.method('getBoolean', '(I)Z')
        self.getBytes = self.method('getBytes', '(I)[B')
        self.getDate = self.method('getDate', '(I)Ljava/sql/Date;')
        self.getDouble = self.method('getDouble', '(I)D')
        self.getFloat = self.method('getFloat', '(I)F')
        self.getInt = self.method('getInt', '(I)I')
        self.getLong = self.method('getLong', '(I)J')
        self.getString = self.method('getString', '(I)Ljava/lang/String;')
        self.getTime = self.method('getTime', '(I)Ljava/sql/Time;')
        self.getTimestamp = self.method('getTimestamp', '(I)Ljava/sql/Timestamp;')
        self.registerOutParameter = self.method('registerOutParameter', '(II)V')
        self.setBoolean = self.method('setBoolean', '(Ljava/lang/String;Z)V')
        self.setBytes = self.method('setBytes', '(Ljava/lang/String;[B)V')
        self.setDate = self.method('setDate', '(Ljava/lang/String;Ljava/sql/Date;)V')
        self.setDouble = self.method('setDouble', '(Ljava/lang/String;D)V')
        self.setLong = self.method('setLong', '(Ljava/lang/String;J)V')
        self.setNull = self.method('setNull', '(Ljava/lang/String;I)V')
        self.setString = self.method('setString', '(Ljava/lang/String;Ljava/lang/String;)V')
        self.setTime = self.method('setTime', '(Ljava/lang/String;Ljava/sql/Time;)V')
        self.setTimestamp = self.method(
            'setTimestamp',
            '(Ljava/lang/String;Ljava/sql/Timestamp;)V'
        )
        self.wasNull = self.method('wasNull', '()Z')


class ResultSet(Object):
    """
    Wrapper for java.sql.ResultSet java class
    """
    class_name = 'java.sql.ResultSet'

    class Instance(Object.Instance):
        """
        Wrapper for java.sql.ResultSet object instance.

        It implements a Python iterator for iteration over rows.
        """
        def __init__(self, cls, obj):
            super(ResultSet.Instance, self).__init__(cls, obj)
            self.close = lambda o=obj: cls.close(o)
            self.getBoolean = lambda i, o=obj: cls.getBoolean(o, i)
            self.getBytes = lambda i, o=obj: cls.getBytes(o, i)
            self.getDouble = lambda i, o=obj: cls.getDouble(o, i)
            self.getInt = lambda i, o=obj: cls.getInt(o, i)
            self.getLong = lambda i, o=obj: cls.getLong(o, i)
            self.getString = lambda i, o=obj: cls.getString(o, i)
            self._next = lambda o=obj: cls.next(o)
            self.wasNull = lambda o=obj: cls.wasNull(o)

        def __iter__(self):
            return self

        def getDate(self, i):
            cls = self.env.get('java.sql.Date')
            return cls(self.cls.getDate(self.obj, i))

        def getMetaData(self):
            cls = self.env.get('java.sql.ResultSetMetaData')
            return cls(self.cls.getMetaData(self.obj))

        def getTime(self, i):
            cls = self.env.get('java.sql.Time')
            return cls(self.cls.getTime(self.obj, i))

        def getTimestamp(self, i):
            cls = self.env.get('java.sql.Timestamp')
            return cls(self.cls.getTimestamp(self.obj, i))

        def __next__(self):
            try:
                row = self._next()
            except LangException:
                raise StopIteration()
            if not row:
                raise StopIteration()
            return row

        next = __next__

    def __init__(self, env):
        super(ResultSet, self).__init__(env)
        self.close = self.method('close', '()V')
        self.getBoolean = self.method('getBoolean', '(I)Z')
        self.getBytes = self.method('getBytes', '(I)[B')
        self.getDate = self.method('getDate', '(I)Ljava/sql/Date;')
        self.getDouble = self.method('getDouble', '(I)D')
        self.getInt = self.method('getInt', '(I)I')
        self.getLong = self.method('getLong', '(I)J')
        self.getMetaData = self.method('getMetaData', '()Ljava/sql/ResultSetMetaData;')
        self.getString = self.method('getString', '(I)Ljava/lang/String;')
        self.getTime = self.method('getTime', '(I)Ljava/sql/Time;')
        self.getTimestamp = self.method('getTimestamp', '(I)Ljava/sql/Timestamp;')
        self.next = self.method('next', '()Z')
        self.wasNull = self.method('wasNull', '()Z')


class ResultSetMetaData(Object):
    """
    Wrapper for java.sql.ResultSetMetaData java class
    """
    class_name = 'java.sql.ResultSetMetaData'

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

    def __init__(self, env):
        super(ResultSetMetaData, self).__init__(env)
        self._columnNoNulls = self.static_field('columnNoNulls', 'I')
        self._columnNullable = self.static_field('columnNullable', 'I')
        self._columnNullableUnknown = self.static_field('columnNullableUnknown', 'I')
        self.getColumnCount = self.method('getColumnCount', '()I')
        self.getColumnDisplaySize = self.method('getColumnDisplaySize', '(I)I')
        self.getColumnName = self.method('getColumnName', '(I)Ljava/lang/String;')
        self.getColumnType = self.method('getColumnType', '(I)I')
        self.getColumnTypeName = self.method('getColumnTypeName', '(I)Ljava/lang/String;')
        self.getPrecision = self.method('getPrecision', '(I)I')
        self.getScale = self.method('getScale', '(I)I')
        self.isNullable = self.method('isNullable', '(I)I')

    @property
    def columnNoNulls(self):
        return self._columnNoNulls.get(self.cls)

    @property
    def columnNullable(self):
        return self._columnNullable.get(self.cls)

    @property
    def columnNullableUnknown(self):
        return self._columnNullableUnknown.get(self.cls)


class SQLDate(Date):
    """
    Wrapper for java.util.Date java class
    """
    class_name = 'java.sql.Date'

    class Instance(Date.Instance):
        """
        Wrapper for java.util.Date object instance
        """
        def __init__(self, cls, obj):
            super(SQLDate.Instance, self).__init__(cls, obj)
            self.setTime = lambda value, o=obj: cls.settime(o, value)

    def __init__(self, env):
        super(SQLDate, self).__init__(env)
        if self.class_name == SQLDate.class_name:
            self.cons_j = self.constructor('J')
        self.setTime = self.method('setTime', '(J)V')
        self.valueOf = self.static_method(
            'valueOf',
            '(Ljava/lang/String;)Ljava/sql/Date;'
        )

    def new(self, *args):
        if len(args) == 1:
            if isinstance(args[0], int):
                return self.cons_j(args[0])
        return super(SQLDate, self).new(*args)


class Statement(Object):
    """
    Wrapper for java.sql.Statement java class
    """
    class_name = 'java.sql.Statement'

    class Instance(Object.Instance):
        """
        Wrapper for java.sql.Statement object instance
        """
        def __init__(self, cls, obj):
            super(Statement.Instance, self).__init__(cls, obj)
            self.addBatch = lambda s, o=obj: cls.addBatch(o, s)
            self.executeUpdate = lambda s, o=obj: cls.executeUpdate(o, s)
            self.setQueryTimeout = lambda v, o=obj: cls.setQueryTimeout(o, v)

        def executeQuery(self, sql):
            cls = self.env.get('java.sql.ResultSet')
            return cls(self.cls.executeQuery(self.obj, sql))

    def __init__(self, env):
        super(Statement, self).__init__(env)
        self.addBatch = self.method('addBatch', '(Ljava/lang/String;)V')
        self.executeQuery = self.method(
            'executeQuery',
            '(Ljava/lang/String;)Ljava/sql/ResultSet;'
        )
        self.executeUpdate = self.method('executeUpdate', '(Ljava/lang/String;)I')
        self.setQueryTimeout = self.method('setQueryTimeout', '(I)V')


class Time(Date):
    """
    Wrapper for java.sql.Time java class
    """
    class_name = 'java.sql.Time'

    class Instance(Date.Instance):
        def __init__(self, cls, obj):
            super(Time.Instance, self).__init__(cls, obj)
            self.getTime = lambda o=obj: cls.getTime(o)
            self.setTime = lambda time, o=obj: cls.setTime(o, time)

        def to_python(self):
            offset = self.getTime() % 86400000
            microsecond, offset = (offset % 1000) * 1000, offset // 1000
            second, offset = offset % 60, offset // 60
            minute, hour = offset % 60, offset // 60
            return datetime.time(hour, minute, second, microsecond)

    def __init__(self, env):
        super(Time, self).__init__(env)
        if self.class_name == Time.class_name:
            self.cons_j = self.constructor('J')
        self.getTime = self.method('getTime', '()J')
        self.setTime = self.method('setTime', '(J)V')
        self._valueOf = self.static_method('valueOf', '(Ljava/lang/String;)Ljava/sql/Time;')

    def valueOf(self, s):
        return self(self._valueOf(self.cls, s))

    def new(self, *args):
        if len(args) == 1:
            if isinstance(args[0], int):
                return self.cons_j(int(args[0]))
        return super(Time, self).new(*args)

    def from_python(self, value):
        offset = (
            (value.hour * 3600) +
            (value.minute * 60) +
            value.second +
            (value.microsecond / 1e6)
        )
        return self.new(int(offset * 1000))


class Timestamp(Date):
    """
    Wrapper for java.sql.Timestamp java class
    """
    class_name = 'java.sql.Timestamp'

    class Instance(Date.Instance):
        def __init__(self, cls, obj):
            super(Timestamp.Instance, self).__init__(cls, obj)
            self.getTime = lambda o=obj: cls.getTime(o)
            self.setTime = lambda time, o=obj: cls.setTime(o, time)

        def to_python(self):
            cal = self.cls.Calendar.getInstance()
            cal.setTimeInMillis(self.getTime())
            return datetime.datetime(
                cal.YEAR,
                cal.MONTH,
                cal.DAY_OF_MONTH,
                cal.HOUR_OF_DAY,
                cal.MINUTE,
                cal.SECOND,
                cal.MILLISECOND * 1000
            )

    def __init__(self, env):
        super(Timestamp, self).__init__(env)
        self.Calendar = self.env.get('java.util.Calendar')
        if self.class_name == Timestamp.class_name:
            self.cons_j = self.constructor('J')
            self.cons6 = self.constructor('IIIIIII')
        self.getTime = self.method('getTime', '()J')
        self.setTime = self.method('setTime', '(J)V')
        self._valueOf = self.static_method(
            'valueOf',
            '(Ljava/lang/String;)Ljava/sql/Timestamp;'
        )

    def valueOf(self, s):
        return self(self._valueOf(self.cls, s))

    def new(self, *args):
        if len(args) == 1:
            if isinstance(args[0], int) or type(args[0]).__name__ == 'long':
                return self.cons_j(int(args[0]))
        return super(Timestamp, self).new(*args)

    def from_python(self, value):
        print('from_python', type(value))
        if isinstance(value, datetime.datetime):
            cal = self.Calendar.getInstance()
            cal.set(self.cal.YEAR, value.year)
            cal.set(self.cal.MONTH, value.month)
            cal.set(self.cal.DAY_OF_MONTH, value.day)
            cal.set(self.cal.HOUR_OF_DAY, value.hour)
            cal.set(self.cal.MINUTE, value.minute)
            cal.set(self.cal.SECOND, value.second)
            cal.set(self.cal.MILLISECOND, value.microsecond // 1000)
            value = cal.getTimeInMillis()
        return self.new(value)


class Types(Object):
    """
    Wrapper for java.sql.Types java class.

    This is basically just a set of static fields, so it
    really just loads the values for each static field.
    """
    class_name = 'java.sql.Types'

    def __init__(self, env):
        super(Types, self).__init__(env)
        self._ARRAY = self.static_field('ARRAY', 'I')
        self._BIGINT = self.static_field('BIGINT', 'I')
        self._BINARY = self.static_field('BINARY', 'I')
        self._BIT = self.static_field('BIT', 'I')
        self._BLOB = self.static_field('BLOB', 'I')
        self._BOOLEAN = self.static_field('BOOLEAN', 'I')
        self._CHAR = self.static_field('CHAR', 'I')
        self._CLOB = self.static_field('CLOB', 'I')
        self._DATALINK = self.static_field('DATALINK', 'I')
        self._DATE = self.static_field('DATE', 'I')
        self._DECIMAL = self.static_field('DECIMAL', 'I')
        self._DISTINCT = self.static_field('DISTINCT', 'I')
        self._DOUBLE = self.static_field('DOUBLE', 'I')
        self._FLOAT = self.static_field('FLOAT', 'I')
        self._INTEGER = self.static_field('INTEGER', 'I')
        self._JAVA_OBJECT = self.static_field('JAVA_OBJECT', 'I')
        self._LONGNVARCHAR = self.static_field('LONGNVARCHAR', 'I')
        self._LONGVARBINARY = self.static_field('LONGVARBINARY', 'I')
        self._LONGVARCHAR = self.static_field('LONGVARCHAR', 'I')
        self._NCHAR = self.static_field('NCHAR', 'I')
        self._NCLOB = self.static_field('NCLOB', 'I')
        self._NULL = self.static_field('NULL', 'I')
        self._NUMERIC = self.static_field('NUMERIC', 'I')
        self._NVARCHAR = self.static_field('NVARCHAR', 'I')
        self._OTHER = self.static_field('OTHER', 'I')
        self._REAL = self.static_field('REAL', 'I')
        self._REF = self.static_field('REF', 'I')
        self._REF_CURSOR = self.static_field('REF_CURSOR', 'I')
        self._ROWID = self.static_field('ROWID', 'I')
        self._SMALLINT = self.static_field('SMALLINT', 'I')
        self._SQLXML = self.static_field('SQLXML', 'I')
        self._STRUCT = self.static_field('STRUCT', 'I')
        self._TIME = self.static_field('TIME', 'I')
        self._TIME_WITH_TIMEZONE = self.static_field('TIME_WITH_TIMEZONE', 'I')
        self._TIMESTAMP = self.static_field('TIMESTAMP', 'I')
        self._TIMESTAMP_WITH_TIMEZONE = self.static_field('TIMESTAMP_WITH_TIMEZONE', 'I')
        self._TINYINT = self.static_field('TINYINT', 'I')
        self._VARBINARY = self.static_field('VARBINARY', 'I')
        self._VARCHAR = self.static_field('VARCHAR', 'I')

    @property
    def ARRAY(self):
        return self._ARRAY.get(self.cls)

    @property
    def BIGINT(self):
        return self._BIGINT.get(self.cls)

    @property
    def BINARY(self):
        return self._BINARY.get(self.cls)

    @property
    def BIT(self):
        return self._BIT.get(self.cls)

    @property
    def BLOB(self):
        return self._BLOB.get(self.cls)

    @property
    def BOOLEAN(self):
        return self._BOOLEAN.get(self.cls)

    @property
    def CHAR(self):
        return self._CHAR.get(self.cls)

    @property
    def CLOB(self):
        return self._CLOB.get(self.cls)

    @property
    def DATALINK(self):
        return self._DATALINK.get(self.cls)

    @property
    def DATE(self):
        return self._DATE.get(self.cls)

    @property
    def DECIMAL(self):
        return self._DECIMAL.get(self.cls)

    @property
    def DISTINCT(self):
        return self._DISTINCT.get(self.cls)

    @property
    def DOUBLE(self):
        return self._DOUBLE.get(self.cls)

    @property
    def FLOAT(self):
        return self._FLOAT.get(self.cls)

    @property
    def INTEGER(self):
        return self._INTEGER.get(self.cls)

    @property
    def JAVA_OBJECT(self):
        return self._JAVA_OBJECT.get(self.cls)

    @property
    def LONGNVARCHAR(self):
        return self._LONGNVARCHAR.get(self.cls)

    @property
    def LONGVARBINARY(self):
        return self._LONGVARBINARY.get(self.cls)

    @property
    def LONGVARCHAR(self):
        return self._LONGVARCHAR.get(self.cls)

    @property
    def NCHAR(self):
        return self._NCHAR.get(self.cls)

    @property
    def NCLOB(self):
        return self._NCLOB.get(self.cls)

    @property
    def NULL(self):
        return self._NULL.get(self.cls)

    @property
    def NUMERIC(self):
        return self._NUMERIC.get(self.cls)

    @property
    def NVARCHAR(self):
        return self._NVARCHAR.get(self.cls)

    @property
    def OTHER(self):
        return self._OTHER.get(self.cls)

    @property
    def REAL(self):
        return self._REAL.get(self.cls)

    @property
    def REF(self):
        return self._REF.get(self.cls)

    @property
    def REF_CURSOR(self):
        return self._REF_CURSOR.get(self.cls)

    @property
    def ROWID(self):
        return self._ROWID.get(self.cls)

    @property
    def SMALLINT(self):
        return self._SMALLINT.get(self.cls)

    @property
    def SQLXML(self):
        return self._SQLXML.get(self.cls)

    @property
    def STRUCT(self):
        return self._STRUCT.get(self.cls)

    @property
    def TIME(self):
        return self._TIME.get(self.cls)

    @property
    def TIME_WITH_TIMEZONE(self):
        return self._TIME_WITH_TIMEZONE.get(self.cls)

    @property
    def TIMESTAMP(self):
        return self._TIMESTAMP.get(self.cls)

    @property
    def TIMESTAMP_WITH_TIMEZONE(self):
        return self._TIMESTAMP_WITH_TIMEZONE.get(self.cls)

    @property
    def TINYINT(self):
        return self._TINYINT.get(self.cls)

    @property
    def VARBINARY(self):
        return self._VARBINARY.get(self.cls)

    @property
    def VARCHAR(self):
        return self._VARCHAR.get(self.cls)
