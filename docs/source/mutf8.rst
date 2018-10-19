Java Modified UTF-8 Encoding
============================

Synopsis
--------

This module creates a Python `codecs <https://docs.python.org/3/library/codecs.html>`_
interface for the Java
`Modified UTF-8 <https://docs.oracle.com/javase/8/docs/api/java/io/DataInput.html>`_ Encoding,
for JNI interface calls.  It is slightly different than the UTF-8 encoding.

The differences are:

* The null byte '\\u0000' is encoded in 2-bytes rather than 1-byte,
  so that the encoded string never has an embedded zero-byte.
* Onle the 1-byte, 2-byte, and 3-byte formats are used.
* `Supplementary characters <https://docs.oracle.com/javase/8/docs/api/java/lang/Character.html#unicode>`_
  are represented in the form of surrogate pairs, which take 6-bytes.

This gives us the following mapping:

+-----------------+------------------+-----------------+------+----------+----------+----------+----------+----------+----------+
| Number of bytes | First code point | Last code point | Bits | Byte 1   | Byte 2   | Byte 3   | Byte 4   | Byte 5   | Byte 6   |
+-----------------+------------------+-----------------+------+----------+----------+----------+----------+----------+----------+
| 2               | U+0000           | U+0000          | --   | 11000000 | 10000000 |          |          |          |          |
+-----------------+------------------+-----------------+------+----------+----------+----------+----------+----------+----------+
| 1               | U+0001           | U+007F          | 7    | 0xxxxxxx |          |          |          |          |          |
+-----------------+------------------+-----------------+------+----------+----------+----------+----------+----------+----------+
| 2               | U+0080           | U+07FF          | 11   | 110xxxxx | 10xxxxxx |          |          |          |          |
+-----------------+------------------+-----------------+------+----------+----------+----------+----------+----------+----------+
| 3               | U+0800           | U+FFFF          | 16   | 1110xxxx | 10xxxxxx | 10xxxxxx |          |          |          |
+-----------------+------------------+-----------------+------+----------+----------+----------+----------+----------+----------+
| 6               | U+10000          | U+FFFFF         | 20   | 11101101 | 1010xxxx | 10xxxxxx | 11101101 | 1011xxxx | 10xxxxxx |
+-----------------+------------------+-----------------+------+----------+----------+----------+----------+----------+----------+

To implement as a Python codec, all that is needed is an encode and decode function.
The codec is registered by passing a custom function to search for potentially multiple
codecs and return the two functions in a CodecInfo object.

Sometimes this encoding is referred to as CESU-8 or
`Compatibility Encoding Scheme for UTF-16: 8-bit <https://en.wikipedia.org/wiki/CESU-8>`_,
but changes the way zero bytes ('\\x00') are encoded.  There doesn't seem to be an official
designation for this encoding, and a request to officially added to Python was rejected,
so I'll just use "mutf8" or "mutf-8" for my implementation.

Usage
-----

To use this encoding, you could do this::

    import codecs
    import py2jdbc.mutf8
    codecs.register(py2jdbc.mutf8.info)

    codecs.encode(u'a string', 'mutf8')
    codecs.encode(u'a string', 'mutf-8')
    codecs.encode(u'a string', py2jdbc.mutf8.NAME)

The :doc:`jni` module registers and imports this module and maps it to :py:func:`jni.encode`
and :func:`jni.decode` already, so you could also use it with::

    from py2jdbc.jni import encode

    encode(u'a string')
    decode(b'a string')

Although JNI will do this automatically for any calls needing a character pointer argument
or returning a character poiter result.


API Reference
-------------

.. automodule:: py2jdbc.mutf8
    :members:
