.. _JNI Specifications: https://docs.oracle.com/javase/8/docs/technotes/guides/jni/spec/functions.html

JNI Interface
=============

Synopsis
--------

A pure Python JNI interface using ctypes.
This is mostly a straight-forward mapping of jni.h from C++ to Python's FFI `ctypes`.
There is some additional functionality to manage a singleton JVM and an JNIEnv
object for each thread.

It should be functional enough that you could use it in any project needing a pure
Python JNI interface, but may need some work to be more comprehensive.

More detailed documentation of the C side can be found in the `JNI Specifications`_.


API Reference
-------------

.. automodule:: py2jdbc.jni
    :members:
