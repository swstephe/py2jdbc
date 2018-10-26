# -*- coding: utf8 -*-
import six
from collections import OrderedDict, namedtuple
import time

from py2jdbc.wrap import get_env
from py2jdbc.lang import LangException
from py2jdbc.sql import SQLException
from py2jdbc.exc import (
    Warning,
    Error,
    InterfaceError,
    DatabaseError,
    DataError,
    OperationalError,
    IntegrityError,
    InternalError,
    ProgrammingError,
    NotSupportedError,
)

apilevel = '2.0'
threadsafety = 1
paramstyle = 'qmark'


class DataTypes(object):
    def __init__(self):
        self.registry = OrderedDict()
        self.regtypes = OrderedDict()

    def __getitem__(self, key):
        return (self.regtypes if isinstance(key, int) else self.registry).get(key)

    def __iter__(self):
        return iter(self.registry)

    def register(self, cls):
        if cls.__name__ in self.registry:
            raise RuntimeError("duplicate type name in registry")
        self.registry[cls.__name__] = cls
        if cls.type_code in self.regtypes:
            raise RuntimeError("duplicate type code in registry")
        self.regtypes[cls.type_code] = cls
        return cls


datatypes = DataTypes()


class DataType(object):
    @property
    def name(self):
        return self.__class__.__name__

    def get(self, rs, i):
        raise NotImplementedError("DataType.get")



@datatypes.register
class ARRAY(DataType):
    type_code = 2003


@datatypes.register
class BIGINT(DataType):
    type_code = -5

    def get(self, rs, i):
        value = rs.getLong(i)
        return None if rs.wasNull() else value


@datatypes.register
class BINARY(DataType):
    type_code = -2

    def get(self, rs, i):
        value = rs.getBytes(i)
        return None if rs.wasNull() else value



@datatypes.register
class BIT(DataType):
    type_code = -7

    def get(self, rs, i):
        value = rs.getInt(i)
        return None if rs.wasNull() else value


@datatypes.register
class BLOB(DataType):
    type_code = 2004

    def get(self, rs, i):
        value = rs.getBytes(i)
        return None if rs.wasNull() else value


@datatypes.register
class BOOLEAN(DataType):
    type_code = 16

    def get(self, rs, i):
        value = rs.getBoolean(i)
        return None if rs.wasNull() else value


@datatypes.register
class CHAR(DataType):
    type_code = 1

    def get(self, rs, i):
        value = rs.getString(i)
        return None if rs.wasNull() else value


@datatypes.register
class CLOB(DataType):
    type_code = 2005

    def get(self, rs, i):
        value = rs.getString(i)
        return None if rs.wasNull() else value


@datatypes.register
class DATALINK(DataType):
    type_code = 70


@datatypes.register
class DATE(DataType):
    type_code = 91

    def get(self, rs, i):
        value = rs.getDate(i)
        return None if rs.wasNull() else value.to_python()


@datatypes.register
class DECIMAL(DataType):
    type_code = 3

    def get(self, rs, i):
        value = rs.getDouble(i)
        return None if rs.wasNull() else value


@datatypes.register
class DISTINCT(DataType):
    type_code = 2001


@datatypes.register
class DOUBLE(DataType):
    type_code = 8

    def get(self, rs, i):
        value = rs.getDouble(i)
        return None if rs.wasNull() else value


@datatypes.register
class FLOAT(DataType):
    type_code = 6

    def get(self, rs, i):
        value = rs.getFloat(i)
        return None if rs.wasNull() else value


@datatypes.register
class INTEGER(DataType):
    type_code = 4

    def get(self, rs, i):
        value = rs.getInt(i)
        return None if rs.wasNull() else value


@datatypes.register
class JAVA_OBJECT(DataType):
    type_code = 2000


@datatypes.register
class LONGNVARCHAR(DataType):
    type_code = -16

    def get(self, rs, i):
        value = rs.getString(i)
        return None if rs.wasNull() else value


@datatypes.register
class LONGVARBINARY(DataType):
    type_code = -4

    def get(self, rs, i):
        value = rs.getBytes(i)
        return None if rs.wasNull() else value


