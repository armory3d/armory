"""Decides what a build can skip because it is unchanged since the last
build, and what a skipped scene has to put back.

Every skippable file is described by a stamp: a digest of everything its
content depends on. The stamp of each written file is kept in the build
folder (compiled/export_cache.json), so unchanged data is skipped across
builds and Blender sessions alike:

- Scenes from other .blend files (linked scenes): their libraries, the
  Armory SDK and every project and render path setting.
- Meshes whose object and data both come from other .blend files: their
  libraries, the exporter code and the settings that change mesh files.
- Animations (actions), linked or local: their own keyframes, the
  armature, the exporter code and the settings that change action files.

Code counts by content, not by modification time: touching a file or
switching to a branch with the same code doesn't make anything stale.
"""
import array
import hashlib
import json
import os
from typing import Any, Dict, Iterable, Optional, Tuple

import bpy

import arm
import arm.log as log
import arm.utils
from arm import assets

if arm.is_reload(__name__):
    log = arm.reload_module(log)
    arm.utils = arm.reload_module(arm.utils)
    assets = arm.reload_module(assets)
else:
    arm.enable_reload(__name__)

MANIFEST = 'export_cache.json'

# The code that writes mesh and action files, relative to blender/arm. Files
# exported by another version of it are exported again; code moved to other
# modules has to be listed here
DATA_SOURCES = ('exporter.py', 'exporter_opt.py', 'linked_utils.py', 'utils.py', 'lib/armpack.py', 'lib/lz4.py')

# Settings of the Arm world that change around a build without changing
# what is exported (play and publish set them)
VOLATILE_SETTINGS = ('arm_recompile', 'arm_project_version')

# Everything a scene export contributes to the state that khafile.js is
# written from. Skipping a scene has to put all of it back, see
# take_contributions() and replay_scene()
CONTRIBUTION_FLAGS = ('export_physics', 'export_navigation', 'export_ui', 'export_network', 'export_particles')

# Properties of animation data that can decide how the active action is evaluated
ANIMDATA_SETTINGS = ('action_blend_type', 'action_extrapolation', 'action_influence')
BONE_SETTINGS = ('use_deform', 'use_connect', 'inherit_scale', 'use_inherit_rotation', 'use_local_location',
                 'use_relative_parent')
# Keyframe properties that decide an F-curve's values, read in bulk: (name,
# array type, values per keyframe); enums are read as integers. Handle types
# only decide how Blender places the handles, whose positions are read
KEYFRAME_VALUES = (('co', 'f', 2), ('handle_left', 'f', 2), ('handle_right', 'f', 2),
                   ('interpolation', 'i', 1), ('easing', 'i', 1),
                   ('back', 'f', 1), ('amplitude', 'f', 1), ('period', 'f', 1))


def exporter():
    """The exporter class, imported on use: arm.exporter imports this module."""
    from arm.exporter import ArmoryExporter
    return ArmoryExporter


def rna_values(struct, names: Iterable[str] = None) -> str:
    """The values of a struct's own properties (all of them, or `names`),
    pointers and collections left out."""
    out = []
    props = struct.bl_rna.properties
    for name in (names if names is not None else (p.identifier for p in props)):
        prop = props.get(name)
        if prop is None or name == 'rna_type' or prop.type in ('POINTER', 'COLLECTION'):
            continue
        value = getattr(struct, name)
        if isinstance(value, set):
            value = tuple(sorted(value))  # enum flags: sets don't keep an order
        elif prop.type != 'STRING' and getattr(prop, 'is_array', False):
            value = tuple(tuple(v) if hasattr(v, '__len__') else v for v in value)
        out.append(f'{name}={value!r}')
    return '|'.join(out)


def depends_on_other_objects(armature_object) -> bool:
    """Whether the armature's pose depends on other data than its action:
    drivers, or bone constraints targeting other objects. Such armatures are
    sampled in the current scene, with their targets, and never cached."""
    animation_data = armature_object.animation_data
    armature = armature_object.data
    if (animation_data is not None and len(animation_data.drivers) > 0) or \
       (armature.animation_data is not None and len(armature.animation_data.drivers) > 0):
        return True
    for pose_bone in armature_object.pose.bones:
        for constraint in pose_bone.constraints:
            targets = [getattr(constraint, 'target', None), getattr(constraint, 'pole_target', None)]
            targets += [t.target for t in getattr(constraint, 'targets', [])]
            if any(t is not None and t != armature_object for t in targets):
                return True
    return False


