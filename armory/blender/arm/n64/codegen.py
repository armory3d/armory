"""
N64 Code Generator

Thin emitter that reads n64_traits.json from the macro and fills C templates.
All heavy lifting (button mapping, type resolution, coordinate conversion)
is done by the Haxe macro. This script just fills template placeholders.

Usage:
    As module: from arm.n64 import codegen
    Standalone: python codegen.py <build_dir>
"""

import json
import os
import sys

import arm.utils


def get_template_dir() -> str:
    """Get the path to N64 templates in Deployment."""
    return os.path.join(arm.utils.get_n64_deployment_path(), "src", "data")


def load_template(name: str) -> str:
    """Load a .j2 template from the Deployment directory."""
    path = os.path.join(get_template_dir(), name)
    with open(path, 'r') as f:
        return f.read()


def load_traits_json(build_dir: str = None) -> dict:
    """Load the macro-generated traits JSON."""
    if build_dir is None:
        build_dir = arm.utils.build_dir()

    # Try multiple locations - macro may write to build/ subdirectory
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
    """
    Load and restructure trait info for easy lookup by exporter.

    Returns dict with:
    - traits: {name: trait_data} for easy lookup
    - summary: aggregated info (input_buttons, has_transform, etc.)
    """
    data = load_traits_json(build_dir)

    # Convert traits list to dict for easy lookup
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

def generate_trait_data_structs(traits: list) -> str:
    """Generate struct definitions for {trait_data_structs} placeholder."""
    lines = []
    for trait in traits:
        name = trait["name"]
        members = trait.get("members", {})
        target_scene = trait.get("target_scene")

        lines.append(f"// {name} trait data")
        lines.append(f"typedef struct {{")

        # Add target_scene field if trait uses scene switching
        if target_scene is not None:
            lines.append(f"    SceneId target_scene;")

        # Add member fields (members is now a dict: name -> {type, default_value})
        if members:
            for member_name, member_info in members.items():
                lines.append(f"    {member_info['type']} {member_name};")

        # Empty struct placeholder if no fields
        if not members and target_scene is None:
            lines.append(f"    int _dummy;  // empty struct placeholder")

        lines.append(f"}} {name}Data;")
        lines.append("")

    return "\n".join(lines)


def generate_trait_data_externs(traits: list) -> str:
    """Generate extern declarations for {trait_data_externs} placeholder."""
    lines = []
    for trait in traits:
        name = trait["name"]
        name_lower = name.lower()
        # Each trait has a static instance for its data
        lines.append(f"extern {name}Data {name_lower}_data;")
    return "\n".join(lines)


def generate_trait_declarations(traits: list) -> str:
    """Generate function declarations for {trait_declarations} placeholder.

    Uses void* signatures to match ArmTrait function pointer types in types.h.
    """
    lines = []
    for trait in traits:
        name = trait["name"]
        name_lower = name.lower()

        lines.append(f"// {name}")
        lines.append(f"void {name_lower}_on_ready(void* obj, void* data);")
        lines.append(f"void {name_lower}_on_update(void* obj, float dt, void* data);")
        lines.append(f"void {name_lower}_on_remove(void* obj, void* data);")
        lines.append("")

    return "\n".join(lines)


def generate_trait_data_definitions(traits: list) -> str:
    """Generate static data definitions for {trait_data_definitions} placeholder."""
    lines = []
    for trait in traits:
        name = trait["name"]
        name_lower = name.lower()
        members = trait.get("members", {})
        target_scene = trait.get("target_scene")

        # Build initializer
        init_parts = []
        if target_scene is not None:
            init_parts.append(f".target_scene = {target_scene}")
        if members:
            for member_name, member_info in members.items():
                default = member_info.get("default_value", "0")
                init_parts.append(f".{member_name} = {default}")

        if init_parts:
            init_str = " = {" + ", ".join(init_parts) + "}"
        else:
            init_str = " = {0}"

        lines.append(f"{name}Data {name_lower}_data{init_str};")

    return "\n".join(lines)


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


def generate_trait_implementations(traits: list) -> str:
    """Generate function implementations for {trait_implementations} placeholder.

    Uses void* signatures to match ArmTrait typedefs, with casts at the top.
    """
    lines = []

    for trait in traits:
        name = trait["name"]
        name_lower = name.lower()

        init_code = trait.get("init", [])
        update_code = trait.get("update", [])
        remove_code = trait.get("remove", [])

        lines.append(f"// ============================================")
        lines.append(f"// {name}")
        lines.append(f"// ============================================")
        lines.append("")

        # Init function (on_ready)
        lines.append(f"void {name_lower}_on_ready(void* _obj, void* _data) {{")
        lines.append(f"    ArmObject* obj = (ArmObject*)_obj;")
        lines.append(f"    {name}Data* tdata = ({name}Data*)_data;")
        lines.append(f"    (void)obj; (void)tdata;  // Suppress unused warnings")
        for stmt in init_code:
            if _is_valid_statement(stmt):
                lines.append(f"    {stmt}")
        lines.append("}")
        lines.append("")

        # Update function (on_update)
        lines.append(f"void {name_lower}_on_update(void* _obj, float dt, void* _data) {{")
        lines.append(f"    ArmObject* obj = (ArmObject*)_obj;")
        lines.append(f"    {name}Data* tdata = ({name}Data*)_data;")
        lines.append(f"    (void)obj; (void)tdata; (void)dt;  // Suppress unused warnings")
        for stmt in update_code:
            if _is_valid_statement(stmt):
                lines.append(f"    {stmt}")
        lines.append("}")
        lines.append("")

        # Remove function (on_remove)
        lines.append(f"void {name_lower}_on_remove(void* _obj, void* _data) {{")
        lines.append(f"    ArmObject* obj = (ArmObject*)_obj;")
        lines.append(f"    {name}Data* tdata = ({name}Data*)_data;")
        lines.append(f"    (void)obj; (void)tdata;  // Suppress unused warnings")
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
    """Load traits.h.j2 template and fill placeholders."""
    template = load_template("traits.h.j2")

    return template.format(
        trait_data_structs=generate_trait_data_structs(traits),
        trait_data_externs=generate_trait_data_externs(traits),
        trait_declarations=generate_trait_declarations(traits),
    )


def fill_traits_c_template(traits: list) -> str:
    """Load traits.c.j2 template and fill placeholders."""
    template = load_template("traits.c.j2")

    return template.format(
        trait_data_definitions=generate_trait_data_definitions(traits),
        trait_implementations=generate_trait_implementations(traits),
    )


def write_traits_files(build_dir: str = None):
    """Write all trait C files to build directory by filling templates."""
    if build_dir is None:
        build_dir = arm.utils.build_dir()

    data = load_traits_json(build_dir)
    traits = data.get("traits", [])

    # All trait files go in src/data/ (matching mini engine structure)
    data_dir = os.path.join(build_dir, "n64", "src", "data")
    os.makedirs(data_dir, exist_ok=True)

    # traits.h - filled from template
    h_path = os.path.join(data_dir, "traits.h")
    with open(h_path, 'w') as f:
        f.write(fill_traits_h_template(traits))

    # traits.c - filled from template
    c_path = os.path.join(data_dir, "traits.c")
    with open(c_path, 'w') as f:
        f.write(fill_traits_c_template(traits))


def main():
    if len(sys.argv) < 2:
        print("Usage: python codegen.py <build_dir>")
        sys.exit(1)

    build_dir = sys.argv[1]

    # Load macro output
    data = load_traits_json(build_dir)

    version = data.get("version", 0)
    if version < 4:
        print(f"Warning: Expected JSON version 4, got {version}")

    traits = data.get("traits", [])
    print(f"Generating code for {len(traits)} trait(s)...")

    write_traits_files(build_dir)
    print("Done!")


if __name__ == "__main__":
    main()
