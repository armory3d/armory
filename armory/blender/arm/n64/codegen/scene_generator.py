"""
Scene Generator - Generates C code blocks for scene data.

This module contains functions for generating scene headers from exported
scene data (cameras, lights, objects, physics).
"""

import math
from typing import Dict, List

from arm import log
from arm.n64 import utils as n64_utils
from arm.n64.utils import convert_vec3_list, convert_quat_list, convert_scale_list, SCALE_FACTOR


# =============================================================================
# Scene Data Conversion
# =============================================================================

def convert_scene_data(scene_data: dict) -> dict:
    """Apply coordinate conversion to all scene data (modifies in place).

    Converts from Blender coordinates (X=right, Y=forward, Z=up)
    to N64/T3D coordinates (X=right, Y=up, Z=back).
    """
    for scene_name, scene in scene_data.items():
        # Convert cameras
        for cam in scene.get('cameras', []):
            cam['pos'] = convert_vec3_list(cam['pos'])
            cam['target'] = convert_vec3_list(cam['target'])

        # Convert lights
        for light in scene.get('lights', []):
            light['dir'] = convert_vec3_list(light['dir'])
            # Normalize direction
            d = light['dir']
            length = math.sqrt(d[0]**2 + d[1]**2 + d[2]**2)
            if length > 0:
                light['dir'] = [d[0]/length, d[1]/length, d[2]/length]

        # Convert objects
        for obj in scene.get('objects', []):
            obj['pos'] = convert_vec3_list(obj['pos'])
            obj['rot'] = convert_quat_list(obj['rot'])
            obj['scale'] = convert_scale_list(obj['scale'])
            if 'bounds_center' in obj:
                obj['bounds_center'] = convert_vec3_list(obj['bounds_center'])
                obj['bounds_radius'] = obj['bounds_radius'] * SCALE_FACTOR

    return scene_data


# =============================================================================
# Scene Code Generation
# =============================================================================

def _fmt_vec3(v: List[float]) -> str:
    """Format a 3-element list as T3DVec3 initializer."""
    return f'(T3DVec3){{{{ {v[0]:.6f}f, {v[1]:.6f}f, {v[2]:.6f}f }}}}'


def generate_transform_block(prefix: str, pos: List[float],
                             rot: List[float] = None,
                             scale: List[float] = None,
                             is_static: bool = False) -> List[str]:
    """Generate C code for transform initialization."""
    lines = []
    lines.append(f'    {prefix}.transform.loc = (T3DVec3){{{{{pos[0]:.6f}f, {pos[1]:.6f}f, {pos[2]:.6f}f}}}};')

    if rot:
        lines.append(f'    {prefix}.transform.rot = (T3DQuat){{{{{rot[0]:.6f}f, {rot[1]:.6f}f, {rot[2]:.6f}f, {rot[3]:.6f}f}}}};')

    if scale:
        lines.append(f'    {prefix}.transform.scale = (T3DVec3){{{{{scale[0]:.6f}f, {scale[1]:.6f}f, {scale[2]:.6f}f}}}};')
        dirty_count = "1" if is_static else "FB_COUNT"
        lines.append(f'    {prefix}.transform.dirty = {dirty_count};')

    return lines


