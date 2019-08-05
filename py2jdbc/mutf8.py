# -*- coding: utf8 -*-
import logging
import codecs
import six

log = logging.getLogger(__name__)
NAME = 'mutf8'      # not cesu-8, which uses a different zero-byte


def mutf8_unichr(value):
    return chr(value) if six.PY3 else six.u('\\U%08x' % value)


def _bytes(*vals):
    """
    This is a private utility function which takes a list of byte values
    and creates a binary string appropriate for the current Python version.
    It will return a `str` type in Python 2, but a `bytes` value in Python 3.

    Values should be in byte range, (0x00-0xff)::

        _bytes(1, 2, 3) == six.b('\\x01\\x02\\x03')

    :param vals: arguments are a list of unsigned bytes.
    :return: a `str` in Python 2, or `bytes` in Python 3
    """
    return six.b('').join(six.int2byte(v) for v in vals)


def encoder(text):
    """
    This generator processes a string and generates a sequence of bytes
    in the Modified UTF-8 encoding.

    Automatically handle UTF-16 "surrogate pairs" if being used from "narrow Python",
    where unicode characters are indexed as 2 surrogates.

    :param text: a string, usually unicode
    :return: a string of bytes in Modified UTF-8 encoding.
    """
    it = iter(enumerate(ord(c) for c in text))
    for i, x in it:
        if 0xd800 <= x <= 0xdbff:       # high surrogate
            j, x2 = next(it)
            if not 0xd800 <= x2 <= 0xdfff:  # low surrogate
                raise UnicodeEncodeError(
                    NAME,
                    text,
                    i,
                    j + 1,
                    'bad surrogate pair (high)'
                )
            x = 0x10000 | ((x & 0x3ff) << 10) | (x2 & 0x3ff)
        if x == 0:
            yield _bytes(0xc0, 0x80)
        elif x <= 0x7f:
            yield _bytes(x)
        elif x <= 0x07ff:
            yield _bytes(
                0xc0 | (x >> 6),
                0x80 | (x & 0x3f)
            )
        elif x <= 0xffff:
            yield _bytes(
                0xe0 | (x >> 12),
                0x80 | ((x >> 6) & 0x3f),
                0x80 | (x & 0x3f)
            )
        elif x <= 0xfffff:
            yield _bytes(
                0xed,
                0xa0 | (x >> 16),
                0x80 | ((x >> 10) & 0x3f),
                0xed,
                0xb0 | ((x >> 6) & 0x0f),
                0x80 | (x & 0x3f)
            )
        else:
            raise UnicodeEncodeError(
                NAME,
                text,
                i,
                i + 1,
                'ordinal not in range(%d)' % 0xfffff
            )


def encode(text, errors='strict'):
    """
    Encodes the input unicode text and returns a tuple, (output
    bytes, length consumed).

    :param text: unicode text to be encoded
    :param errors: how to handle encoding errors: strict, ignore, replace, etc.
    :return: a string of bytes in Modified UTF-8
    """
    value, length = six.b(''), 0
    it = iter(encoder(text))
    while True:
        try:
            b = next(it)
            value += b
            length += 1
        except StopIteration:
            break
        except UnicodeEncodeError as e:
            if errors == 'strict':
                raise e
            elif errors == 'ignore':
                pass
            elif errors == 'replace':
                value += six.b('?')
                length += 1
            elif errors == 'xmlcharrefreplace':
                v = six.b('&#{};'.format(ord(e.object[e.start])))
                value += v
                length += len(v)
            elif errors == 'backslashreplace':
                v = six.b('\\')
                v += six.b('U{:08X}'.format(ord(e.object[e.start])))
                value += v
                length += len(v)
    return value, length


class DecodeMap(object):
    """
    A utility class which manages masking, comparing and mapping in bits.
    If the mask and compare fails, this will raise UnicodeDecodeError so
    encode and decode will correctly handle bad characters.
    """
    def __init__(self, count, mask, value, bits):
        """
        Initialize a DecodeMap, entry from a static dictionary for the module.
        It automatically calculates the mask for the bits for the value, (always
        assumed to be at the bottom of the byte).

        :param count: The number of bytes in this entire sequence.
        :param mask: The mask to apply to the byte at this position.
        :param value: The value of masked bits, (without shifting).
        :param bits: The number of bits.
        """
        self.count = count
        self.mask = mask
        self.value = value
        self.bits = bits
        self.mask2 = (1 << bits) - 1

    def apply(self, byte, value, data, i, count):
        """
        Apply mask, compare to expected value, shift and return
        result.  Eventually, this could become a `reduce` function.

        :param byte: The byte to compare
        :param value: The currently accumulated value.
        :param data: The data buffer, (array of bytes).
        :param i: The position within the data buffer.
        :param count: The position of this comparison.
        :return: A new value with the bits merged in.

        :raises: UnicodeDecodeError if maked bits don't match.
        """
        if byte & self.mask == self.value:
            value <<= self.bits
            value |= byte & self.mask2
        else:
            raise UnicodeDecodeError(
                NAME, data, i, i + count,
                "invalid {}-byte sequence".format(self.count)
            )
        return value

    def __repr__(self):
        return "DecodeMap({})".format(
            ', '.join(
                '{}=0x{:02x}'.format(n, getattr(self, n))
                for n in ('count', 'mask', 'value', 'bits', 'mask2')
            )
        )