@datatypes.register
class LONGVARCHAR(DataType):
    type_code = -1

    def get(self, rs, i):
        value = rs.getString(i)
        return None if rs.wasNull() else value


@datatypes.register
class NCHAR(DataType):
    type_code = -15

    def get(self, rs, i):
        value = rs.getString(i)
        return None if rs.wasNull() else value


@datatypes.register
class NCLOB(DataType):
    type_code = 2011


@datatypes.register
class NULL(DataType):
    type_code = 0

    def get(self, rs, i):
        return None


@datatypes.register
class NUMERIC(DataType):
    type_code = 2

    def get(self, rs, i):
        value = rs.getDouble(i)
        return None if rs.wasNull() else value


@datatypes.register
class NVARCHAR(DataType):
    type_code = -9

    def get(self, rs, i):
        value = rs.getString()
        return None if rs.wasNull() else value


@datatypes.register
class OTHER(DataType):
    type_code = 1111


@datatypes.register
class REAL(DataType):
    type_code = 7

    def get(self, rs, i):
        value = rs.getDouble(i)
        return None if rs.wasNull() else value


@datatypes.register
class REF(DataType):
    type_code = 2006


@datatypes.register
class REF_CURSOR(DataType):
    type_code = 2012


@datatypes.register
class ROWID(DataType):
    type_code = -8


@datatypes.register
class SMALLINT(DataType):
    type_code = 5

    def get(self, rs, i):
        value = rs.getInt(i)
        return None if rs.wasNull() else value


@datatypes.register
class SQLXML(DataType):
    type_code = 2009


@datatypes.register
class STRUCT(DataType):
    type_code = 2002


@datatypes.register
class TIME(DataType):
    type_code = 92

    def get(self, rs, i):
        value = rs.getTime(i)
        return None if rs.wasNull() else value.to_python()


@datatypes.register
class TIME_WITH_TIMEZONE(DataType):
    type_code = 2013


@datatypes.register
class TIMESTAMP(DataType):
    type_code = 93

    def get(self, rs, i):
        value = rs.getTimestamp(i)
        return None if rs.wasNull() else value.to_python()


@datatypes.register
class TIMESTAMP_WITH_TIMEZONE(DataType):
    type_code = 2014


@datatypes.register
class TINYINT(DataType):
    type_code = -6

    def get(self, rs, i):
        value = rs.getInt(i)
        return None if rs.wasNull() else value


@datatypes.register
class VARBINARY(DataType):
    type_code = -3


@datatypes.register
class VARCHAR(DataType):
    type_code = 12

    def get(self, rs, i):
        value = rs.getString(i)
        return None if rs.wasNull() else value


def _fetch_funcs(rs):
    meta = rs.getMetaData()
    try:
        count = meta.getColumnCount()
    except LangException.Instance:
        return
    errors = []
    for i in range(count):
        dt = datatypes[meta.getColumnType(i + 1)]
        if dt is None:
            errors.append("unsupported datatype %r (%d) for column %r" % (
                meta.getColumnTypeName(i + 1),
                meta.getColumnType(i + 1),
                meta.getColumnName(i + 1)
            ))
        yield dt()
    if errors:
        raise DataError('\n'.join(errors))


def _fetch_row(rs, funcs):
    for i, fn in enumerate(funcs):
        yield fn.get(rs, i + 1)


class Cursor(object):
    """
    The DBI Cursor object.  It allows you to execute SQL statements and manage
    the results.  If a query, this object becaomes an interator.
    """
    def __init__(self, conn):
        self._conn = conn
        self._rs = None
        self.rowcount = None
        self.arraysize = 100

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __iter__(self):
        return self

    def __next__(self):
        row = self.fetchone()
        if row is not None:
            return row
        raise StopIteration()

    next = __next__

    @property
    def connection(self):
        return self._conn

    @property
    def description(self):
        """
        Return a sequence of query result column information.

        * name
        * type_code
        * display_size
        * internal_size
        * precision
        * scale
        * null_ok

        :return: a squence of column description entries
        """
        if self._rs is None:
            return None
        meta = self._rs.getMetaData()
        count = meta.getColumnCount()
        results = tuple(
            (
                meta.getColumnName(i + 1),
                meta.getColumnType(i + 1),
                meta.getColumnTypeName(i + 1),
                meta.getColumnDisplaySize(i + 1),
                meta.getPrecision(i + 1),
                meta.getScale(i + 1),
                meta.isNullable(i + 1) == meta.cls.columnNullable
            )
            for i in range(count)
        )
        return tuple(
            (
                res[0],
                datatypes[res[1]],
                res[3],
                None,
                res[4],
                res[5],
                res[6]
            )
            for res in results
        )

    def callproc(self, procname, *args):
        """
        Call a stored database procesure with the given name.
        The squence of parameters must contain one entry
        for each argument that the procedure expects.

        :param procname: the procedure name
        :param args: the sequence of arguments to pass to the procedure
        :return: the return value of the procedure
        """
        env = get_env()
        meta = env.get('java.sql.DatabaseMetaData')
        Types = env.get('java.sql.Types')
        for func in self._conn.functions(functions=procname):
            name = func.function_name
            if func.function_schem:
                name = func.function_schem + '.' + name
            cols = self._conn.function_columns(functions=func.function_name, schemas=func.function_schem)
            params = tuple(col for col in cols if col.column_type != meta.functionReturn)
            returns = any(col.column_type == meta.functionReturn for col in cols)
            break
        else:
            for proc in self._conn.procedures(procedures=procname):
                name = proc.procedure_name
                if proc.procedure_schem:
                    name = proc.procedure_schem + '.' + name
                cols = self._conn.procedure_columns(schemas=proc.procedure_schem, procedures=proc.procedure_name)
                params = tuple(cols)
                returns = False
                break
            else:
                raise RuntimeError("function not found %r" % procname)
        sql = 'call {}({})'.format(name, ', '.join('?' for _ in range(len(params))))
        if returns:
            sql = '?= ' + sql
        stmt = self._conn.conn.prepareCall('{ %s }' % sql)
        j = 0
        for i, col in enumerate(cols):
            if col.column_type in (meta.functionColumnIn, meta.functionColumnInOut):
                stmt.set(col.column_name, args[j])
                j += 1
            elif col.column_type in (
                meta.functionColumnInOut,
                meta.functionColumnOut,
                meta.functionReturn,
            ):
                stmt.registerOutParameter(col.ordinal_position + 1, col.data_type)
        check = stmt.execute()
        if check:
            rs2 = stmt.getResultSet()
            funcs = tuple(_fetch_funcs(rs2))
            return tuple(
                tuple(_fetch_row(rs2, funcs))
                for _ in rs2
            )

        results = []
        for i, col in enumerate(cols):
            if col.column_type in (meta.functionColumnOut, meta.functionReturn):
                dt = datatypes[col.data_type]()
                value = dt.get(stmt, col.ordinal_position + 1)
                results.append(value)
        if len(results) == 0:
            return None
        elif len(results) == 1:
            return results[0]
        return results


    def close(self):
        """
        Close the cursor and make it inaccessible.
        """
        if self._rs is not None:
            self._rs.close()
            self._rs = None

    def execute(self, sql, args=None):
        """
        Prepare and execute a database operation (query or command).

        :param sql: the SQL to execute
        :param args: a sequence of bind variables
        :return: the Cursor object
        """
        if not isinstance(sql, six.string_types):
            raise ValueError("sql must be string")
        try:
            stmt = self._conn.conn.prepareStatement(sql)
        except SQLException.Instance as e:
            raise OperationalError(e.message)
        if args:
            if hasattr(args, '__getitem__'):
                args = [args[i] for i in range(len(args))]
            try:
                for i, arg in enumerate(args):
                    stmt.set(i + 1, arg)
            except SQLException.Instance as e2:
                raise ProgrammingError(e2.message)
            except LangException.Instance as e1:
                raise ProgrammingError(e1.message)
        try:
            check = stmt.execute()
        except LangException.Instance as e:
            if isinstance(e, SQLException.Instance):
                raise OperationalError(e.message)
            raise ProgrammingError(e.message)

        if check:
            self._rs = stmt.getResultSet()
        else:
            count = stmt.getUpdateCount()
            if count == -1:
                self._rs = None
            else:
                self.rowcount = count
            stmt.close()
        return self

    def executemany(self, sql, rows):
        """
        Prepare a database operation and execute it against each row.

        :param sql: the SQL to prepare
        :param rows: a sequence of rows to execute
        :return: True if successful
        """
        if not isinstance(sql, six.string_types):
            raise ValueError("wrong datatype for sql")
        self.rowcount = None
        try:
            stmt = self._conn.conn.prepareStatement(sql)
        except SQLException.Instance as e:
            raise DatabaseError(e.message)

        for row in rows:
            for i, col in enumerate(row):
                stmt.set(i + 1, col)
            stmt.addBatch()
        self.rowcount = sum(stmt.executeBatch())
        return True

    def fetchall(self):
        """
        Fetch the rest of rows of a query result, returning a sequence of
        sequences.  An empty sequence is returned when no more rows are available.
        :return: a sequence of sequences or empty sequence.
        """
        funcs = tuple(_fetch_funcs(self._rs))
        return tuple(
            tuple(_fetch_row(self._rs, funcs))
            for row in self._rs
        )

    def fetchmany(self, size=None):
        """
        Fetch the next set of rows of a query result, returning a sequence of
        sequences.  An empty sequence is returned when no more rows are available.

        :param size: the number of rows to fetch, or arraysize if not specified.
        :return: a sequence of sequences or empty sequence.
        """
        funcs = tuple(_fetch_funcs(self._rs))
        rows = []
        for i in range(size or self.arraysize):
            try:
                six.next(self._rs)
            except StopIteration:
                break
            rows.append(tuple(_fetch_row(self._rs, funcs)))
        return tuple(rows)

    def fetchone(self):
        """
        Fetch the next row of a query result set, returning a single sequence
        or None if there is no more data.
        :return: a sequence of column data or None
        """
        if self._rs is None:
            return
        try:
            self._rs.next()
        except StopIteration:
            return
        funcs = tuple(_fetch_funcs(self._rs))
        return tuple(_fetch_row(self._rs, funcs))

    def setinputsizes(self, sizes):
        """
        This can be used to predefine memory areas for an execute operation parameters.

        This implementation does nothing.

        :param sizes: a sequence of parameter sizes
        """
        pass

    def setoutputsize(self, size, column=None):
        """
        Set the column buffer size for fetches of large columns.
        The column s specfied as an index into the result sequence.
        Not specifying the column will set the default size for all large
        columns.

        This implementation currently does nothing.

        :param size: the size of the column.
        :param column: the column index to apply this size
        """
        pass


Function = namedtuple('Function', (
    'function_cat',
    'function_schem',
    'function_name',
    'remarks',
    'function_type',
    'specific_name'
))

FunctionColumns = namedtuple('FunctionColumn', (
    'function_cat',
    'function_schem',
    'function_name',
    'column_name',
    'column_type',
    'data_type',
    'type_name',
    'precision',
    'length',
    'scale',
    'radix',
    'nullable',
    'remarks',
    'char_octet_length',
    'ordinal_position',
    'is_nullable',
    'specific_name'
))

Procedure = namedtuple('Procedure', (
    'procedure_cat',
    'procedure_schem',
    'procedure_name',
    'remarks',
    'procedure_type',
    'specific_name'
))

ProcedureColumn = namedtuple('ProcedureColumn', (
    'procedure_cat',
    'procedure_schem',
    'procedure_name',
    'column_name',
    'column_type',
    'data_type',
    'type_name',
    'precision',
    'length',
    'scale',
    'radix',
    'nullable',
    'remarks',
    'column_def',
    'sql_data_type',
    'sql_datetime_sub',
    'char_octet_length',
    'ordinal_position',
    'is_nullable',
    'specific_name'
))


Schema = namedtuple('Schema', (
    'table_schem',
    'table_catalog'
))

Table = namedtuple('Table', (
    'table_cat',
    'table_schem',
    'table_name',
    'table_type',
    'remarks',
    'type_cat',
    'type_schem',
    'type_name',
    'self_referencing_col_name',
    'ref_generation'
))


class Connection(object):
    Warning = Warning
    Error = Error
    InterfaceError = InterfaceError
    DatabaseError = DatabaseError
    DataError = DataError
    OperationalError = OperationalError
    IntegrityError = IntegrityError
    InternalError = InternalError
    ProgrammingError = ProgrammingError
    NotSupportedError = NotSupportedError

    def __init__(self):
        self.conn = None
        self._autocommit = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def is_connected(self):
        if self.conn is None:
            raise InterfaceError("not connected")

    @property
    def autocommit(self):
        """
        Check whether DML transactions are automatically committed.

        :return: the current autocommit value
        """
        self.is_connected()
        return self._autocommit

    @autocommit.setter
    def autocommit(self, value):
        """
        Change whether DML transactions are automatically committed.

        :param value: the new autocommit value
        """
        self.is_connected()
        self.conn.setAutoCommit(value)
        self._autocommit = value

    @property
    def catalogs(self):
        rs = self.conn.getMetaData().getCatalogs()
        return tuple(rs.getString(1) for _ in rs)   # table_cat

    def close(self):
        """
        Close the connection now.
        """
        if self.conn is not None:
            self.conn.close()
        self.conn = None

    def commit(self):
        """
        Commit any pending transaction to the database.
        :return:
        """
        self.is_connected()
        if not self._autocommit:
            self.conn.commit()

    def cursor(self):
        """
        Create a new Cursor object using this connection.
        :return: a new Cursor object
        """
        self.is_connected()
        return Cursor(self)

    def function_columns(self, catalog=None, schemas=None, functions=None, columns=None):
        meta = self.conn.getMetaData()
        rs = meta.getFunctionColumns(catalog, schemas, functions, columns)
        return tuple(
            FunctionColumns(
                function_cat=rs.getString(1),    # FUNCTION_CAT
                function_schem=rs.getString(2),    # FUNCTION_SCHEM
                function_name=rs.getString(3),    # FUNCTION_NAME
                column_name=rs.getString(4),    # COLUMN_NAME
                column_type=rs.getInt(5),       # COLUMN_TYPE
                data_type=rs.getInt(6),       # DATA_TYPE
                type_name=rs.getString(7),    # TYPE_NAME
                precision=rs.getInt(8),       # PRECISION
                length=rs.getInt(9),       # LENGTH
                scale=rs.getInt(10),      # SCALE
                radix=rs.getInt(11),      # RADIX
                nullable=rs.getInt(12),      # NULLABLE
                remarks=rs.getString(13),   # REMARKS
                char_octet_length=rs.getInt(14),      # CHAR_OCTET_LENGTH
                ordinal_position=rs.getInt(15),      # ORDINAL_POSITION
                is_nullable=rs.getString(16),   # IS_NULLABLE
                specific_name=rs.getString(17),   # SPECIFIC_NAME
            )
            for _ in rs
        )

    def functions(self, catalog=None, schemas=None, functions=None):
        rs = self.conn.getMetaData().getFunctions(catalog, schemas, functions)
        return tuple(
            Function(
                function_cat=rs.getString(1),
                function_schem=rs.getString(2),
                function_name=rs.getString(3),
                remarks=rs.getString(4),
                function_type=rs.getInt(5),
                specific_name=rs.getString(6)
            )
            for _ in rs
        )

    def open(self, *args, **kwargs):
        """
        Opens the connection to the database.

        :param args: JDBC url, or JDBC url, username, password
        :param kwargs: JVM kwargs, like classpath and verbose
        :return: the Connection object
        """
        env = get_env(**kwargs)
        dm = env.get('java.sql.DriverManager')
        self.close()
        try:
            self.conn = dm.getConnection(*args)
        except SQLException.Instance as e:
            raise OperationalError(e.message)
        self._autocommit = self.conn.getAutoCommit()
        return self

    def procedure_columns(self, catalog=None, schemas=None, procedures=None, columns=None):
        meta = self.conn.getMetaData()
        rs = meta.getProcedureColumns(catalog, schemas, procedures, columns)
        return tuple(
            ProcedureColumn(
                procedure_cat=rs.getString(1),
                procedure_schem=rs.getString(2),
                procedure_name=rs.getString(3),
                column_name=rs.getString(4),
                column_type=rs.getInt(5),
                data_type=rs.getInt(6),
                type_name=rs.getString(7),
                precision=rs.getInt(8),
                length=rs.getInt(9),
                scale=rs.getInt(10),
                radix=rs.getInt(11),
                nullable=rs.getInt(12),
                remarks=rs.getString(13),
                column_def=rs.getString(14),
                sql_data_type=rs.getInt(15),
                sql_datetime_sub=rs.getInt(16),
                char_octet_length=rs.getInt(17),
                ordinal_position=rs.getInt(18),
                is_nullable=rs.getString(19),
                specific_name=rs.getString(20)
            )
            for _ in rs
        )

    def procedures(self, catalog=None, schemas=None, procedures=None):
        rs = self.conn.getMetaData().getProcedures(catalog, schemas, procedures)
        return tuple(
            Procedure(
                procedure_cat=rs.getString(1),
                procedure_schem=rs.getString(2),
                procedure_name=rs.getString(3),
                remarks=rs.getString(7),
                procedure_type=rs.getInt(8),
                specific_name=rs.getString(9)
            )
            for _ in rs
        )

    def rollback(self):
        """
        Roll back any pending transactions, if driver supports it.
        :return:
        """
        self.is_connected()
        if not self._autocommit:
            self.conn.rollback()

    def schemas(self, catalog=None, schemas=None):
        rs = self.conn.getMetaData().getSchemas(catalog, schemas)
        return tuple(
            Schema(
                table_schem=rs.getString(1),
                table_catalog=rs.getString(2)
            )
            for _ in rs
        )

    def tables(self, catalog=None, schemas=None, tables=None, types=None):
        rs = self.conn.getMetaData().getTables(catalog, schemas, tables, types)
        return tuple(
            Table(
                table_cat=rs.getString(1),
                table_schem=rs.getString(2),
                table_name=rs.getString(3),
                table_type=rs.getString(4),
                remarks=rs.getString(5),
                type_cat=rs.getString(6),
                type_schem=rs.getString(7),
                type_name=rs.getString(8),
                self_referencing_col_name=rs.getString(9),
                ref_generation=rs.getString(10)
            )
            for _ in rs
        )



def connect(*args, **kwargs):
    """
    Constructor for reating a connection to the database.

    Arguments can be a connection string, or connection string with
    username and password separated out.  For example::

        'jdbc:sqlite:/path/filename.db'
        'jdbc:sqlite::memory'
        'jdbc:oracle:thin:scott/tiger@localhost:1521:orcl'
        'jdbc:oracle:thin@localhost:1521:orcl', 'scott', 'tiger'
        'jdbc:hive2://localhost:10000/default'

    :param args: JDBC URL, with optional username and password
    :param kwargs: JVM environment; classpath, verbose, check, etc.
    :return: a `Connection` object.
    """
    db = Connection()
    db.open(*args, **kwargs)
    return db


def Date(year, month, day):
    env = get_env()
    return env.get('java.sql.Date').new(year, month, day)


def Time(hour, minute, second):
    env = get_env()
    return env.get('java.sql.Time').new(hour, minute, second)


def Timestamp(year, month, day, hour, minute, second):
    env = get_env()
    return env.get('java.sql.Timestamp').new(year, month, day, hour, minute, second)


def DateFromTicks(ticks):
    return Date(*time.localtime(ticks)[:3])


def TimeFromTicks(ticks):
    return Time(*time.localtime(ticks)[3:6])


def TimestampFromTicks(ticks):
    return Timestamp(*time.localtime(ticks)[:6])


def Binary(string):
    return string
