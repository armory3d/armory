"""N64 Utilities"""

import os
import shutil
from typing import List, Optional

import bpy
import bmesh

import arm.utils
import arm.log as log


# =============================================================================
# Coordinate Conversion: Blender (X,Y,Z) → N64 (X,Z,-Y)
# =============================================================================

SCALE_FACTOR: float = 0.015

# Python value conversion
def convert_vec3_list(vec: List[float]) -> List[float]:
    return [vec[0], vec[2], -vec[1]]

def convert_quat_list(quat: List[float]) -> List[float]:
    return [quat[0], quat[2], -quat[1], quat[3]]

def convert_scale_list(vec: List[float], factor: float = SCALE_FACTOR) -> List[float]:
    return [vec[0] * factor, vec[2] * factor, vec[1] * factor]

# C expression conversion
def c_vec3_convert(x: str, y: str, z: str) -> tuple:
    return (x, z, f"-({y})")

def c_vec3_expr(x: str, y: str, z: str, convert: bool = True) -> str:
    if convert:
        x, y, z = c_vec3_convert(x, y, z)
    return f"{{{x}, {y}, {z}}}"

def c_oimo_vec3(vec_expr: str, convert: bool = True) -> str:
    if convert:
        return f"(OimoVec3){{{vec_expr}.x, {vec_expr}.z, -({vec_expr}.y)}}"
    return f"(OimoVec3){{{vec_expr}.x, {vec_expr}.y, {vec_expr}.z}}"

def c_float(value) -> str:
    f = float(value)
    s = str(f)
    return f"{s}f" if '.' in s else f"{int(f)}.0f"


# =============================================================================
# Build Helpers
# =============================================================================

N64_CONFIG = {
    'max_physics_bodies': 32,
    'max_button_subscribers': 16,
}

def get_physics_debug_mode() -> int:
    wrd = bpy.data.worlds.get('Arm')
    if wrd is None:
        return 0
    flags = [
        ('arm_physics_dbg_draw_wireframe', 1),
        ('arm_physics_dbg_draw_aabb', 2),
        ('arm_physics_dbg_draw_contact_points', 8),
        ('arm_physics_dbg_draw_constraints', 2048),
        ('arm_physics_dbg_draw_constraint_limits', 4096),
        ('arm_physics_dbg_draw_normals', 16384),
        ('arm_physics_dbg_draw_axis_gizmo', 32768),
        ('arm_physics_dbg_draw_raycast', 65536),
    ]
    return sum(bit for prop, bit in flags if getattr(wrd, prop, False))

def get_config(key, default=None):
    return N64_CONFIG.get(key, default)

def copy_src(name, path=''):
    tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), path, name)
    out_path = os.path.join(arm.utils.build_dir(), 'n64', path, name)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    shutil.copyfile(tmpl_path, out_path)

def copy_dir(name, path=''):
    tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), path, name)
    out_path = os.path.join(arm.utils.build_dir(), 'n64', path, name)
    if os.path.exists(out_path):
        shutil.rmtree(out_path)
    shutil.copytree(tmpl_path, out_path)


# =============================================================================
# Blender Data Extraction
# =============================================================================

def get_clear_color(scene):
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
        return [max(min(v, 1.0), 0.0) for v in ar]
    return [0.051, 0.051, 0.051, 1.0]

def deselect_from_all_viewlayers():
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
    return int(max(0, min(1, value)) * 255)

def extract_blender_trait_props(trait) -> dict:
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
                if prop.value_scene is not None:
                    values[prop.name] = prop.value_scene.name
                    types[prop.name] = 'SceneId'
    return {'values': values, 'types': types}


# =============================================================================
# Trait IR Helpers
# =============================================================================

def get_trait(trait_info: dict, trait_class: str) -> dict:
    return trait_info.get("traits", {}).get(trait_class, {})

def trait_needs_data(trait_info: dict, trait_class: str) -> bool:
    return len(get_trait(trait_info, trait_class).get("members", [])) > 0

def build_trait_initializer(trait_info: dict, trait_class: str, current_scene: str,
                            instance_props: dict = None, type_overrides: dict = None) -> str:
    trait = get_trait(trait_info, trait_class)
    members = trait.get("members", [])
    if not members:
        return ""

    init_fields = []
    instance_props = instance_props or {}
    type_overrides = type_overrides or {}

    for member in members:
        member_name = member.get("name", "")
        if not member_name:
            continue
        member_ctype = type_overrides.get(member_name, member.get("ctype", "float"))
        if member_name in instance_props:
            c_value = to_c_literal(instance_props[member_name], member_ctype)
        else:
            c_value = extract_default_value(member.get("default_value"), member_ctype)
        init_fields.append(f'.{member_name} = {c_value}')

    return ', '.join(init_fields)


# =============================================================================
# C Literal Helpers
# =============================================================================

