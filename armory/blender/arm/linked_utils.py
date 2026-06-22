"""Utilities for handling linked blend files in Armory exports."""
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Optional

import bpy

import arm

if arm.is_reload(__name__):
    pass
else:
    arm.enable_reload(__name__)


def is_linked(bdata) -> bool:
    """Check if a data block is linked from an external library."""
    if bdata is None:
        return False
    return bdata.library is not None


def get_library_name(bdata) -> Optional[str]:
    """Get the library filename for a linked data block."""
    if bdata is None or bdata.library is None:
        return None
    return bdata.library.name


def get_library_path(bdata) -> Optional[Path]:
    """Get the absolute path to the library .blend file."""
    if bdata is None or bdata.library is None:
        return None
    return Path(bpy.path.abspath(bdata.library.filepath))


def asset_name(bdata) -> Optional[str]:
    """Get qualified asset name with library suffix for linked data."""
    if bdata is None:
        return None
    name = bdata.name
    if bdata.library is not None:
        name += '_' + bdata.library.name
    return name


def get_source_path(bdata) -> Optional[Path]:
    """Get Sources folder path for a linked data block's project."""
    lib_path = get_library_path(bdata)
    if lib_path is None:
        return None
    sources_path = lib_path.parent / 'Sources'
    if sources_path.exists() and sources_path.is_dir():
        return sources_path
    return None


class TransformEvaluator:
    """Context manager for evaluating linked object transforms (Blender 4.2+ workaround)."""

    def __init__(self, bobject: bpy.types.Object, scene: bpy.types.Scene,
                 depsgraph: bpy.types.Depsgraph):
        self.bobject = bobject
        self.scene = scene
        self.depsgraph = depsgraph
        self._temp_collection: Optional[bpy.types.Collection] = None
        self._evaluated_obj: Optional[bpy.types.Object] = None
        self._is_linked = False

    def __enter__(self) -> 'TransformEvaluator':
        if bpy.app.version >= (4, 2, 0):
            self._is_linked = self.bobject.name not in self.scene.collection.children
            if self._is_linked:
                self._temp_collection = bpy.data.collections.new("_armory_temp_eval")
                bpy.context.scene.collection.children.link(self._temp_collection)
                self._temp_collection.objects.link(self.bobject)
                temp_depsgraph = bpy.context.evaluated_depsgraph_get()
                self._evaluated_obj = self.bobject.evaluated_get(temp_depsgraph)
            else:
                self._evaluated_obj = self.bobject.evaluated_get(self.depsgraph)
        else:
            self._evaluated_obj = self.bobject
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._is_linked and self._temp_collection is not None:
            try:
                self._temp_collection.objects.unlink(self.bobject)
                bpy.context.scene.collection.children.unlink(self._temp_collection)
                bpy.data.collections.remove(self._temp_collection)
            except Exception:
                pass
        self._temp_collection = None
        return False

    @property
    def evaluated_object(self) -> bpy.types.Object:
        return self._evaluated_obj

    @property
    def matrix_local(self):
        if bpy.app.version >= (4, 2, 0):
            return self._evaluated_obj.matrix_local.copy()
        return self.bobject.matrix_local


@contextmanager
def evaluated_mesh(bobject: bpy.types.Object, scene: bpy.types.Scene,
                   depsgraph: bpy.types.Depsgraph, apply_modifiers: bool = True):
    """Context manager for mesh export with Blender 4.2+ linked object workaround."""
    temp_collection = None
    is_linked = False

    try:
        if apply_modifiers and bpy.app.version >= (4, 2, 0):
            is_linked = bobject.name not in scene.collection.children
            if is_linked:
                temp_collection = bpy.data.collections.new("_armory_temp_mesh_eval")
                bpy.context.scene.collection.children.link(temp_collection)
                temp_collection.objects.link(bobject)

        temp_depsgraph = bpy.context.evaluated_depsgraph_get()
        bobject_eval = bobject.evaluated_get(temp_depsgraph)
        yield bobject_eval, temp_depsgraph

    finally:
        if is_linked and temp_collection is not None:
            try:
                temp_collection.objects.unlink(bobject)
                bpy.context.scene.collection.children.unlink(temp_collection)
                bpy.data.collections.remove(temp_collection)
            except Exception:
                pass


def discover_linked_sources() -> Dict[str, Path]:
    """Discover Sources folders from all linked libraries."""
    sources: Dict[str, Path] = {}
    for lib in bpy.data.libraries:
        lib_path = Path(bpy.path.abspath(lib.filepath))
        sources_path = lib_path.parent / 'Sources'
        if sources_path.exists() and sources_path.is_dir():
            sources[lib.name] = sources_path
    return sources

