Java Signatures
===============

Synopsis
--------

To use the :doc:`jni`, functions need to be mapped to things like the return
type of functions, or field data type, which come from the method or field
signatures.

For example, a field with signature 'Z' should be called with `GetBooleanField`,
while a static field with that signature should be called with `GetBooleanStaticField`.

A method with a signature '()B' should be called with 'CallByteMethod' and a static
method with the same signature should be called with CallByteStaticMethod`.

To simplify this struture, this module will try to automatically map signatures to
the functions that need to be called.  It also tries to convert given Python
values to a similar type.

For example:

.. code-block::python

    from py2jdbc import jni
    from py2jdbc import sig

    _env = jni.get_env()

    # get the first signature object returned
    c = next(sig.type_signature(_env, 'C')

    # convert jchar (short) to Python unicode character:
    c.j2py(12) == u'\u0012'

    # convert Python unicode character to jchar (short)
    c.py2j('.') == ord('.')

    # assign jchar to jvalue union
    val = jni.jvalue()
    c.jval(val, 'X')
    assert val.c == ord('X')


For method signatures:

.. code-block::python

    from py2jdbc import jni
    from py2jdbc import sig

    _env = jni.get_env()

    # JNI function to load class
    cls = _env.FindClass('java.lang.System')

    signature = '(Ljava/lang/String;)Ljava/lang/String;'

    # JNI function to fetch method ID
    mid = _env.GetStaticMethodID(cls, 'getProperty', signature)

    # map signture to a list of argument type mappers and the result type mapper
    argtypes, restype = sig.method_signature(_env, signature)

    # call the function through the result's 'call_static' method
    result = restype.call_static(cls, mid, argtypes, 'java.class.path')



API Reference
-------------

.. automodule:: py2jdbc.sig
    :members:
