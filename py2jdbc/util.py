# -*- coding: utf8 -*-
import datetime
import time
from . import exc
from . import wrap

JAVA_PYTHON = dict((
    ('BIGINT', 'getInt'),
    ('BIT', 'getInt'),
    ('BOOLEAN', 'getBoolean'),
    ('CHAR', 'getString'),
    ('DATE', ('getData', '%Y-%m-%d', 'date')),
    ('DECIMAL', 'getDouble'),
    ('FLOAT', 'getFloat'),
    ('INTEGER', 'getInt'),
    ('LONGNVARCHAR', 'getString'),
    ('LONGVARCHAR', 'getString'),
    ('NCHAR', 'getString'),
    ('NUMERIC', 'getDouble'),
    ('NVARCHAR', 'getString'),
    ('REAL', 'getDouble'),
    ('SMALLINT', 'getInt'),
    ('STRING', 'getString'),
    ('TEXT', 'getString'),
    ('TIME', ('getTime', '%H:%M:%S', 'time')),
    ('TIMESTAMP', ('getTimestamp', '%Y-%m-%d %H:%M:%S.%f')),
    ('TINYINT', 'getInt'),
    ('VARCHAR', 'getString'),
    ('OTHER', 'getString')
))

PYTHON_BIND = {
    bool: lambda stmt, i, arg: stmt.setBoolean(i, arg),
    # long: lambda stmt, i, arg: stmt.setLong(i, arg),
    int: lambda stmt, i, arg: stmt.setInt(i, arg),
    float: lambda stmt, i, arg: stmt.setDouble(i, arg),
    str: lambda stmt, i, arg: stmt.setString(i, arg),
    # unicode: lambda stmt, i, arg: stmt.setString(i, arg),
    datetime.datetime: lambda stmt, i, arg: stmt.setTimestamp(
        i,
        None if arg is None else wrap.Timestamp(time.mktime(arg.timetuple()) * 1000)
    ),
    datetime.date: lambda stmt, i, arg: stmt.setDate(
        i,
        None if arg is None else wrap.Date(time.mktime(arg.timetuple()) * 1000)
    )
}


def bind_funcs(rows):
    funcs = None
    for row in rows:
        if funcs is None:
            funcs = [None] * len(row)
        for i, value in enumerate(row):
            if funcs[i] is not None:
                continue
            if type(value) in PYTHON_BIND:
                funcs[i] = PYTHON_BIND[type(value)]
        if all(f is not None for f in funcs):
            break
    return funcs


def bind_row(stmt, funcs, row):
    for i, value in enumerate(row):
        if funcs[i] is None:
            stmt.setNull(i + 1, 12)
        else:
            funcs[i](stmt, i + 1, value)


def check_null(fn):
    def inner(rs, i):
        value = getattr(rs, fn)(i)
        return None if rs.wasNull() else value
    return inner


def date_format(fn, fmt, fn2=None):
    def inner(rs, n):
        value = fn(rs, n)
        if value is None:
            return None
        value = datetime.datetime.strptime(value.toString(), fmt)
        if fn2 is None:
            return value
        return getattr(value, fn2)()
    return inner


def fetch_funcs(rs):
    env = rs.env
    meta = env.classes['java.sql.ResultSetMetaData'](rs.getMetaData())
    print('SQLState', rs.getSQLState())
    count = meta.getColumnCount()
    errors = []
    for i in range(count):
        fn = JAVA_PYTHON.get(meta.getColumnTypeName(i + 1))
        if fn is None:
            errors.append("unsupported datatype %r (%d) for column %r" % (
                meta.getColumnTypeName(i + 1),
                meta.getColumnType(i + 1),
                meta.getColumnName(i + 1)
            ))
        elif isinstance(fn, str):
            yield check_null(fn)
        else:
            yield date_format(check_null(fn[0]), *fn[i:])
    if errors:
        raise exc.DataError('\n'.join(errors))


def fetch_row(rs, funcs):
    for i, fn in enumerate(funcs):
        yield fn(rs, i + 1)


def fetch_one(rs):
    if rs is None:
        return
    try:
        rs.next()
    except StopIteration:
        return
    funcs = list(fetch_funcs(rs))
    return tuple(fetch_row(rs, funcs))


def fetch_many(rs, size):
    funcs = list(fetch_funcs(rs))
    for i in range(size):
        try:
            rs.next()
        except StopIteration:
            return
        yield tuple(fetch_row(rs, funcs))


def fetch_all(rs):
    funcs = list(fetch_funcs(rs))
    while rs.next():
        yield tuple(fetch_row(rs, funcs))
