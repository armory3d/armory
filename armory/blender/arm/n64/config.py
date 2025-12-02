"""
N64 Configuration - Coordinate conversion constants and functions.

All semantic mappings (buttons, types, math functions) are handled by
the Haxe macro (N64TraitMacro.hx) which is the single source of truth.

This module only contains:
- Coordinate system conversion (Blender → N64)
- Scale factor constant
"""

from typing import List
import math


# =============================================================================
# Coordinate System Conversion
# =============================================================================
# Blender: X=right, Y=forward, Z=up
# N64/T3D: X=right, Y=up,      Z=back
#
# Position:  (X, Y, Z) → (X, Z, -Y)
# Scale:     (X, Y, Z) → (X, Z, Y) * factor
# Direction: (X, Y, Z) → (X, Z, -Y), normalized

SCALE_FACTOR: float = 0.015


def convert_position_str(x: str, y: str, z: str) -> str:
    """Convert position strings from Blender to N64 coordinates."""
    return f"{x}, {z}, -({y})"


def convert_scale_str(x: str, y: str, z: str) -> str:
    """Convert scale strings from Blender to N64 coordinates."""
    return f"{x}, {z}, {y}"


def convert_vec3_list(vec: List[float]) -> List[float]:
    """Convert a 3-element list from Blender to N64 coordinates."""
    return [vec[0], vec[2], -vec[1]]


def convert_quat_list(quat: List[float]) -> List[float]:
    """Convert quaternion list from Blender to N64 coordinates."""
    return [quat[0], quat[2], -quat[1], quat[3]]


def convert_scale_list(vec: List[float], factor: float = SCALE_FACTOR) -> List[float]:
    """Convert scale list from Blender to N64 coordinates with factor."""
    return [vec[0] * factor, vec[2] * factor, vec[1] * factor]

