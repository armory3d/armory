"""Utilities for handling linked blend files in Armory exports."""
from contextlib import contextmanager
import os
from typing import Optional

import bpy

import arm

if arm.is_reload(__name__):
    pass
else:
    arm.enable_reload(__name__)


def library_suffix(lib: bpy.types.Library) -> str:
    """Get the unique name suffix of a library.

    The suffix is the path of the library's blend file relative to the
    project root, without the extension and with path separators replaced
    by `_` (e.g. `levels/forest/level.blend` -> `levels_forest_level`), so
    blend files with the same name in different folders don't collide.
    Blend files outside the project root give just their file name.
    """
    import arm.utils

    lib_path = os.path.normpath(bpy.path.abspath(lib.filepath))
    try:
        rel_path = os.path.relpath(lib_path, arm.utils.get_fp())
    except ValueError:
        # On another drive than the project
        rel_path = os.path.basename(lib_path)
    if rel_path.startswith(os.pardir):
        rel_path = os.path.basename(lib_path)

    return arm.utils.safestr(os.path.splitext(rel_path)[0].replace(os.sep, '_'))


def asset_name(bdata) -> Optional[str]:
    """Get qualified asset name with library suffix for linked data."""
    if bdata is None:
        return None
    name = bdata.name
    if bdata.library is not None:
        name += '_' + library_suffix(bdata.library)
    return name


def get_scene_name(scene) -> str:
    """Get the unique export name of a scene (without file extension).

    Local scenes keep their name. Scenes from an external blend file are
    named `[scene_name]_[blend_subdir_path]_[blend_name]`, where the subdirectories
    are relative to the external blends path, so scenes with the same name
    in different files or folders don't collide. Blend files directly in
    the external blends path give `[scene_name]_[blend_name]`.
    """
    import arm.utils

    if scene.library is None:
        return arm.utils.safestr(scene.name)

    wrd = bpy.data.worlds['Arm']
    lib_path = os.path.normpath(bpy.path.abspath(scene.library.filepath))
    root = os.path.normpath(bpy.path.abspath(wrd.arm_external_blends_path.strip()))
    try:
        rel_dir = os.path.relpath(os.path.dirname(lib_path), root)
    except ValueError:
        # On another drive than the external blends path: no relative path
        rel_dir = os.curdir
    subdirs = [] if rel_dir == os.curdir else rel_dir.split(os.sep)

    blend_name = os.path.splitext(os.path.basename(lib_path))[0]
    return arm.utils.safestr('_'.join([scene.name, *subdirs, blend_name]))


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

