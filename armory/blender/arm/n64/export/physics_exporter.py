"""
Physics Exporter - Handles physics engine file generation for N64.

This module provides functions for copying and configuring the Oimo physics
engine files for N64 export.
"""

import os

import arm.utils
import arm.n64.utils as n64_utils


def write_physics(exporter):
    """Copy physics engine files if physics is enabled.

    Copies the Oimo physics library and generates configuration templates.

    Args:
        exporter: N64Exporter instance (checks exporter.has_physics)
    """
    if not exporter.has_physics:
        return

    # Copy oimo library first (header-only physics engine)
    # Must be done BEFORE rendering templates, since copy_dir clears the target
    n64_utils.copy_dir('oimo', 'src')

    # Render physics.c template (after copy_dir so it doesn't get deleted)
    tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'oimo', 'physics.c.j2')
    out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'oimo', 'physics.c')

    with open(tmpl_path, 'r', encoding='utf-8') as f:
        tmpl_content = f.read()

    max_physics_bodies = n64_utils.get_config('max_physics_bodies', 32)
    output = tmpl_content.format(max_physics_bodies=max_physics_bodies)

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(output)

    # Render physics_events.h template
    tmpl_path = os.path.join(arm.utils.get_n64_deployment_path(), 'src', 'events', 'physics_events.h.j2')
    out_path = os.path.join(arm.utils.build_dir(), 'n64', 'src', 'events', 'physics_events.h')

    with open(tmpl_path, 'r', encoding='utf-8') as f:
        tmpl_content = f.read()

    max_contact_subscribers = n64_utils.get_config('max_contact_subscribers', 4)
    max_contact_bodies = n64_utils.get_config('max_contact_bodies', 16)
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
