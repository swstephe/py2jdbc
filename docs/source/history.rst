History
=======

Originally, in my day job, I needed to access a Teradata database.  After a lot of difficulty
getting ODBC for Linux to work in Red Hat, I decided to look at integrating the Teradata
JDBC drivers.  Previous developers had actually ported everything to Jython, just to
accommodate JDBC drivers.

My first approach was to convert my app to pure Python, then create a small Java
WebSerice API to serve DBI requests.  At first, I used Google's protobuf and ZeroMQ
on both Java and Python sides to send messages back-and-forth.

Later, while teaching myself Hadoop, I found Thrift, which contained a server and a
message protocol built-in, so I ported both sides to use Thrift on both sides.

Still later, I came across pyjnius, which is a Cython interface to JNI, with class
autoloading introspection of classes and methods.  However, it was painful to build
pyjnius in our Windows environment, and it had some incompatibility problems with Python 3.

Finally I decided to write my own Pure Python interface to JNI, (using built-in ctypes),
then wrap enough classes to get a Python interface to JDBC calls that approached DBI 2.0
compliance.

I hope to provide this as a connector, like pyodbc, to SQLAlchemy and other database
frameworks.

As an expierment for my own education, I hope to create alternative branches where
this package is ported back to Cython and even raw C++ on different branches, as well
as trying out Python package distribution.
