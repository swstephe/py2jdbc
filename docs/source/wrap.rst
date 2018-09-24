Wrappers
========

Synopsis
--------

This module is a set of of classes which wrap jclass and jobject values, so
they can be accessed approximately the same way as Python classes and objects.

1. Each `jni.JNIEnv` object must be tied to the local thread.  So this module
   has an object `ThreadEnv`, which is a thread-specific "singleton".  There is
   one instance per thread.
2. Each `ThreadEnv` object contains a list of classes called `classes`.
3. Each value is a Python wrapper for the class which wraps the jclass, mapping
   Java methods and fields to the class.
4. If a jobject is encountered, it can be wrapped with an `Instance` of the class,
   which is a nested class of the class.

For example:

.. code-block::python

    from py2jdbc import wrap

    # loads the local thread ThreadEnv instance
    env = wrap.get_env()
    # access java.lang.System wrapper
    system = env.classes['java.lang.System']

    # call static method `getProperty` of java.lang.System
    # `sig` module will automatically convert strings.
    classpath = system.getProperty('java.class.path')

    # access/import class wrappers
    enumeration = env.classes['java.lang.Enumeration]
    driver = env.classes['java.sql.Driver']
    driver_manager = env.classes['java.sql.DriverManager']

    # call static method `getDrivers` to fetch a list of drivers
    # wrap the result in an Enumeration wrapper, which acts like a Python iterator
    # for each jobject returned, use a Driver wrapper and print string repreentations
    for obj in enumeration(driver_manager.getDrivers()):
        print(driver(obj).toString())


API Reference
-------------

.. automodule:: py2jdbc.wrap
    :members:
