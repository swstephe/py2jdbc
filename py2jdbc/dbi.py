# -*- coding: utf8 -*-
import six
from collections import OrderedDict
import datetime
import time

from py2jdbc.wrap import get_env
from py2jdbc.lang import LangException
from py2jdbc.math import BigDecimal
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

    def __getitem__(self, key):
        return self.registry.get(key)

    def __iter__(self):
        return iter(self.registry)

    def register(self, cls):
        print('registering', cls.__name__)
        self.registry[cls.__name__] = cls
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
    pass


@datatypes.register
class BIGINT(DataType):
    def get(self, rs, i):
        value = rs.getInt(i)
        return None if rs.wasNull() else value



@datatypes.register
class BINARY(DataType):
    pass


@datatypes.register
class BIT(DataType):
    def get(self, rs, i):
        value = rs.getInt(i)
        return None if rs.wasNull() else value


@datatypes.register
class BLOB(DataType):
    pass


@datatypes.register
class BOOLEAN(DataType):
    def get(self, rs, i):
        value = rs.getBoolean(i)
        return None if rs.wasNull() else value


@datatypes.register
class CHAR(DataType):
    def get(self, rs, i):
        value = rs.getString(i)
        return None if rs.wasNull() else value


@datatypes.register
class CLOB(DataType):
    pass


@datatypes.register
class DATALINK(DataType):
    pass


@datatypes.register
class DATE(DataType):
    # 'DATE': ('getDate', '%Y-%m-%d', 'date'),
    def get(self, rs, i):
        value = rs.getDate(i)
        return None if rs.wasNull() else value


@datatypes.register
class DECIMAL(DataType):
    def get(self, rs, i):
        value = rs.getDouble(i)
        return None if rs.wasNull() else value


@datatypes.register
class DISTINCT(DataType):
    pass


@datatypes.register
class DOUBLE(DataType):
    def get(self, rs, i):
        value = rs.getDouble(i)
        return None if rs.wasNull() else value


@datatypes.register
class FLOAT(DataType):
    def get(self, rs, i):
        value = rs.getFloat(i)
        return None if rs.wasNull() else value


@datatypes.register
class INTEGER(DataType):
    def get(self, rs, i):
        value = rs.getInt(i)
        return None if rs.wasNull() else value


@datatypes.register
class JAVA_OBJECT(DataType):
    pass


@datatypes.register
class LONGNVARCHAR(DataType):
    def get(self, rs, i):
        value = rs.getString(i)
        return None if rs.wasNull() else value


@datatypes.register
class LONGVARBINARY(DataType):
    pass


@datatypes.register
class LONGVARCHAR(DataType):
    def get(self, rs, i):
        value = rs.getString(i)
        return None if rs.wasNull() else value


@datatypes.register
class NCHAR(DataType):
    def get(self, rs, i):
        value = rs.getString(i)
        return None if rs.wasNull() else value


@datatypes.register
class NCLOB(DataType):
    pass


@datatypes.register
class NULL(DataType):
    pass


@datatypes.register
class NUMERIC(DataType):
    def get(self, rs, i):
        value = rs.getDouble()
        return None if rs.wasNull() else value


@datatypes.register
class NVARCHAR(DataType):
    def get(self, rs, i):
        value = rs.getString()
        return None if rs.wasNull() else value


@datatypes.register
class OTHER(DataType):
    pass


@datatypes.register
class REAL(DataType):
    def get(self, rs, i):
        value = rs.getDouble(i)
        return None if rs.wasNull() else value


@datatypes.register
class REF(DataType):
    pass


@datatypes.register
class REF_CURSOR(DataType):
    pass


@datatypes.register
class ROWID(DataType):
    pass


@datatypes.register
class SMALLINT(DataType):
    def get(self, rs, i):
        value = rs.getInt(i)
        return None if rs.wasNull() else value


@datatypes.register
class SQLXML(DataType):
    pass


@datatypes.register
class STRUCT(DataType):
    pass


@datatypes.register
class TEXT(DataType):
    def get(self, rs, i):
        value = rs.getString(i)
        return None if rs.wasNull() else value


@datatypes.register
class TIME(DataType):
    # 'TIME': ('getTime', '%H:M:%S', 'time'),
    def get(self, rs, i):
        value = rs.getTime(i)
        return None if rs.wasNull() else value


@datatypes.register
class TIME_WITH_TIMEZONE(DataType):
    pass


@datatypes.register
class TIMESTAMP(DataType):
    # 'TIMESTAMP': ('getTimestamp', '%Y-%m-%d %H:%M:%S.%f'),
    def get(self, rs, i):
        value = rs.getTimestamp(i)
        return None if rs.wasNull() else value


@datatypes.register
class TIMESTAMP_WITH_TIMEZONE(DataType):
    pass


@datatypes.register
class TINYINT(DataType):
    def get(self, rs, i):
        value = rs.getInt(i)
        return None if rs.wasNull() else value


@datatypes.register
class VARBINARY(DataType):
    pass


@datatypes.register
class VARCHAR(DataType):
    def get(self, rs, i):
        value = rs.getString(i)
        return None if rs.wasNull() else value


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

    def _fetch_funcs(self):
        meta = self._rs.getMetaData()
        try:
            count = meta.getColumnCount()
        except LangException.Instance as e:
            return
        errors = []
        for i in range(count):
            fn = datatypes[meta.getColumnTypeName(i + 1)]()
            if fn is None:
                errors.append("unsupported datatype %r (%d) for column %r" % (
                    meta.getColumnTypeName(i + 1),
                    meta.getColumnType(i + 1),
                    meta.getColumnName(i + 1)
                ))
            yield fn
        if errors:
            raise DataError('\n'.join(errors))

    def _fetch_row(self, funcs):
        for i, fn in enumerate(funcs):
            yield fn.get(self._rs, i + 1)

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
        return [
            [
                meta.getColumnName(i + 1),
                datatypes[meta.getColumnTypeName(i + 1)],
                meta.getColumnDisplaySize(i + 1),
                None,
                meta.getPrecision(i + 1),
                meta.getScale(i + 1),
                meta.isNullable(i + 1) == meta.cls.columnNullable
            ]
            for i in range(count)
        ]

    def callproc(self, procname, *args):
        """
        Call a stored database procesure with the given name.
        The squence of parameters must contain one entry
        for each argument that the procedure expects.

        :param procname: the procedure name
        :param args: the sequence of arguments to pass to the procedure
        :return: the return value of the procedure
        """
        if self._rs is None:
            raise InterfaceError("not open")
        return self._rs.callproc(procname, *args)

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
        _env = self._conn.env
        if not isinstance(sql, six.string_types):
            raise ValueError("sql must be string")
        try:
            stmt = self._conn.prepareStatement(sql)
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
        _env = self._conn.env
        if not isinstance(sql, six.string_types):
            raise ValueError("wrong datatype for sql")
        self.rowcount = None
        try:
            stmt = self._conn.prepareStatement(sql)
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
        funcs = tuple(self._fetch_funcs())
        rows = []
        while self._rs.next():
            rows.append(tuple(self._fetch_row(funcs)))
        return tuple(rows)

    def fetchmany(self, size=None):
        """
        Fetch the next set of rows of a query result, returning a sequence of
        sequences.  An empty sequence is returned when no more rows are available.

        :param size: the number of rows to fetch, or arraysize if not specified.
        :return: a sequence of sequences or empty sequence.
        """
        funcs = tuple(self._fetch_funcs())
        rows = []
        for i in range(size or self.arraysize):
            try:
                self._rs.next()
            except StopIteration:
                break
            rows.append(tuple(self._fetch_row(funcs)))
        return rows

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
        funcs = tuple(self._fetch_funcs())
        return tuple(self._fetch_row(funcs))

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
        return Cursor(self.conn)

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

    def rollback(self):
        """
        Roll back any pending transactions, if driver supports it.
        :return:
        """
        self.is_connected()
        if not self._autocommit:
            self.conn.rollback()


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
