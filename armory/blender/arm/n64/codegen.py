"""N64 Code Generator - Reads n64_traits.json from macro and fills C templates."""

import json
import os
import sys

import arm.utils


def get_template_dir() -> str:
    return os.path.join(arm.utils.get_n64_deployment_path(), "src", "data")


def load_template(name: str) -> str:
    path = os.path.join(get_template_dir(), name)
    with open(path, 'r') as f:
        return f.read()


def load_traits_json(build_dir: str = None) -> dict:
    if build_dir is None:
        build_dir = arm.utils.build_dir()

    possible_paths = [
        os.path.join(build_dir, "n64_traits.json"),
        os.path.join(build_dir, "build", "n64_traits.json"),
        os.path.join(build_dir, "debug", "n64_traits.json"),
    ]

    for path in possible_paths:
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)

    return {"version": 0, "traits": [], "summary": {}}


def get_trait_info(build_dir: str = None) -> dict:
    data = load_traits_json(build_dir)

    traits_dict = {}
    for trait in data.get("traits", []):
        traits_dict[trait["name"]] = trait

    return {
        "version": data.get("version", 0),
        "traits": traits_dict,
        "summary": data.get("summary", {})
    }


def _is_valid_statement(stmt: str) -> bool:
    """Check if statement is valid C code."""
    if not stmt or not stmt.strip():
        return False
    # Filter out malformed if statements with empty conditions
    if stmt.strip().startswith("if ()") or stmt.strip().startswith("if ( )"):
        return False
    # Filter out empty blocks
    if stmt.strip() in ["{}", "{ }", ";", ""]:
        return False
    return True


def _should_skip_trait(trait: dict) -> bool:
    """Check if trait should be skipped."""
    return trait.get("skip", False)


def generate_trait_data_structs(traits: list) -> str:
    lines = []
    for trait in traits:
        if _should_skip_trait(trait):
            continue
        if not trait.get("needs_data", False):
            continue

        name = trait["name"]
        members = trait.get("members", {})

        lines.append(f"// {name} trait data")
        lines.append(f"typedef struct {{")

        for member_name, member_info in members.items():
            lines.append(f"    {member_info['type']} {member_name};")

        lines.append(f"}} {name}Data;")
        lines.append("")

    return "\n".join(lines)


def generate_trait_data_externs(traits: list) -> str:
    lines = []
    for trait in traits:
        if _should_skip_trait(trait):
            continue
        if not trait.get("needs_data", False):
            continue
        name = trait["name"]
        name_lower = name.lower()
        lines.append(f"extern {name}Data {name_lower}_data;")
    return "\n".join(lines)


def generate_trait_declarations(traits: list) -> str:
    lines = []
    for trait in traits:
        if _should_skip_trait(trait):
            continue

        name = trait["name"]
        name_lower = name.lower()

        lines.append(f"// {name}")
        lines.append(f"void {name_lower}_on_ready(void* obj, void* data);")
        lines.append(f"void {name_lower}_on_fixed_update(void* obj, float dt, void* data);")
        lines.append(f"void {name_lower}_on_update(void* obj, float dt, void* data);")
        lines.append(f"void {name_lower}_on_remove(void* obj, void* data);")
        lines.append("")

    return "\n".join(lines)


def generate_trait_data_definitions(traits: list) -> str:
    lines = []
    for trait in traits:
        if _should_skip_trait(trait):
            continue
        if not trait.get("needs_data", False):
            continue

        name = trait["name"]
        name_lower = name.lower()
        members = trait.get("members", {})

        # Build initializer
        init_parts = []
        for member_name, member_info in members.items():
            default = member_info.get("default_value", "0")
            init_parts.append(f".{member_name} = {default}")

        init_str = " = {" + ", ".join(init_parts) + "}" if init_parts else " = {0}"
        lines.append(f"{name}Data {name_lower}_data{init_str};")

    return "\n".join(lines)


