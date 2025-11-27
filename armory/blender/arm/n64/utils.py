"""
N64 Utilities

Helper functions for Blender operations and trait data extraction.
"""

import os
import shutil
import arm.utils


# =============================================================================
# Coordinate Conversion (Blender Z-up → N64/T3D Y-up)
# =============================================================================

def blender_to_n64_position(loc):
    """Convert Blender position (Z-up) to N64 (Y-up).

    Blender: X=right, Y=forward, Z=up
    N64/T3D: X=right, Y=up, Z=back
    """
    return (loc[0], loc[2], -loc[1])


def blender_to_n64_scale(scale, factor=0.015):
    """Convert Blender scale to N64 scale with optional scaling factor.

    Swaps Y and Z to match coordinate system change.
    """
    return (scale[0] * factor, scale[2] * factor, scale[1] * factor)


def blender_to_n64_euler(matrix_world):
    """Convert Blender world matrix rotation to N64 Euler angles.

    Returns tuple of (rx, ry, rz) in radians for T3D's euler system.
    """
    e = matrix_world.to_quaternion().to_euler('YZX')
    return (-e.x, -e.z, e.y)


def blender_to_n64_direction(dir_vec):
    """Convert Blender direction vector to N64 coordinate system."""
    return (dir_vec[0], dir_vec[2], -dir_vec[1])


def normalize_direction(dir_vec):
    """Normalize a direction vector."""
    import math
    length = math.sqrt(dir_vec[0]**2 + dir_vec[1]**2 + dir_vec[2]**2)
    if length > 0:
        return (dir_vec[0]/length, dir_vec[1]/length, dir_vec[2]/length)
    return dir_vec


# Axis mapping for runtime rotation (used by traits_generator.py)
# Maps Blender axis to (N64 rot[] index, needs_negate)
# Based on exporter's euler conversion: (-e.x, -e.z, e.y)
N64_AXIS_ROTATION_MAP = {
    'x': (0, True),   # Blender X -> N64 rot[0], negated
    'y': (2, False),  # Blender Y -> N64 rot[2], same sign
    'z': (1, True),   # Blender Z -> N64 rot[1], negated
}


# =============================================================================
# Blender Utilities
# =============================================================================

def copy_src(name, path=''):
    """Copy a source file from the N64 deployment templates to the build directory."""
    tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), path, name)
    out_path = os.path.join(arm.utils.build_dir(), 'n64', path, name)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    shutil.copyfile(tmpl_path, out_path)


def get_clear_color(scene):
    """Extract the clear/background color from a Blender scene."""
    if scene.world is None:
        return [0.051, 0.051, 0.051, 1.0]

    if scene.world.node_tree is None:
        c = scene.world.color
        return [c[0], c[1], c[2], 1.0]

    if 'Background' in scene.world.node_tree.nodes:
        background_node = scene.world.node_tree.nodes['Background']
        col = background_node.inputs[0].default_value
        strength = background_node.inputs[1].default_value
        ar = [col[0] * strength, col[1] * strength, col[2] * strength, col[3]]
        ar[0] = max(min(ar[0], 1.0), 0.0)
        ar[1] = max(min(ar[1], 1.0), 0.0)
        ar[2] = max(min(ar[2], 1.0), 0.0)
        ar[3] = max(min(ar[3], 1.0), 0.0)
        return ar
    return [0.051, 0.051, 0.051, 1.0]


def deselect_from_all_viewlayers():
    """Deselect all objects in all view layers across all scenes."""
    import bpy
    for scene in bpy.data.scenes:
        for view_layer in scene.view_layers:
            for obj in scene.objects:
                obj.select_set(False, view_layer=view_layer)


def to_uint8(value):
    """Convert a 0.0-1.0 float value to 0-255 integer."""
    return int(max(0, min(1, value)) * 255)


# =============================================================================
# Trait Utilities
# =============================================================================

def extract_blender_trait_props(trait) -> dict:
    """Extract per-instance property values from a Blender trait.

    This pulls values set in Blender UI that override the Haxe defaults.
    Required because macros cannot read Blender scene instances.
    """
    props = {}
    if hasattr(trait, 'arm_traitpropslist'):
        for prop in trait.arm_traitpropslist:
            if prop.type == 'Float':
                props[prop.name] = prop.value_float
            elif prop.type == 'Int':
                props[prop.name] = prop.value_int
            elif prop.type == 'Bool':
                props[prop.name] = prop.value_bool
    return props
