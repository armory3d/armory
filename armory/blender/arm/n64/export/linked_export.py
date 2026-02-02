"""Linked Export - Handles linked blend file objects for N64 export.

Creates temporary local copies of linked objects so Fast64 can convert
their materials. Cleans up after export.
"""

import bpy

import arm.log as log
import arm.linked_utils as linked_utils


TEMP_SCENE_NAME = "_armory_n64_export_temp"
TEMP_COLLECTION_NAME = "_armory_n64_linked"


class _LinkedExportState:
    """Encapsulates state for linked object export.

    Using a class avoids scattered module-level globals and makes state clearer.
    """
    def __init__(self):
        self.reset()

    def reset(self):
        """Reset all state to initial values."""
        self.temp_scene_name = None
        self.temp_object_names = []
        self.temp_material_names = []
        self.temp_mesh_names = []
        self.original_mesh_refs = {}  # {mesh_name: original_mesh}


# Single module-level state instance
_state = _LinkedExportState()


def _collect_linked_instance_collections():
    """Find all instance collections containing linked objects."""
    collections = set()
    for scene in bpy.data.scenes:
        if scene.library:
            continue
        for obj in scene.collection.all_objects:
            if obj.instance_type == 'COLLECTION' and obj.instance_collection:
                coll = obj.instance_collection
                if any(cobj.library for cobj in coll.all_objects):
                    collections.add(coll)
    return list(collections)


def prepare_linked_for_export():
    """Create temp scene with localized copies of linked objects for export.

    Returns:
        List of (local_object_name, original_mesh_name) tuples for export
    """
    linked_collections = _collect_linked_instance_collections()
    if not linked_collections:
        return []

    # Create temporary scene
    temp_scene = bpy.data.scenes.new(TEMP_SCENE_NAME)
    _state.temp_scene_name = temp_scene.name

    temp_collection = bpy.data.collections.new(TEMP_COLLECTION_NAME)
    temp_scene.collection.children.link(temp_collection)

    # Ensure view layer exists (required for selection/export)
    if not temp_scene.view_layers:
        temp_scene.view_layers.new("ViewLayer")

    local_objects = []
    processed_meshes = set()

    for coll in linked_collections:
        for obj in coll.all_objects:
            if obj.type != 'MESH':
                continue

            mesh = obj.data
            mesh_name = linked_utils.asset_name(mesh)
            if mesh_name in processed_meshes:
                continue
            processed_meshes.add(mesh_name)

            # Store reference to original mesh for exported_meshes lookup
            _state.original_mesh_refs[mesh_name] = mesh

            # Create local copy of the object
            local_obj = obj.copy()
            local_obj.name = f"_armory_temp_{mesh_name}"
            _state.temp_object_names.append(local_obj.name)

            # Make mesh data local
            if mesh.library:
                local_mesh = mesh.copy()
                local_mesh.name = mesh_name
                local_obj.data = local_mesh
                _state.temp_mesh_names.append(local_mesh.name)

            # Make materials local (required for Fast64 conversion)
            for slot in local_obj.material_slots:
                if slot.material and slot.material.library:
                    local_mat = slot.material.copy()
                    local_mat.name = linked_utils.asset_name(slot.material)
                    slot.material = local_mat
                    _state.temp_material_names.append(local_mat.name)

            temp_collection.objects.link(local_obj)
            local_objects.append((local_obj.name, mesh_name))

    return local_objects


def get_temp_scene():
    """Get the temporary export scene (or None if not created)."""
    if not _state.temp_scene_name:
        return None
    return bpy.data.scenes.get(_state.temp_scene_name)


def get_original_mesh(mesh_name):
    """Get original mesh data block by qualified name."""
    return _state.original_mesh_refs.get(mesh_name)


def is_temp_scene(scene):
    """Check if a scene is the temporary export scene."""
    return _state.temp_scene_name and scene.name == _state.temp_scene_name


def _safe_remove(data_collection, name):
    """Safely remove a data block by name."""
    try:
        item = data_collection.get(name)
        if item:
            data_collection.remove(item, do_unlink=True)
    except Exception:
        pass


def cleanup_linked_export():
    """Remove temporary scene and all localized objects."""
    # Remove objects first (they reference meshes/materials)
    for name in _state.temp_object_names:
        _safe_remove(bpy.data.objects, name)

    # Remove collection
    _safe_remove(bpy.data.collections, TEMP_COLLECTION_NAME)

    # Remove materials and meshes
    for name in _state.temp_material_names:
        _safe_remove(bpy.data.materials, name)
    for name in _state.temp_mesh_names:
        _safe_remove(bpy.data.meshes, name)

    # Remove scene
    if _state.temp_scene_name:
        try:
            scene = bpy.data.scenes.get(_state.temp_scene_name)
            if scene:
                bpy.data.scenes.remove(scene)
        except Exception:
            pass

    _state.reset()
