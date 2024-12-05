# Using IES profiles from http://www.derekjenson.com/3d-blog/ies-light-profiles
# IES parser based on:
# https://github.com/tobspr/RenderPipeline
# Copyright (c) 2014-2016 tobspr <tobias.springer1@gmail.com>
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import re
import os
import math
import bpy
import random

def load(filepath):
    global _vertical_angles
    global _horizontal_angles
    global _candela_values
    KEYWORD_REGEX = re.compile(r"\[([A-Za-z0-8_-]+)\](.*)")

    PROFILES = [
        "IESNA:LM-63-1986",
        "IESNA:LM-63-1991",
        "IESNA91",
        "IESNA:LM-63-1995",
        "IESNA:LM-63-2002",
        "ERCO Leuchten GmbH  BY: ERCO/LUM650/8701",
        "ERCO Leuchten GmbH"
    ]

    with open(filepath, "r") as handle:
        lines = handle.readlines()

    lines = [i.strip() for i in lines]

    # Parse version header
    first_line = lines.pop(0)
    if first_line not in PROFILES:
        raise "Unsupported Profile: " + first_line

    # Extracts the keywords
    keywords = {}
    while lines:
        line = lines.pop(0)
        if not line.startswith("["):
            if line != "TILT=NONE":
                continue
            lines.insert(0, line)
            break
        else:
            match = KEYWORD_REGEX.match(line)
            if match:
                key, val = match.group(1, 2)
                keywords[key.strip()] = val.strip()
            else:
                raise "Invalid keyword line: " + line

    # Next line should be TILT=NONE according to the spec
    if lines.pop(0) != "TILT=NONE":
        raise "Expected TILT=NONE line, but none found!"

    # From now on, lines do not matter anymore, instead everything is space seperated
    new_parts = (' '.join(lines)).replace(",", " ").split()

    def read_int():
        return int(new_parts.pop(0))

    def read_float():
        return float(new_parts.pop(0))

    # Amount of Lamps
    if read_int() != 1:
        raise "Only 1 Lamp supported!"

    # Extract various properties
    lumen_per_lamp = read_float()
    candela_multiplier = read_float()
    num_vertical_angles = read_int()
    num_horizontal_angles = read_int()

    if num_vertical_angles < 1 or num_horizontal_angles < 1:
        raise "Invalid of vertical/horizontal angles!"

    photometric_type = read_int()
    unit_type = read_int()

    # Check for a correct unit type, should be 1 for meters and 2 for feet
    if unit_type not in [1, 2]:
        raise "Invalid unit type"

    width = read_float()
    length = read_float()
    height = read_float()
    ballast_factor = read_float()
    future_use = read_float()
    input_watts = read_float()

    _vertical_angles = [read_float() for i in range(num_vertical_angles)]
    _horizontal_angles = [read_float() for i in range(num_horizontal_angles)]

    _candela_values = []
    candela_scale = 0.0

    for i in range(num_horizontal_angles):
        vertical_data = [read_float() for i in range(num_vertical_angles)]
        candela_scale = max(candela_scale, max(vertical_data))
        _candela_values += vertical_data

    # Rescale values, divide by maximum
    _candela_values = [i / candela_scale for i in _candela_values]
    generate_texture()

def generate_texture():
    tex = bpy.data.images.new("iestexture", width=128, height=128, float_buffer=True) # R16
    resolution_vertical = 128
    resolution_horizontal = 128

    for vert in range(resolution_vertical):
        for horiz in range(resolution_horizontal):
            vert_angle = vert / (resolution_vertical - 1.0)
            vert_angle = math.cos(vert_angle * math.pi) * 90.0 + 90.0
            horiz_angle = horiz / (resolution_horizontal - 1.0) * 360.0
            candela = get_candela_value(vert_angle, horiz_angle)
            x = vert
            y = horiz
            i = x + y * resolution_horizontal
            tex.pixels[i * 4] = candela
            tex.pixels[i * 4 + 1] = candela
            tex.pixels[i * 4 + 2] = candela
            tex.pixels[i * 4 + 3] = 1.0

def get_candela_value(vertical_angle, horizontal_angle):
    # Assume a dataset without horizontal angles
    return get_vertical_candela_value(0, vertical_angle)

def get_vertical_candela_value(horizontal_angle_idx, vertical_angle):
    if vertical_angle < 0.0:
        return 0.0

    if vertical_angle > _vertical_angles[len(_vertical_angles) - 1]:
        return 0.0

    for vertical_index in range(1, len(_vertical_angles)):
        curr_angle = _vertical_angles[vertical_index]
        if curr_angle > vertical_angle:
            prev_angle = _vertical_angles[vertical_index - 1]
            prev_value = get_candela_value_from_index(vertical_index - 1, horizontal_angle_idx)
            curr_value = get_candela_value_from_index(vertical_index, horizontal_angle_idx)
            lerp = (vertical_angle - prev_angle) / (curr_angle - prev_angle)
            assert lerp >= 0.0 and lerp <= 1.0
            return curr_value * lerp + prev_value * (1.0 - lerp)
    return 0.0

def get_candela_value_from_index(vertical_angle_idx, horizontal_angle_idx):
    index = vertical_angle_idx + horizontal_angle_idx * len(_vertical_angles)
    return _candela_values[index]

filepath = "/Users/lubos/Desktop/ies/JellyFish.ies"
load(filepath)
