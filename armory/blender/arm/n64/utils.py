"""
N64 Utilities

Helper functions for Blender operations and trait data extraction.
NO coordinate conversion here - that's handled by converter.py using macro rules.
"""

import os
import shutil
import arm.utils


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
    bpy.context.view_layer.objects.active = None
    bpy.ops.object.select_all(action='DESELECT')
    for scene in bpy.data.scenes:
        for view_layer in scene.view_layers:
            view_layer.objects.active = None
            for obj in scene.objects:
                obj.select_set(False, view_layer=view_layer)
            view_layer.update()
    bpy.context.view_layer.update()


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
            elif prop.type == 'String':
                props[prop.name] = prop.value_string
            elif prop.type == 'TSceneFormat':
                # Scene property - extract scene name
                if prop.value_scene is not None:
                    props[prop.name] = prop.value_scene.name
    return props


def get_trait(trait_info: dict, trait_class: str) -> dict:
    """Get trait data from macro JSON."""
    return trait_info.get("traits", {}).get(trait_class, {})


def trait_needs_data(trait_info: dict, trait_class: str) -> bool:
    """Check if trait needs per-instance data. Macro provides this directly."""
    return get_trait(trait_info, trait_class).get("needs_data", False)


def build_trait_initializer(trait_info: dict, trait_class: str, current_scene: str, instance_props: dict = None) -> str:
    """
    Build C initializer string for trait data.

    The macro provides default values as C literals.
    Blender per-instance props override defaults.
    """
    trait = get_trait(trait_info, trait_class)
    members = trait.get("members", {})
    target_scene = trait.get("target_scene")

    init_fields = []
    instance_props = instance_props or {}

    # Add target_scene if trait uses scene switching
    if target_scene is not None:
        # Use instance prop if provided, otherwise macro's resolved scene
        scene_name = instance_props.get("target_scene", target_scene)
        init_fields.append(f'.target_scene = SCENE_{scene_name.upper()}')

    # Add member initializers
    for member_name, member_info in members.items():
        if member_name in instance_props:
            # Per-instance value from Blender - format as C literal
            value = instance_props[member_name]
            c_value = _to_c_literal(value, member_info["type"])
        else:
            # Use macro's default (already a C literal)
            c_value = member_info["default_value"]

        init_fields.append(f'.{member_name} = {c_value}')

    return ', '.join(init_fields)


def _to_c_literal(value, c_type: str) -> str:
    """Convert a Python value to C literal string."""
    if c_type == "float":
        f = float(value)
        return f"{f}f" if '.' in str(f) else f"{int(f)}.0f"
    elif c_type == "int32_t":
        return str(int(value))
    elif c_type == "bool":
        return "true" if value else "false"
    elif c_type == "SceneId":
        # Convert scene name string to SCENE_XXX enum
        scene_name = arm.utils.safesrc(str(value)).upper()
        return f"SCENE_{scene_name}"
    else:
        return str(value)
