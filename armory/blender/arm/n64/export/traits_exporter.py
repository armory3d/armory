"""
Traits Exporter - Handles trait and autoload code generation for N64.

This module provides functions for generating traits.c/h and autoload
C files from Haxe IR data.
"""

import os

import arm.utils
import arm.n64.codegen as codegen


def write_types(exporter):
    """Generate types.h from template with debug HUD settings."""
    import bpy  # Import here to avoid circular imports at module level
    import arm.n64.utils as n64_utils

    tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'types.h.j2')
    out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'types.h')

    with open(tmpl_path, 'r', encoding='utf-8') as f:
        tmpl_content = f.read()

    wrd = bpy.data.worlds.get('Arm')
    debug_hud_define = '\n#define ARM_DEBUG_HUD' if wrd and wrd.arm_debug_console else ''
    output = tmpl_content.format(debug_hud_define=debug_hud_define)

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(output)


def write_traits(exporter):
    """Generate traits.h and traits.c files.

    Args:
        exporter: N64Exporter instance with scene_data for type overrides

    Returns:
        dict with 'has_ui' and 'has_physics' feature flags
    """
    # Collect all type overrides from all trait instances across all scenes
    type_overrides = _collect_type_overrides(exporter)

    # Get template data from codegen
    template_data, features = codegen.prepare_traits_template_data(type_overrides)

    # Write files
    if template_data is None:
        # No traits - create empty stubs
        _write_traits_h_empty()
        _write_traits_c_empty()
    else:
        _write_traits_h(template_data)
        _write_traits_c(template_data)

    return features or {}


def _write_traits_h(template_data: dict):
    """Generate traits.h from template."""
    tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'data', 'traits.h.j2')
    out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'data', 'traits.h')

    with open(tmpl_path, 'r', encoding='utf-8') as f:
        template = f.read()

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(template.format(**template_data))


def _write_traits_c(template_data: dict):
    """Generate traits.c from template."""
    tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'data', 'traits.c.j2')
    out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'data', 'traits.c')

    with open(tmpl_path, 'r', encoding='utf-8') as f:
        template = f.read()

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(template.format(**template_data))


def _write_traits_h_empty():
    """Generate empty traits.h stub."""
    out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'data', 'traits.h')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("// Auto-generated empty traits header\n#ifndef _TRAITS_H_\n#define _TRAITS_H_\n#endif\n")


def _write_traits_c_empty():
    """Generate empty traits.c stub."""
    out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'data', 'traits.c')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("// Auto-generated empty traits implementation\n#include \"traits.h\"\n")


def _collect_type_overrides(exporter) -> dict:
    """Collect all type overrides from trait instances across all scenes.

    Args:
        exporter: N64Exporter instance with scene_data

    Returns:
        dict mapping trait_class -> member_name -> c_type
    """
    overrides = {}

    def collect_from_traits(traits):
        for trait in traits:
            class_name = trait.get("class_name", "")
            trait_overrides = trait.get("type_overrides", {})
            if trait_overrides:
                if class_name not in overrides:
                    overrides[class_name] = {}
                overrides[class_name].update(trait_overrides)

    for scene_data in exporter.scene_data.values():
        # Scene-level traits
        collect_from_traits(scene_data.get("traits", []))
        # Camera traits
        for cam in scene_data.get("cameras", []):
            collect_from_traits(cam.get("traits", []))
        # Light traits
        for light in scene_data.get("lights", []):
            collect_from_traits(light.get("traits", []))
        # Object traits
        for obj in scene_data.get("objects", []):
            collect_from_traits(obj.get("traits", []))

    return overrides


def write_autoloads(exporter):
    """Generate autoload C files from IR JSON.

    Autoloads are singleton classes marked with @:n64Autoload.
    They become globally accessible C modules.

    Args:
        exporter: N64Exporter instance to update with autoload info

    Returns:
        dict with 'has_audio' feature flag and autoload_info
    """
    # Get template data from codegen
    autoload_data, master_data, features = codegen.prepare_autoload_template_data()

    if not autoload_data:
        exporter.autoload_info = {'autoloads': [], 'has_autoloads': False}
        return {'has_audio': False}

    autoloads_dir = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'autoloads')
    os.makedirs(autoloads_dir, exist_ok=True)

    autoload_names = []
    for c_name, tmpl_data in autoload_data:
        autoload_names.append(c_name)
        _write_autoload_h(c_name, tmpl_data)
        _write_autoload_c(c_name, tmpl_data)

    # Write master autoloads.h
    _write_autoloads_h(master_data)

    exporter.autoload_info = {'autoloads': autoload_names, 'has_autoloads': True}

    return features or {}


def _write_autoload_h(c_name: str, template_data: dict):
    """Generate individual autoload .h file."""
    tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'autoloads', 'autoload.h.j2')
    out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'autoloads', f'{c_name}.h')

    with open(tmpl_path, 'r', encoding='utf-8') as f:
        template = f.read()

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(template.format(**template_data))


def _write_autoload_c(c_name: str, template_data: dict):
    """Generate individual autoload .c file."""
    tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'autoloads', 'autoload.c.j2')
    out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'autoloads', f'{c_name}.c')

    with open(tmpl_path, 'r', encoding='utf-8') as f:
        template = f.read()

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(template.format(**template_data))


def _write_autoloads_h(template_data: dict):
    """Generate master autoloads.h that includes all autoloads."""
    tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'autoloads', 'autoloads.h.j2')
    out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'autoloads', 'autoloads.h')

    with open(tmpl_path, 'r', encoding='utf-8') as f:
        template = f.read()

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(template.format(**template_data))


def write_engine(exporter):
    """Generate engine.c and engine.h files.

    Args:
        exporter: N64Exporter instance with has_physics, has_ui, has_audio flags
    """
    import arm.n64.utils as n64_utils

    n64_utils.copy_src('engine.c', 'src')

    # Generate engine.h from template with feature flags
    tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'engine.h.j2')
    out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'engine.h')

    with open(tmpl_path, 'r', encoding='utf-8') as f:
        tmpl_content = f.read()

    # Calculate physics debug mode from Blender settings
    physics_debug_mode = n64_utils.get_physics_debug_mode()

    output = tmpl_content.format(
        enable_physics=1 if exporter.has_physics else 0,
        enable_physics_debug=1 if physics_debug_mode > 0 else 0,
        enable_ui=1 if exporter.has_ui else 0,
        enable_audio=1 if exporter.has_audio else 0
    )

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(output)
