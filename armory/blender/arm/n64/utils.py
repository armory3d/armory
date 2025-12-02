"""N64 Utilities - Helper functions for Blender operations and trait data."""

import os
import shutil
import arm.utils


def copy_src(name, path=''):
    """Copy a source file from N64 deployment templates to build directory."""
    tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), path, name)
    out_path = os.path.join(arm.utils.build_dir(), 'n64', path, name)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    shutil.copyfile(tmpl_path, out_path)


def copy_dir(name, path=''):
    """Copy a directory from N64 deployment templates to build directory."""
    tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), path, name)
    out_path = os.path.join(arm.utils.build_dir(), 'n64', path, name)

    if os.path.exists(out_path):
        shutil.rmtree(out_path)
    shutil.copytree(tmpl_path, out_path)


def get_clear_color(scene):
    """Extract clear/background color from a Blender scene."""
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
    """Deselect all objects in all view layers."""
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
    """Convert 0.0-1.0 float to 0-255 int."""
    return int(max(0, min(1, value)) * 255)


def extract_blender_trait_props(trait) -> dict:
    """Extract per-instance property values and types from a Blender trait.

    Returns:
        dict with 'values' and 'types' keys:
        - values: {prop_name: value}
        - types: {prop_name: blender_type}  (only for types that need override, like TSceneFormat)
    """
    values = {}
    types = {}
    if hasattr(trait, 'arm_traitpropslist'):
        for prop in trait.arm_traitpropslist:
            if prop.type == 'Float':
                values[prop.name] = prop.value_float
            elif prop.type == 'Int':
                values[prop.name] = prop.value_int
            elif prop.type == 'Bool':
                values[prop.name] = prop.value_bool
            elif prop.type == 'String':
                values[prop.name] = prop.value_string
            elif prop.type == 'TSceneFormat':
                # Scene property - extract scene name AND mark type for override
                if prop.value_scene is not None:
                    values[prop.name] = prop.value_scene.name
                    types[prop.name] = 'SceneId'  # Override String -> SceneId
    return {'values': values, 'types': types}


def get_trait(trait_info: dict, trait_class: str) -> dict:
    """Get trait data from IR by class name."""
    return trait_info.get("traits", {}).get(trait_class, {})


def get_ir_version(trait_info: dict) -> int:
    """Get IR schema version."""
    return trait_info.get("ir_version", 0)


def trait_needs_data(trait_info: dict, trait_class: str) -> bool:
    """Check if trait has custom data members."""
    trait = get_trait(trait_info, trait_class)
    members = trait.get("members", [])
    return len(members) > 0


def build_trait_initializer(trait_info: dict, trait_class: str, current_scene: str,
                            instance_props: dict = None, type_overrides: dict = None) -> str:
    """Build C initializer for trait data.

    Args:
        trait_info: Full trait IR from macro (ir_version 1)
        trait_class: Class name of the trait
        current_scene: Name of the scene being generated
        instance_props: Per-instance property values from Blender
        type_overrides: Type overrides from Blender (e.g. TSceneFormat -> SceneId)

    Returns:
        C struct initializer string like ".member1 = value, .member2 = value"
    """
    trait = get_trait(trait_info, trait_class)
    members = trait.get("members", [])  # Now an array in IR v1

    if not members:
        return ""

    init_fields = []
    instance_props = instance_props or {}
    type_overrides = type_overrides or {}

    # Iterate members array (IR v1 format)
    for member in members:
        member_name = member.get("name", "")
        if not member_name:
            continue

        # Use Blender's type override if available, else macro's ctype
        member_ctype = type_overrides.get(member_name, member.get("ctype", "float"))

        if member_name in instance_props:
            # Per-instance value from Blender - format as C literal
            c_value = _to_c_literal(instance_props[member_name], member_ctype)
        else:
            # Use macro's default - extract value from IR node
            default_node = member.get("default_value")
            c_value = _extract_default_value(default_node, member_ctype)

        init_fields.append(f'.{member_name} = {c_value}')

    return ', '.join(init_fields)


def _extract_default_value(node, member_ctype: str) -> str:
    """Extract a C literal from an IR node default value.

    IR v1 uses lowercase type names: int, float, string, bool, null, new
    """
    if node is None:
        return _get_type_default(member_ctype)

    if isinstance(node, dict):
        node_type = node.get("type", "")
        value = node.get("value")

        # IR v1 types (lowercase)
        if node_type == "int":
            # If expecting a float, format as float
            if member_ctype == "float":
                return f"{value}.0f"
            return str(value)
        elif node_type == "float":
            v = value
            return f"{v}f" if '.' in str(v) else f"{int(v)}.0f"
        elif node_type == "string":
            # For SceneId, convert scene name to enum
            if member_ctype == "SceneId":
                scene_name = arm.utils.safesrc(str(value)).upper()
                return f"SCENE_{scene_name}"
            return f'"{value}"'
        elif node_type == "bool":
            return "true" if value else "false"
        elif node_type == "null":
            # For SceneId, use proper default instead of NULL
            if member_ctype == "SceneId":
                return "SCENE_UNKNOWN"
            return "NULL"
        elif node_type == "new":
            # Constructor call, e.g. new Vec3(x, y, z), new Vec4(x, y, z, w)
            type_name = value
            args = node.get("args", [])
            if type_name == "Vec4":
                # Vec4 can have 0-4 args, defaults to 0 for missing
                x = _extract_default_value(args[0], "float") if len(args) > 0 else "0.0f"
                y = _extract_default_value(args[1], "float") if len(args) > 1 else "0.0f"
                z = _extract_default_value(args[2], "float") if len(args) > 2 else "0.0f"
                w = _extract_default_value(args[3], "float") if len(args) > 3 else "0.0f"
                return f"(ArmVec4){{{x}, {y}, {z}, {w}}}"
            elif type_name == "Vec3" and len(args) >= 3:
                x = _extract_default_value(args[0], "float")
                y = _extract_default_value(args[1], "float")
                z = _extract_default_value(args[2], "float")
                return f"(ArmVec3){{{x}, {y}, {z}}}"
            elif type_name == "Vec2" and len(args) >= 2:
                x = _extract_default_value(args[0], "float")
                y = _extract_default_value(args[1], "float")
                return f"(ArmVec2){{{x}, {y}}}"
            return _get_type_default(member_ctype)

        # Legacy IR types (PascalCase) - keep for backwards compat
        elif node_type == "IntLit":
            return str(value)
        elif node_type == "FloatLit":
            return str(value)
        elif node_type == "StringLit":
            if member_ctype == "SceneId":
                return value  # Already "SCENE_XXX"
            return f'"{value}"'
        elif node_type == "BoolLit":
            return "true" if value else "false"
        elif node_type == "NullLit":
            if member_ctype == "SceneId":
                return "SCENE_UNKNOWN"
            return "NULL"
        elif node_type == "Vec3Create":
            children = node.get("children", [])
            if len(children) >= 3:
                x = _extract_default_value(children[0], "float")
                y = _extract_default_value(children[1], "float")
                z = _extract_default_value(children[2], "float")
                return f"(ArmVec3){{{x}, {y}, {z}}}"
            return "(ArmVec3){0, 0, 0}"

    # Fallback: use as-is or get type default
    if isinstance(node, (int, float, str, bool)):
        return _to_c_literal(node, member_ctype)
    return _get_type_default(member_ctype)


def _get_type_default(ctype: str) -> str:
    """Return the default C value for a ctype."""
    defaults = {
        "float": "0.0f",
        "int32_t": "0",
        "int": "0",
        "bool": "false",
        "const char*": "NULL",
        "SceneId": "SCENE_UNKNOWN",
        "ArmVec2": "(ArmVec2){0, 0}",
        "ArmVec3": "(ArmVec3){0, 0, 0}",
        "ArmVec4": "(ArmVec4){0, 0, 0, 0}",
        "void*": "NULL",
    }
    return defaults.get(ctype, "0")


def _to_c_literal(value, ctype: str) -> str:
    """Convert a Python value to C literal based on ctype."""
    if ctype == "float":
        f = float(value)
        return f"{f}f" if '.' in str(f) else f"{int(f)}.0f"
    elif ctype in ("int32_t", "int"):
        return str(int(value))
    elif ctype == "bool":
        return "true" if value else "false"
    elif ctype == "const char*":
        return f'"{value}"' if value else "NULL"
    elif ctype == "SceneId":
        # Convert scene name string to SCENE_XXX enum
        scene_name = arm.utils.safesrc(str(value)).upper()
        return f"SCENE_{scene_name}"
    elif "Vec3" in ctype and isinstance(value, (list, tuple)) and len(value) >= 3:
        return f"(ArmVec3){{{value[0]}f, {value[1]}f, {value[2]}f}}"
    elif "Vec2" in ctype and isinstance(value, (list, tuple)) and len(value) >= 2:
        return f"(ArmVec2){{{value[0]}f, {value[1]}f}}"
    else:
        return str(value)
