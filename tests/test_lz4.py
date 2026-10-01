"""Regression tests for armory/blender/arm/lib/lz4.py.

These tests only need numpy (no bpy/Blender, no Kha/Haxe build), so they can
run directly with pytest.
"""
import os
import struct
import sys

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__), "..", "armory", "blender", "arm", "lib"
    ),
)

from lz4 import LZ4  # noqa: E402


def decode_reference(data: bytes, out_len: int) -> bytes:
    """Independent LZ4 block decoder, ported 1:1 from the project's own
    reference implementation at armory/Sources/iron/system/Lz4.hx
    (Lz4.decode), used here only to verify what LZ4.encode() actually
    produces. Not a copy of any code under test.
    """
    i_buf = data
    i_len = len(i_buf)
    o_buf = bytearray(out_len)
    i_pos = 0
    o_pos = 0

    while i_pos < i_len:
        token = i_buf[i_pos]
        i_pos += 1

        clen = token >> 4
        if clen != 0:
            if clen == 15:
                while True:
                    l = i_buf[i_pos]
                    i_pos += 1
                    if l != 255:
                        break
                    clen += 255
                clen += l
            end = i_pos + clen
            while i_pos < end:
                o_buf[o_pos] = i_buf[i_pos]
                o_pos += 1
                i_pos += 1
            if i_pos == i_len:
                break

        m_offset = i_buf[i_pos + 0] | (i_buf[i_pos + 1] << 8)
        if m_offset == 0 or m_offset > o_pos:
            raise ValueError("bad match offset")
        i_pos += 2

        clen = (token & 0x0F) + 4
        if clen == 19:
            while True:
                l = i_buf[i_pos]
                i_pos += 1
                if l != 255:
                    break
                clen += 255
            clen += l

        m_pos = o_pos - m_offset
        end = o_pos + clen
        while o_pos < end:
            o_buf[o_pos] = o_buf[m_pos]
            o_pos += 1
            m_pos += 1

    return bytes(o_buf)


def roundtrip(data: bytes) -> bytes:
    return decode_reference(LZ4.encode(data), len(data))


def test_roundtrip_repetitive_ascii():
    # Long repeated pattern: any working LZ4 encoder should find matches
    # here and compress it well below its original size.
    original = b"ABCDEFGHIJabcdefghij" * 20
    compressed = LZ4.encode(original)
    assert roundtrip(original) == original
    assert len(compressed) < len(original)


def test_roundtrip_packed_integers_with_zero_bytes():
    # Packed little-endian uint32s: typical of exported mesh/index data,
    # and (unlike the ASCII case) contains literal 0x00 bytes. Before the
    # fix, encode() silently dropped each newly read byte's high bits
    # before combining it into the rolling match-hash sequence (because a
    # numpy uint8 scalar shifted left by >= 8 bits overflows to 0 instead
    # of widening first), which both broke match-finding and could emit
    # match references that do not correspond to the source data.
    original = b"".join(struct.pack("<I", i % 7) for i in range(100))
    assert roundtrip(original) == original


def test_roundtrip_all_byte_values():
    original = bytes(range(256)) * 4
    assert roundtrip(original) == original
