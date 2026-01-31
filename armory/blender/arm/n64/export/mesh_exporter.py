"""
Mesh Exporter - Handles GLTF mesh export for N64.

This module provides functions for exporting Blender meshes to GLTF format
for subsequent conversion to N64 model format.
"""

import os
import bpy

import arm.utils
import arm.log as log
import arm.n64.utils as n64_utils


def export_meshes(exporter):
    """Export all meshes from all scenes to GLTF format.

    Exports each unique mesh to build/n64/assets/ as a GLTF file.
    Updates exporter.exported_meshes with {mesh: mesh_name} mapping.

    Args:
        exporter: N64Exporter instance to update with exported mesh info
    """
    build_dir = arm.utils.build_dir()
    assets_dir = f'{build_dir}/n64/assets'

    exporter.exported_meshes = {}

    for scene in bpy.data.scenes:
        if scene.library:
            continue

        n64_utils.deselect_from_all_viewlayers()
        main_scene = bpy.context.scene
        main_view_layer = bpy.context.view_layer

        for obj in scene.objects:
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.update()

            if obj.type != 'MESH':
                continue

            mesh = obj.data
            if mesh in exporter.exported_meshes:
                continue

            mesh_name = arm.utils.safesrc(mesh.name)
            model_output_path = os.path.join(assets_dir, f'{mesh_name}.gltf')

            orig_loc = obj.location.copy()
            orig_rot = obj.rotation_euler.copy()
            orig_scale = obj.scale.copy()

            obj.location = (0.0, 0.0, 0.0)
            obj.rotation_euler = (0.0, 0.0, 0.0)
            obj.scale = (1.0, 1.0, 1.0)

            bpy.context.window.scene = scene
            bpy.context.window.view_layer = scene.view_layers[0]

            # HACK: force delay to properly export meshes from other scenes
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
            bpy.context.view_layer.update()

            obj.select_set(True)

            bpy.ops.export_scene.gltf(
                filepath=model_output_path,
                export_format='GLTF_SEPARATE',
                export_extras=True,
                use_selection=True,
                export_yup=True
            )

            obj.location = orig_loc
            obj.rotation_euler = orig_rot
            obj.scale = orig_scale

            bpy.context.view_layer.update()
            exporter.exported_meshes[mesh] = mesh_name

        bpy.context.window.scene = main_scene
        bpy.context.window.view_layer = main_view_layer
