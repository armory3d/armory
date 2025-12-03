"""N64 Utilities - Helper functions for Blender operations and trait data."""

import os
import shutil
from typing import List, Optional

import bpy
import bmesh

import arm.utils
import arm.log as log


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


def convert_vec3_list(vec: List[float]) -> List[float]:
    """Convert a 3-element list from Blender to N64 coordinates."""
    return [vec[0], vec[2], -vec[1]]


def convert_quat_list(quat: List[float]) -> List[float]:
    """Convert quaternion list from Blender to N64 coordinates."""
    return [quat[0], quat[2], -quat[1], quat[3]]


def convert_scale_list(vec: List[float], factor: float = SCALE_FACTOR) -> List[float]:
    """Convert scale list from Blender to N64 coordinates with factor."""
    return [vec[0] * factor, vec[2] * factor, vec[1] * factor]


def topological_sort_objects(objects: List[dict]) -> List[dict]:
    """Sort objects so parents come before children (topological order).

    This ensures that when updating transforms at runtime, parent positions
    are always computed before their children, enabling nested hierarchies.
    """
    # Build name → object mapping
    name_to_obj = {obj['name']: obj for obj in objects}

    # Build adjacency: parent → list of children
    children = {obj['name']: [] for obj in objects}
    roots = []

    for obj in objects:
        parent_name = obj.get('parent')
        if parent_name and parent_name in name_to_obj:
            children[parent_name].append(obj['name'])
        else:
            roots.append(obj['name'])

    # BFS from roots to get topological order
    sorted_names = []
    queue = list(roots)
    while queue:
        name = queue.pop(0)
        sorted_names.append(name)
        for child_name in children[name]:
            queue.append(child_name)

    # Return objects in sorted order
    return [name_to_obj[name] for name in sorted_names]


# =============================================================================
# N64 Build Configuration
# =============================================================================
# Internal config - can be expanded later with Blender UI or project file
N64_CONFIG = {
    'max_physics_bodies': 32,       # Max rigid bodies per scene
    'max_button_subscribers': 16,   # Max traits subscribed to a single button event
}


def get_physics_debug_mode() -> int:
    """Calculate physics debug mode flags from Blender settings.

    Returns a bitmask matching the PhysicsDebugMode enum in physics_debug.h.
    """
    wrd = bpy.data.worlds.get('Arm')
    if wrd is None:
        return 0

    debug_mode = 0
    debug_mode |= 1 if getattr(wrd, 'arm_physics_dbg_draw_wireframe', False) else 0
    debug_mode |= 2 if getattr(wrd, 'arm_physics_dbg_draw_aabb', False) else 0
    debug_mode |= 8 if getattr(wrd, 'arm_physics_dbg_draw_contact_points', False) else 0
    debug_mode |= 2048 if getattr(wrd, 'arm_physics_dbg_draw_constraints', False) else 0
    debug_mode |= 4096 if getattr(wrd, 'arm_physics_dbg_draw_constraint_limits', False) else 0
    debug_mode |= 16384 if getattr(wrd, 'arm_physics_dbg_draw_normals', False) else 0
    debug_mode |= 32768 if getattr(wrd, 'arm_physics_dbg_draw_axis_gizmo', False) else 0
    debug_mode |= 65536 if getattr(wrd, 'arm_physics_dbg_draw_raycast', False) else 0
    return debug_mode

def get_config(key, default=None):
    """Get N64 config value."""
    return N64_CONFIG.get(key, default)


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


# =============================================================================
# Static Object Detection
# =============================================================================

def compute_static_flags(scene_data: dict, trait_info: dict) -> None:
    """Compute is_static for all objects based on physics and trait analysis.

    An object is static if:
    1. It has no rigid body physics (or is a PASSIVE/static body)
    2. None of its traits mutate the transform

    Static objects skip matrix updates after initialization and can be
    batched into a combined display list for better performance.

    Args:
        scene_data: Dict mapping scene names to scene data containing objects
        trait_info: Dict containing trait metadata from the macro JSON
    """
    traits_data = trait_info.get('traits', {})

    def trait_mutates_transform(trait_class: str) -> bool:
        """Check if a trait class mutates the transform."""
        trait_ir = traits_data.get(trait_class, {})
        meta = trait_ir.get('meta', {})
        return meta.get('mutates_transform', False)

    for scene in scene_data.values():
        for obj in scene.get("objects", []):
            # Check if has dynamic physics (non-passive rigid body)
            has_dynamic_physics = False
            rigid_body = obj.get("rigid_body")
            if rigid_body:
                # mass == 0 means static/passive body
                has_dynamic_physics = rigid_body.get("mass", 0.0) > 0.0

            # Check if any trait mutates transform
            any_trait_mutates = False
            for trait in obj.get("traits", []):
                trait_class = trait.get("class_name", "")
                if trait_mutates_transform(trait_class):
                    any_trait_mutates = True
                    break

            # Object is static if no dynamic physics and no mutating traits
            obj["is_static"] = not has_dynamic_physics and not any_trait_mutates


# =============================================================================
# Collision Mesh Extraction
# =============================================================================

def extract_collision_mesh(obj: bpy.types.Object, max_triangles: int = 256) -> Optional[dict]:
    """Extract mesh collision data from a Blender object.

    Returns a dict with 'vertices' and 'indices' lists, or None on failure.
    Vertices are in LOCAL/OBJECT space (not world space) with N64 coordinate system (Y-up).
    The physics system will position the mesh using the object's transform.

    Args:
        obj: Blender mesh object to extract collision data from
        max_triangles: Maximum number of triangles (default 256 for N64 memory constraints)

    Returns:
        Dict with vertices, indices, num_vertices, num_triangles - or None on failure
    """
    if obj.type != 'MESH':
        return None

    # Get evaluated mesh with modifiers applied
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    mesh = obj_eval.to_mesh()

    if mesh is None:
        return None

    try:
        # Convert to BMesh for triangulation
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='FIXED')

        # Get object scale (we apply scale to local coordinates)
        scale = obj.scale

        # Extract vertices in LOCAL space, scaled and converted to N64 coords (Y-up)
        vertices = []
        for v in bm.verts:
            # Apply scale to local coordinates
            local_pos = v.co
            # Convert from Blender Z-up to N64 Y-up: swap Y and Z, apply scale
            vertices.append([
                local_pos.x * scale.x,
                local_pos.z * scale.z,  # Blender Z -> N64 Y
                local_pos.y * scale.y   # Blender Y -> N64 Z
            ])

        # Extract triangle indices
        indices = []
        for face in bm.faces:
            if len(face.verts) == 3:
                indices.extend([v.index for v in face.verts])
            else:
                # Should not happen after triangulation
                log.warn(f'Object "{obj.name}": non-triangle face in collision mesh')

        # Limit triangle count for N64 memory constraints
        num_triangles = len(indices) // 3
        if num_triangles > max_triangles:
            log.warn(f'Object "{obj.name}": collision mesh has {num_triangles} triangles, limiting to {max_triangles}')
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