def generate_trait_block(prefix: str, traits: List[Dict],
                         trait_info: dict, scene_name: str) -> List[str]:
    """Generate C code for trait initialization on an object.

    Pure 1:1 emitter - all data comes from macro-generated trait_info.
    """
    lines = []
    lines.append(f'    {prefix}.trait_count = {len(traits)};')
    lines.append(f'    {prefix}.lifecycle_flags = 0;')

    if len(traits) > 0:
        lines.append(f'    {prefix}.traits = malloc(sizeof(ArmTrait) * {len(traits)});')

        for t_idx, trait in enumerate(traits):
            trait_class = trait["class_name"]

            # Get trait IR - must exist, macro provides all data
            trait_ir = n64_utils.get_trait(trait_info, trait_class)
            c_name = trait_ir.get("c_name", "")
            meta = trait_ir.get("meta", {})

            if not c_name:
                log.warn(f"No c_name found for trait '{trait_class}'")

            # Lifecycle hooks - use the full c_name
            lines.append(f'    {prefix}.traits[{t_idx}].on_add = {c_name}_on_add;')
            lines.append(f'    {prefix}.traits[{t_idx}].on_ready = {c_name}_on_ready;')
            lines.append(f'    {prefix}.traits[{t_idx}].on_fixed_update = {c_name}_on_fixed_update;')
            lines.append(f'    {prefix}.traits[{t_idx}].on_update = {c_name}_on_update;')
            lines.append(f'    {prefix}.traits[{t_idx}].on_late_update = {c_name}_on_late_update;')
            lines.append(f'    {prefix}.traits[{t_idx}].on_remove = {c_name}_on_remove;')
            lines.append(f'    {prefix}.traits[{t_idx}].on_render2d = {c_name}_on_render2d;')

            # Trait data
            if n64_utils.trait_needs_data(trait_info, trait_class):
                struct_name = f'{c_name}Data'
                instance_props = trait.get("props", {})
                type_overrides = trait.get("type_overrides", {})
                # Pass entity pointer for .object field initialization
                entity_ptr = f'&{prefix}' if not prefix.startswith('&') else prefix
                initializer = n64_utils.build_trait_initializer(
                    trait_info, trait_class, scene_name, instance_props, type_overrides, entity_ptr
                )
                lines.append(f'    {prefix}.traits[{t_idx}].data = malloc(sizeof({struct_name}));')
                lines.append(f'    *({struct_name}*){prefix}.traits[{t_idx}].data = ({struct_name}){{{initializer}}};')
            else:
                lines.append(f'    {prefix}.traits[{t_idx}].data = NULL;')

            # Subscribe to button events using structured metadata from macro
            for btn_evt in meta.get("button_events", []):
                event_name = btn_evt.get("event_name", "")
                c_button = btn_evt.get("c_button", "N64_BTN_A")
                event_type = btn_evt.get("event_type", "started")

                handler_name = f"{c_name}_{event_name}"
                obj_ptr = f"&{prefix}" if not prefix.startswith("&") else prefix
                data_ptr = f"{prefix}.traits[{t_idx}].data"

                lines.append(f'    trait_events_subscribe_{event_type}({c_button}, {handler_name}, {obj_ptr}, {data_ptr});')

            # Note: Contact event subscriptions are generated separately in generate_contact_subscriptions_block
            # after physics bodies are created
    else:
        lines.append(f'    {prefix}.traits = NULL;')

    return lines


def generate_camera_block(cameras: List[Dict], trait_info: dict, scene_name: str) -> str:
    """Generate C code for all cameras in a scene."""
    lines = []
    for i, cam in enumerate(cameras):
        prefix = f'cameras[{i}]'
        lines.extend(generate_transform_block(prefix, cam["pos"]))
        lines.append(f'    {prefix}.target = {_fmt_vec3(cam["target"])};')
        lines.append(f'    {prefix}.fov = {cam["fov"]:.6f}f;')
        lines.append(f'    {prefix}.near = {cam["near"]:.6f}f;')
        lines.append(f'    {prefix}.far = {cam["far"]:.6f}f;')

        lines.extend(generate_trait_block(prefix, cam.get("traits", []), trait_info, scene_name))
    return '\n'.join(lines)


def generate_light_block(lights: List[Dict], trait_info: dict, scene_name: str) -> str:
    """Generate C code for all lights in a scene."""
    lines = []
    for i, light in enumerate(lights):
        prefix = f'lights[{i}]'
        lines.append(f'    {prefix}.color[0] = {n64_utils.to_uint8(light["color"][0])};')
        lines.append(f'    {prefix}.color[1] = {n64_utils.to_uint8(light["color"][1])};')
        lines.append(f'    {prefix}.color[2] = {n64_utils.to_uint8(light["color"][2])};')
        lines.append(f'    {prefix}.dir = {_fmt_vec3(light["dir"])};')

        lines.extend(generate_trait_block(prefix, light.get("traits", []), trait_info, scene_name))
    return '\n'.join(lines)


def generate_object_block(objects: List[Dict], trait_info: dict, scene_name: str) -> str:
    """Generate C code for all objects in a scene."""
    lines = []

    for i, obj in enumerate(objects):
        prefix = f'objects[{i}]'
        is_static = obj.get("is_static", False)
        lines.extend(generate_transform_block(prefix, obj["pos"], obj["rot"], obj["scale"], is_static))
        lines.append(f'    models_get({obj["mesh"]});')
        lines.append(f'    {prefix}.dpl = models_get_dpl({obj["mesh"]});')
        mat_count = "1" if is_static else "FB_COUNT"
        lines.append(f'    {prefix}.model_mat = malloc_uncached(sizeof(T3DMat4FP) * {mat_count});')
        lines.append(f'    {prefix}.visible = {str(obj["visible"]).lower()};')
        lines.append(f'    {prefix}.is_static = {str(is_static).lower()};')
        lines.append(f'    {prefix}.is_removed = false;')

        bc = obj.get("bounds_center", [0, 0, 0])
        br = obj.get("bounds_radius", 1.0)
        pos = obj["pos"]
        scale = obj["scale"]
        lines.append(f'    {prefix}.bounds_center = {_fmt_vec3(bc)};')
        lines.append(f'    {prefix}.bounds_radius = {br:.6f}f;')

        # Initialize cached world bounds (will be updated when transform.dirty > 0)
        world_center = [pos[0] + bc[0], pos[1] + bc[1], pos[2] + bc[2]]
        max_scale = max(scale[0], scale[1], scale[2])
        world_radius = br * max_scale
        lines.append(f'    {prefix}.cached_world_center = {_fmt_vec3(world_center)};')
        lines.append(f'    {prefix}.cached_world_radius = {world_radius:.6f}f;')

        lines.append(f'    {prefix}.rigid_body = NULL;')

        lines.extend(generate_trait_block(prefix, obj.get("traits", []), trait_info, scene_name))
    return '\n'.join(lines)


