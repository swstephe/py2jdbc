# -*- coding: utf8 -*-


# noinspection PyShadowingBuiltins
class Warning(Exception):
    """
    Exception raised for important warnings like data truncations while inserting, etc.
    """
    pass


class Error(Exception):
    """
    Exception that is the base class of all other error exceptions.
    """
    pass


class InterfaceError(Error):
    """
    Exception raised for errors that are related to the database interface
    rather than the database itself.
    """
    pass


class DatabaseError(Error):
    """
    Exception raised for errors that are related to the database.
    """
    pass


class DataError(DatabaseError):
    """
    Exception raised for erors that are due to problems with the
    processed data like division by zero, numeric value out of range,
    etc.
    """
    pass


class OperationalError(DatabaseError):
    """
    Exception raised for errors that are related to the database's operation
    and not necessarily under the control of the programmer, e.g. an
    unexpected disconnect occursm, the data source name is not found,
    a transaction could not be processed, a memory allocation error occurred
    during processing, etc.
    """
    pass


class IntegrityError(DatabaseError):
    """
    Exception raised when the relational integrity of the database is affected,
    a foreign key check fails.
    """
    pass


class InternalError(DatabaseError):
    """
    Exception raised when the database encounters an eternal error, e.g.,
    the cursor is not valid anymorem, the transaction is out of sync, etc.
    """
    pass


class ProgrammingError(DatabaseError):
    """
    Exception raised for programming erros, e.g. table not found or already
    exists, syntax error in the SQL statement, wrong number of parameters
    specified, etc.
    """
    pass


class NotSupportedError(DatabaseError):
    """
    Exception raised in case of method or database API was used which is not
    supported by the database, e.g. requesting a `rollback` on a connection
    that does not support ransaction or has transactions turned off.
    """
    pass