def generate_trait_implementations(traits: list) -> str:
    lines = []

    for trait in traits:
        if _should_skip_trait(trait):
            continue
        name = trait["name"]
        name_lower = name.lower()

        init_code = trait.get("init", [])
        fixed_update_code = trait.get("fixed_update", [])
        update_code = trait.get("update", [])
        remove_code = trait.get("remove", [])

        lines.append(f"// {name}")
        lines.append("")

        # Init function (on_ready)
        lines.append(f"void {name_lower}_on_ready(void* obj, void* data) {{")
        lines.append(f"    (void)obj; (void)data;")
        for stmt in init_code:
            if _is_valid_statement(stmt):
                lines.append(f"    {stmt}")
        lines.append("}")
        lines.append("")

        # Fixed update function (on_fixed_update)
        lines.append(f"void {name_lower}_on_fixed_update(void* obj, float dt, void* data) {{")
        lines.append(f"    (void)obj; (void)data; (void)dt;")
        for stmt in fixed_update_code:
            if _is_valid_statement(stmt):
                lines.append(f"    {stmt}")
        lines.append("}")
        lines.append("")

        # Update function (on_update)
        lines.append(f"void {name_lower}_on_update(void* obj, float dt, void* data) {{")
        lines.append(f"    (void)obj; (void)data; (void)dt;")
        for stmt in update_code:
            if _is_valid_statement(stmt):
                lines.append(f"    {stmt}")
        lines.append("}")
        lines.append("")

        # Remove function (on_remove)
        lines.append(f"void {name_lower}_on_remove(void* obj, void* data) {{")
        lines.append(f"    (void)obj; (void)data;")
        for stmt in remove_code:
            if _is_valid_statement(stmt):
                lines.append(f"    {stmt}")
        lines.append("}")
        lines.append("")

    return "\n".join(lines)


def fill_traits_h_template(traits: list) -> str:
    template = load_template("traits.h.j2")

    return template.format(
        trait_data_structs=generate_trait_data_structs(traits),
        trait_data_externs=generate_trait_data_externs(traits),
        trait_declarations=generate_trait_declarations(traits)
    )


def fill_traits_c_template(traits: list) -> str:
    template = load_template("traits.c.j2")

    return template.format(
        trait_data_definitions=generate_trait_data_definitions(traits),
        trait_implementations=generate_trait_implementations(traits)
    )


def write_traits_files():
    build_dir = arm.utils.build_dir()

    data = load_traits_json(build_dir)
    traits = data.get("traits", [])
    data_dir = os.path.join(build_dir, "n64", "src", "data")

    h_path = os.path.join(data_dir, "traits.h")
    with open(h_path, 'w') as f:
        f.write(fill_traits_h_template(traits))

    c_path = os.path.join(data_dir, "traits.c")
    with open(c_path, 'w') as f:
        f.write(fill_traits_c_template(traits))


def generate_transform_block(prefix: str, pos: list, rot: list = None, scale: list = None) -> list:
    """Generate C code for transform initialization."""
    lines = []
    lines.append(f'    {prefix}.transform.loc[0] = {pos[0]:.6f}f;')
    lines.append(f'    {prefix}.transform.loc[1] = {pos[1]:.6f}f;')
    lines.append(f'    {prefix}.transform.loc[2] = {pos[2]:.6f}f;')
    if rot is not None:
        # Quaternion: [x, y, z, w]
        lines.append(f'    {prefix}.transform.rot[0] = {rot[0]:.6f}f;')
        lines.append(f'    {prefix}.transform.rot[1] = {rot[1]:.6f}f;')
        lines.append(f'    {prefix}.transform.rot[2] = {rot[2]:.6f}f;')
        lines.append(f'    {prefix}.transform.rot[3] = {rot[3]:.6f}f;')
    if scale is not None:
        lines.append(f'    {prefix}.transform.scale[0] = {scale[0]:.6f}f;')
        lines.append(f'    {prefix}.transform.scale[1] = {scale[1]:.6f}f;')
        lines.append(f'    {prefix}.transform.scale[2] = {scale[2]:.6f}f;')
        lines.append(f'    {prefix}.transform.dirty = FB_COUNT;')
    return lines


def generate_trait_block(prefix: str, traits: list, trait_info: dict, scene_name: str) -> list:
    """Generate C code for trait initialization."""
    from arm.n64 import utils as n64_utils

    lines = []
    lines.append(f'    {prefix}.trait_count = {len(traits)};')
    if len(traits) > 0:
        lines.append(f'    {prefix}.traits = malloc(sizeof(ArmTrait) * {len(traits)});')
        for t_idx, trait in enumerate(traits):
            trait_class = trait["class_name"]
            trait_func_name = arm.utils.safesrc(trait_class).lower()
            lines.append(f'    {prefix}.traits[{t_idx}].on_ready = {trait_func_name}_on_ready;')
            lines.append(f'    {prefix}.traits[{t_idx}].on_fixed_update = {trait_func_name}_on_fixed_update;')
            lines.append(f'    {prefix}.traits[{t_idx}].on_update = {trait_func_name}_on_update;')
            lines.append(f'    {prefix}.traits[{t_idx}].on_remove = {trait_func_name}_on_remove;')

            if n64_utils.trait_needs_data(trait_info, trait_class):
                struct_name = f'{trait_class}Data'
                instance_props = trait.get("props", {})
                initializer = n64_utils.build_trait_initializer(trait_info, trait_class, scene_name, instance_props)
                lines.append(f'    {prefix}.traits[{t_idx}].data = malloc(sizeof({struct_name}));')
                lines.append(f'    *({struct_name}*){prefix}.traits[{t_idx}].data = ({struct_name}){{{initializer}}};')
            else:
                lines.append(f'    {prefix}.traits[{t_idx}].data = NULL;')
    else:
        lines.append(f'    {prefix}.traits = NULL;')
    return lines


def _fmt_vec3(v: list) -> str:
    """Format a 3-element list as T3DVec3 initializer."""
    return f'(T3DVec3){{{{ {v[0]:.6f}f, {v[1]:.6f}f, {v[2]:.6f}f }}}}'


def generate_camera_block(cameras: list, trait_info: dict, scene_name: str) -> str:
    """Generate C code for all cameras in a scene."""
    from arm.n64 import utils as n64_utils

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


def generate_light_block(lights: list, trait_info: dict, scene_name: str) -> str:
    """Generate C code for all lights in a scene."""
    from arm.n64 import utils as n64_utils

    lines = []
    for i, light in enumerate(lights):
        prefix = f'lights[{i}]'
        lines.append(f'    {prefix}.color[0] = {n64_utils.to_uint8(light["color"][0])};')
        lines.append(f'    {prefix}.color[1] = {n64_utils.to_uint8(light["color"][1])};')
        lines.append(f'    {prefix}.color[2] = {n64_utils.to_uint8(light["color"][2])};')
        lines.append(f'    {prefix}.dir = {_fmt_vec3(light["dir"])};')
        lines.extend(generate_trait_block(prefix, light.get("traits", []), trait_info, scene_name))
    return '\n'.join(lines)


def generate_object_block(objects: list, trait_info: dict, scene_name: str) -> str:
    """Generate C code for all objects in a scene."""
    lines = []
    for i, obj in enumerate(objects):
        prefix = f'objects[{i}]'
        lines.extend(generate_transform_block(prefix, obj["pos"], obj["rot"], obj["scale"]))
        lines.append(f'    models_get({obj["mesh"]});')
        lines.append(f'    {prefix}.dpl = models_get_dpl({obj["mesh"]});')
        lines.append(f'    {prefix}.model_mat = malloc_uncached(sizeof(T3DMat4FP) * FB_COUNT);')
        lines.append(f'    {prefix}.visible = {str(obj["visible"]).lower()};')
        bc = obj.get("bounds_center", [0, 0, 0])
        br = obj.get("bounds_radius", 1.0)
        lines.append(f'    {prefix}.bounds_center = {_fmt_vec3(bc)};')
        lines.append(f'    {prefix}.bounds_radius = {br:.6f}f;')
        lines.append(f'    {prefix}.rigid_body = NULL;')  # Initialize to NULL, physics block will set if needed
        lines.extend(generate_trait_block(prefix, obj.get("traits", []), trait_info, scene_name))
    return '\n'.join(lines)


def generate_physics_block(objects: list, world_data: dict) -> str:
    """Generate C code for physics initialization (inside #if ENGINE_ENABLE_PHYSICS)."""
    lines = []

    # Set gravity from world data (convert Blender Z-up to N64 Y-up)
    # Blender (X, Y, Z) -> N64 (X, Z, -Y)
    gravity = world_data.get("gravity", [0, 0, -9.81])
    gx, gy, gz = gravity[0], gravity[1], gravity[2]
    n64_gx, n64_gy, n64_gz = gx, gz, -gy  # Convert to N64 Y-up
    lines.append(f'    physics_set_gravity({n64_gx:.6f}f, {n64_gy:.6f}f, {n64_gz:.6f}f);')
    lines.append('')

    # Create rigid bodies for objects that have physics
    for i, obj in enumerate(objects):
        rb = obj.get("rigid_body")
        if rb is None:
            continue

        obj_name = obj.get("name", f"object_{i}")
        shape = rb.get("shape", "box")
        mass = rb.get("mass", 0.0)
        friction = rb.get("friction", 0.5)
        restitution = rb.get("restitution", 0.0)
        col_group = rb.get("collision_group", 1)
        col_mask = rb.get("collision_mask", 1)
        is_trigger = rb.get("is_trigger", False)
        is_kinematic = rb.get("is_kinematic", False)

        # Determine body type
        if mass == 0.0:
            body_type = "OIMO_BODY_STATIC"
        elif is_kinematic:
            body_type = "OIMO_BODY_KINEMATIC"
        else:
            body_type = "OIMO_BODY_DYNAMIC"

        lines.append(f'    // Physics body for {obj_name}')
        lines.append('    {')

        # Create rigid body config
        lines.append(f'        OimoRigidBodyConfig rb_config = oimo_rigidbody_config_default();')
        lines.append(f'        rb_config.type = {body_type};')

        # Set initial position from object transform
        lines.append(f'        rb_config.position = oimo_vec3(objects[{i}].transform.loc[0], objects[{i}].transform.loc[1], objects[{i}].transform.loc[2]);')

        # Set initial rotation from object transform (quaternion XYZW)
        lines.append(f'        OimoQuat init_rot = oimo_quat(objects[{i}].transform.rot[0], objects[{i}].transform.rot[1], objects[{i}].transform.rot[2], objects[{i}].transform.rot[3]);')
        lines.append(f'        rb_config.rotation = oimo_quat_to_mat3(&init_rot);')

        # Create shape config based on type
        lines.append(f'        OimoShapeConfig shape_config = oimo_shape_config_default();')
        lines.append(f'        shape_config.collision_group = {col_group};')
        lines.append(f'        shape_config.collision_mask = {col_mask};')

        if shape == "sphere":
            radius = rb.get("radius", 1.0)
            lines.append(f'        shape_config.geometry = oimo_geometry_sphere({radius:.6f}f);')
        elif shape == "capsule":
            radius = rb.get("radius", 0.5)
            half_height = rb.get("half_height", 0.5)
            lines.append(f'        shape_config.geometry = oimo_geometry_capsule({radius:.6f}f, {half_height:.6f}f);')
        else:  # box
            he = rb.get("half_extents", [1, 1, 1])
            lines.append(f'        shape_config.geometry = oimo_geometry_box({he[0]:.6f}f, {he[1]:.6f}f, {he[2]:.6f}f);')

        # Allocate and init rigid body
        lines.append(f'        OimoRigidBody* body = (OimoRigidBody*)malloc(sizeof(OimoRigidBody));')
        lines.append(f'        oimo_rigidbody_init(body, &rb_config);')

        # Allocate and init shape
        lines.append(f'        OimoShape* shape = (OimoShape*)malloc(sizeof(OimoShape));')
        lines.append(f'        oimo_shape_init(shape, &shape_config);')
        lines.append(f'        oimo_rigidbody_add_shape(body, shape);')

        # Set mass if specified (for dynamic bodies)
        if body_type == "OIMO_BODY_DYNAMIC" and mass > 0:
            lines.append(f'        // Set explicit mass from Blender')
            lines.append(f'        body->mass = {mass:.6f}f;')
            lines.append(f'        oimo_rigidbody_update_mass(body);')

        # Add to world and link to object
        lines.append('        oimo_world_add_rigidbody(physics_get_world(), body);')
        lines.append(f'        objects[{i}].rigid_body = body;')
        lines.append('    }')
        lines.append('')

    return '\n'.join(lines)


def generate_scene_traits_block(traits: list, trait_info: dict, scene_name: str) -> str:
    """Generate C code for scene-level traits."""
    lines = generate_trait_block('(*scene)', traits, trait_info, scene_name)
    return '\n'.join(lines)
