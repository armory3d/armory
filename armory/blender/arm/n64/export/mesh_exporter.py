"""Mesh Exporter - Handles GLTF mesh export for N64.

This module exports Blender meshes to GLTF format for subsequent
conversion to N64 model format (T3D).
"""

import os
import bpy

import arm.utils
import arm.log as log
import arm.linked_utils as linked_utils
import arm.n64.utils as n64_utils
from arm.n64.export import linked_export


def _collect_all_objects(scene):
    """Collect all objects including those inside instance collections.

    Returns:
        List of (object, instance_matrix) tuples. instance_matrix is None
        for direct scene objects, or the parent empty's world matrix for
        objects inside instanced collections.
    """
    objects = []
    processed_collections = set()

    for obj in scene.collection.all_objects:
        if obj.instance_type == 'COLLECTION' and obj.instance_collection:
            coll = obj.instance_collection
            if coll not in processed_collections:
                processed_collections.add(coll)
                for cobj in coll.all_objects:
                    objects.append((cobj, obj.matrix_world))
        else:
            objects.append((obj, None))

    return objects


def _export_mesh_to_gltf(obj, output_path):
    """Export a single mesh object to GLTF format.

    Temporarily resets object transforms to origin for export,
    then restores them.
    """
    # Save original transforms
    orig_loc = obj.location.copy()
    orig_rot = obj.rotation_euler.copy()
    orig_scale = obj.scale.copy()

    # Reset to origin for export
    obj.location = (0.0, 0.0, 0.0)
    obj.rotation_euler = (0.0, 0.0, 0.0)
    obj.scale = (1.0, 1.0, 1.0)

    # Force view layer update (needed for cross-scene export)
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
    bpy.context.view_layer.update()

    obj.select_set(True)

    bpy.ops.export_scene.gltf(
        filepath=output_path,
        export_format='GLTF_SEPARATE',
        export_extras=True,
        use_selection=True,
        export_yup=True
    )

    # Restore original transforms
    obj.location = orig_loc
    obj.rotation_euler = orig_rot
    obj.scale = orig_scale
    bpy.context.view_layer.update()


def export_meshes(exporter):
    """Export all meshes from all scenes to GLTF format.

    Exports linked objects from temp scene first (with F3D materials),
    then local objects from user scenes.

    Updates exporter.exported_meshes with {mesh: mesh_name} mapping.
    """
    assets_dir = os.path.join(arm.utils.build_dir(), 'n64', 'assets')
    exporter.exported_meshes = {}

    _export_linked_meshes(exporter, assets_dir)
    _export_scene_meshes(exporter, assets_dir)


def _export_linked_meshes(exporter, assets_dir):
    """Export meshes from temp scene (localized linked objects)."""
    if not exporter.linked_objects:
        return

    temp_scene = linked_export.get_temp_scene()
    if not temp_scene:
        return

    n64_utils.deselect_from_all_viewlayers()
    main_scene = bpy.context.scene
    main_view_layer = bpy.context.view_layer

    # Switch to temp scene
    bpy.context.window.scene = temp_scene
    bpy.context.window.view_layer = temp_scene.view_layers[0]

    for local_obj_name, original_mesh_name in exporter.linked_objects:
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.update()

        local_obj = bpy.data.objects.get(local_obj_name)
        if not local_obj or local_obj.type != 'MESH':
            if not local_obj:
                log.warn(f'Linked object not found: {local_obj_name}')
            continue

        mesh_name = arm.utils.safesrc(original_mesh_name)
        if mesh_name in exporter.exported_meshes.values():
            continue

        output_path = os.path.join(assets_dir, f'{mesh_name}.gltf')
        _export_mesh_to_gltf(local_obj, output_path)

        # Store by original mesh for scene_exporter lookup
        original_mesh = linked_export.get_original_mesh(original_mesh_name)
        if original_mesh:
            exporter.exported_meshes[original_mesh] = mesh_name
            log.info(f'Exported linked mesh: {mesh_name}')
        else:
            log.warn(f'Could not find original mesh for: {original_mesh_name}')

    # Restore original scene
    bpy.context.window.scene = main_scene
    bpy.context.window.view_layer = main_view_layer


def _export_scene_meshes(exporter, assets_dir):
    """Export meshes from local objects in user scenes."""
    for scene in bpy.data.scenes:
        if scene.library or linked_export.is_temp_scene(scene):
            continue

        n64_utils.deselect_from_all_viewlayers()
        main_scene = bpy.context.scene
        main_view_layer = bpy.context.view_layer

        for obj, _ in _collect_all_objects(scene):
            if obj.type != 'MESH' or obj.library:
                continue

            mesh = obj.data
            if mesh in exporter.exported_meshes:
                continue

            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.update()

            mesh_name = arm.utils.safesrc(linked_utils.asset_name(mesh))
            output_path = os.path.join(assets_dir, f'{mesh_name}.gltf')

            bpy.context.window.scene = scene
            bpy.context.window.view_layer = scene.view_layers[0]

            _export_mesh_to_gltf(obj, output_path)

            exporter.exported_meshes[mesh] = mesh_name
            log.info(f'Exported mesh: {mesh_name}')

        bpy.context.window.scene = main_scene
        bpy.context.window.view_layer = main_view_layer