def modifier_libraries(bobject) -> set:
    """The libraries of the data the object's modifiers read (Boolean
    cutters, Shrinkwrap targets, Geometry Nodes groups and object inputs...).
    Linked data can only reference library data, so for a linked object
    these libraries cover everything its evaluated mesh depends on."""
    referenced = []
    for modifier in bobject.modifiers:
        for prop in modifier.bl_rna.properties:
            if prop.type == 'POINTER':
                referenced.append(getattr(modifier, prop.identifier))
        # Geometry Nodes inputs are custom properties of the modifier
        try:
            referenced += modifier.values()
        except TypeError:
            pass  # a modifier type without custom properties
    libraries = set()
    for data in referenced:
        if not isinstance(data, bpy.types.ID):
            continue
        if isinstance(data, bpy.types.Collection):
            items = list(data.all_objects)
        else:
            items = [data]
        for item in items:
            libraries.update(lib for lib in (item.library, getattr(getattr(item, 'data', None), 'library', None))
                             if lib is not None)
    return libraries


def library_stamp(library) -> str:
    try:
        stat = os.stat(arm.utils.to_absolute_path(library.filepath))
        return f'{library.filepath}={stat.st_size}:{stat.st_mtime_ns}'
    except OSError:
        # Broken library links stay broken, so note that rather than refusing
        # to cache. The stamp still changes if the file ever does turn up
        return f'{library.filepath}=missing'


