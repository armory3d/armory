"""
N64 Code Generator

Thin emitter that reads n64_traits.json from the macro and fills C templates.
All heavy lifting (button mapping, type resolution, coordinate conversion)
is done by the Haxe macro. This script just fills template placeholders.
"""

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


# ============================================
# Template placeholder generators
# ============================================

def _is_valid_statement(stmt: str) -> bool:
    """Check if a statement is valid C code (not empty or malformed)."""
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
    """Check if trait should be skipped (determined by macro)."""
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


# ============================================
# Template filling and file writing
# ============================================

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


# ============================================
# Scene initialization code generators
# ============================================

def generate_transform_block(prefix: str, pos: list, rot: list = None, scale: list = None) -> list:
    """Generate C code lines for transform initialization."""
    lines = []
    lines.append(f'    {prefix}.transform.loc[0] = {pos[0]:.6f}f;')
    lines.append(f'    {prefix}.transform.loc[1] = {pos[1]:.6f}f;')
    lines.append(f'    {prefix}.transform.loc[2] = {pos[2]:.6f}f;')
    if rot is not None:
        lines.append(f'    {prefix}.transform.rot[0] = {rot[0]:.6f}f;')
        lines.append(f'    {prefix}.transform.rot[1] = {rot[1]:.6f}f;')
        lines.append(f'    {prefix}.transform.rot[2] = {rot[2]:.6f}f;')
    if scale is not None:
        lines.append(f'    {prefix}.transform.scale[0] = {scale[0]:.6f}f;')
        lines.append(f'    {prefix}.transform.scale[1] = {scale[1]:.6f}f;')
        lines.append(f'    {prefix}.transform.scale[2] = {scale[2]:.6f}f;')
        lines.append(f'    {prefix}.transform.dirty = FB_COUNT;')
    return lines


def generate_trait_block(prefix: str, traits: list, trait_info: dict, scene_name: str) -> list:
    """Generate C code lines for trait initialization."""
    from arm.n64 import utils as n64_utils

    lines = []
    lines.append(f'    {prefix}.trait_count = {len(traits)};')
    if len(traits) > 0:
        lines.append(f'    {prefix}.traits = malloc(sizeof(ArmTrait) * {len(traits)});')
        for t_idx, trait in enumerate(traits):
            trait_class = trait["class_name"]
            trait_func_name = arm.utils.safesrc(trait_class).lower()
            lines.append(f'    {prefix}.traits[{t_idx}].on_ready = {trait_func_name}_on_ready;')
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