def generate_physics_block(objects: List[Dict], world_data: dict) -> str:
    """Generate C code for physics initialization."""
    lines = []

    gravity = world_data.get("gravity", [0, 0, -9.81])
    n64_gravity = convert_vec3_list(gravity)
    lines.append(f'    physics_set_gravity({n64_gravity[0]:.6f}f, {n64_gravity[1]:.6f}f, {n64_gravity[2]:.6f}f);')
    lines.append('')

    # Physics debug drawing (from Blender's Debug Drawing panel)
    debug_mode = world_data.get("physics_debug_mode", 0)
    if debug_mode != 0:
        lines.append(f'    // Physics debug drawing (from Blender Debug Drawing panel)')
        lines.append(f'    physics_debug_init();')
        lines.append(f'    physics_debug_set_mode({debug_mode});')
        lines.append(f'    physics_debug_enable(true);')
        lines.append('')

    for i, obj in enumerate(objects):
        rb = obj.get("rigid_body")
        if rb is None:
            continue

        prefix = f'objects[{i}]'
        obj_name = obj.get("name", f"object_{i}")

        # Extract all physics parameters
        mass = rb.get("mass", 1.0)
        friction = rb.get("friction", 0.5)
        restitution = rb.get("restitution", 0.0)
        linear_damping = rb.get("linear_damping", 0.04)
        angular_damping = rb.get("angular_damping", 0.1)
        is_trigger = rb.get("is_trigger", False)
        use_deactivation = rb.get("use_deactivation", True)
        col_group = rb.get("collision_group", 1)
        col_mask = rb.get("collision_mask", 1)

        # Blender rigid body properties
        blender_type = rb.get("rb_type", "ACTIVE")  # 'PASSIVE' or 'ACTIVE'
        is_animated = rb.get("is_animated", False)   # Animated checkbox
        is_dynamic = rb.get("is_dynamic", True)      # Dynamic checkbox

        # Determine Oimo rigid body type:
        # Passive -> Static
        # Passive + Animated -> Kinematic
        # Active -> Kinematic
        # Active + Animated -> Kinematic
        # Active + Animated + Dynamic -> Kinematic
        # Active + Dynamic -> Dynamic
        if blender_type == "PASSIVE":
            if is_animated:
                rb_type = "OIMO_RIGID_BODY_KINEMATIC"
            else:
                rb_type = "OIMO_RIGID_BODY_STATIC"
        else:  # ACTIVE
            if is_dynamic and not is_animated:
                rb_type = "OIMO_RIGID_BODY_DYNAMIC"
            else:
                rb_type = "OIMO_RIGID_BODY_KINEMATIC"

        shape = rb.get("shape", "box")

        lines.append(f'    // Rigid body for {obj_name}')
        lines.append('    {')
        lines.append(f'        PhysicsBodyParams params = physics_body_params_default();')
        lines.append(f'        params.mass = {mass:.6f}f;')
        lines.append(f'        params.friction = {friction:.6f}f;')
        lines.append(f'        params.restitution = {restitution:.6f}f;')
        lines.append(f'        params.linear_damping = {linear_damping:.6f}f;')
        lines.append(f'        params.angular_damping = {angular_damping:.6f}f;')
        lines.append(f'        params.collision_group = {col_group};')
        lines.append(f'        params.collision_mask = {col_mask};')
        lines.append(f'        params.animated = {"true" if is_animated else "false"};')
        lines.append(f'        params.trigger = {"true" if is_trigger else "false"};')
        lines.append(f'        params.use_deactivation = {"true" if use_deactivation else "false"};')

        if shape == "box":
            half_extents = rb.get("half_extents", [0.5, 0.5, 0.5])
            hx, hy, hz = half_extents[0], half_extents[1], half_extents[2]
            lines.append(f'        physics_create_box_full(&{prefix}, {rb_type}, {hx:.6f}f, {hy:.6f}f, {hz:.6f}f, &params);')
        elif shape == "sphere":
            r = rb.get("radius", 0.5)
            lines.append(f'        physics_create_sphere_full(&{prefix}, {rb_type}, {r:.6f}f, &params);')
        elif shape == "capsule":
            r = rb.get("radius", 0.5)
            hh = rb.get("half_height", 0.5)
            lines.append(f'        physics_create_capsule_full(&{prefix}, {rb_type}, {r:.6f}f, {hh:.6f}f, &params);')
        elif shape == "mesh":
            mesh_data = rb.get("mesh_data", {})
            vertices = mesh_data.get("vertices", [])
            indices = mesh_data.get("indices", [])
            num_vertices = mesh_data.get("num_vertices", len(vertices))
            index_count = len(indices)

            if vertices and indices:
                # Generate static arrays using OimoVec3 for vertices
                lines.append(f'        static OimoVec3 {obj_name}_col_verts[] = {{')
                for v_idx, v in enumerate(vertices):
                    comma = ',' if v_idx < len(vertices) - 1 else ''
                    lines.append(f'            {{{v[0]:.6f}f, {v[1]:.6f}f, {v[2]:.6f}f}}{comma}')
                lines.append('        };')
                lines.append(f'        static int16_t {obj_name}_col_indices[] = {{')
                for t_idx in range(0, len(indices), 6):
                    end_idx = min(t_idx + 6, len(indices))
                    idx_str = ', '.join(str(indices[j]) for j in range(t_idx, end_idx))
                    comma = ',' if end_idx < len(indices) else ''
                    lines.append(f'            {idx_str}{comma}')
                lines.append('        };')
                lines.append(f'        physics_create_mesh_full(&{prefix}, {obj_name}_col_verts, {obj_name}_col_indices, {num_vertices}, {index_count}, &params);')
            else:
                # Fallback to box if mesh data is missing
                lines.append(f'        physics_create_box_full(&{prefix}, {rb_type}, 0.5f, 0.5f, 0.5f, &params);')
        else:
            # Default to box
            lines.append(f'        physics_create_box_full(&{prefix}, {rb_type}, 0.5f, 0.5f, 0.5f, &params);')

        lines.append('    }')
        lines.append('')

    return '\n'.join(lines)


def generate_contact_subscriptions_block(objects: List[Dict], trait_info: dict) -> str:
    """Generate physics contact subscription calls after physics bodies exist.

    This must be called AFTER physics bodies are created, so the rigid_body
    pointers are valid when subscribing.

    Pure 1:1 emitter - handler_name comes directly from macro's contact_events.
    """
    lines = []
    has_subscriptions = False

    for i, obj in enumerate(objects):
        traits = obj.get("traits", [])
        prefix = f'objects[{i}]'

        for t_idx, trait in enumerate(traits):
            trait_class = trait["class_name"]
            trait_ir = n64_utils.get_trait(trait_info, trait_class)
            meta = trait_ir.get("meta", {})

            for contact_evt in meta.get("contact_events", []):
                handler_name = contact_evt.get("handler_name", "")
                is_subscribe = contact_evt.get("subscribe", True)

                if is_subscribe and handler_name:
                    if not has_subscriptions:
                        lines.append('    // Physics contact event subscriptions')
                        has_subscriptions = True

                    obj_ptr = f"&{prefix}" if not prefix.startswith("&") else prefix
                    data_ptr = f"{prefix}.traits[{t_idx}].data"
                    lines.append(f'    physics_contact_subscribe({prefix}.rigid_body, {handler_name}, {obj_ptr}, {data_ptr});')

    if not has_subscriptions:
        return ""

    return '\n'.join(lines)


def generate_scene_traits_block(traits: List[Dict], trait_info: dict, scene_name: str) -> str:
    """Generate C code for scene-level traits.

    Pure 1:1 emitter - all data comes from macro-generated trait_info.
    """
    if not traits:
        return "    // No scene-level traits"

    lines = []
    lines.append(f'    static ArmTrait scene_traits[{len(traits)}];')

    for i, trait in enumerate(traits):
        trait_class = trait["class_name"]

        # Get trait IR - must exist, macro provides all data
        trait_ir = n64_utils.get_trait(trait_info, trait_class)
        c_name = trait_ir.get("c_name", "")
        meta = trait_ir.get("meta", {})

        lines.append(f'    scene_traits[{i}].on_add = {c_name}_on_add;')
        lines.append(f'    scene_traits[{i}].on_ready = {c_name}_on_ready;')
        lines.append(f'    scene_traits[{i}].on_fixed_update = {c_name}_on_fixed_update;')
        lines.append(f'    scene_traits[{i}].on_update = {c_name}_on_update;')
        lines.append(f'    scene_traits[{i}].on_late_update = {c_name}_on_late_update;')
        lines.append(f'    scene_traits[{i}].on_remove = {c_name}_on_remove;')
        lines.append(f'    scene_traits[{i}].on_render2d = {c_name}_on_render2d;')

        if n64_utils.trait_needs_data(trait_info, trait_class):
            struct_name = f'{c_name}Data'
            instance_props = trait.get("props", {})
            type_overrides = trait.get("type_overrides", {})
            initializer = n64_utils.build_trait_initializer(
                trait_info, trait_class, scene_name, instance_props, type_overrides
            )
            lines.append(f'    scene_traits[{i}].data = malloc(sizeof({struct_name}));')
            lines.append(f'    *({struct_name}*)scene_traits[{i}].data = ({struct_name}){{{initializer}}};')
        else:
            lines.append(f'    scene_traits[{i}].data = NULL;')

        # Subscribe to button events using structured metadata from macro
        for btn_evt in meta.get("button_events", []):
            event_name = btn_evt.get("event_name", "")
            c_button = btn_evt.get("c_button", "N64_BTN_A")
            event_type = btn_evt.get("event_type", "started")

            handler_name = f"{c_name}_{event_name}"
            lines.append(f'    trait_events_subscribe_{event_type}({c_button}, {handler_name}, scene, scene_traits[{i}].data);')

    lines.append(f'    scene->traits = scene_traits;')
    return '\n'.join(lines)
