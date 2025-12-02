"""
N64 Configuration - All mappings and constants for N64 code generation.

This is the single source of truth for:
- Button mappings (Armory → N64)
- Type mappings (Haxe → C)
- Math function mappings
- Coordinate system conversion rules
- Skip filters
"""

from typing import Dict, List, Tuple
import math


# =============================================================================
# Button Mappings: Armory/Iron → N64
# =============================================================================

BUTTON_MAP: Dict[str, str] = {
    # PlayStation-style
    "cross": "N64_BTN_A",
    "square": "N64_BTN_B",
    "circle": "N64_BTN_CRIGHT",
    "triangle": "N64_BTN_CLEFT",
    # Xbox-style
    "a": "N64_BTN_A",
    "b": "N64_BTN_CRIGHT",
    "x": "N64_BTN_B",
    "y": "N64_BTN_CLEFT",
    # Shoulders/Triggers
    "r1": "N64_BTN_CDOWN",
    "r2": "N64_BTN_R",
    "r3": "N64_BTN_CUP",
    "l1": "N64_BTN_Z",
    "l2": "N64_BTN_L",
    "l3": "N64_BTN_CUP",
    # System
    "start": "N64_BTN_START",
    "options": "N64_BTN_START",
    "share": "N64_BTN_START",
    # D-Pad
    "up": "N64_BTN_DUP",
    "down": "N64_BTN_DDOWN",
    "left": "N64_BTN_DLEFT",
    "right": "N64_BTN_DRIGHT",
}


# =============================================================================
# Input State Mappings
# =============================================================================

INPUT_STATE_MAP: Dict[str, str] = {
    "down": "input_down",
    "started": "input_started",
    "released": "input_released",
}

STICK_MAP: Dict[str, str] = {
    "getStickX": "input_stick_x",
    "getStickY": "input_stick_y",
}


# =============================================================================
# Type Mappings: Haxe → C
# =============================================================================

TYPE_MAP: Dict[str, str] = {
    "Float": "float",
    "float": "float",
    "double": "float",
    "Int": "int32_t",
    "int": "int32_t",
    "Bool": "bool",
    "bool": "bool",
    "String": "const char*",
    "Vec2": "ArmVec2",
    "iron.math.Vec2": "ArmVec2",
    "Vec3": "ArmVec3",
    "Vec4": "ArmVec3",
    "iron.math.Vec4": "ArmVec3",
    "SceneId": "SceneId",
}


# =============================================================================
# Math Function Mappings: Haxe/Iron → C
# =============================================================================

MATH_FUNC_MAP: Dict[str, str] = {
    "sqrt": "sqrtf",
    "abs": "fabsf",
    "pow": "powf",
    "sin": "sinf",
    "cos": "cosf",
    "tan": "tanf",
    "asin": "asinf",
    "acos": "acosf",
    "atan": "atanf",
    "atan2": "atan2f",
    "log": "logf",
    "exp": "expf",
    "floor": "floorf",
    "ceil": "ceilf",
    "round": "roundf",
    "min": "fminf",
    "max": "fmaxf",
    "PI": "M_PI",
    "POSITIVE_INFINITY": "INFINITY",
    "NEGATIVE_INFINITY": "(-INFINITY)",
    "NaN": "NAN",
}


# =============================================================================
# Skip Filters - Members to exclude from trait processing
# =============================================================================

SKIP_MEMBERS: set = {
    "object",
    "transform",
    "gamepad",
    "keyboard",
    "mouse",
    "name",
    "physics",
    "rb",
}


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


def convert_position(x: float, y: float, z: float) -> Tuple[float, float, float]:
    """Convert position from Blender to N64 coordinates."""
    return (x, z, -y)


def convert_position_str(x: str, y: str, z: str) -> str:
    """Convert position strings from Blender to N64 coordinates."""
    return f"{x}, {z}, -({y})"


def convert_scale(x: float, y: float, z: float, factor: float = SCALE_FACTOR) -> Tuple[float, float, float]:
    """Convert scale from Blender to N64 coordinates with scale factor."""
    return (x * factor, z * factor, y * factor)


def convert_scale_str(x: str, y: str, z: str) -> str:
    """Convert scale strings from Blender to N64 coordinates."""
    return f"{x}, {z}, {y}"


def convert_direction(x: float, y: float, z: float) -> Tuple[float, float, float]:
    """Convert and normalize direction from Blender to N64 coordinates."""
    # Swizzle
    nx, ny, nz = x, z, -y
    # Normalize
    length = math.sqrt(nx*nx + ny*ny + nz*nz)
    if length > 0:
        return (nx/length, ny/length, nz/length)
    return (nx, ny, nz)


def convert_direction_str(x: str, y: str, z: str) -> str:
    """Convert direction strings from Blender to N64 coordinates."""
    return f"{x}, {z}, -({y})"


def convert_quaternion(x: float, y: float, z: float, w: float) -> Tuple[float, float, float, float]:
    """Convert quaternion from Blender to N64 coordinates (swizzle XYZ, keep W)."""
    return (x, z, -y, w)


def convert_vec3_list(vec: List[float]) -> List[float]:
    """Convert a 3-element list from Blender to N64 coordinates."""
    return [vec[0], vec[2], -vec[1]]


def convert_quat_list(quat: List[float]) -> List[float]:
    """Convert quaternion list from Blender to N64 coordinates."""
    return [quat[0], quat[2], -quat[1], quat[3]]


def convert_scale_list(vec: List[float], factor: float = SCALE_FACTOR) -> List[float]:
    """Convert scale list from Blender to N64 coordinates with factor."""
    return [vec[0] * factor, vec[2] * factor, vec[1] * factor]


# =============================================================================
# Helper Functions
# =============================================================================

def map_button(button: str) -> str:
    """Map an Armory button name to N64 constant."""
    return BUTTON_MAP.get(button.lower(), "N64_BTN_A")


def map_input_state(state: str) -> str:
    """Map input state method to N64 function."""
    return INPUT_STATE_MAP.get(state, "input_down")


def map_stick(method: str) -> str:
    """Map stick method to N64 function."""
    return STICK_MAP.get(method, "input_stick_x")


def map_type(haxe_type: str) -> str:
    """Map a Haxe type to C type."""
    return TYPE_MAP.get(haxe_type, "float")


def is_supported_type(type_name: str) -> bool:
    """Check if type is supported for N64."""
    return type_name in TYPE_MAP


def should_skip_member(name: str) -> bool:
    """Check if member should be skipped (API objects like gamepad, transform)."""
    return name in SKIP_MEMBERS


def map_math_func(func: str) -> str:
    """Map a math function name to C equivalent."""
    return MATH_FUNC_MAP.get(func, func)
