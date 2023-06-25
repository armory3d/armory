"""Msgpack parser with typed arrays"""

# Based on u-msgpack-python v2.4.1 - v at sergeev.io
# https://github.com/vsergeev/u-msgpack-python
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
import io
import struct
import numpy as np


def _pack_integer(obj, fp):
    if obj < 0:
        if obj >= -32:
            fp.write(struct.pack("b", obj))
        elif obj >= -(2 ** (8 - 1)):
            fp.write(b"\xd0" + struct.pack("b", obj))
        elif obj >= -(2 ** (16 - 1)):
            fp.write(b"\xd1" + struct.pack("<h", obj))
        elif obj >= -(2 ** (32 - 1)):
            fp.write(b"\xd2" + struct.pack("<i", obj))
        elif obj >= -(2 ** (64 - 1)):
            fp.write(b"\xd3" + struct.pack("<q", obj))
        else:
            raise Exception("huge signed int")
    else:
        if obj <= 127:
            fp.write(struct.pack("B", obj))
        elif obj <= 2**8 - 1:
            fp.write(b"\xcc" + struct.pack("B", obj))
        elif obj <= 2**16 - 1:
            fp.write(b"\xcd" + struct.pack("<H", obj))
        elif obj <= 2**32 - 1:
            fp.write(b"\xce" + struct.pack("<I", obj))
        elif obj <= 2**64 - 1:
            fp.write(b"\xcf" + struct.pack("<Q", obj))
        else:
            raise Exception("huge unsigned int")


def _pack_nil(obj, fp):
    fp.write(b"\xc0")


def _pack_boolean(obj, fp):
    fp.write(b"\xc3" if obj else b"\xc2")


def _pack_float(obj, fp):
    # NOTE: forced 32-bit floats for Armory
    # fp.write(b"\xcb" + struct.pack("<d", obj)) # Double
    fp.write(b"\xca" + struct.pack("<f", obj))


def _pack_string(obj, fp):
    obj = obj.encode("utf-8")
    if len(obj) <= 31:
        fp.write(struct.pack("B", 0xA0 | len(obj)) + obj)
    elif len(obj) <= 2**8 - 1:
        fp.write(b"\xd9" + struct.pack("B", len(obj)) + obj)
    elif len(obj) <= 2**16 - 1:
        fp.write(b"\xda" + struct.pack("<H", len(obj)) + obj)
    elif len(obj) <= 2**32 - 1:
        fp.write(b"\xdb" + struct.pack("<I", len(obj)) + obj)
    else:
        raise Exception("huge string")


def _pack_binary(obj, fp):
    if len(obj) <= 2**8 - 1:
        fp.write(b"\xc4" + struct.pack("B", len(obj)) + obj)
    elif len(obj) <= 2**16 - 1:
        fp.write(b"\xc5" + struct.pack("<H", len(obj)) + obj)
    elif len(obj) <= 2**32 - 1:
        fp.write(b"\xc6" + struct.pack("<I", len(obj)) + obj)
    else:
        raise Exception("huge binary string")


def _pack_array(obj, fp):
    if len(obj) <= 15:
        fp.write(struct.pack("B", 0x90 | len(obj)))
    elif len(obj) <= 2**16 - 1:
        fp.write(b"\xdc" + struct.pack("<H", len(obj)))
    elif len(obj) <= 2**32 - 1:
        fp.write(b"\xdd" + struct.pack("<I", len(obj)))
    else:
        raise Exception("huge array")

    if len(obj) > 0 and isinstance(obj[0], float):
        fp.write(b"\xca")
        for e in obj:
            fp.write(struct.pack("<f", e))
    elif len(obj) > 0 and isinstance(obj[0], bool):
        for e in obj:
            pack(e, fp)
    elif len(obj) > 0 and isinstance(obj[0], int):
        fp.write(b"\xd2")
        for e in obj:
            fp.write(struct.pack("<i", e))
    # Float32
    elif len(obj) > 0 and isinstance(obj[0], np.float32):
        fp.write(b"\xca")
        fp.write(obj.tobytes())
    # Int32
    elif len(obj) > 0 and isinstance(obj[0], np.int32):
        fp.write(b"\xd2")
        fp.write(obj.tobytes())
    # Int16
    elif len(obj) > 0 and isinstance(obj[0], np.int16):
        fp.write(b"\xd1")
        fp.write(obj.tobytes())
    # Regular
    else:
        for e in obj:
            pack(e, fp)


def _pack_map(obj, fp):
    if len(obj) <= 15:
        fp.write(struct.pack("B", 0x80 | len(obj)))
    elif len(obj) <= 2**16 - 1:
        fp.write(b"\xde" + struct.pack("<H", len(obj)))
    elif len(obj) <= 2**32 - 1:
        fp.write(b"\xdf" + struct.pack("<I", len(obj)))
    else:
        raise Exception("huge array")

    for k, v in obj.items():
        pack(k, fp)
        pack(v, fp)


def pack(obj, fp):
    if obj is None:
        _pack_nil(obj, fp)
    elif isinstance(obj, bool):
        _pack_boolean(obj, fp)
    elif isinstance(obj, int):
        _pack_integer(obj, fp)
    elif isinstance(obj, float):
        _pack_float(obj, fp)
    elif isinstance(obj, str):
        _pack_string(obj, fp)
    elif isinstance(obj, bytes):
        _pack_binary(obj, fp)
    elif isinstance(obj, (list, np.ndarray, tuple)):
        _pack_array(obj, fp)
    elif isinstance(obj, dict):
        _pack_map(obj, fp)
    else:
        raise Exception(f"unsupported type: {str(type(obj))}")


def packb(obj):
    fp = io.BytesIO()
    pack(obj, fp)
    return fp.getvalue()
