"""
Physics Exporter - Handles physics engine file generation for N64.

This module provides functions for copying and configuring the Oimo physics
engine files for N64 export.
"""

import os

import arm.utils
import arm.n64.utils as n64_utils


def _get_physics_limit(exporter_value: int, config_key: str, default: int, buffer: int = 4, minimum: int = 8) -> int:
    """Get physics limit, preferring calculated value with buffer.

    Args:
        exporter_value: Value calculated during scene export
        config_key: Config key name to check for explicit override
        default: Default value if no calculation available
        buffer: Extra buffer to add to calculated value
        minimum: Minimum value to ensure

    Returns:
        Final value to use for the limit
    """
    # Calculate value with buffer
    calculated = max(exporter_value + buffer, minimum)

    # Check for explicit config override
    config_value = n64_utils.get_config(config_key, None)
    if config_value is not None:
        # If user explicitly set a value, use the higher of config or calculated
        return max(config_value, calculated)

    return calculated


def write_physics(exporter):
    """Copy physics engine files if physics is enabled.

    Copies the Oimo physics library and generates configuration templates.
    Uses dynamically calculated body counts from scene export with buffers.

    Args:
        exporter: N64Exporter instance (checks exporter.has_physics)
    """
    if not exporter.has_physics:
        return

    # Copy oimo library first (header-only physics engine)
    # Must be done BEFORE rendering templates, since copy_dir clears the target
    n64_utils.copy_dir('oimo', 'src')

    # Calculate physics limits from scene data with buffer
    max_physics_bodies = _get_physics_limit(
        exporter.max_physics_bodies, 'max_physics_bodies', 32, buffer=4, minimum=8
    )
    max_mesh_colliders = _get_physics_limit(
        exporter.max_mesh_colliders, 'max_mesh_colliders', 8, buffer=2, minimum=4
    )
    max_contact_bodies = _get_physics_limit(
        exporter.max_contact_bodies, 'max_contact_bodies', 16, buffer=4, minimum=8
    )

    # Log calculated values
    print(f"  Physics limits: bodies={max_physics_bodies} (from {exporter.max_physics_bodies}), "
          f"mesh_colliders={max_mesh_colliders} (from {exporter.max_mesh_colliders}), "
          f"contact_bodies={max_contact_bodies} (from {exporter.max_contact_bodies})")

    # Render physics.h template (after copy_dir so it doesn't get deleted)
    tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'oimo', 'physics.h.j2')
    out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'oimo', 'physics.h')

    with open(tmpl_path, 'r', encoding='utf-8') as f:
        tmpl_content = f.read()

    output = tmpl_content.format(max_mesh_colliders=max_mesh_colliders)

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(output)

    # Render physics.c template
    tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'oimo', 'physics.c.j2')
    out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'oimo', 'physics.c')

    with open(tmpl_path, 'r', encoding='utf-8') as f:
        tmpl_content = f.read()

    output = tmpl_content.format(max_physics_bodies=max_physics_bodies)

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(output)

    # Render physics_events.h template
    tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'events', 'physics_events.h.j2')
    out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'events', 'physics_events.h')

    with open(tmpl_path, 'r', encoding='utf-8') as f:
        tmpl_content = f.read()

    max_contact_subscribers = n64_utils.get_config('max_contact_subscribers', 4)
    output = tmpl_content.format(
        max_contact_subscribers=max_contact_subscribers,
        max_contact_bodies=max_contact_bodies
    )

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(output)

    # Copy physics_events.c
    n64_utils.copy_src('physics_events.c', 'src/events')

    # Copy physics debug drawing files only if debug is enabled
    if n64_utils.get_physics_debug_mode() > 0:
        n64_utils.copy_src('physics_debug.h', 'src/oimo/debug')
        n64_utils.copy_src('physics_debug.c', 'src/oimo/debug')
