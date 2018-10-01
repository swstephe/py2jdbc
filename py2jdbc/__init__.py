# -*- coding: utf8 -*-
import six
import time
from . import util
from . import wrap
from . import exc

version = '0.0.3'
apilevel = '2.0'
threadsafety = 1
paramstyle = 'qmark'

# noinspection PyShadowingBuiltins
Warning = exc.Warning
Error = exc.Error
InterfaceError = exc.InterfaceError
DatabaseError = exc.DatabaseError
DataError = exc.DataError
OperationalError = exc.OperationalError
IntegrityError = exc.IntegrityError
InternalError = exc.InternalError
ProgrammingError = exc.ProgrammingError
NotSupportedError = exc.NotSupportedError


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
        except wrap.JavaException as e:
            raise OperationalError(e.message)
        if args:
            if hasattr(args, '__getitem__'):
                args = [args[i] for i in range(len(args))]
            try:
                for i, arg in enumerate(args):
                    if arg is None:
                        stmt.setNull(i + 1, 12)
                    elif type(arg) in util.PYTHON_BIND:
                        util.PYTHON_BIND[type(arg)](stmt, i + 1, arg)
                    else:
                        raise RuntimeError("can't bind to python value %r(%r)", arg, type(arg))
            except wrap.JavaException as e:
                raise ProgrammingError(e.message)
        try:
            check = stmt.execute()
        except wrap.JavaException as e:
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
        except wrap.JavaException as e:
            raise DatabaseError(e.message)

        funcs = util.bind_funcs(rows)
        for row in rows:
            row = tuple(row)
            util.bind_row(stmt, funcs, row)
            stmt.addBatch()
        self.rowcount = sum(stmt.executeBatch())
        return True

    def fetchall(self):
        """
        Fetch the rest of rows of a query result, returning a sequence of
        sequences.  An empty sequence is returned when no more rows are available.
        :return: a sequence of sequences or empty sequence.
        """
        return tuple(util.fetch_all(self._rs))

    def fetchmany(self, size=None):
        """
        Fetch the next set of rows of a query result, returning a sequence of
        sequences.  An empty sequence is returned when no more rows are available.

        :param size: the number of rows to fetch, or arraysize if not specified.
        :return: a sequence of sequences or empty sequence.
        """
        return list(util.fetch_many(self._rs, size=size or self.arraysize))

    def fetchone(self):
        """
        Fetch the next row of a query result set, returning a single sequence
        or None if there is no more data.
        :return: a sequence of column data or None
        """
        return util.fetch_one(self._rs)

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
    Warning = exc.Warning
    Error = exc.Error
    InterfaceError = exc.InterfaceError
    DatabaseError = exc.DatabaseError
    DataError = exc.DataError
    OperationalError = exc.OperationalError
    IntegrityError = exc.IntegrityError
    InternalError = exc.InternalError
    ProgrammingError = exc.ProgrammingError
    NotSupportedError = exc.NotSupportedError

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
        env = wrap.get_env(**kwargs)
        dm = env.classes['java.sql.DriverManager']
        self.close()
        try:
            self.conn = dm.getConnection(*args)
        except wrap.JavaException as e:
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
    env = wrap.get_env()
    return env.classes['java.sql.Date'](year, month, day)


def Time(hour, minute, second):
    env = wrap.get_env()
    return env.classes['java.sql.Time'](hour, minute, second)


def Timestamp(year, month, day, hour, minute, second):
    env = wrap.get_env()
    return env.classes['java.sql.Timestamp'](year, month, day, hour, minute, second)


def DateFromTicks(ticks):
    return Date(*time.localtime(ticks)[:3])

def TimeFromTicks(ticks):
    return Time(*time.localtime(ticks)[3:6])

def TimestampFromTicks(ticks):
    return Timestamp(*time.localtime(ticks)[:6])


def Binary(string):
    return string
