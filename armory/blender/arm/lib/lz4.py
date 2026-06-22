"""
Port of the Iron LZ4 compression module based on
https://github.com/gorhill/lz4-wasm. Original license:

BSD 2-Clause License
Copyright (c) 2018, Raymond Hill
All rights reserved.
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import numpy as np
from numpy import uint8, int32, uint32


class LZ4RangeException(Exception):
    pass


class LZ4:
    hash_table = None

    @staticmethod
    def encode_bound(size: int) -> int:
        return 0 if size > 0x7E000000 else size + (size // 255 | 0) + 16

    @staticmethod
    def encode(b: bytes) -> bytes:
        i_buf: np.ndarray = np.frombuffer(b, dtype=uint8)
        i_len = i_buf.size

        if i_len >= 0x7E000000:
            raise LZ4RangeException("Input buffer is too large")

        # "The last match must start at least 12 bytes before end of block"
        last_match_pos = i_len - 12

        # "The last 5 bytes are always literals"
        last_literal_pos = i_len - 5

        if LZ4.hash_table is None:
            LZ4.hash_table = np.full(shape=65536, fill_value=-65536, dtype=int32)

        LZ4.hash_table.fill(-65536)

        o_len = LZ4.encode_bound(i_len)
        o_buf = np.full(shape=o_len, fill_value=0, dtype=uint8)
        i_pos = 0
        o_pos = 0
        anchor_pos = 0

        # Sequence-finding loop
        while True:
            ref_pos = int32(0)
            m_offset = 0
            sequence = uint32(
                i_buf[i_pos] << 8 | i_buf[i_pos + 1] << 16 | i_buf[i_pos + 2] << 24
            )

            # Match-finding loop
            while i_pos <= last_match_pos:
                # Conversion to uint32 is mandatory to ensure correct
                # unsigned right shift (compare with .hx implementation)
                sequence = uint32(
                    uint32(sequence) >> uint32(8) | i_buf[i_pos + 3] << 24
                )
                hash_val = (sequence * 0x9E37 & 0xFFFF) + (
                    uint32(sequence * 0x79B1) >> uint32(16)
                ) & 0xFFFF
                ref_pos = LZ4.hash_table[hash_val]
                LZ4.hash_table[hash_val] = i_pos
                m_offset = i_pos - ref_pos
                if (
                    m_offset < 65536
                    and i_buf[ref_pos + 0] == (sequence & 0xFF)
                    and i_buf[ref_pos + 1] == ((sequence >> uint32(8)) & 0xFF)
                    and i_buf[ref_pos + 2] == ((sequence >> uint32(16)) & 0xFF)
                    and i_buf[ref_pos + 3] == ((sequence >> uint32(24)) & 0xFF)
                ):
                    break

                i_pos += 1

            # No match found
            if i_pos > last_match_pos:
                break

            # Match found
            l_len = i_pos - anchor_pos
            m_len = i_pos
            i_pos += 4
            ref_pos += 4
            while i_pos < last_literal_pos and i_buf[i_pos] == i_buf[ref_pos]:
                i_pos += 1
                ref_pos += 1

            m_len = i_pos - m_len
            token = m_len - 4 if m_len < 19 else 15

            # Write token, length of literals if needed
            if l_len >= 15:
                o_buf[o_pos] = 0xF0 | token
                o_pos += 1
                l = l_len - 15
                while l >= 255:
                    o_buf[o_pos] = 255
                    o_pos += 1
                    l -= 255
                o_buf[o_pos] = l
                o_pos += 1
            else:
                o_buf[o_pos] = (l_len << 4) | token
                o_pos += 1

            # Write literals
            while l_len > 0:
                l_len -= 1
                o_buf[o_pos] = i_buf[anchor_pos]
                o_pos += 1
                anchor_pos += 1

            if m_len == 0:
                break

            # Write offset of match
            o_buf[o_pos + 0] = m_offset
            o_buf[o_pos + 1] = m_offset >> 8
            o_pos += 2

            # Write length of match if needed
            if m_len >= 19:
                l = m_len - 19
                while l >= 255:
                    o_buf[o_pos] = 255
                    o_pos += 1
                    l -= 255

                o_buf[o_pos] = l
                o_pos += 1

            anchor_pos = i_pos

        # Last sequence is literals only
        l_len = i_len - anchor_pos
        if l_len >= 15:
            o_buf[o_pos] = 0xF0
            o_pos += 1
            l = l_len - 15
            while l >= 255:
                o_buf[o_pos] = 255
                o_pos += 1
                l -= 255

            o_buf[o_pos] = l
            o_pos += 1

        else:
            o_buf[o_pos] = l_len << 4
            o_pos += 1

        while l_len > 0:
            l_len -= 1
            o_buf[o_pos] = i_buf[anchor_pos]
            o_pos += 1
            anchor_pos += 1

        return np.resize(o_buf, o_pos).tobytes()