DECODER_MAP = {
    2: (
        (0xc0, 0x80, 6),
    ),
    3: (
        (0xc0, 0x80, 6),
        (0xc0, 0x80, 6)
    ),
    6: (
        (0xf0, 0xa0, 4),
        (0xc0, 0x80, 6),
        (0xff, 0xed, 0),
        (0xf0, 0xb0, 4),
        (0xc0, 0x80, 6),
    )
}
DECODE_MAP = dict(
    (k, tuple(
        DecodeMap(k, *vv) for vv in v)
     )
    for k, v in DECODER_MAP.items()
)


def decoder(data):
    """
    This generator processes a sequence of bytes in Modified UTF-8 encoding and produces
    a sequence of unicode string characters.  It takes bits from the byte until it matches
    one of the known encoding serquences.

    It uses `DecodeMap` to mask, compare and generate values.

    :param data: a string of bytes in Modified UTF-8 encoding.
    :return: a generator producing a string of unicode characters
    :raises: `UnicodeDecodeError` if unrecognized byte in sequence is encountered.
    """
    def next_byte(_it, start, count):
        try:
            return next(_it)[1]
        except StopIteration:
            raise UnicodeDecodeError(
                NAME, data, start, start + count,
                "incomplete byte sequence"
            )

    it = iter(enumerate(six.iterbytes(data)))
    for i, d in it:
        if d == 0x00:               # 00000000
            raise UnicodeDecodeError(
                NAME, data, i, i + 1,
                "embedded zero-byte not allowed"
            )
        elif d & 0x80:              # 1xxxxxxx
            if d & 0x40:            # 11xxxxxx
                if d & 0x20:        # 111xxxxx
                    if d & 0x10:    # 1111xxxx
                        raise UnicodeDecodeError(
                            NAME, data, i, i + 1,
                            "invalid encoding character"
                        )
                    elif d == 0xed:
                        value = 0
                        for i1, dm in enumerate(DECODE_MAP[6]):
                            d1 = next_byte(it, i, i1 + 1)
                            value = dm.apply(d1, value, data, i, i1 + 1)
                    else:           # 1110xxxx
                        value = d & 0x0f
                        for i1, dm in enumerate(DECODE_MAP[3]):
                            d1 = next_byte(it, i, i1 + 1)
                            value = dm.apply(d1, value, data, i, i1 + 1)
                else:               # 110xxxxx
                    value = d & 0x1f
                    for i1, dm in enumerate(DECODE_MAP[2]):
                        d1 = next_byte(it, i, i1 + 1)
                        value = dm.apply(d1, value, data, i, i1 + 1)
            else:                   # 10xxxxxx
                raise UnicodeDecodeError(
                    NAME, data, i, i + 1,
                    "misplaced continuation character"
                )
        else:                       # 0xxxxxxx
            value = d
        # noinspection PyCompatibility
        yield mutf8_unichr(value)


def decode(data, errors='strict'):
    """
    Decodes a sequence of bytes to a unicode text and length using Modified UTF-8.
    This function is designed to be used with Python `codecs` module.

    :param data: a string of bytes in Modified UTF-8
    :param errors: handle decoding errors
    :return: unicode text and length
    :raises: `UnicodeDecodeError` if sequence is invalid.
    """
    value, length = six.u(''), 0
    it = iter(decoder(data))
    while True:
        try:
            value += next(it)
            length += 1
        except StopIteration:
            break
        except UnicodeDecodeError as e:
            if errors == 'strict':
                raise e
            elif errors == 'ignore':
                pass
            elif errors == 'replace':
                value += six.u('\uFFFD')
                length += 1
    return value, length


def info(name):
    """
    Custom encoding lookup function for registering with Python `codecs`.
    It seems that when the module needs to look up a codec it doesn't understand,
    it will call this function.  If the name matches 'mutf8' or 'mutf-8', it will
    return this module's codec.

    :param name: the name of the codec
    :return: this module's codec, if the name is mutf8 or mutf-8.
    """
    if name in ('mutf8', 'mutf-8'):
        return codecs.CodecInfo(encode, decode, name=NAME)


def mutf8_encode(text, **kwargs):
    """
    Utility to encode strings into Java Modified UTF8 format

    :param text: Python unicode/str text
    :param kwargs: `errors` type, default is `strict`
    :return: the string encoded in Java's Modified UTF-8
    """
    return codecs.encode(text, NAME, kwargs.get('errors', 'strict'))


def mutf8_decode(data, **kwargs):
    """
    Utility to decode Java Modified UTF8 to Python unicode/str text.

    :param data: some Java Modified UTF8 bytes
    :param kwargs: `errors` keyword, default is `strict`
    :return: the Python unicode/str text
    """
    return codecs.decode(data, NAME, kwargs.get('errors', 'strict'))


# register this codec when module is loaded
codecs.register(info)
