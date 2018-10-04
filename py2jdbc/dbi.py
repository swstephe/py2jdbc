# -*- coding: utf8 -*-
import six
import datetime
import time

from py2jdbc.wrap import JavaException, get_env
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

_fetch_map = {
    'ARRAY': None,
    'BIGINT': 'getInt',
    'BINARY': None,
    'BIT': 'getInt',
    'BLOB': None,
    'BOOLEAN': 'getBoolean',
    'CHAR': 'getString',
    'CLOB': None,
    'DATALINK': None,
    'DATE': ('getDate', '%Y-%m-%d', 'date'),
    'DECIMAL': 'geDouble',
    'DISTINCT': None,
    'DOUBLE': 'getDouble',
    'FLOAT': 'getFloat',
    'INTEGER': 'getInt',
    'JAVA_OBJECT': None,
    'LONGNVARCHAR': 'getString',
    'LONGVARBINARY': None,
    'LONGVARCHAR': 'getString',
    'NCHAR': 'getString',
    'NCLOB': None,
    'NULL': None,
    'NUMERIC': 'getDouble',
    'NVARCHAR': 'getString',
    'OTHER': 'getString',
    'REAL': 'getDouble',
    'REF': None,
    'REF_CURSOR': None,
    'ROWID': None,
    'SMALLINT': 'getInt',
    'SQLXML': None,
    'STRUCT': None,
    'TIME': ('getTime', '%H:M:%S', 'time'),
    'TIME_WITH_TIMEZONE': None,
    'TIMESTAMP': ('getTimestamp', '%Y-%m-%d %H:%M:%S.%f'),
    'TIMESTAMP_WITH_TIMEZONE': None,
    'TINYINT': 'getInt',
    'VARBINARY': None,
    'VRCHAR': 'getString',
}

apilevel = '2.0'
threadsafety = 1
paramstyle = 'qmark'


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
        # noinspection PyShadowingNames
        def check_null(fn):
            # noinspection PyShadowingNames
            def inner(i):
                value = getattr(self._rs, fn)(i)
                return None if self._rs.wasNull() else value
            return inner

        # noinspection PyShadowingNames
        def date_format(fn, fmt, fn2=None):
            def inner(n):
                value = fn(self._rs, n)
                if value is None:
                    return None
                value = datetime.datetime.strptime(value.toString(), fmt)
                if fn2 is None:
                    return value
                return getattr(value, fn2)()
            return inner

        meta = self._rs.getMetaData()
        count = meta.getColumnCount()
        errors = []
        for i in range(count):
            fn = _fetch_map.get(meta.getColumnTypeName(i + 1))
            if fn is None:
                errors.append("unsupported datatype %r (%d) for column %r" % (
                    meta.getColumntypename(i + 1),
                    meta.getColumnType(i + 1),
                    meta.getColumnName(i + 1)
                ))
            elif isinstance(fn, str):
                yield check_null(fn)
            else:
                yield date_format(check_null(fn[0]), *fn[i:])
        if errors:
            raise DataError('\n'.join(errors))

    def _fetch_row(self, funcs):
        for i, fn in enumerate(funcs):
            yield fn(self._rs, i + 1)

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
                meta.getColumnType(i + 1),
                meta.getColumnDisplaySize(i + 1),
                None,
                meta.getPrecision(i + 1),
                meta.getScale(i + 1),
                meta.isnullable(i + 1)
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
            stmt = _env.classes['java.sql.PreparedStatement'](self._conn.prepareStatement(sql))
        except JavaException as e:
            raise OperationalError(e.message)
        if args:
            if hasattr(args, '__getitem__'):
                args = [args[i] for i in range(len(args))]
            try:
                for i, arg in enumerate(args):
                    stmt.set(i + 1, arg)
            except JavaException as e:
                raise ProgrammingError(e.message)
        try:
            check = stmt.execute()
        except JavaException as e:
            raise OperationalError(e.message)

        if check:
            self._rs = _env.classes['java.sql.ResultSet'](stmt.getResultSet())
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
            stmt = _env.classes['java.sql.PreparedStatement'](self._conn.prepareStatement(sql))
        except JavaException as e:
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
        dm = env.classes['java.sql.DriverManager']
        self.close()
        try:
            self.conn = dm.getConnection(*args)
        except JavaException as e:
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
    return env.classes['java.sql.Date'](year, month, day)


def Time(hour, minute, second):
    env = get_env()
    return env.classes['java.sql.Time'](hour, minute, second)


def Timestamp(year, month, day, hour, minute, second):
    env = get_env()
    return env.classes['java.sql.Timestamp'](year, month, day, hour, minute, second)


def DateFromTicks(ticks):
    return Date(*time.localtime(ticks)[:3])


def TimeFromTicks(ticks):
    return Time(*time.localtime(ticks)[3:6])


def TimestampFromTicks(ticks):
    return Timestamp(*time.localtime(ticks)[:6])


def Binary(string):
    return string