class BuildExportCache:
    """Shared by all scene exports of one build: created in make.py and
    passed to each ArmoryExporter instance."""

    def __init__(self):
        self.exported_mesh_files: set = set()
        self.exported_action_files: set = set()
        self.processed_mesh_names: set = set()

        self.path = os.path.join(arm.utils.get_fp_build(), 'compiled', MANIFEST)
        self.data_manifest: Dict[str, str] = {}     # file name -> stamp of its content
        self.scene_manifest: Dict[str, Any] = {}    # scene file name -> {stamp, contributions}
        self.file_hashes: Dict[str, list] = {}      # SDK file -> [size, mtime_ns, sha1 of its content]
        self.linked_actions: Dict[str, str] = {}    # library stamp|action name -> action_hash()
        self.load()

        # Per build: computed once, see environment_stamp()
        self._environment: Optional[str] = None
        self._data_stamp: Optional[str] = None
        self._action_hashes: Dict[int, str] = {}
        self._armature_stamps: Dict[int, Optional[str]] = {}
        self._used_linked_actions: Dict[str, str] = {}  # saved: digests of libraries no longer loaded go

    def load(self) -> None:
        try:
            with open(self.path, encoding='utf-8') as f:
                data = json.load(f)
            self.data_manifest = data.get('data', {})
            self.scene_manifest = data.get('scenes', {})
            self.file_hashes = data.get('files', {})
            self.linked_actions = data.get('linked_actions', {})
        except (OSError, ValueError, AttributeError):
            # No manifest yet or it is unreadable: everything counts as not
            # exported and is simply exported again
            pass

    def save(self) -> None:
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            arm.utils.write_file_if_changed(
                self.path,
                json.dumps({'data': self.data_manifest, 'scenes': self.scene_manifest, 'files': self.file_hashes,
                            'linked_actions': self._used_linked_actions}, sort_keys=True, indent=1),
                encoding='utf-8')
        except OSError as err:
            log.warn(f'Could not write the export cache: {err}')

    # --- Files -------------------------------------------------------------

    def is_cached(self, filepath: str, stamp: Optional[str]) -> bool:
        """Whether `filepath` was written from data described by `stamp`
        and is still there. A `None` stamp is never cached."""
        return (stamp is not None and os.path.exists(filepath)
                and self.data_manifest.get(os.path.basename(filepath)) == stamp)

    def store(self, filepath: str, stamp: Optional[str]) -> None:
        """Remembers what `filepath` was just written from."""
        if stamp is None:
            self.data_manifest.pop(os.path.basename(filepath), None)
        else:
            self.data_manifest[os.path.basename(filepath)] = stamp

    # --- Shared parts of the stamps ------------------------------------------

    def file_digest(self, path: str, key: str) -> str:
        """The SHA-1 of a file's content, re-read only when its size or
        modification time changed since the last build."""
        stat = os.stat(path)
        known = self.file_hashes.get(key)
        if known is not None and known[0] == stat.st_size and known[1] == stat.st_mtime_ns:
            return known[2]
        with open(path, 'rb') as f:
            digest = hashlib.sha1(f.read()).hexdigest()
        self.file_hashes[key] = [stat.st_size, stat.st_mtime_ns, digest]
        return digest

    def sdk_digest(self, folders: Iterable[str]) -> str:
        """Digest of every file in the given folders of the SDK's armory folder."""
        sdk_path = os.path.join(arm.utils.get_sdk_path(), 'armory')
        digest = hashlib.sha1()
        for folder in folders:
            for root, dirs, files in os.walk(os.path.join(sdk_path, folder)):
                # Python writes bytecode on import, which isn't an edit
                dirs[:] = sorted(d for d in dirs if d != '__pycache__')
                for name in sorted(files):
                    path = os.path.join(root, name)
                    key = os.path.relpath(path, sdk_path).replace('\\', '/')
                    digest.update(f'{key}={self.file_digest(path, key)}\n'.encode())
        return digest.hexdigest()

    def environment_stamp(self) -> str:
        """Everything besides the library files that the export of a linked
        scene depends on: the Blender version, the Armory SDK (exporter and
        shader code), the project settings of the Arm world and the settings
        of the active render path.

        Computed once per build: the export itself changes some of these
        values (materials add '_SSS' to world_defs), and a scene's stamp
        must not differ before and after its export.
        """
        if self._environment is None:
            wrd = bpy.data.worlds['Arm']
            parts = [bpy.app.version_string, self.sdk_digest(('blender', 'Shaders')),
                     rna_values(wrd, ['world_defs', 'compo_defs'] + [p.identifier for p in wrd.bl_rna.properties
                                if p.identifier.startswith('arm_') and p.identifier not in VOLATILE_SETTINGS]),
                     rna_values(arm.utils.get_rp())]
            self._environment = hashlib.sha1('\n'.join(parts).encode()).hexdigest()
        return self._environment

    def data_stamp(self) -> str:
        """What every mesh and action file depends on besides its own data:
        the Blender version, the exporter code and the file format settings."""
        if self._data_stamp is None:
            sdk_path = os.path.join(arm.utils.get_sdk_path(), 'armory')
            parts = [bpy.app.version_string]
            for source in DATA_SOURCES:
                key = 'blender/arm/' + source
                parts.append(f'{key}={self.file_digest(os.path.join(sdk_path, key), key)}')
            self._data_stamp = hashlib.sha1('\n'.join(parts).encode()).hexdigest()
        ArmoryExporter = exporter()
        return ':'.join((self._data_stamp, str(ArmoryExporter.compress_enabled), str(ArmoryExporter.optimize_enabled),
                         str(bpy.data.worlds['Arm'].arm_minimize)))

    # --- Meshes -------------------------------------------------------------

    def mesh_stamp(self, bobject, layout: Tuple) -> Optional[str]:
        """Stamp of a mesh file, for an object and mesh that both come from
        other .blend files (local data uses the arm_cached flag). `layout`
        is what the exported vertex data depends on besides the libraries:
        the attributes its materials need and the settings that change it."""
        if bobject.library is None or bobject.data is None or bobject.data.library is None:
            return None
        libraries = {bobject.library, bobject.data.library}
        armature = bobject.find_armature()
        if armature is not None:
            libraries.update(lib for lib in (armature.library, armature.data.library) if lib is not None)
        libraries.update(modifier_libraries(bobject))
        parts = sorted(library_stamp(lib) for lib in libraries)
        parts += [self.data_stamp(), repr(layout)]
        return hashlib.sha1('\n'.join(parts).encode()).hexdigest()

    # --- Actions ------------------------------------------------------------

    def action_hash(self, action) -> str:
        """Digest of an action's own content: frame range, markers and every
        F-curve with its keyframes and modifiers. A linked action can only
        change with its library file, so its digest is reused until that
        file changes."""
        key = action.as_pointer()
        known = self._action_hashes.get(key)
        if known is not None:
            return known
        if action.library is not None:
            linked_key = f'{library_stamp(action.library)}|{action.name}'
            known = self.linked_actions.get(linked_key) or self.hash_action(action)
            self._used_linked_actions[linked_key] = known
        else:
            known = self.hash_action(action)
        self._action_hashes[key] = known
        return known

    @staticmethod
    def hash_action(action) -> str:
        digest = hashlib.sha1(rna_values(action, ('frame_range', 'use_frame_range', 'use_cyclic')).encode())
        digest.update(repr([(m.name, m.frame) for m in action.pose_markers]).encode())
        if bpy.app.version >= (5, 0, 0):
            digest.update(repr([slot.identifier for slot in action.slots]).encode())
        for fcurve in sorted(exporter().get_fcurves(action), key=lambda fc: (fc.data_path, fc.array_index)):
            points = fcurve.keyframe_points
            count = len(points)
            digest.update(f'{fcurve.data_path}[{fcurve.array_index}]|{fcurve.extrapolation}|{fcurve.mute}|{count}'.encode())
            for prop, kind, size in KEYFRAME_VALUES:
                values = array.array(kind, [0]) * (size * count)
                points.foreach_get(prop, values)
                digest.update(values.tobytes())
            for modifier in fcurve.modifiers:
                digest.update(rna_values(modifier).encode())
        return digest.hexdigest()

    def action_stamp(self, armature_object, action) -> Optional[str]:
        """Stamp of an armature action file. Actions are sampled from the
        evaluated pose, on their own: NLA off, bones the action doesn't key
        at rest (see ArmoryExporter.export_armature_actions()). So besides
        the action itself the stamp covers the armature's bones and
        constraints. Returns `None` (export every time) when the pose
        depends on other objects (see depends_on_other_objects())."""
        armature = self.armature_stamp(armature_object)
        if armature is None:
            return None
        return hashlib.sha1('\n'.join((self.data_stamp(), self.action_hash(action), armature)).encode()).hexdigest()

    def armature_stamp(self, armature_object) -> Optional[str]:
        """The part of action_stamp() shared by all actions of an armature
        object, computed once per build."""
        key = armature_object.as_pointer()
        if key in self._armature_stamps:
            return self._armature_stamps[key]
        self._armature_stamps[key] = self._armature_stamp(armature_object)
        return self._armature_stamps[key]

    def _armature_stamp(self, armature_object) -> Optional[str]:
        if depends_on_other_objects(armature_object):
            return None
        animation_data = armature_object.animation_data
        armature = armature_object.data
        parts = [f'autobake={armature.arm_autobake}|deform_only={arm.utils.get_rp().arm_use_armature_deform_only}'
                 f'|pose_position={armature.pose_position}']
        for bone in armature.bones:
            parent = bone.parent.name if bone.parent is not None else ''
            parts.append(f'B{bone.name}<{parent}|{rna_values(bone, BONE_SETTINGS)}|{tuple(tuple(r) for r in bone.matrix_local)}')
        for pose_bone in armature_object.pose.bones:
            parts.append(f'P{pose_bone.name}|{pose_bone.rotation_mode}')
            for constraint in pose_bone.constraints:
                parts.append(f'C{constraint.type}|{rna_values(constraint)}')
        if animation_data is not None:
            parts.append(rna_values(animation_data, ANIMDATA_SETTINGS))
        return '\n'.join(parts)

    def object_action_stamp(self, action) -> str:
        """Stamp of an object action file: its tracks are the action's own
        F-curves, evaluated frame by frame."""
        return hashlib.sha1((self.data_stamp() + '\n' + self.action_hash(action)).encode()).hexdigest()

    # --- Scenes -------------------------------------------------------------

    def scene_stamp(self, scene) -> Optional[str]:
        """Describes everything the export of a scene depends on. Returns
        `None` for scenes of the current file, which is written on every
        build and can therefore never be considered unchanged.

        Every loaded library counts, not just the one holding the scene,
        because a scene reaches data across all of them.
        """
        if scene.library is None:
            return None
        parts = [library_stamp(lib) for lib in sorted(bpy.data.libraries, key=lambda lib: lib.filepath)]
        ArmoryExporter = exporter()
        parts.append(f'settings={ArmoryExporter.compress_enabled}:{ArmoryExporter.optimize_enabled}:{bpy.data.worlds["Arm"].arm_minimize}')
        parts.append(f'environment={self.environment_stamp()}')
        return '|'.join(parts)

    def replay_scene(self, scene, filepath: str) -> bool:
        """Puts back what a scene contributed the last time it was exported,
        if nothing it depends on has changed since. Returns whether the
        scene export can be skipped."""
        stamp = self.scene_stamp(scene)
        if stamp is None or not os.path.exists(filepath):
            return False
        record = self.scene_manifest.get(os.path.basename(filepath))
        if record is None or record.get('stamp') != stamp:
            return False
        self.replay_contributions(record.get('contributions', {}))
        return True

    def store_scene(self, scene, filepath: str, mark: Dict[str, Any]) -> None:
        """Ends the recording of a scene export (every scene, see
        mark_contributions()) and remembers it if the scene can be skipped
        on a later build."""
        contributions = self.take_contributions(mark)
        stamp = self.scene_stamp(scene)
        if stamp is None:
            return
        self.scene_manifest[os.path.basename(filepath)] = {'stamp': stamp, 'contributions': contributions}

    @staticmethod
    def contribution_lists() -> Tuple[Tuple[Any, str], ...]:
        """The lists a scene export appends to: (owner, attribute)."""
        return ((assets, 'assets'), (assets, 'shader_datas'), (assets, 'khafile_defs'),
                (assets, 'khafile_params'), (exporter(), 'import_traits'))

    @staticmethod
    def mark_contributions() -> Dict[str, Any]:
        """Starts recording a scene export: the lists it appends to are
        swapped for empty ones until take_contributions(). The lists skip
        duplicates, so recording into the build's own lists would miss what
        an earlier scene already added, and a skipped scene must put back
        everything it uses."""
        mark = {}
        for owner, name in BuildExportCache.contribution_lists():
            mark[name] = getattr(owner, name)
            setattr(owner, name, [])
        return mark

    @staticmethod
    def take_contributions(mark: Dict[str, Any]) -> Dict[str, Any]:
        """Ends the recording started by mark_contributions(): returns what
        the scene export added, ready to be stored and replayed when the
        scene is skipped on a later build, and adds it to the build's lists."""
        contributions = {name: getattr(owner, name) for owner, name in BuildExportCache.contribution_lists()}
        # Flags are per scene: preprocess() sets them again for every export
        contributions['flags'] = [name for name in CONTRIBUTION_FLAGS if getattr(exporter(), name)]
        for owner, name in BuildExportCache.contribution_lists():
            setattr(owner, name, mark[name])
        BuildExportCache.replay_contributions(contributions)
        return contributions

    @staticmethod
    def replay_contributions(contributions: Dict[str, Any]) -> None:
        for asset in contributions.get('assets', []):
            assets.add(asset)
        for shader_data in contributions.get('shader_datas', []):
            assets.add_shader_data(shader_data)
        for define in contributions.get('khafile_defs', []):
            assets.add_khafile_def(define)
        for param in contributions.get('khafile_params', []):
            assets.add_khafile_param(param)
        ArmoryExporter = exporter()
        ArmoryExporter.import_traits.extend(contributions.get('import_traits', []))
        # As the export left them, read by make.export_data() after each scene
        for name in CONTRIBUTION_FLAGS:
            setattr(ArmoryExporter, name, name in contributions.get('flags', []))
