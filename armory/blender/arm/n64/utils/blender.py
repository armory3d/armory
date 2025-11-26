"""
Blender Utilities

Helper functions for interacting with Blender and the build system.
"""

import os
import shutil
import arm.utils


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