def extract_default_value(node, member_ctype: str) -> str:
    """Convert an IR node to a C literal string."""
    if node is None:
        return get_type_default(member_ctype)

    if isinstance(node, dict):
        node_type = node.get("type", "")
        value = node.get("value")

        if node_type == "int":
            return c_float(value) if member_ctype == "float" else str(value)
        elif node_type == "float":
            return c_float(value)
        elif node_type == "string":
            if member_ctype == "SceneId":
                return f"SCENE_{arm.utils.safesrc(str(value)).upper()}"
            return f'"{value}"'
        elif node_type == "bool":
            return "true" if value else "false"
        elif node_type == "null":
            return "SCENE_UNKNOWN" if member_ctype == "SceneId" else "NULL"
        elif node_type == "new":
            return _extract_vec_constructor(value, node.get("args", []))

    if isinstance(node, (int, float, str, bool)):
        return to_c_literal(node, member_ctype)
    return get_type_default(member_ctype)

def _extract_vec_constructor(type_name: str, args: list) -> str:
    def arg(i): return extract_default_value(args[i], "float") if i < len(args) else "0.0f"
    if type_name == "Vec4":
        return f"(ArmVec4){{{arg(0)}, {arg(1)}, {arg(2)}, {arg(3)}}}"
    elif type_name == "Vec3":
        return f"(ArmVec3){{{arg(0)}, {arg(1)}, {arg(2)}}}"
    elif type_name == "Vec2":
        return f"(ArmVec2){{{arg(0)}, {arg(1)}}}"
    return "0"

TYPE_DEFAULTS = {
    "float": "0.0f", "int32_t": "0", "int": "0", "bool": "false",
    "const char*": "NULL", "SceneId": "SCENE_UNKNOWN",
    "ArmVec2": "(ArmVec2){0, 0}", "ArmVec3": "(ArmVec3){0, 0, 0}",
    "ArmVec4": "(ArmVec4){0, 0, 0, 0}", "void*": "NULL",
    "KouiLabel*": "NULL",
}

def get_type_default(ctype: str) -> str:
    """Get the default C literal for a given C type."""
    return TYPE_DEFAULTS.get(ctype, "0")

def to_c_literal(value, ctype: str) -> str:
    """Convert a Python value to a C literal string."""
    if ctype == "float":
        return c_float(value)
    elif ctype in ("int32_t", "int"):
        return str(int(value))
    elif ctype == "bool":
        return "true" if value else "false"
    elif ctype == "const char*":
        return f'"{value}"' if value else "NULL"
    elif ctype == "SceneId":
        return f"SCENE_{arm.utils.safesrc(str(value)).upper()}"
    elif "Vec3" in ctype and isinstance(value, (list, tuple)) and len(value) >= 3:
        return f"(ArmVec3){{{c_float(value[0])}, {c_float(value[1])}, {c_float(value[2])}}}"
    elif "Vec2" in ctype and isinstance(value, (list, tuple)) and len(value) >= 2:
        return f"(ArmVec2){{{c_float(value[0])}, {c_float(value[1])}}}"
    return str(value)


# =============================================================================
# Static Object Detection
# =============================================================================

def compute_static_flags(scene_data: dict, trait_info: dict) -> None:
    """Mark objects as static if no dynamic physics and no transform-mutating traits."""
    traits_data = trait_info.get('traits', {})

    def trait_mutates_transform(trait_class: str) -> bool:
        return traits_data.get(trait_class, {}).get('meta', {}).get('mutates_transform', False)

    for scene in scene_data.values():
        for obj in scene.get("objects", []):
            rb = obj.get("rigid_body")
            has_dynamic_physics = rb and rb.get("mass", 0.0) > 0.0
            any_trait_mutates = any(
                trait_mutates_transform(t.get("class_name", ""))
                for t in obj.get("traits", [])
            )
            obj["is_static"] = not has_dynamic_physics and not any_trait_mutates


# =============================================================================
# Collision Mesh
# =============================================================================

def extract_collision_mesh(obj: bpy.types.Object, max_triangles: int = 256) -> Optional[dict]:
    """Extract triangulated mesh data for physics collision."""
    if obj.type != 'MESH':
        return None

    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    mesh = obj_eval.to_mesh()
    if mesh is None:
        return None

    try:
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='FIXED')

        scale = obj.scale
        vertices = []
        for v in bm.verts:
            scaled = [v.co.x * scale.x, v.co.y * scale.y, v.co.z * scale.z]
            vertices.append(convert_vec3_list(scaled))

        indices = []
        for face in bm.faces:
            if len(face.verts) == 3:
                indices.extend([v.index for v in face.verts])
            else:
                log.warn(f'Object "{obj.name}": non-triangle face')

        num_triangles = len(indices) // 3
        if num_triangles > max_triangles:
            log.warn(f'Object "{obj.name}": {num_triangles} triangles, limiting to {max_triangles}')
            indices = indices[:max_triangles * 3]

        bm.free()
        return {
            "vertices": vertices,
            "indices": indices,
            "num_vertices": len(vertices),
            "num_triangles": len(indices) // 3
        }
    finally:
        obj_eval.to_mesh_clear()
