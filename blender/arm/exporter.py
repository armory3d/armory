"""
Armory Scene Exporter
https://armory3d.org/

Based on Open Game Engine Exchange
https://opengex.org/
Export plugin for Blender by Eric Lengyel
Copyright 2015, Terathon Software LLC

This software is licensed under the Creative Commons
Attribution-ShareAlike 3.0 Unported License:
https://creativecommons.org/licenses/by-sa/3.0/deed.en_US
"""
from enum import Enum, unique
import math
import os
import time
from typing import Any, Dict, List, Tuple, Union, Optional

import numpy as np

import bpy
from mathutils import Matrix, Vector

import bmesh

import arm.utils
import arm.profiler
from arm import assets, exporter_opt, log, make_renderpath
from arm.material import cycles, make as make_material, mat_batch

if arm.is_reload(__name__):
    assets = arm.reload_module(assets)
    exporter_opt = arm.reload_module(exporter_opt)
    log = arm.reload_module(log)
    make_renderpath = arm.reload_module(make_renderpath)
    cycles = arm.reload_module(cycles)
    make_material = arm.reload_module(make_material)
    mat_batch = arm.reload_module(mat_batch)
    arm.utils = arm.reload_module(arm.utils)
    arm.profiler = arm.reload_module(arm.profiler)
else:
    arm.enable_reload(__name__)


@unique
class NodeType(Enum):
    """Represents the type of an object."""
    EMPTY = 0
    BONE = 1
    MESH = 2
    LIGHT = 3
    CAMERA = 4
    SPEAKER = 5
    DECAL = 6
    PROBE = 7

    @classmethod
    def get_bobject_type(cls, bobject: bpy.types.Object) -> "NodeType":
        """Returns the NodeType enum member belonging to the type of
        the given blender object."""
        if bobject.type == "MESH":
            if bobject.data.polygons:
                return cls.MESH
        elif bobject.type in ('FONT', 'META'):
            return cls.MESH
        elif bobject.type == "LIGHT":
            return cls.LIGHT
        elif bobject.type == "CAMERA":
            return cls.CAMERA
        elif bobject.type == "SPEAKER":
            return cls.SPEAKER
        elif bobject.type == "LIGHT_PROBE":
            return cls.PROBE
        return cls.EMPTY


STRUCT_IDENTIFIER = ("object", "bone_object", "mesh_object",
                     "light_object", "camera_object", "speaker_object",
                     "decal_object", "probe_object")

# Internal target names for single FCurve data paths
FCURVE_TARGET_NAMES = {
    "location": ("xloc", "yloc", "zloc"),
    "rotation_euler": ("xrot", "yrot", "zrot"),
    "rotation_quaternion": ("qwrot", "qxrot", "qyrot", "qzrot"),
    "scale": ("xscl", "yscl", "zscl"),
    "delta_location": ("dxloc", "dyloc", "dzloc"),
    "delta_rotation_euler": ("dxrot", "dyrot", "dzrot"),
    "delta_rotation_quaternion": ("dqwrot", "dqxrot", "dqyrot", "dqzrot"),
    "delta_scale": ("dxscl", "dyscl", "dzscl"),
}

current_output = None


class ArmoryExporter:
    """Export to Armory format.

    Some common naming patterns:
    - out_[]: Variables starting with "out_" represent data that is
              exported to Iron
    - bobject: A Blender object (bpy.types.Object). Used because
               `object` is a reserved Python keyword
    """

    compress_enabled = False
    export_all_flag = True
    # Indicates whether rigid body is exported
    export_physics = False
    optimize_enabled = False
    option_mesh_only = False

    # Class names of referenced traits
    import_traits: List[str] = []

    def __init__(self, context: bpy.types.Context, filepath: str, scene: bpy.types.Scene = None, depsgraph: bpy.types.Depsgraph = None):
        global current_output

        self.filepath = filepath
        self.scene = context.scene if scene is None else scene
        self.depsgraph = context.evaluated_depsgraph_get() if depsgraph is None else depsgraph

        # The output dict contains all data that is later exported to Iron format
        self.output: Dict[str, Any] = {'frame_time': 1.0 / (self.scene.render.fps / self.scene.render.fps_base)}
        current_output = self.output

        # Stores the object type ("objectType") and the asset name
        # ("structName") in a dict for each object
        self.bobject_array: Dict[bpy.types.Object, Dict[str, Union[NodeType, str]]] = {}
        self.bobject_bone_array = {}
        self.mesh_array = {}
        self.light_array = {}
        self.probe_array = {}
        self.camera_array = {}
        self.speaker_array = {}
        self.material_array = []
        self.world_array = []
        self.particle_system_array = {}

        self.referenced_collections: list[bpy.types.Collection] = []
        """Collections referenced by collection instances"""

        self.has_spawning_camera = False
        """Whether there is at least one camera in the scene that spawns by default"""

        self.material_to_object_dict = {}
        # If no material is assigned, provide default to mimic cycles
        self.default_material_objects = []
        self.default_skin_material_objects = []
        self.default_part_material_objects = []
        self.material_to_arm_object_dict = {}
        # Stores the link between a blender object and its
        # corresponding export data (arm object)
        self.object_to_arm_object_dict: Dict[bpy.types.Object, Dict] = {}

        self.bone_tracks = []

        ArmoryExporter.preprocess()

    @classmethod
    def export_scene(cls, context: bpy.types.Context, filepath: str, scene: bpy.types.Scene = None, depsgraph: bpy.types.Depsgraph = None) -> None:
        """Exports the given scene to the given file path. This is the
        function that is called in make.py and the entry point of the
        exporter."""
        with arm.profiler.Profile('profile_exporter.prof', arm.utils.get_pref_or_default('profile_exporter', False)):
            cls(context, filepath, scene, depsgraph).execute()

    @classmethod
    def preprocess(cls):
        wrd = bpy.data.worlds['Arm']

        if wrd.arm_physics == 'Enabled':
            cls.export_physics = True
        cls.export_navigation = False
        if wrd.arm_navigation == 'Enabled':
            cls.export_navigation = True
        cls.export_ui = False
        cls.export_network = False
        if wrd.arm_network == 'Enabled':
            cls.export_network = True

    @staticmethod
    def write_matrix(matrix):
        return [matrix[0][0], matrix[0][1], matrix[0][2], matrix[0][3],
                matrix[1][0], matrix[1][1], matrix[1][2], matrix[1][3],
                matrix[2][0], matrix[2][1], matrix[2][2], matrix[2][3],
                matrix[3][0], matrix[3][1], matrix[3][2], matrix[3][3]]

    def get_meshes_file_path(self, object_id: str, compressed=False) -> str:
        index = self.filepath.rfind('/')
        mesh_fp = self.filepath[:(index + 1)] + 'meshes/'

        if not os.path.exists(mesh_fp):
            os.makedirs(mesh_fp)

        ext = '.lz4' if compressed else '.arm'
        return mesh_fp + object_id + ext

    @staticmethod
    def get_shape_keys(mesh):
        rpdat = arm.utils.get_rp()
        if rpdat.arm_morph_target != 'On':
            return False
        # Metaball
        if not hasattr(mesh, 'shape_keys'):
            return False

        shape_keys = mesh.shape_keys
        if not shape_keys:
            return False
        if len(shape_keys.key_blocks) < 2:
            return False
        for shape_key in shape_keys.key_blocks[1:]:
            if not shape_key.mute:
                return True
        return False

    @staticmethod
    def get_morph_uv_index(mesh):
        i = 0
        for uv_layer in mesh.uv_layers:
            if uv_layer.name == 'UVMap_shape_key':
                return i
            i +=1

    def find_bone(self, name: str) -> Optional[Tuple[bpy.types.Bone, Dict]]:
        """Finds the bone reference (a tuple containing the bone object
        and its data) by the given name and returns it."""
        for bone_ref in self.bobject_bone_array.items():
            if bone_ref[0].name == name:
                return bone_ref
        return None

    @staticmethod
    def collect_bone_animation(armature: bpy.types.Object, name: str) -> List[bpy.types.FCurve]:
        path = f"pose.bones[\"{name}\"]."

        if armature.animation_data:
            action = armature.animation_data.action
            if action:
                return [fcurve for fcurve in action.fcurves if fcurve.data_path.startswith(path)]

        return []

    def export_bone(self, armature, bone: bpy.types.Bone, o, action: bpy.types.Action):
        rpdat = arm.utils.get_rp()
        bobject_ref = self.bobject_bone_array.get(bone)

        if rpdat.arm_use_armature_deform_only:
            if not bone.use_deform:
                return

        if bobject_ref:
            o['type'] = STRUCT_IDENTIFIER[bobject_ref["objectType"].value]
            o['name'] = bobject_ref["structName"]
            self.export_bone_transform(armature, bone, o, action)
            self.export_bone_layers(armature, bone, o)
            o['bone_length'] = bone.length

        o['children'] = []
        for sub_bobject in bone.children:
            so = {}
            self.export_bone(armature, sub_bobject, so, action)
            o['children'].append(so)

    @staticmethod
    def export_pose_markers(oanim, action):
        if action.pose_markers is None or len(action.pose_markers) == 0:
            return

        oanim['marker_frames'] = []
        oanim['marker_names'] = []

        for pos_marker in action.pose_markers:
            oanim['marker_frames'].append(int(pos_marker.frame))
            oanim['marker_names'].append(pos_marker.name)

    @staticmethod
    def export_root_motion(oanim, action):
        oanim['root_motion_pos'] = action.arm_root_motion_pos
        oanim['root_motion_rot'] = action.arm_root_motion_rot

    @staticmethod
    def calculate_anim_frame_range(action: bpy.types.Action) -> Tuple[int, int]:
        """Calculates the required frame range of the given action by
        also taking fcurve modifiers into account.

        Modifiers that are not range-restricted are ignored in this
        calculation.
        """
        start = action.frame_range[0]
        end = action.frame_range[1]

        # Take FCurve modifiers into account if they have a restricted
        # frame range
        for fcurve in action.fcurves:
            for modifier in fcurve.modifiers:
                if not modifier.use_restricted_range:
                    continue

                if modifier.frame_start < start:
                    start = modifier.frame_start

                if modifier.frame_end > end:
                    end = modifier.frame_end

        return int(start), int(end)

    @staticmethod
    def export_animation_track(fcurve: bpy.types.FCurve, frame_range: Tuple[int, int], target: str) -> Dict:
        """This function exports a single animation track."""
        out_track = {'target': target, 'frames': [], 'values': []}

        start = frame_range[0]
        end = frame_range[1]

        for frame in range(start, end + 1):
            out_track['frames'].append(frame)
            out_track['values'].append(fcurve.evaluate(frame))

        return out_track

    def export_object_transform(self, bobject: bpy.types.Object, o):
        wrd = bpy.data.worlds['Arm']

        # Static transform
        o['transform'] = {'values': ArmoryExporter.write_matrix(bobject.matrix_local)}

        # Animated transform
        if bobject.animation_data is not None and bobject.type != "ARMATURE":
            action = bobject.animation_data.action

            if action is not None:
                action_name = arm.utils.safestr(arm.utils.asset_name(action))

                fp = self.get_meshes_file_path('action_' + action_name, compressed=ArmoryExporter.compress_enabled)
                assets.add(fp)
                ext = '.lz4' if ArmoryExporter.compress_enabled else ''
                if ext == '' and not wrd.arm_minimize:
                    ext = '.json'

                if 'object_actions' not in o:
                    o['object_actions'] = []
                o['object_actions'].append('action_' + action_name + ext)

                frame_range = self.calculate_anim_frame_range(action)
                out_anim = {
                    'begin': frame_range[0],
                    'end': frame_range[1],
                    'tracks': []
                }

                self.export_pose_markers(out_anim, action)

                unresolved_data_paths = set()
                for fcurve in action.fcurves:
                    data_path = fcurve.data_path

                    try:
                        out_track = self.export_animation_track(fcurve, frame_range, FCURVE_TARGET_NAMES[data_path][fcurve.array_index])
                    except KeyError:
                        if data_path not in FCURVE_TARGET_NAMES:
                            # This can happen if the target is simply not
                            # supported or the action shares both bone
                            # and object transform data (FCURVE_TARGET_NAMES
                            # only contains object transform targets)
                            unresolved_data_paths.add(data_path)
                            continue
                        # Missing target entry for array_index or something else
                        raise

                    if data_path.startswith('delta_'):
                        out_anim['has_delta'] = True

                    out_anim['tracks'].append(out_track)

                if len(unresolved_data_paths) > 0:
                    warning = (
                        f'The action "{action_name}" has fcurve channels with data paths that could not be resolved.'
                        ' This can be caused by the following things:\n'
                        '  - The data paths are not supported.\n'
                        '  - The action exists on both armature and non-armature objects or has both bone and object transform data.'
                    )
                    if wrd.arm_verbose_output:
                        warning += f'\n  Unresolved data paths: {unresolved_data_paths}'
                    else:
                        warning += '\n  To see the list of unresolved data paths please recompile with Armory Project > Verbose Output enabled.'
                    log.warn(warning)

                if True:  # not action.arm_cached or not os.path.exists(fp):
                    if wrd.arm_verbose_output:
                        print('Exporting object action ' + action_name)

                    out_object_action = {
                        'name': action_name,
                        'anim': out_anim,
                        'type': 'object',
                        'data_ref': '',
                        'transform': None
                    }
                    action_file = {'objects': [out_object_action]}
                    arm.utils.write_arm(fp, action_file)

    def process_bone(self, bone: bpy.types.Bone) -> None:
        if ArmoryExporter.export_all_flag or bone.select:
            self.bobject_bone_array[bone] = {
                "objectType": NodeType.BONE,
                "structName": bone.name
            }

        for subbobject in bone.children:
            self.process_bone(subbobject)

    def process_bobject(self, bobject: bpy.types.Object) -> None:
        """Stores some basic information about the given object (its
        name and type).
        If the given object is an armature, its bones are also
        processed.
        """
        if ArmoryExporter.export_all_flag or bobject.select_get():
            btype: NodeType = NodeType.get_bobject_type(bobject)

            if btype is not NodeType.MESH and ArmoryExporter.option_mesh_only:
                return

            self.bobject_array[bobject] = {
                "objectType": btype,
                "structName": arm.utils.asset_name(bobject)
            }

            if bobject.type == "ARMATURE":
                armature: bpy.types.Armature = bobject.data
                if armature:
                    for bone in armature.bones:
                        if not bone.parent:
                            self.process_bone(bone)

        if bobject.arm_instanced == 'Off':
            for subbobject in bobject.children:
                self.process_bobject(subbobject)

    def process_skinned_meshes(self):
        """Iterates through all objects that are exported and ensures
        that bones are actually stored as bones."""
        for bobject_ref in self.bobject_array.items():
            if bobject_ref[1]["objectType"] is NodeType.MESH:
                armature = bobject_ref[0].find_armature()
                if armature is not None:
                    for bone in armature.data.bones:
                        bone_ref = self.find_bone(bone.name)
                        if bone_ref is not None:
                            # If an object is used as a bone, then we
                            # force its type to be a bone
                            bone_ref[1]["objectType"] = NodeType.BONE

    def export_bone_transform(self, armature: bpy.types.Object, bone: bpy.types.Bone, o, action: bpy.types.Action):
        pose_bone = armature.pose.bones.get(bone.name)
        # if pose_bone is not None:
        #     transform = pose_bone.matrix.copy()
        #     if pose_bone.parent is not None:
        #         transform = pose_bone.parent.matrix.inverted_safe() * transform
        # else:
        transform = bone.matrix_local.copy()
        if bone.parent is not None:
            transform = (bone.parent.matrix_local.inverted_safe() @ transform)

        o['transform'] = {'values': ArmoryExporter.write_matrix(transform)}

        fcurve_list = self.collect_bone_animation(armature, bone.name)

        if fcurve_list and pose_bone:
            begin_frame, end_frame = int(action.frame_range[0]), int(action.frame_range[1])

            out_track = {'target': "transform", 'frames': [], 'values': []}
            o['anim'] = {'tracks': [out_track]}

            for i in range(begin_frame, end_frame + 1):
                out_track['frames'].append(i - begin_frame)

            self.bone_tracks.append((out_track['values'], pose_bone))
    
    def export_bone_layers(self, armature: bpy.types.Object, bone: bpy.types.Bone, o):
        layers = []
        if bpy.app.version < (4, 0, 0):
            for layer in bone.layers:
                layers.append(layer)
        else:
            for bonecollection in armature.data.collections:
                layers.append(bonecollection.is_visible)
        o['bone_layers'] = layers

    def use_default_material(self, bobject: bpy.types.Object, o):
        if arm.utils.export_bone_data(bobject):
            o['material_refs'].append('armdefaultskin')
            self.default_skin_material_objects.append(bobject)
        else:
            o['material_refs'].append('armdefault')
            self.default_material_objects.append(bobject)

    def use_default_material_part(self):
        """Select the particle material variant for all particle system
        instance objects that use the armdefault material.
        """
        for ps in bpy.data.particles:
            if ps.render_type != 'OBJECT' or ps.instance_object is None or not ps.instance_object.arm_export:
                continue

            po = ps.instance_object
            if po not in self.object_to_arm_object_dict:
                self.process_bobject(po)
                self.export_object(po)
            o = self.object_to_arm_object_dict[po]

            # Check if the instance object uses the armdefault material
            if len(o['material_refs']) > 0 and o['material_refs'][0] == 'armdefault' and po not in self.default_part_material_objects:
                self.default_part_material_objects.append(po)
                o['material_refs'] = ['armdefaultpart']  # Replace armdefault

    def export_material_ref(self, bobject: bpy.types.Object, material, index, o):
        if material is None:  # Use default for empty mat slots
            self.use_default_material(bobject, o)
            return
        if material not in self.material_array:
            self.material_array.append(material)
        o['material_refs'].append(arm.utils.asset_name(material))

    def export_particle_system_ref(self, psys: bpy.types.ParticleSystem, out_object):
        if psys.settings.instance_object is None or psys.settings.render_type != 'OBJECT' or not psys.settings.instance_object.arm_export:
            return

        self.particle_system_array[psys.settings] = {"structName": psys.settings.name}
        pref = {
            'name': psys.name,
            'seed': psys.seed,
            'particle': psys.settings.name
        }
        out_object['particle_refs'].append(pref)

    @staticmethod
    def get_view3d_area() -> Optional[bpy.types.Area]:
        screen = bpy.context.window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                return area
        return None

    @staticmethod
    def get_viewport_view_matrix() -> Optional[Matrix]:
        play_area = ArmoryExporter.get_view3d_area()
        if play_area is None:
            return None
        for space in play_area.spaces:
            if space.type == 'VIEW_3D':
                return space.region_3d.view_matrix
        return None

    @staticmethod
    def get_viewport_projection_matrix() -> Tuple[Optional[Matrix], bool]:
        play_area = ArmoryExporter.get_view3d_area()
        if play_area is None:
            return None, False
        for space in play_area.spaces:
            if space.type == 'VIEW_3D':
                # return space.region_3d.perspective_matrix # pesp = window * view
                return space.region_3d.window_matrix, space.region_3d.is_perspective
        return None, False

    def write_bone_matrices(self, scene, action):
        # profile_time = time.time()
        begin_frame, end_frame = int(action.frame_range[0]), int(action.frame_range[1])
        if len(self.bone_tracks) > 0:
            for i in range(begin_frame, end_frame + 1):
                scene.frame_set(i)
                for track in self.bone_tracks:
                    values, pose_bone = track[0], track[1]
                    parent = pose_bone.parent
                    if parent:
                        values += ArmoryExporter.write_matrix((parent.matrix.inverted_safe() @ pose_bone.matrix))
                    else:
                        values += ArmoryExporter.write_matrix(pose_bone.matrix)
        # print('Bone matrices exported in ' + str(time.time() - profile_time))

    @staticmethod
    def has_baked_material(bobject, materials):
        for mat in materials:
            if mat is None:
                continue
            baked_mat = mat.name + '_' + bobject.name + '_baked'
            if baked_mat in bpy.data.materials:
                return True
        return False

    @staticmethod
    def create_material_variants(scene: bpy.types.Scene) -> Tuple[List[bpy.types.Material], List[bpy.types.MaterialSlot]]:
        """Creates unique material variants for skinning, tilesheets and
        particles."""
        matvars: List[bpy.types.Material] = []
        matslots: List[bpy.types.MaterialSlot] = []

        bobject: bpy.types.Object
        for bobject in scene.collection.all_objects.values():
            variant_suffix = ''

            # Skinning
            if arm.utils.export_bone_data(bobject):
                variant_suffix = '_armskin'
            # Tilesheets
            elif bobject.arm_tilesheet != '':
                if not bobject.arm_use_custom_tilesheet_node:
                    variant_suffix = '_armtile'
            elif arm.utils.export_morph_targets(bobject):
                variant_suffix = '_armskey'

            if variant_suffix == '':
                continue

            for slot in bobject.material_slots:
                if slot.material is None or slot.material.library is not None:
                    continue
                if slot.material.name.endswith(variant_suffix):
                    continue

                matslots.append(slot)
                mat_name = slot.material.name + variant_suffix
                mat = bpy.data.materials.get(mat_name)
                # Create material variant
                if mat is None:
                    mat = slot.material.copy()
                    mat.name = mat_name
                    if variant_suffix == '_armtile':
                        mat.arm_tilesheet_flag = True
                    matvars.append(mat)
                slot.material = mat

        # Particle and non-particle objects can not share material
        particle_sys: bpy.types.ParticleSettings
        for particle_sys in bpy.data.particles:
            bobject = particle_sys.instance_object
            if bobject is None or particle_sys.render_type != 'OBJECT' or not bobject.arm_export:
                continue

            for slot in bobject.material_slots:
                if slot.material is None or slot.material.library is not None:
                    continue
                if slot.material.name.endswith('_armpart'):
                    continue

                matslots.append(slot)
                mat_name = slot.material.name + '_armpart'
                mat = bpy.data.materials.get(mat_name)
                if mat is None:
                    mat = slot.material.copy()
                    mat.name = mat_name
                    mat.arm_particle_flag = True
                    matvars.append(mat)
                slot.material = mat

        return matvars, matslots

    @staticmethod
    def slot_to_material(bobject: bpy.types.Object, slot: bpy.types.MaterialSlot):
        mat = slot.material
        # Pick up backed material if present
        if mat is not None:
            baked_mat = mat.name + '_' + bobject.name + '_baked'
            if baked_mat in bpy.data.materials:
                mat = bpy.data.materials[baked_mat]
        return mat

    # def ExportMorphWeights(self, node, shapeKeys, scene):
        # action = None
        # curveArray = []
        # indexArray = []

        # if (shapeKeys.animation_data):
        #     action = shapeKeys.animation_data.action
        #     if (action):
        #         for fcurve in action.fcurves:
        #             if ((fcurve.data_path.startswith("key_blocks[")) and (fcurve.data_path.endswith("].value"))):
        #                 keyName = fcurve.data_path.strip("abcdehklopstuvy[]_.")
        #                 if ((keyName[0] == "\"") or (keyName[0] == "'")):
        #                     index = shapeKeys.key_blocks.find(keyName.strip("\"'"))
        #                     if (index >= 0):
        #                         curveArray.append(fcurve)
        #                         indexArray.append(index)
        #                 else:
        #                     curveArray.append(fcurve)
        #                     indexArray.append(int(keyName))

        # if ((not action) and (node.animation_data)):
        #     action = node.animation_data.action
        #     if (action):
        #         for fcurve in action.fcurves:
        #             if ((fcurve.data_path.startswith("data.shape_keys.key_blocks[")) and (fcurve.data_path.endswith("].value"))):
        #                 keyName = fcurve.data_path.strip("abcdehklopstuvy[]_.")
        #                 if ((keyName[0] == "\"") or (keyName[0] == "'")):
        #                     index = shapeKeys.key_blocks.find(keyName.strip("\"'"))
        #                     if (index >= 0):
        #                         curveArray.append(fcurve)
        #                         indexArray.append(index)
        #                 else:
        #                     curveArray.append(fcurve)
        #                     indexArray.append(int(keyName))

        # animated = (len(curveArray) != 0)
        # referenceName = shapeKeys.reference_key.name if (shapeKeys.use_relative) else ""

        # for k in range(len(shapeKeys.key_blocks)):
        #     self.IndentWrite(B"MorphWeight", 0, (k == 0))

        #     if (animated):
        #         self.Write(B" %mw")
        #         self.WriteInt(k)

        #     self.Write(B" (index = ")
        #     self.WriteInt(k)
        #     self.Write(B") {float {")

        #     block = shapeKeys.key_blocks[k]
        #     self.WriteFloat(block.value if (block.name != referenceName) else 1.0)

        #     self.Write(B"}}\n")

        # if (animated):
        #     self.IndentWrite(B"Animation (begin = ", 0, True)
        #     self.WriteFloat((action.frame_range[0]) * self.frameTime)
        #     self.Write(B", end = ")
        #     self.WriteFloat((action.frame_range[1]) * self.frameTime)
        #     self.Write(B")\n")
        #     self.IndentWrite(B"{\n")
        #     self.indentLevel += 1

        #     structFlag = False

        #     for a in range(len(curveArray)):
        #         k = indexArray[a]
        #         target = bytes("mw" + str(k), "UTF-8")

        #         fcurve = curveArray[a]
        #         kind = OpenGexExporter.ClassifyAnimationCurve(fcurve)
        #         if ((kind != kAnimationSampled) and (not self.sampleAnimationFlag)):
        #             self.ExportAnimationTrack(fcurve, kind, target, structFlag)
        #         else:
        #             self.ExportMorphWeightSampledAnimationTrack(shapeKeys.key_blocks[k], target, scene, structFlag)

        #         structFlag = True

        #     self.indentLevel -= 1
        #     self.IndentWrite(B"}\n")

    def export_object(self, bobject: bpy.types.Object, out_parent: Dict = None) -> None:
        """This function exports a single object in the scene and
        includes its name, object reference, material references (for
        meshes), and transform.
        Subobjects are then exported recursively.
        """
        if not bobject.arm_export:
            return

        bobject_ref = self.bobject_array.get(bobject)
        if bobject_ref is not None:
            object_type = bobject_ref["objectType"]

            # Linked object, not present in scene
            if bobject not in self.object_to_arm_object_dict:
                out_object = {
                    'traits': [],
                    'spawn': False
                }
                self.object_to_arm_object_dict[bobject] = out_object

            out_object = self.object_to_arm_object_dict[bobject]
            out_object['type'] = STRUCT_IDENTIFIER[object_type.value]
            out_object['name'] = bobject_ref["structName"]

            if bobject.parent_type == "BONE":
                out_object['parent_bone'] = bobject.parent_bone

            if bobject.hide_render or not bobject.arm_visible:
                out_object['visible'] = False

           if bpy.app.version < (3, 0, 0):
                if not bobject.cycles_visibility:
                    out_object['visible_mesh'] = False
                    out_object['visible_shadow'] = False
            else:
                if not bobject.visible_camera:
                    out_object['visible_mesh'] = False
                if not bobject.visible_shadow:
                    out_object['visible_shadow'] = False

            if not bobject.arm_spawn:
                out_object['spawn'] = False

            out_object['mobile'] = bobject.arm_mobile

            if bobject.instance_type == 'COLLECTION' and bobject.instance_collection is not None:
                out_object['group_ref'] = bobject.instance_collection.name
                self.referenced_collections.append(bobject.instance_collection)

            if bobject.arm_tilesheet != '':
                out_object['tilesheet_ref'] = bobject.arm_tilesheet
                out_object['tilesheet_action_ref'] = bobject.arm_tilesheet_action

            if len(bobject.arm_propertylist) > 0:
                out_object['properties'] = []
                for proplist_item in bobject.arm_propertylist:
                    # Check if the property is a collection (array type).
                    if proplist_item.type_prop == 'array':
                        # Convert the collection to a list. 
                        array_type = proplist_item.array_item_type
                        collection_value = getattr(proplist_item, 'array_prop')
                        property_name = array_type + '_prop'
                        value = [str(getattr(item, property_name)) for item in collection_value]
                    else:
                        # Handle other types of properties.
                        value = getattr(proplist_item, proplist_item.type_prop + '_prop')

                    out_property = {
                        'name': proplist_item.name_prop,
                        'value': value
                    }
                    out_object['properties'].append(out_property)


            # Export the object reference and material references
            objref = bobject.data
            if objref is not None:
                objname = arm.utils.asset_name(objref)

            # LOD
            if bobject.type == 'MESH' and hasattr(objref, 'arm_lodlist') and len(objref.arm_lodlist) > 0:
                out_object['lods'] = []
                for lodlist_item in objref.arm_lodlist:
                    if not lodlist_item.enabled_prop:
                        continue
                    out_lod = {
                        'object_ref': lodlist_item.name,
                        'screen_size': lodlist_item.screen_size_prop
                    }
                    out_object['lods'].append(out_lod)
                if objref.arm_lod_material:
                    out_object['lod_material'] = True

            if object_type is NodeType.MESH:
                if objref not in self.mesh_array:
                    self.mesh_array[objref] = {"structName": objname, "objectTable": [bobject]}
                else:
                    self.mesh_array[objref]["objectTable"].append(bobject)

                oid = arm.utils.safestr(self.mesh_array[objref]["structName"])

                wrd = bpy.data.worlds['Arm']
                if wrd.arm_single_data_file:
                    out_object['data_ref'] = oid
                else:
                    ext = '' if not ArmoryExporter.compress_enabled else '.lz4'
                    if ext == '' and not bpy.data.worlds['Arm'].arm_minimize:
                        ext = '.json'
                    out_object['data_ref'] = 'mesh_' + oid + ext + '/' + oid

                out_object['material_refs'] = []
                for i in range(len(bobject.material_slots)):
                    mat = self.slot_to_material(bobject, bobject.material_slots[i])
                    # Export ref
                    self.export_material_ref(bobject, mat, i, out_object)
                    # Decal flag
                    if mat is not None and mat.arm_decal:
                        out_object['type'] = 'decal_object'
                # No material, mimic cycles and assign default
                if len(out_object['material_refs']) == 0:
                    self.use_default_material(bobject, out_object)

                num_psys = len(bobject.particle_systems)
                if num_psys > 0:
                    out_object['particle_refs'] = []
                    out_object['render_emitter'] = bobject.show_instancer_for_render
                    for i in range(num_psys):
                        self.export_particle_system_ref(bobject.particle_systems[i], out_object)

                aabb = bobject.data.arm_aabb
                if aabb[0] == 0 and aabb[1] == 0 and aabb[2] == 0:
                    self.calc_aabb(bobject)
                out_object['dimensions'] = [aabb[0], aabb[1], aabb[2]]

                # shapeKeys = ArmoryExporter.get_shape_keys(objref)
                # if shapeKeys:
                #     self.ExportMorphWeights(bobject, shapeKeys, scene, out_object)

            elif object_type is NodeType.LIGHT:
                if objref not in self.light_array:
                    self.light_array[objref] = {"structName" : objname, "objectTable" : [bobject]}
                else:
                    self.light_array[objref]["objectTable"].append(bobject)
                out_object['data_ref'] = self.light_array[objref]["structName"]

            elif object_type is NodeType.PROBE:
                if objref not in self.probe_array:
                    self.probe_array[objref] = {"structName" : objname, "objectTable" : [bobject]}
                else:
                    self.probe_array[objref]["objectTable"].append(bobject)

                dist = bobject.data.influence_distance

                if objref.type == "PLANAR":
                    out_object['dimensions'] = [1.0, 1.0, dist]

                # GRID, CUBEMAP
                else:
                    out_object['dimensions'] = [dist, dist, dist]
                out_object['data_ref'] = self.probe_array[objref]["structName"]

            elif object_type is NodeType.CAMERA:
                if out_object.get('spawn', True):  # Also spawn object if 'spawn' attr doesn't exist
                    self.has_spawning_camera = True

                if objref not in self.camera_array:
                    self.camera_array[objref] = {"structName" : objname, "objectTable" : [bobject]}
                else:
                    self.camera_array[objref]["objectTable"].append(bobject)
                out_object['data_ref'] = self.camera_array[objref]["structName"]

            elif object_type is NodeType.SPEAKER:
                if objref not in self.speaker_array:
                    self.speaker_array[objref] = {"structName" : objname, "objectTable" : [bobject]}
                else:
                    self.speaker_array[objref]["objectTable"].append(bobject)
                out_object['data_ref'] = self.speaker_array[objref]["structName"]

            # Export the transform. If object is animated, then animation tracks are exported here
            if bobject.type != 'ARMATURE' and bobject.animation_data is not None:
                action = bobject.animation_data.action
                export_actions = [action]
                for track in bobject.animation_data.nla_tracks:
                    if track.strips is None:
                        continue
                    for strip in track.strips:
                        if strip.action is None or strip.action in export_actions:
                            continue
                        export_actions.append(strip.action)
                orig_action = action
                for a in export_actions:
                    bobject.animation_data.action = a
                    self.export_object_transform(bobject, out_object)
                if len(export_actions) >= 2 and export_actions[0] is None: # No action assigned
                    out_object['object_actions'].insert(0, 'null')
                bobject.animation_data.action = orig_action
            else:
                self.export_object_transform(bobject, out_object)

            # If the object is parented to a bone and is not relative, then undo the bone's transform
            if bobject.parent_type == "BONE":
                armature = bobject.parent.data
                bone = armature.bones[bobject.parent_bone]
                # if not bone.use_relative_parent:
                out_object['parent_bone_connected'] = bone.use_connect
                if bone.use_connect:
                    bone_translation = Vector((0, bone.length, 0)) + bone.head
                    out_object['parent_bone_tail'] = [bone_translation[0], bone_translation[1], bone_translation[2]]
                else:
                    bone_translation = bone.tail - bone.head
                    out_object['parent_bone_tail'] = [bone_translation[0], bone_translation[1], bone_translation[2]]
                    pose_bone = bobject.parent.pose.bones[bobject.parent_bone]
                    bone_translation_pose = pose_bone.tail - pose_bone.head
                    out_object['parent_bone_tail_pose'] = [bone_translation_pose[0], bone_translation_pose[1], bone_translation_pose[2]]

            if bobject.type == 'ARMATURE' and bobject.data is not None:
                # Armature data
                bdata = bobject.data
                # Reference start action
                action = None
                adata = bobject.animation_data

                # Active action
                if adata is not None:
                    action = adata.action
                if action is None:
                    log.warn('Object ' + bobject.name + ' - No action assigned, setting to pose')
                    bobject.animation_data_create()
                    actions = bpy.data.actions
                    action = actions.get('armorypose')
                    if action is None:
                        action = actions.new(name='armorypose')

                # Export actions
                export_actions = [action]
                # hasattr - armature modifier may reference non-parent
                # armature object to deform with
                if hasattr(adata, 'nla_tracks') and adata.nla_tracks is not None:
                    for track in adata.nla_tracks:
                        if track.strips is None:
                            continue
                        for strip in track.strips:
                            if strip.action is None:
                                continue
                            if strip.action.name == action.name:
                                continue
                            export_actions.append(strip.action)

                armatureid = arm.utils.safestr(arm.utils.asset_name(bdata))
                ext = '.lz4' if ArmoryExporter.compress_enabled else ''
                if ext == '' and not bpy.data.worlds['Arm'].arm_minimize:
                    ext = '.json'
                out_object['bone_actions'] = []
                for action in export_actions:
                    aname = arm.utils.safestr(arm.utils.asset_name(action))
                    out_object['bone_actions'].append('action_' + armatureid + '_' + aname + ext)

                clear_op = set()
                skelobj = bobject
                baked_actions = []
                orig_action = bobject.animation_data.action
                if bdata.arm_autobake and bobject.name not in bpy.context.collection.all_objects:
                    clear_op.add('unlink')
                    # Clone bobject and put it in the current scene so
                    # the bake operator can run
                    if bobject.library is not None:
                        skelobj = bobject.copy()
                        clear_op.add('rem')
                    bpy.context.collection.objects.link(skelobj)

                for action in export_actions:
                    aname = arm.utils.safestr(arm.utils.asset_name(action))
                    skelobj.animation_data.action = action
                    fp = self.get_meshes_file_path('action_' + armatureid + '_' + aname, compressed=ArmoryExporter.compress_enabled)
                    assets.add(fp)
                    if not bdata.arm_cached or not os.path.exists(fp):
                        # Store action to use it after autobake was handled
                        original_action = action

                        # Handle autobake
                        if bdata.arm_autobake:
                            sel = bpy.context.selected_objects[:]
                            for _o in sel:
                                _o.select_set(False)
                            skelobj.select_set(True)

                            bake_result = bpy.ops.nla.bake(
                                frame_start=int(action.frame_range[0]),
                                frame_end=int(action.frame_range[1]),
                                step=1,
                                only_selected=False,
                                visual_keying=True
                            )
                            action = skelobj.animation_data.action

                            skelobj.select_set(False)
                            for _o in sel:
                                _o.select_set(True)

                            # Baking creates a new action, but only if it
                            # was successful
                            if 'FINISHED' in bake_result:
                                baked_actions.append(action)

                        wrd = bpy.data.worlds['Arm']
                        if wrd.arm_verbose_output:
                            print('Exporting armature action ' + aname)
                        bones = []
                        self.bone_tracks = []
                        for bone in bdata.bones:
                            if not bone.parent:
                                boneo = {}
                                self.export_bone(skelobj, bone, boneo, action)
                                bones.append(boneo)
                        self.write_bone_matrices(bpy.context.scene, action)
                        if len(bones) > 0 and 'anim' in bones[0]:
                            self.export_pose_markers(bones[0]['anim'], original_action)
                            self.export_root_motion(bones[0]['anim'], original_action)
                        # Save action separately
                        action_obj = {'name': aname, 'objects': bones}
                        arm.utils.write_arm(fp, action_obj)

                # Use relative bone constraints
                out_object['relative_bone_constraints'] = bdata.arm_relative_bone_constraints

                # Restore settings
                skelobj.animation_data.action = orig_action
                for a in baked_actions:
                    bpy.data.actions.remove(a, do_unlink=True)
                if 'unlink' in clear_op:
                    bpy.context.collection.objects.unlink(skelobj)
                if 'rem' in clear_op:
                    bpy.data.objects.remove(skelobj, do_unlink=True)

                # TODO: cache per action
                bdata.arm_cached = True

            if out_parent is None:
                self.output['objects'].append(out_object)
            else:
                out_parent['children'].append(out_object)

            self.post_export_object(bobject, out_object, object_type)

            if not hasattr(out_object, 'children') and len(bobject.children) > 0:
                out_object['children'] = []

        if bobject.arm_instanced == 'Off':
            for subbobject in bobject.children:
                self.export_object(subbobject, out_object)

    def export_skin(self, bobject: bpy.types.Object, armature, export_mesh: bpy.types.Mesh, out_mesh):
        """This function exports all skinning data, which includes the
        skeleton and per-vertex bone influence data"""
        oskin = {}
        out_mesh['skin'] = oskin

        # Write the skin bind pose transform
        otrans = {'values': ArmoryExporter.write_matrix(bobject.matrix_world)}
        oskin['transform'] = otrans

        bone_array = armature.data.bones
        bone_count = len(bone_array)
        rpdat = arm.utils.get_rp()
        max_bones = rpdat.arm_skin_max_bones
        bone_count = min(bone_count, max_bones)

        # Write the bone object reference array
        oskin['bone_ref_array'] = np.empty(bone_count, dtype=object)
        oskin['bone_len_array'] = np.empty(bone_count, dtype='<f4')

        for i in range(bone_count):
            bone_ref = self.find_bone(bone_array[i].name)
            if bone_ref:
                oskin['bone_ref_array'][i] = bone_ref[1]["structName"]
                oskin['bone_len_array'][i] = bone_array[i].length
            else:
                oskin['bone_ref_array'][i] = ""
                oskin['bone_len_array'][i] = 0.0

        # Write the bind pose transform array
        oskin['transformsI'] = []
        for i in range(bone_count):
            skeleton_inv = (armature.matrix_world @ bone_array[i].matrix_local).inverted_safe()
            skeleton_inv = (skeleton_inv @ bobject.matrix_world)
            oskin['transformsI'].append(ArmoryExporter.write_matrix(skeleton_inv))

        # Export the per-vertex bone influence data
        group_remap = []
        for group in bobject.vertex_groups:
            for i in range(bone_count):
                if bone_array[i].name == group.name:
                    group_remap.append(i)
                    break
            else:
                group_remap.append(-1)

        bone_count_array = np.empty(len(export_mesh.loops), dtype='<i2')
        bone_index_array = np.empty(len(export_mesh.loops) * 4, dtype='<i2')
        bone_weight_array = np.empty(len(export_mesh.loops) * 4, dtype='<f4')

        vertices = bobject.data.vertices
        count = 0
        for index, l in enumerate(export_mesh.loops):
            bone_count = 0
            total_weight = 0.0
            bone_values = []
            for g in vertices[l.vertex_index].groups:
                bone_index = group_remap[g.group]
                bone_weight = g.weight
                if bone_index >= 0:  #and bone_weight != 0.0:
                    bone_values.append((bone_weight, bone_index))
                    total_weight += bone_weight
                    bone_count += 1

            if bone_count > 4:
                bone_count = 4
                bone_values.sort(reverse=True)
                bone_values = bone_values[:4]

            bone_count_array[index] = bone_count
            for bv in bone_values:
                bone_weight_array[count] = bv[0]
                bone_index_array[count] = bv[1]
                count += 1

            if total_weight not in (0.0, 1.0):
                normalizer = 1.0 / total_weight
                for i in range(bone_count):
                    bone_weight_array[count - i - 1] *= normalizer

        bone_index_array = bone_index_array[:count]
        bone_weight_array = bone_weight_array[:count]
        bone_weight_array *= 32767
        bone_weight_array = np.array(bone_weight_array, dtype='<i2')

        oskin['bone_count_array'] = bone_count_array
        oskin['bone_index_array'] = bone_index_array
        oskin['bone_weight_array'] = bone_weight_array

        # Bone constraints
        if not armature.data.arm_autobake:
            for bone in armature.pose.bones:
                if len(bone.constraints) > 0:
                    if 'constraints' not in oskin:
                        oskin['constraints'] = []
                    self.add_constraints(bone, oskin, bone=True)

    def export_shape_keys(self, bobject: bpy.types.Object, export_mesh: bpy.types.Mesh, out_mesh):

        # Max shape keys supported
        max_shape_keys = 32
        # Path to store shape key textures
        output_dir = bpy.path.abspath('//') + "MorphTargets"
        name = bobject.data.name
        vert_pos = []
        vert_nor = []
        names = []
        default_values = [0] * max_shape_keys
        # Shape key base mesh
        shape_key_base = bobject.data.shape_keys.key_blocks[0]

        count = 0
        # Loop through all shape keys
        for shape_key in bobject.data.shape_keys.key_blocks[1:]:

            if count > max_shape_keys - 1:
                break
            # get vertex data from shape key
            if shape_key.mute:
                continue
            vert_data = self.get_vertex_data_from_shape_key(shape_key_base, shape_key)
            vert_pos.append(vert_data['pos'])
            vert_nor.append(vert_data['nor'])
            names.append(shape_key.name)
            default_values[count] = shape_key.value

            count += 1

        # No shape keys present or all shape keys are muted
        if count < 1:
            return

        # Convert to array for easy manipulation
        pos_array = np.array(vert_pos)
        nor_array = np.array(vert_nor)

        # Min and Max values of shape key displacements
        max = np.amax(pos_array)
        min = np.amin(pos_array)

        array_size = len(pos_array[0]), len(pos_array)

        # Get best 2^n image size to fit shape key data (min = 2 X 2, max = 4096 X 4096)
        img_size, extra_zeros, block_size = self.get_best_image_size(array_size)

        # Image size required is too large. Skip export
        if img_size < 1:
            log.error(f"""object {bobject.name} contains too many vertices or shape keys to support shape keys export""")
            self.remove_morph_uv_set(bobject)
            return

        # Write data to image
        self.bake_to_image(pos_array, nor_array, max, min, extra_zeros, img_size, name, output_dir)

        # Create a new UV set for shape keys
        self.create_morph_uv_set(bobject, img_size)

        # Export Shape Key names, defaults, etc..
        morph_target = {}
        morph_target['morph_target_data_file'] = name
        morph_target['morph_target_ref'] = names
        morph_target['morph_target_defaults'] = default_values
        morph_target['num_morph_targets'] = count
        morph_target['morph_scale'] = max - min
        morph_target['morph_offset'] = min
        morph_target['morph_img_size'] = img_size
        morph_target['morph_block_size'] = block_size

        out_mesh['morph_target'] = morph_target
        return

    def get_vertex_data_from_shape_key(self, shape_key_base, shape_key_data):

        base_vert_pos = shape_key_base.data.values()
        base_vert_nor = shape_key_base.normals_split_get()
        vert_pos = shape_key_data.data.values()
        vert_nor = shape_key_data.normals_split_get()

        num_verts = len(vert_pos)

        pos = []
        nor = []

        # Loop through all vertices
        for i in range(num_verts):
            # Vertex position relative to base vertex
            pos.append(list(vert_pos[i].co - base_vert_pos[i].co))
            temp = []
            for j in range(3):
                # Vertex normal relative to base vertex
                temp.append(vert_nor[j + i * 3] - base_vert_nor[j + i * 3])
            nor.append(temp)

        return {'pos': pos, 'nor': nor}

    def bake_to_image(self, pos_array, nor_array, pos_max, pos_min, extra_x, img_size, name, output_dir):
        # Scale position data between [0, 1] to bake to image
        pos_array_scaled = np.interp(pos_array, (pos_min, pos_max), (0, 1))
        # Write positions to image
        self.write_output_image(pos_array_scaled, extra_x, img_size, name + '_morph_pos', output_dir)
        # Scale normal data between [0, 1] to bake to image
        nor_array_scaled = np.interp(nor_array, (-1, 1), (0, 1))
        # Write normals to image
        self.write_output_image(nor_array_scaled, extra_x, img_size, name + '_morph_nor', output_dir)

    def write_output_image(self, data, extra_x, img_size, name, output_dir):

        # Pad data with zeros to make up for required number of pixels of 2^n format
        data = np.pad(data, ((0, 0), (0, extra_x), (0, 0)), 'minimum')
        pixel_list = []

        for y in range(len(data)):
            for x in range(len(data[0])):
                # assign RGBA
                pixel_list.append(data[y, x, 0])
                pixel_list.append(data[y, x, 1])
                pixel_list.append(data[y, x, 2])
                pixel_list.append(1.0)

        pixel_list = (pixel_list + [0] * (img_size * img_size * 4 - len(pixel_list)))

        image = bpy.data.images.new(name, width = img_size, height = img_size, is_data = True)
        image.pixels = pixel_list
        output_path = os.path.join(output_dir,  name + ".png")
        image.save_render(output_path, scene= bpy.context.scene)
        bpy.data.images.remove(image)

    def get_best_image_size(self, size):

        for i in range(1, 12):
            block_len = pow(2, i)
            block_height = np.ceil(size[0]/block_len)
            if block_height * size[1] <= block_len:
                extra_zeros_x = block_height * block_len - size[0]
                return pow(2,i), round(extra_zeros_x), block_height

        return 0, 0, 0

    def remove_morph_uv_set(self, obj):
        layer = obj.data.uv_layers.get('UVMap_shape_key')
        if layer is not None:
            obj.data.uv_layers.remove(layer)

    def create_morph_uv_set(self, obj, img_size):
        # Get/ create morph UV set
        if obj.data.uv_layers.get('UVMap_shape_key') is None:
            obj.data.uv_layers.new(name = 'UVMap_shape_key')

        bm = bmesh.new()
        bm.from_mesh(obj.data)
        uv_layer = bm.loops.layers.uv.get('UVMap_shape_key')

        pixel_size = 1.0 / img_size

        i = 0
        j = 0
        # Arrange UVs to match exported image pixels
        for v in bm.verts:
            for l in v.link_loops:
                uv_data = l[uv_layer]
                uv_data.uv = Vector(((i + 0.5) * pixel_size, (j + 0.5) * pixel_size))
            i += 1
            if i > img_size - 1:
                j += 1
                i = 0

        bm.to_mesh(obj.data)
        bm.free()

    def write_mesh(self, bobject: bpy.types.Object, fp, out_mesh):
        if bpy.data.worlds['Arm'].arm_single_data_file:
            self.output['mesh_datas'].append(out_mesh)

        # One mesh data per file
        else:
            mesh_obj = {'mesh_datas': [out_mesh]}
            arm.utils.write_arm(fp, mesh_obj)
            bobject.data.arm_cached = True

    @staticmethod
    def calc_aabb(bobject):
        aabb_center = 0.125 * sum((Vector(b) for b in bobject.bound_box), Vector())
        bobject.data.arm_aabb = [
            abs((bobject.bound_box[6][0] - bobject.bound_box[0][0]) / 2 + abs(aabb_center[0])) * 2,
            abs((bobject.bound_box[6][1] - bobject.bound_box[0][1]) / 2 + abs(aabb_center[1])) * 2,
            abs((bobject.bound_box[6][2] - bobject.bound_box[0][2]) / 2 + abs(aabb_center[2])) * 2
        ]

    @staticmethod
    def get_num_vertex_colors(mesh: bpy.types.Mesh) -> int:
        """Return the amount of vertex color attributes of the given mesh."""
        num = 0
        for attr in mesh.attributes:
            if attr.data_type in ('BYTE_COLOR', 'FLOAT_COLOR'):
                if attr.domain == 'CORNER':
                    num += 1
                else:
                    log.warn(f'Only vertex colors with domain "Face Corner" are supported for now, ignoring "{attr.name}"')

        return num

    @staticmethod
    def get_nth_vertex_colors(mesh: bpy.types.Mesh, n: int) -> Optional[bpy.types.Attribute]:
        """Return the n-th vertex color attribute from the given mesh,
        ignoring all other attribute types and unsupported domains.
        """
        i = 0
        for attr in mesh.attributes:
            if attr.data_type in ('BYTE_COLOR', 'FLOAT_COLOR'):
                if attr.domain != 'CORNER':
                    log.warn(f'Only vertex colors with domain "Face Corner" are supported for now, ignoring "{attr.name}"')
                    continue
                if i == n:
                    return attr
                i += 1
        return None

    @staticmethod
    def check_uv_precision(mesh: bpy.types.Mesh, uv_max_dim: float, max_dim_uvmap: bpy.types.MeshUVLoopLayer, invscale_tex: float):
        """Check whether the pixel size (assuming max_texture_size below)
        can be represented inside the usual [0, 1] UV range with the
        given `invscale_tex` that is used to normalize the UV coords.
        If it is not possible, display a warning.
        """
        max_texture_size = 16384
        pixel_size = 1 / max_texture_size

        # There are fewer distinct floating point values around 1 than
        # around 0, so we use 1 for checking here. We do not check whether
        # UV coords with an absolute value > 1 can be reliably represented.
        if np.float32(1.0) == np.float32(1.0) - np.float32(pixel_size * invscale_tex):
            log.warn(
                f'Mesh "{mesh.name}": The UV map "{max_dim_uvmap.name}"'
                ' contains very large coordinates (max. distance from'
                f' origin: {uv_max_dim}). The UV precision may suffer.'
            )

    def export_mesh_data(self, export_mesh: bpy.types.Mesh, bobject: bpy.types.Object, o, has_armature=False):
        if bpy.app.version < (4, 1, 0):
            export_mesh.calc_normals_split()
        else:
            updated_normals = export_mesh.corner_normals
        export_mesh.calc_loop_triangles()

        loops = export_mesh.loops
        num_verts = len(loops)
        num_uv_layers = len(export_mesh.uv_layers)
        is_baked = self.has_baked_material(bobject, export_mesh.materials)
        num_colors = self.get_num_vertex_colors(export_mesh)
        has_col = self.get_export_vcols(bobject.data) and num_colors > 0
        # Check if shape keys were exported
        has_morph_target = self.get_shape_keys(bobject.data)
        if has_morph_target:
            # Shape keys UV are exported separately, so reduce UV count by 1
            num_uv_layers -= 1
            morph_uv_index = self.get_morph_uv_index(bobject.data)
        has_tex = (self.get_export_uvs(bobject.data) and num_uv_layers > 0) or is_baked
        has_tex1 = has_tex and num_uv_layers > 1
        has_tang = self.has_tangents(bobject.data)

        pdata = np.empty(num_verts * 4, dtype='<f4') # p.xyz, n.z
        ndata = np.empty(num_verts * 2, dtype='<f4') # n.xy
        if has_tex or has_morph_target:
            uv_layers = export_mesh.uv_layers
            maxdim = 1.0
            maxdim_uvlayer = None
            if has_tex:
                t0map = 0 # Get active uvmap
                t0data = np.empty(num_verts * 2, dtype='<f4')
                if uv_layers is not None:
                    if 'UVMap_baked' in uv_layers:
                        for i in range(0, len(uv_layers)):
                            if uv_layers[i].name == 'UVMap_baked':
                                t0map = i
                                break
                    else:
                        for i in range(0, len(uv_layers)):
                            if uv_layers[i].active_render and uv_layers[i].name != 'UVMap_shape_key':
                                t0map = i
                                break
                if has_tex1:
                    for i in range(0, len(uv_layers)):
                        # Not UVMap 0
                        if i != t0map:
                            # Not Shape Key UVMap
                            if has_morph_target and uv_layers[i].name == 'UVMap_shape_key':
                                continue
                            # Neither UVMap 0 Nor Shape Key Map
                            t1map = i
                    t1data = np.empty(num_verts * 2, dtype='<f4')
                # Scale for packed coords
                lay0 = uv_layers[t0map]
                maxdim_uvlayer = lay0
                for v in lay0.data:
                    if abs(v.uv[0]) > maxdim:
                        maxdim = abs(v.uv[0])
                    if abs(v.uv[1]) > maxdim:
                        maxdim = abs(v.uv[1])
                if has_tex1:
                    lay1 = uv_layers[t1map]
                    for v in lay1.data:
                        if abs(v.uv[0]) > maxdim:
                            maxdim = abs(v.uv[0])
                            maxdim_uvlayer = lay1
                        if abs(v.uv[1]) > maxdim:
                            maxdim = abs(v.uv[1])
                            maxdim_uvlayer = lay1
            if has_morph_target:
                morph_data = np.empty(num_verts * 2, dtype='<f4')
                lay2 = uv_layers[morph_uv_index]
                for v in lay2.data:
                    if abs(v.uv[0]) > maxdim:
                        maxdim = abs(v.uv[0])
                        maxdim_uvlayer = lay2
                    if abs(v.uv[1]) > maxdim:
                        maxdim = abs(v.uv[1])
                        maxdim_uvlayer = lay2
            if maxdim > 1:
                o['scale_tex'] = maxdim
                invscale_tex = (1 / o['scale_tex']) * 32767
            else:
                invscale_tex = 1 * 32767
            self.check_uv_precision(export_mesh, maxdim, maxdim_uvlayer, invscale_tex)
            if has_tang:
                try:
                    export_mesh.calc_tangents(uvmap=lay0.name)
                except Exception as e:
                    if hasattr(e, 'message'):
                        log.error(e.message)
                    else:
                        # Assume it was caused because of encountering n-gons
                        log.error(f"""object {bobject.name} contains n-gons in its mesh, so it's impossible to compute tanget space for normal mapping.
Make sure the mesh only has tris/quads.""")

                tangdata = np.empty(num_verts * 3, dtype='<f4')
        if has_col:
            cdata = np.empty(num_verts * 3, dtype='<f4')

        # Scale for packed coords
        maxdim = max(bobject.data.arm_aabb[0], max(bobject.data.arm_aabb[1], bobject.data.arm_aabb[2]))
        if maxdim > 2:
            o['scale_pos'] = maxdim / 2
        else:
            o['scale_pos'] = 1.0
        if has_armature: # Allow up to 2x bigger bounds for skinned mesh
            o['scale_pos'] *= 2.0

        scale_pos = o['scale_pos']
        invscale_pos = (1 / scale_pos) * 32767

        verts = export_mesh.vertices
        if has_tex:
            lay0 = export_mesh.uv_layers[t0map]
            if has_tex1:
                lay1 = export_mesh.uv_layers[t1map]
        if has_morph_target:
            lay2 = export_mesh.uv_layers[morph_uv_index]
        if has_col:
            vcol0 = self.get_nth_vertex_colors(export_mesh, 0).data

        loop: bpy.types.MeshLoop
        for i, loop in enumerate(loops):
            v = verts[loop.vertex_index]
            co = v.co
            normal = loop.normal
            tang = loop.tangent

            i4 = i * 4
            i2 = i * 2
            pdata[i4    ] = co[0]
            pdata[i4 + 1] = co[1]
            pdata[i4 + 2] = co[2]
            pdata[i4 + 3] = normal[2] * scale_pos # Cancel scale
            ndata[i2    ] = normal[0]
            ndata[i2 + 1] = normal[1]
            if has_tex:
                uv = lay0.data[loop.index].uv
                t0data[i2    ] = uv[0]
                t0data[i2 + 1] = 1.0 - uv[1] # Reverse Y
                if has_tex1:
                    uv = lay1.data[loop.index].uv
                    t1data[i2    ] = uv[0]
                    t1data[i2 + 1] = 1.0 - uv[1]
                if has_tang:
                    i3 = i * 3
                    tangdata[i3    ] = tang[0]
                    tangdata[i3 + 1] = tang[1]
                    tangdata[i3 + 2] = tang[2]
            if has_morph_target:
                uv = lay2.data[loop.index].uv
                morph_data[i2    ] = uv[0]
                morph_data[i2 + 1] = 1.0 - uv[1]
            if has_col:
                col = vcol0[loop.index].color
                i3 = i * 3
                cdata[i3    ] = col[0]
                cdata[i3 + 1] = col[1]
                cdata[i3 + 2] = col[2]

        mats = export_mesh.materials
        poly_map = []
        for i in range(max(len(mats), 1)):
            poly_map.append([])
        for poly in export_mesh.polygons:
            poly_map[poly.material_index].append(poly)

        o['index_arrays'] = []

        # map polygon indices to triangle loops
        tri_loops = {}
        for loop in export_mesh.loop_triangles:
            if loop.polygon_index not in tri_loops:
                tri_loops[loop.polygon_index] = []
            tri_loops[loop.polygon_index].append(loop)

        for index, polys in enumerate(poly_map):
            tris = 0
            for poly in polys:
                tris += poly.loop_total - 2
            if tris == 0: # No face assigned
                continue
            prim = np.empty(tris * 3, dtype='<i4')
            v_map = np.empty(tris * 3, dtype='<i4')

            i = 0
            for poly in polys:
                for loop in tri_loops[poly.index]:
                    prim[i    ] = loops[loop.loops[0]].index
                    prim[i + 1] = loops[loop.loops[1]].index
                    prim[i + 2] = loops[loop.loops[2]].index
                    i += 3

            j = 0
            for poly in polys:
                for loop in tri_loops[poly.index]:
                    v_map[j    ] = loops[loop.loops[0]].vertex_index
                    v_map[j + 1] = loops[loop.loops[1]].vertex_index
                    v_map[j + 2] = loops[loop.loops[2]].vertex_index
                    j += 3

            ia = {'values': prim, 'material': 0, 'vertex_map': v_map}
            if len(mats) > 1:
                for i in range(len(mats)):  # Multi-mat mesh
                    if mats[i] == mats[index]:  # Default material for empty slots
                        ia['material'] = i
                        break
            o['index_arrays'].append(ia)

        # Pack
        pdata *= invscale_pos
        ndata *= 32767
        pdata = np.array(pdata, dtype='<i2')
        ndata = np.array(ndata, dtype='<i2')
        if has_tex:
            t0data *= invscale_tex
            t0data = np.array(t0data, dtype='<i2')
            if has_tex1:
                t1data *= invscale_tex
                t1data = np.array(t1data, dtype='<i2')
        if has_morph_target:
            morph_data *= invscale_tex
            morph_data = np.array(morph_data, dtype='<i2')
        if has_col:
            cdata *= 32767
            cdata = np.array(cdata, dtype='<i2')
        if has_tang:
            tangdata *= 32767
            tangdata = np.array(tangdata, dtype='<i2')

        # Output
        o['vertex_arrays'] = []
        o['vertex_arrays'].append({ 'attrib': 'pos', 'values': pdata, 'data': 'short4norm' })
        o['vertex_arrays'].append({ 'attrib': 'nor', 'values': ndata, 'data': 'short2norm' })
        if has_tex:
            o['vertex_arrays'].append({ 'attrib': 'tex', 'values': t0data, 'data': 'short2norm' })
            if has_tex1:
                o['vertex_arrays'].append({ 'attrib': 'tex1', 'values': t1data, 'data': 'short2norm' })
        if has_morph_target:
            o['vertex_arrays'].append({ 'attrib': 'morph', 'values': morph_data, 'data': 'short2norm' })
        if has_col:
            o['vertex_arrays'].append({ 'attrib': 'col', 'values': cdata, 'data': 'short4norm', 'padding': 1 })
        if has_tang:
            o['vertex_arrays'].append({ 'attrib': 'tang', 'values': tangdata, 'data': 'short4norm', 'padding': 1 })

        # If there are multiple morph targets, export them here.
        # if (shapeKeys):
        #     shapeKeys.key_blocks[0].value = 0.0
        #     for m in range(1, len(currentMorphValue)):
        #         shapeKeys.key_blocks[m].value = 1.0
        #         mesh.update()

        #         node.active_shape_key_index = m
        #         morphMesh = node.to_mesh(scene, applyModifiers, "RENDER", True, False)

        #         # Write the morph target position array.

        #         self.IndentWrite(B"VertexArray (attrib = \"position\", morph = ", 0, True)
        #         self.WriteInt(m)
        #         self.Write(B")\n")
        #         self.IndentWrite(B"{\n")
        #         self.indentLevel += 1

        #         self.IndentWrite(B"float[3]\t\t// ")
        #         self.WriteInt(vertexCount)
        #         self.IndentWrite(B"{\n", 0, True)
        #         self.WriteMorphPositionArray3D(unifiedVertexArray, morphMesh.vertices)
        #         self.IndentWrite(B"}\n")

        #         self.indentLevel -= 1
        #         self.IndentWrite(B"}\n\n")

        #         # Write the morph target normal array.

        #         self.IndentWrite(B"VertexArray (attrib = \"normal\", morph = ")
        #         self.WriteInt(m)
        #         self.Write(B")\n")
        #         self.IndentWrite(B"{\n")
        #         self.indentLevel += 1

        #         self.IndentWrite(B"float[3]\t\t// ")
        #         self.WriteInt(vertexCount)
        #         self.IndentWrite(B"{\n", 0, True)
        #         self.WriteMorphNormalArray3D(unifiedVertexArray, morphMesh.vertices, morphMesh.tessfaces)
        #         self.IndentWrite(B"}\n")

        #         self.indentLevel -= 1
        #         self.IndentWrite(B"}\n")

        #         bpy.data.meshes.remove(morphMesh)

    def has_tangents(self, exportMesh):
        return self.get_export_uvs(exportMesh) and self.get_export_tangents(exportMesh) and len(exportMesh.uv_layers) > 0

    def export_mesh(self, object_ref):
        """Exports a single mesh object."""
        # profile_time = time.time()
        table = object_ref[1]["objectTable"]
        bobject = table[0]
        oid = arm.utils.safestr(object_ref[1]["structName"])

        wrd = bpy.data.worlds['Arm']
        if wrd.arm_single_data_file:
            fp = None
        else:
            fp = self.get_meshes_file_path('mesh_' + oid, compressed=ArmoryExporter.compress_enabled)
            assets.add(fp)
            # No export necessary
            if bobject.data.arm_cached and os.path.exists(fp):
                return

        # Mesh users have different modifier stack
        for i in range(1, len(table)):
            if not self.mod_equal_stack(bobject, table[i]):
                log.warn('{0} users {1} and {2} differ in modifier stack - use Make Single User - Object & Data for now'.format(oid, bobject.name, table[i].name))
                break

        if wrd.arm_verbose_output:
            print('Exporting mesh ' + arm.utils.asset_name(bobject.data))

        out_mesh = {'name': oid}
        mesh = object_ref[0]
        struct_flag = False

        # Save the morph state if necessary
        active_shape_key_index = 0
        show_only_shape_key = False
        current_morph_value = 0

        shape_keys = ArmoryExporter.get_shape_keys(mesh)
        if shape_keys:
            # Save the morph state
            active_shape_key_index = bobject.active_shape_key_index
            show_only_shape_key = bobject.show_only_shape_key
            current_morph_value = bobject.active_shape_key.value
            # Reset morph state to base for mesh export
            bobject.active_shape_key_index = 0
            bobject.show_only_shape_key = True
            self.depsgraph.update()

        armature = bobject.find_armature()
        apply_modifiers = not armature

        bobject_eval = bobject.evaluated_get(self.depsgraph) if apply_modifiers else bobject
        export_mesh = bobject_eval.to_mesh()

        # Export shape keys here
        if shape_keys:
            self.export_shape_keys(bobject, export_mesh, out_mesh)
            # Update dependancy after new UV layer was added
            self.depsgraph.update()
            bobject_eval = bobject.evaluated_get(self.depsgraph) if apply_modifiers else bobject
            export_mesh = bobject_eval.to_mesh()

        if export_mesh is None:
            log.warn(oid + ' was not exported')
            return

        if len(export_mesh.uv_layers) > 2:
            log.warn(oid + ' exceeds maximum of 2 UV Maps supported')

        # Update aabb
        self.calc_aabb(bobject)

        # Process meshes
        if ArmoryExporter.optimize_enabled:
            vert_list = exporter_opt.export_mesh_data(self, export_mesh, bobject, out_mesh, has_armature=armature is not None)
            if armature:
                exporter_opt.export_skin(self, bobject, armature, vert_list, out_mesh)
        else:
            self.export_mesh_data(export_mesh, bobject, out_mesh, has_armature=armature is not None)
            if armature:
                self.export_skin(bobject, armature, export_mesh, out_mesh)

        # Restore the morph state after mesh export
        if shape_keys:
            bobject.active_shape_key_index = active_shape_key_index
            bobject.show_only_shape_key = show_only_shape_key
            bobject.active_shape_key.value = current_morph_value
            self.depsgraph.update()

            mesh.update()

        # Check if mesh is using instanced rendering
        instanced_type, instanced_data = self.object_process_instancing(table, out_mesh['scale_pos'])

        # Save offset data for instanced rendering
        if instanced_type > 0:
            out_mesh['instanced_data'] = instanced_data
            out_mesh['instanced_type'] = instanced_type

        # Export usage
        if bobject.data.arm_dynamic_usage:
            out_mesh['dynamic_usage'] = bobject.data.arm_dynamic_usage

        self.write_mesh(bobject, fp, out_mesh)
        # print('Mesh exported in ' + str(time.time() - profile_time))

        if hasattr(bobject, 'evaluated_get'):
            bobject_eval.to_mesh_clear()

    def export_light(self, object_ref):
        """Exports a single light object."""
        rpdat = arm.utils.get_rp()
        light_ref = object_ref[0]
        objtype = light_ref.type
        out_light = {
            'name': object_ref[1]["structName"],
            'type': objtype.lower(),
            'cast_shadow': light_ref.use_shadow,
            'near_plane': light_ref.arm_clip_start,
            'far_plane': light_ref.arm_clip_end,
            'fov': light_ref.arm_fov,
            'color': [light_ref.color[0], light_ref.color[1], light_ref.color[2]],
            'strength': light_ref.energy,
            'shadows_bias': light_ref.arm_shadows_bias * 0.0001
        }
        if rpdat.rp_shadows:
            if objtype == 'POINT':
                out_light['shadowmap_size'] = int(rpdat.rp_shadowmap_cube)
            else:
                out_light['shadowmap_size'] = arm.utils.get_cascade_size(rpdat)
        else:
            out_light['shadowmap_size'] = 0

        if objtype == 'SUN':
            out_light['strength'] *= 0.325
            # Scale bias for ortho light matrix
            out_light['shadows_bias'] *= 20.0
            if out_light['shadowmap_size'] > 1024:
                # Less bias for bigger maps
                out_light['shadows_bias'] *= 1 / (out_light['shadowmap_size'] / 1024)
        elif objtype == 'POINT':
            out_light['strength'] *= 0.01
            out_light['fov'] = 1.5708 # pi/2
            out_light['shadowmap_cube'] = True
            if light_ref.shadow_soft_size > 0.1:
                out_light['light_size'] = light_ref.shadow_soft_size * 10
        elif objtype == 'SPOT':
            out_light['strength'] *= 0.01
            out_light['spot_size'] = math.cos(light_ref.spot_size / 2)
            # Cycles defaults to 0.15
            out_light['spot_blend'] = light_ref.spot_blend / 10
        elif objtype == 'AREA':
            out_light['strength'] *= 0.01
            out_light['size'] = light_ref.size
            out_light['size_y'] = light_ref.size_y

        self.output['light_datas'].append(out_light)

    def export_probe(self, objectRef):
        o = {'name': objectRef[1]["structName"]}
        bo = objectRef[0]

        if bo.type == 'GRID':
            o['type'] = 'grid'
        elif bo.type == 'PLANAR':
            o['type'] = 'planar'
        else:
            o['type'] = 'cubemap'

        self.output['probe_datas'].append(o)

    def export_collection(self, collection: bpy.types.Collection):
        """Exports a single collection."""
        scene_objects = self.scene.collection.all_objects

        out_collection = {
            'name': collection.name,
            'instance_offset': list(collection.instance_offset),
            'object_refs': []
        }

        for bobject in collection.objects:
            if not bobject.arm_export:
                continue

            # Only add unparented objects or objects with their parent
            # outside the collection, then instantiate the full object
            # child tree if the collection gets spawned as a whole
            if bobject.parent is None or bobject.parent.name not in collection.objects:
                asset_name = arm.utils.asset_name(bobject)

                if collection.library:
                    # Add external linked objects
                    # Iron differentiates objects based on their names,
                    # so errors will happen if two objects with the
                    # same name exists. This check is only required
                    # when the object in question is in a library,
                    # otherwise Blender will not allow duplicate names
                    if asset_name in scene_objects:
                        log.warn("skipping export of the object"
                                 f" {bobject.name} (collection"
                                 f" {collection.name}) because it has the same"
                                 " export name as another object in the scene:"
                                 f" {asset_name}")
                        continue

                    self.process_bobject(bobject)
                    self.export_object(bobject)

                out_collection['object_refs'].append(asset_name)

        self.output['groups'].append(out_collection)


    def get_camera_clear_color(self):
        if self.scene.world is None:
            return [0.051, 0.051, 0.051, 1.0]

        if self.scene.world.node_tree is None:
            c = self.scene.world.color
            return [c[0], c[1], c[2], 1.0]

        if 'Background' in self.scene.world.node_tree.nodes:
            background_node = self.scene.world.node_tree.nodes['Background']
            col = background_node.inputs[0].default_value
            strength = background_node.inputs[1].default_value
            ar = [col[0] * strength, col[1] * strength, col[2] * strength, col[3]]
            ar[0] = max(min(ar[0], 1.0), 0.0)
            ar[1] = max(min(ar[1], 1.0), 0.0)
            ar[2] = max(min(ar[2], 1.0), 0.0)
            ar[3] = max(min(ar[3], 1.0), 0.0)
            return ar
        return [0.051, 0.051, 0.051, 1.0]

    @staticmethod
    def extract_projection(o, proj, with_planes=True):
        a = proj[0][0]
        b = proj[1][1]
        c = proj[2][2]
        d = proj[2][3]
        k = (c - 1.0) / (c + 1.0)
        o['fov'] = 2.0 * math.atan(1.0 / b)
        if with_planes:
            o['near_plane'] = (d * (1.0 - k)) / (2.0 * k)
            o['far_plane'] = k * o['near_plane']

    @staticmethod
    def extract_ortho(o, proj):
        # left, right, bottom, top
        o['ortho'] = [-(1 + proj[3][0]) / proj[0][0], \
                       (1 - proj[3][0]) / proj[0][0], \
                      -(1 + proj[3][1]) / proj[1][1], \
                       (1 - proj[3][1]) / proj[1][1]]
        o['near_plane'] = (1 + proj[3][2]) / proj[2][2]
        o['far_plane'] = -(1 - proj[3][2]) / proj[2][2]
        o['near_plane'] *= 2
        o['far_plane'] *= 2

    def export_camera(self, objectRef):
        o = {}
        o['name'] = objectRef[1]["structName"]
        objref = objectRef[0]

        camera = objectRef[1]["objectTable"][0]
        render = self.scene.render
        proj = camera.calc_matrix_camera(
            self.depsgraph,
            x=render.resolution_x,
            y=render.resolution_y,
            scale_x=render.pixel_aspect_x,
            scale_y=render.pixel_aspect_y)
        if objref.type == 'PERSP':
            self.extract_projection(o, proj)
        else:
            self.extract_ortho(o, proj)

        o['frustum_culling'] = objref.arm_frustum_culling
        o['clear_color'] = self.get_camera_clear_color()

        self.output['camera_datas'].append(o)

    def export_speaker(self, objectRef):
        # This function exports a single speaker object
        o = {}
        o['name'] = objectRef[1]["structName"]
        objref = objectRef[0]
        if objref.sound:
            # Packed
            if objref.sound.packed_file is not None:
                unpack_path = arm.utils.get_fp_build() + '/compiled/Assets/unpacked'
                if not os.path.exists(unpack_path):
                    os.makedirs(unpack_path)
                unpack_filepath = unpack_path + '/' + objref.sound.name
                if not os.path.isfile(unpack_filepath) or os.path.getsize(unpack_filepath) != objref.sound.packed_file.size:
                    with open(unpack_filepath, 'wb') as f:
                        f.write(objref.sound.packed_file.data)
                assets.add(unpack_filepath)
            # External
            else:
                assets.add(arm.utils.asset_path(objref.sound.filepath)) # Link sound to assets
            o['sound'] = arm.utils.extract_filename(objref.sound.filepath)
        else:
            o['sound'] = ''
        o['muted'] = objref.muted
        o['volume'] = objref.volume
        o['pitch'] = objref.pitch
        o['volume_min'] = objref.volume_min
        o['volume_max'] = objref.volume_max
        o['attenuation'] = objref.attenuation
        o['distance_max'] = objref.distance_max
        o['distance_reference'] = objref.distance_reference
        o['play_on_start'] = objref.arm_play_on_start
        o['loop'] = objref.arm_loop
        o['stream'] = objref.arm_stream
        self.output['speaker_datas'].append(o)

    def make_default_mat(self, mat_name, mat_objs, is_particle=False):
        if mat_name in bpy.data.materials:
            return
        mat = bpy.data.materials.new(name=mat_name)
        # if default_exists:
            # mat.arm_cached = True
        if is_particle:
            mat.arm_particle_flag = True
        # Empty material roughness
        mat.use_nodes = True
        for node in mat.node_tree.nodes:
            if node.type == 'BSDF_PRINCIPLED':
                node.inputs[7].default_value = 0.25
        o = {}
        o['name'] = mat.name
        o['contexts'] = []
        mat_users = { mat: mat_objs }
        mat_armusers = { mat: [o] }
        make_material.parse(mat, o, mat_users, mat_armusers)
        self.output['material_datas'].append(o)
        bpy.data.materials.remove(mat)
        rpdat = arm.utils.get_rp()
        if not rpdat.arm_culling:
            o['override_context'] = {}
            o['override_context']['cull_mode'] = 'none'

    def signature_traverse(self, node, sign):
        sign += node.type + '-'
        if node.type == 'TEX_IMAGE' and node.image is not None:
            sign += node.image.filepath + '-'
        for inp in node.inputs:
            if inp.is_linked:
                sign = self.signature_traverse(inp.links[0].from_node, sign)
            else:
                # Unconnected socket
                if not hasattr(inp, 'default_value'):
                    sign += 'o'
                elif inp.type in ('RGB', 'RGBA', 'VECTOR'):
                    sign += str(inp.default_value[0])
                    sign += str(inp.default_value[1])
                    sign += str(inp.default_value[2])
                else:
                    sign += str(inp.default_value)
        return sign

    def get_signature(self, mat):
        nodes = mat.node_tree.nodes
        output_node = cycles.node_by_type(nodes, 'OUTPUT_MATERIAL')
        if output_node is not None:
            sign = self.signature_traverse(output_node, '')
            return sign
        return None

    def export_materials(self):
        wrd = bpy.data.worlds['Arm']

        # Keep materials with fake user
        for material in bpy.data.materials:
            if material.use_fake_user and material not in self.material_array:
                self.material_array.append(material)

        # Ensure the same order for merging materials
        self.material_array.sort(key=lambda x: x.name)

        if wrd.arm_batch_materials:
            mat_users = self.material_to_object_dict
            mat_armusers = self.material_to_arm_object_dict
            mat_batch.build(self.material_array, mat_users, mat_armusers)

        transluc_used = False
        overlays_used = False
        blending_used = False
        depthtex_used = False
        decals_used = False
        sss_used = False

        for material in self.material_array:
            # If the material is unlinked, material becomes None
            if material is None:
                continue

            if not material.use_nodes:
                material.use_nodes = True

            # Recache material
            signature = self.get_signature(material)
            if signature != material.signature:
                material.arm_cached = False
            if signature is not None:
                material.signature = signature

            o = {}
            o['name'] = arm.utils.asset_name(material)

            if material.arm_skip_context != '':
                o['skip_context'] = material.arm_skip_context

            rpdat = arm.utils.get_rp()
            if material.arm_two_sided or not rpdat.arm_culling:
                o['override_context'] = {}
                o['override_context']['cull_mode'] = 'none'
            elif material.arm_cull_mode != 'clockwise':
                o['override_context'] = {}
                o['override_context']['cull_mode'] = material.arm_cull_mode

            o['contexts'] = []

            mat_users = self.material_to_object_dict
            mat_armusers = self.material_to_arm_object_dict
            sd, rpasses, needs_sss = make_material.parse(material, o, mat_users, mat_armusers)
            sss_used |= needs_sss

            # Attach MovieTexture
            for con in o['contexts']:
                for tex in con['bind_textures']:
                    if 'source' in tex and tex['source'] == 'movie':
                        trait = {}
                        trait['type'] = 'Script'
                        trait['class_name'] = 'armory.trait.internal.MovieTexture'
                        ArmoryExporter.import_traits.append(trait['class_name'])
                        trait['parameters'] = ['"' + tex['file'] + '"']
                        for user in mat_armusers[material]:
                            user['traits'].append(trait)

            if 'translucent' in rpasses:
                transluc_used = True
            if 'overlay' in rpasses:
                overlays_used = True
            if 'mesh' in rpasses:
                if material.arm_blending:
                    blending_used = True
                if material.arm_depth_read:
                    depthtex_used = True
            if 'decal' in rpasses:
                decals_used = True

            uv_export = False
            tang_export = False
            vcol_export = False
            vs_str = ''
            for con in sd['contexts']:
                for elem in con['vertex_elements']:
                    if len(vs_str) > 0:
                        vs_str += ','
                    vs_str += elem['name']
                    if elem['name'] == 'tang':
                        tang_export = True
                    elif elem['name'] == 'tex':
                        uv_export = True
                    elif elem['name'] == 'col':
                        vcol_export = True
            for con in o['contexts']: # TODO: blend context
                if con['name'] == 'mesh' and material.arm_blending:
                    con['name'] = 'blend'

            if (material.export_tangents != tang_export) or \
               (material.export_uvs != uv_export) or \
               (material.export_vcols != vcol_export):

                material.export_uvs = uv_export
                material.export_vcols = vcol_export
                material.export_tangents = tang_export

                if material in self.material_to_object_dict:
                    mat_users = self.material_to_object_dict[material]
                    for ob in mat_users:
                        ob.data.arm_cached = False

            self.output['material_datas'].append(o)
            material.arm_cached = True

        # Auto-enable render-path features
        rebuild_rp = False
        rpdat = arm.utils.get_rp()
        if rpdat.rp_translucency_state == 'Auto' and rpdat.rp_translucency != transluc_used:
            rpdat.rp_translucency = transluc_used
            rebuild_rp = True
        if rpdat.rp_overlays_state == 'Auto' and rpdat.rp_overlays != overlays_used:
            rpdat.rp_overlays = overlays_used
            rebuild_rp = True
        if rpdat.rp_blending_state == 'Auto' and rpdat.rp_blending != blending_used:
            rpdat.rp_blending = blending_used
            rebuild_rp = True
        if rpdat.rp_depth_texture_state == 'Auto' and rpdat.rp_depth_texture != depthtex_used:
            rpdat.rp_depth_texture = depthtex_used
            rebuild_rp = True
        if rpdat.rp_decals_state == 'Auto' and rpdat.rp_decals != decals_used:
            rpdat.rp_decals = decals_used
            rebuild_rp = True
        if rpdat.rp_sss_state == 'Auto' and rpdat.rp_sss != sss_used:
            rpdat.rp_sss = sss_used
            rebuild_rp = True
        if rebuild_rp:
            make_renderpath.build()

    def export_particle_systems(self):
        if len(self.particle_system_array) > 0:
            self.output['particle_datas'] = []
        for particleRef in self.particle_system_array.items():
            psettings = particleRef[0]

            if psettings is None:
                continue

            if psettings.instance_object is None or psettings.render_type != 'OBJECT':
                continue

            emit_from = 0  # VERT
            if psettings.emit_from == 'FACE':
                emit_from = 1
            elif psettings.emit_from == 'VOLUME':
                emit_from = 2

            out_particlesys = {
                'name': particleRef[1]["structName"],
                'type': 0 if psettings.type == 'EMITTER' else 1, # HAIR
                'loop': psettings.arm_loop,
                # Emission
                'count': int(psettings.count * psettings.arm_count_mult),
                'frame_start': int(psettings.frame_start),
                'frame_end': int(psettings.frame_end),
                'lifetime': psettings.lifetime,
                'lifetime_random': psettings.lifetime_random,
                'emit_from': emit_from,
                # Velocity
                # 'normal_factor': psettings.normal_factor,
                # 'tangent_factor': psettings.tangent_factor,
                # 'tangent_phase': psettings.tangent_phase,
                'object_align_factor': (
                    psettings.object_align_factor[0],
                    psettings.object_align_factor[1],
                    psettings.object_align_factor[2]
                ),
                # 'object_factor': psettings.object_factor,
                'factor_random': psettings.factor_random,
                # Physics
                'physics_type': 1 if psettings.physics_type == 'NEWTON' else 0,
                'particle_size': psettings.particle_size,
                'size_random': psettings.size_random,
                'mass': psettings.mass,
                # Render
                'instance_object': arm.utils.asset_name(psettings.instance_object),
                # Field weights
                'weight_gravity': psettings.effector_weights.gravity
            }

            if psettings.instance_object not in self.object_to_arm_object_dict:
                # The instance object is not yet exported, e.g. because it is
                # in a different scene outside of every (non-scene) collection
                self.process_bobject(psettings.instance_object)
                self.export_object(psettings.instance_object)
            self.object_to_arm_object_dict[psettings.instance_object]['is_particle'] = True

            self.output['particle_datas'].append(out_particlesys)

    def export_tilesheets(self):
        wrd = bpy.data.worlds['Arm']
        if len(wrd.arm_tilesheetlist) > 0:
            self.output['tilesheet_datas'] = []
        for ts in wrd.arm_tilesheetlist:
            o = {}
            o['name'] = ts.name
            o['tilesx'] = ts.tilesx_prop
            o['tilesy'] = ts.tilesy_prop
            o['framerate'] = ts.framerate_prop
            o['actions'] = []
            for tsa in ts.arm_tilesheetactionlist:
                ao = {}
                ao['name'] = tsa.name
                ao['start'] = tsa.start_prop
                ao['end'] = tsa.end_prop
                ao['loop'] = tsa.loop_prop
                o['actions'].append(ao)
            self.output['tilesheet_datas'].append(o)

    def export_world(self):
        """Exports the world of the current scene."""
        world = self.scene.world

        if world is not None:
            world_name = arm.utils.safestr(world.name)

            if world_name not in self.world_array:
                self.world_array.append(world_name)
                out_world = {'name': world_name}

                self.post_export_world(world, out_world)
                self.output['world_datas'].append(out_world)

        elif arm.utils.get_rp().rp_background == 'World':
            log.warn(f'Scene "{self.scene.name}" is missing a world, some render targets will not be cleared')

    def export_objects(self, scene):
        """Exports all supported blender objects.

        References to objects are dictionaries storing the type and
        name of that object.

        Currently supported:
        - Mesh
        - Light
        - Camera
        - Speaker
        - Light Probe
        """
        if not ArmoryExporter.option_mesh_only:
            self.output['light_datas'] = []
            self.output['camera_datas'] = []
            self.output['speaker_datas'] = []

            for light_ref in self.light_array.items():
                self.export_light(light_ref)

            for camera_ref in self.camera_array.items():
                self.export_camera(camera_ref)

            # Keep sounds with fake user
            for sound in bpy.data.sounds:
                if sound.use_fake_user:
                    assets.add(arm.utils.asset_path(sound.filepath))

            for speaker_ref in self.speaker_array.items():
                self.export_speaker(speaker_ref)

            if bpy.data.lightprobes:
                self.output['probe_datas'] = []
                for lightprobe_object in self.probe_array.items():
                    self.export_probe(lightprobe_object)

        self.output['mesh_datas'] = []
        for mesh_ref in self.mesh_array.items():
            self.export_mesh(mesh_ref)

    def execute(self):
        """Exports the scene."""
        profile_time = time.time()
        wrd = bpy.data.worlds['Arm']
        if wrd.arm_verbose_output:
            print('Exporting ' + arm.utils.asset_name(self.scene))
        if self.compress_enabled:
            print('Scene data will be compressed which might take a while.')

        current_frame, current_subframe = self.scene.frame_current, self.scene.frame_subframe

        scene_objects: List[bpy.types.Object] = self.scene.collection.all_objects.values()
        # bobject => blender object
        for bobject in scene_objects:
            # Initialize object export data (map objects to game objects)
            out_object: Dict[str, Any] = {'traits': []}
            self.object_to_arm_object_dict[bobject] = out_object

            # Process
            # Skip objects that have a parent because children are
            # processed recursively
            if not bobject.parent:
                self.process_bobject(bobject)
                # Softbody needs connected triangles, use optimized
                # geometry export
                for mod in bobject.modifiers:
                    if mod.type in ('CLOTH', 'SOFT_BODY'):
                        ArmoryExporter.optimize_enabled = True

        self.process_skinned_meshes()

        self.output['name'] = arm.utils.safestr(self.scene.name)
        if self.filepath.endswith('.lz4'):
            self.output['name'] += '.lz4'
        elif not bpy.data.worlds['Arm'].arm_minimize:
            self.output['name'] += '.json'

        # Create unique material variants for skinning, tilesheets and particles
        matvars, matslots = self.create_material_variants(self.scene)

        # Auto-bones
        rpdat = arm.utils.get_rp()
        if rpdat.arm_skin_max_bones_auto:
            max_bones = 8
            for armature in bpy.data.armatures:
                if max_bones < len(armature.bones):
                    max_bones = len(armature.bones)
            rpdat.arm_skin_max_bones = max_bones

        # Terrain
        if self.scene.arm_terrain_object is not None:
            assets.add_khafile_def('arm_terrain')

            # Append trait
            out_trait = {
                'type': 'Script',
                'class_name': 'armory.trait.internal.TerrainPhysics'
            }
            if 'traits' not in self.output:
                self.output['traits']: List[Dict[str, str]] = []

            self.output['traits'].append(out_trait)

            ArmoryExporter.import_traits.append(out_trait['class_name'])
            ArmoryExporter.export_physics = True

            # Export material
            mat = self.scene.arm_terrain_object.children[0].data.materials[0]
            self.material_array.append(mat)
            # Terrain data
            out_terrain = {
                'name': 'Terrain',
                'sectors_x': self.scene.arm_terrain_sectors[0],
                'sectors_y': self.scene.arm_terrain_sectors[1],
                'sector_size': self.scene.arm_terrain_sector_size,
                'height_scale': self.scene.arm_terrain_height_scale,
                'material_ref': mat.name
            }
            self.output['terrain_datas'] = [out_terrain]
            self.output['terrain_ref'] = 'Terrain'

        # Export objects
        self.output['objects'] = []
        for bobject in scene_objects:
            # Skip objects that have a parent because children are
            # exported recursively
            if not bobject.parent:
                self.export_object(bobject)

        # Export collections
        if bpy.data.collections:
            self.output['groups'] = []
            for collection in bpy.data.collections:
                if collection.name.startswith(('RigidBodyWorld', 'Trait|')):
                    continue

                if self.scene.user_of_id(collection) or collection.library or collection in self.referenced_collections:
                    self.export_collection(collection)

        if not ArmoryExporter.option_mesh_only:
            if self.scene.camera is not None:
                self.output['camera_ref'] = self.scene.camera.name
            else:
                if self.scene.name == arm.utils.get_project_scene_name():
                    log.warn(f'Scene "{self.scene.name}" is missing a camera')

            self.output['material_datas'] = []

            # Object with no material assigned in the scene
            if len(self.default_material_objects) > 0:
                self.make_default_mat('armdefault', self.default_material_objects)
            if len(self.default_skin_material_objects) > 0:
                self.make_default_mat('armdefaultskin', self.default_skin_material_objects)
            if len(bpy.data.particles) > 0:
                self.use_default_material_part()
            if len(self.default_part_material_objects) > 0:
                self.make_default_mat('armdefaultpart', self.default_part_material_objects, is_particle=True)

            self.export_materials()
            self.export_particle_systems()
            self.output['world_datas'] = []
            self.export_world()
            self.export_tilesheets()

            if self.scene.world is not None:
                self.output['world_ref'] = arm.utils.safestr(self.scene.world.name)

            if self.scene.use_gravity:
                self.output['gravity'] = [self.scene.gravity[0], self.scene.gravity[1], self.scene.gravity[2]]
                rbw = self.scene.rigidbody_world
                if rbw is not None:
                    weights = rbw.effector_weights
                    self.output['gravity'][0] *= weights.all * weights.gravity
                    self.output['gravity'][1] *= weights.all * weights.gravity
                    self.output['gravity'][2] *= weights.all * weights.gravity
            else:
                self.output['gravity'] = [0.0, 0.0, 0.0]

        self.export_objects(self.scene)

        # Create Viewport camera
        if bpy.data.worlds['Arm'].arm_play_camera != 'Scene':
            self.create_default_camera(is_viewport_camera=True)

        elif self.scene.camera is not None and self.scene.camera.type != 'CAMERA':
            # Blender doesn't directly allow to set arbitrary objects as cameras,
            # but there is a `Set Active Object as Camera` operator which might
            # cause cases like this to happen
            log.warn(f'Camera "{self.scene.camera.name}" in scene "{self.scene.name}" is not a camera object, using default camera')
            self.create_default_camera()

        # No camera found, create default one
        if not self.has_spawning_camera:
            log.warn(f'Scene "{self.scene.name}" is missing a camera, using default camera')
            self.create_default_camera()

        self.export_scene_traits()

        self.export_canvas_themes()

        # Write embedded data references
        if len(assets.embedded_data) > 0:
            self.output['embedded_datas'] = []
            for file in assets.embedded_data:
                self.output['embedded_datas'].append(file)

        # Write scene file
        arm.utils.write_arm(self.filepath, self.output)

        # Remove created material variants
        for slot in matslots: # Set back to original material
            orig_mat = bpy.data.materials[slot.material.name[:-8]]  # _armskin, _armpart, _armtile
            orig_mat.export_uvs = slot.material.export_uvs
            orig_mat.export_vcols = slot.material.export_vcols
            orig_mat.export_tangents = slot.material.export_tangents
            orig_mat.arm_cached = slot.material.arm_cached
            slot.material = orig_mat
        for mat in matvars:
            bpy.data.materials.remove(mat, do_unlink=True)

        # Restore frame
        if self.scene.frame_current != current_frame:
            self.scene.frame_set(current_frame, subframe=current_subframe)

        if wrd.arm_verbose_output:
            print('Scene exported in {:0.3f}s'.format(time.time() - profile_time))

    def create_default_camera(self, is_viewport_camera=False):
        """Creates the default camera and adds a WalkNavigation trait to it."""
        out_camera = {
            'name': 'DefaultCamera',
            'near_plane': 0.1,
            'far_plane': 100.0,
            'fov': 0.85,
            'frustum_culling': True,
            'clear_color': self.get_camera_clear_color()
        }

        # Set viewport camera projection
        if is_viewport_camera:
            proj, is_persp = self.get_viewport_projection_matrix()
            if proj is not None:
                if is_persp:
                    self.extract_projection(out_camera, proj, with_planes=False)
                else:
                    self.extract_ortho(out_camera, proj)
        self.output['camera_datas'].append(out_camera)

        out_object = {
            'name': 'DefaultCamera',
            'type': 'camera_object',
            'data_ref': 'DefaultCamera',
            'material_refs': [],
            'transform': {}
        }
        viewport_matrix = self.get_viewport_view_matrix()
        if viewport_matrix is not None:
            out_object['transform']['values'] = ArmoryExporter.write_matrix(viewport_matrix.inverted_safe())
            out_object['local_only'] = True
        else:
            out_object['transform']['values'] = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]

        # Add WalkNavigation trait
        trait = {
            'type': 'Script',
            'class_name': 'armory.trait.WalkNavigation'
        }
        out_object['traits'] = [trait]
        ArmoryExporter.import_traits.append(trait['class_name'])

        self.output['objects'].append(out_object)
        self.output['camera_ref'] = 'DefaultCamera'
        self.has_spawning_camera = True

    @staticmethod
    def get_export_tangents(mesh):
        for material in mesh.materials:
            if material is not None and material.export_tangents:
                return True
        return False

    @staticmethod
    def get_export_vcols(mesh):
        for material in mesh.materials:
            if material is not None and material.export_vcols:
                return True
        return False

    @staticmethod
    def get_export_uvs(mesh):
        for material in mesh.materials:
            if material is not None and material.export_uvs:
                return True
        return False

    @staticmethod
    def object_process_instancing(refs, scale_pos):
        instanced_type = 0
        instanced_data = None
        for bobject in refs:
            inst = bobject.arm_instanced
            if inst != 'Off':
                if inst == 'Loc':
                    instanced_type = 1
                    instanced_data = [0.0, 0.0, 0.0] # Include parent
                elif inst == 'Loc + Rot':
                    instanced_type = 2
                    instanced_data = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                elif inst == 'Loc + Scale':
                    instanced_type = 3
                    instanced_data = [0.0, 0.0, 0.0, 1.0, 1.0, 1.0]
                elif inst == 'Loc + Rot + Scale':
                    instanced_type = 4
                    instanced_data = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0]

                for child in bobject.children:
                    if not child.arm_export or child.hide_render:
                        continue
                    if 'Loc' in inst:
                        loc = child.matrix_local.to_translation() # Without parent matrix
                        instanced_data.append(loc.x / scale_pos)
                        instanced_data.append(loc.y / scale_pos)
                        instanced_data.append(loc.z / scale_pos)
                    if 'Rot' in inst:
                        rot = child.matrix_local.to_euler()
                        instanced_data.append(rot.x)
                        instanced_data.append(rot.y)
                        instanced_data.append(rot.z)
                    if 'Scale' in inst:
                        scale = child.matrix_local.to_scale()
                        instanced_data.append(scale.x)
                        instanced_data.append(scale.y)
                        instanced_data.append(scale.z)
                break

            # Instance render collections with same children?
            # elif bobject.instance_type == 'GROUP' and bobject.instance_collection is not None:
            #     instanced_type = 1
            #     instanced_data = []
            #     for child in bpy.data.collections[bobject.instance_collection].objects:
            #         loc = child.matrix_local.to_translation()
            #         instanced_data.append(loc.x)
            #         instanced_data.append(loc.y)
            #         instanced_data.append(loc.z)
            #     break

        return instanced_type, instanced_data

    @staticmethod
    def rigid_body_static(rb):
        return (not rb.enabled and not rb.kinematic) or (rb.type == 'PASSIVE' and not rb.kinematic)

    def post_export_object(self, bobject: bpy.types.Object, o, type):
        # Export traits
        self.export_traits(bobject, o)

        wrd = bpy.data.worlds['Arm']
        phys_enabled = wrd.arm_physics != 'Disabled'
        phys_pkg = 'bullet' if wrd.arm_physics_engine == 'Bullet' else 'oimo'

        # Rigid body trait
        if bobject.rigid_body is not None and phys_enabled:
            ArmoryExporter.export_physics = True
            rb = bobject.rigid_body
            shape = 0  # BOX
            if rb.collision_shape == 'SPHERE':
                shape = 1
            elif rb.collision_shape == 'CONVEX_HULL':
                shape = 2
            elif rb.collision_shape == 'MESH':
                shape = 3
            elif rb.collision_shape == 'CONE':
                shape = 4
            elif rb.collision_shape == 'CYLINDER':
                shape = 5
            elif rb.collision_shape == 'CAPSULE':
                shape = 6
            body_mass = rb.mass
            is_static = self.rigid_body_static(rb)
            if is_static:
                body_mass = 0
            x = {}
            x['type'] = 'Script'
            x['class_name'] = 'armory.trait.physics.' + phys_pkg + '.RigidBody'
            col_group = ''
            for b in rb.collision_collections:
                col_group = ('1' if b else '0') + col_group
            col_mask = ''
            for b in bobject.arm_rb_collision_filter_mask:
                col_mask = ('1' if b else '0') + col_mask

            x['parameters'] = [str(shape), str(body_mass), str(rb.friction), str(rb.restitution), str(int(col_group, 2)), str(int(col_mask, 2)) ]
            lx = bobject.arm_rb_linear_factor[0]
            ly = bobject.arm_rb_linear_factor[1]
            lz = bobject.arm_rb_linear_factor[2]
            ax = bobject.arm_rb_angular_factor[0]
            ay = bobject.arm_rb_angular_factor[1]
            az = bobject.arm_rb_angular_factor[2]
            if bobject.lock_location[0]:
                lx = 0
            if bobject.lock_location[1]:
                ly = 0
            if bobject.lock_location[2]:
                lz = 0
            if bobject.lock_rotation[0]:
                ax = 0
            if bobject.lock_rotation[1]:
                ay = 0
            if bobject.lock_rotation[2]:
                az = 0
            col_margin = rb.collision_margin if rb.use_margin else 0.0
            if rb.use_deactivation:
                deact_lv = rb.deactivate_linear_velocity
                deact_av = rb.deactivate_angular_velocity
                deact_time = bobject.arm_rb_deactivation_time
            else:
                deact_lv = 0.0
                deact_av = 0.0
                deact_time = 0.0
            body_params = {}
            body_params['linearDamping'] = rb.linear_damping
            body_params['angularDamping'] = rb.angular_damping
            body_params['linearFactorsX'] = lx
            body_params['linearFactorsY'] = ly
            body_params['linearFactorsZ'] = lz
            body_params['angularFactorsX'] = ax
            body_params['angularFactorsY'] = ay
            body_params['angularFactorsZ'] = az
            body_params['angularFriction'] = bobject.arm_rb_angular_friction
            body_params['collisionMargin'] = col_margin
            body_params['linearDeactivationThreshold'] = deact_lv
            body_params['angularDeactivationThrshold'] = deact_av
            body_params['deactivationTime'] = deact_time
            body_flags = {}
            body_flags['animated'] = rb.kinematic
            body_flags['trigger'] = bobject.arm_rb_trigger
            body_flags['ccd'] = bobject.arm_rb_ccd
            body_flags['staticObj'] = is_static
            body_flags['useDeactivation'] = rb.use_deactivation
            x['parameters'].append(arm.utils.get_haxe_json_string(body_params))
            x['parameters'].append(arm.utils.get_haxe_json_string(body_flags))
            o['traits'].append(x)

        # Phys traits
        if phys_enabled:
            for modifier in bobject.modifiers:
                if modifier.type in ('CLOTH', 'SOFT_BODY'):
                    self.add_softbody_mod(o, bobject, modifier)
                elif modifier.type == 'HOOK':
                    self.add_hook_mod(o, bobject, modifier.object.name, modifier.vertex_group)

            # Rigid body constraint
            rbc = bobject.rigid_body_constraint
            if rbc is not None and rbc.enabled:
                self.add_rigidbody_constraint(o, bobject, rbc)

        # Camera traits
        if type is NodeType.CAMERA:
            # Viewport camera enabled, attach navigation to active camera
            if self.scene.camera is not None and bobject.name == self.scene.camera.name and bpy.data.worlds['Arm'].arm_play_camera != 'Scene':
                navigation_trait = {}
                navigation_trait['type'] = 'Script'
                navigation_trait['class_name'] = 'armory.trait.WalkNavigation'
                o['traits'].append(navigation_trait)

        # Map objects to materials, can be used in later stages
        for i in range(len(bobject.material_slots)):
            mat = self.slot_to_material(bobject, bobject.material_slots[i])
            if mat in self.material_to_object_dict:
                self.material_to_object_dict[mat].append(bobject)
                self.material_to_arm_object_dict[mat].append(o)
            else:
                self.material_to_object_dict[mat] = [bobject]
                self.material_to_arm_object_dict[mat] = [o]

        # Add UniformsManager trait
        if type is NodeType.MESH:
            uniformManager = {}
            uniformManager['type'] = 'Script'
            uniformManager['class_name'] = 'armory.trait.internal.UniformsManager'
            o['traits'].append(uniformManager)

        # Export constraints
        if len(bobject.constraints) > 0:
            o['constraints'] = []
            self.add_constraints(bobject, o)

        for x in o['traits']:
            ArmoryExporter.import_traits.append(x['class_name'])

    @staticmethod
    def add_constraints(bobject, o, bone=False):
        for constraint in bobject.constraints:
            if constraint.mute:
                continue
            out_constraint = {'name': constraint.name, 'type': constraint.type}

            if bone:
                out_constraint['bone'] = bobject.name
            if hasattr(constraint, 'target') and constraint.target is not None:
                if constraint.type == 'COPY_LOCATION':
                    out_constraint['target'] = constraint.target.name
                    out_constraint['use_x'] = constraint.use_x
                    out_constraint['use_y'] = constraint.use_y
                    out_constraint['use_z'] = constraint.use_z
                    out_constraint['invert_x'] = constraint.invert_x
                    out_constraint['invert_y'] = constraint.invert_y
                    out_constraint['invert_z'] = constraint.invert_z
                    out_constraint['use_offset'] = constraint.use_offset
                    out_constraint['influence'] = constraint.influence
                elif constraint.type == 'CHILD_OF':
                    out_constraint['target'] = constraint.target.name
                    out_constraint['influence'] = constraint.influence

            o['constraints'].append(out_constraint)

    def export_traits(self, bobject: Union[bpy.types.Scene, bpy.types.Object], o):
        if not hasattr(bobject, 'arm_traitlist'):
            return

        for traitlistItem in bobject.arm_traitlist:
            # Do not export disabled traits but still export those
            # with fake user enabled so that nodes like `TraitNode`
            # still work
            if not traitlistItem.enabled_prop and not traitlistItem.fake_user:
                continue

            out_trait = {}
            if traitlistItem.type_prop == 'Logic Nodes' and traitlistItem.node_tree_prop is not None and traitlistItem.node_tree_prop.name != '':
                group_name = arm.utils.safesrc(traitlistItem.node_tree_prop.name[0].upper() + traitlistItem.node_tree_prop.name[1:])

                out_trait['type'] = 'Script'
                out_trait['class_name'] = arm.utils.safestr(bpy.data.worlds['Arm'].arm_project_package) + '.node.' + group_name

            elif traitlistItem.type_prop == 'WebAssembly':
                wpath = os.path.join(arm.utils.get_fp(), 'Bundled', traitlistItem.webassembly_prop + '.wasm')
                if not os.path.exists(wpath):
                    log.warn(f'Wasm "{traitlistItem.webassembly_prop}" not found, skipping')
                    continue

                out_trait['type'] = 'Script'
                out_trait['class_name'] = 'armory.trait.internal.WasmScript'
                out_trait['parameters'] = ["'" + traitlistItem.webassembly_prop + "'"]

            elif traitlistItem.type_prop == 'UI Canvas':
                cpath = os.path.join(arm.utils.get_fp(), 'Bundled', 'canvas', traitlistItem.canvas_name_prop + '.json')
                if not os.path.exists(cpath):
                    log.warn(f'Scene "{self.scene.name}" - Object "{bobject.name}" - Referenced canvas "{traitlistItem.canvas_name_prop}" not found, skipping')
                    continue

                ArmoryExporter.export_ui = True
                out_trait['type'] = 'Script'
                out_trait['class_name'] = 'armory.trait.internal.CanvasScript'
                out_trait['parameters'] = ["'" + traitlistItem.canvas_name_prop + "'"]

                # Read file list and add canvas assets
                assetpath = os.path.join(arm.utils.get_fp(), 'Bundled', 'canvas', traitlistItem.canvas_name_prop + '.files')
                if os.path.exists(assetpath):
                    with open(assetpath,encoding="utf-8") as f:
                        file_list = f.read().splitlines()
                        for asset in file_list:
                            # Relative to the root/Bundled/canvas path
                            asset = asset[6:]  # Strip ../../ to start in project root
                            assets.add(asset)

            # Haxe/Bundled Script
            else:
                # Empty class name, skip
                if traitlistItem.class_name_prop == '':
                    continue

                out_trait['type'] = 'Script'
                if traitlistItem.type_prop == 'Bundled Script':
                    trait_prefix = 'armory.trait.'

                    # TODO: temporary, export single mesh navmesh as obj
                    if traitlistItem.class_name_prop == 'NavMesh' and bobject.type == 'MESH' and bpy.data.worlds['Arm'].arm_navigation != 'Disabled':
                        ArmoryExporter.export_navigation = True

                        nav_path = os.path.join(arm.utils.get_fp_build(), 'compiled', 'Assets', 'navigation')
                        if not os.path.exists(nav_path):
                            os.makedirs(nav_path)
                        nav_filepath = os.path.join(nav_path, 'nav_' + bobject.data.name + '.arm')
                        assets.add(nav_filepath)

                        # TODO: Implement cache
                        # if not os.path.isfile(nav_filepath):
                        # override = {'selected_objects': [bobject]}
                        # bobject.scale.y *= -1
                        # mesh = obj.data
                        # for face in mesh.faces:
                            # face.v.reverse()
                        # bpy.ops.export_scene.obj(override, use_selection=True, filepath=nav_filepath, check_existing=False, use_normals=False, use_uvs=False, use_materials=False)
                        # bobject.scale.y *= -1
                        armature = bobject.find_armature()
                        apply_modifiers = not armature

                        bobject_eval = bobject.evaluated_get(self.depsgraph) if apply_modifiers else bobject
                        export_mesh = bobject_eval.to_mesh()

                        with open(nav_filepath, 'w') as f:
                            for v in export_mesh.vertices:
                                f.write("v %.4f " % (v.co[0] * bobject_eval.scale.x))
                                f.write("%.4f " % (v.co[2] * bobject_eval.scale.z))
                                f.write("%.4f\n" % (v.co[1] * bobject_eval.scale.y)) # Flipped
                            for p in export_mesh.polygons:
                                f.write("f")
                                # Flipped normals
                                for i in reversed(p.vertices):
                                    f.write(" %d" % (i + 1))
                                f.write("\n")

                # Haxe
                else:
                    trait_prefix = arm.utils.safestr(bpy.data.worlds['Arm'].arm_project_package) + '.'
                    hxfile = os.path.join('Sources', (trait_prefix + traitlistItem.class_name_prop).replace('.', '/') + '.hx')
                    if not os.path.exists(os.path.join(arm.utils.get_fp(), hxfile)):
                        # TODO: Halt build here once this check is tested
                        print(f'Armory Error: Scene "{self.scene.name}" - Object "{bobject.name}": Referenced trait file "{hxfile}" not found')

                out_trait['class_name'] = trait_prefix + traitlistItem.class_name_prop

                # Export trait properties
                if traitlistItem.arm_traitpropslist:
                    out_trait['props'] = []
                    for trait_prop in traitlistItem.arm_traitpropslist:
                        out_trait['props'].append(trait_prop.name)
                        out_trait['props'].append(trait_prop.type)

                        if trait_prop.type.endswith("Object"):
                            value = arm.utils.asset_name(trait_prop.value_object)
                        else:
                            value = trait_prop.get_value()

                        out_trait['props'].append(value)

            if not traitlistItem.enabled_prop:
                # If we're here, fake_user is enabled, otherwise we
                # would have skipped this trait already
                ArmoryExporter.import_traits.append(out_trait['class_name'])
            else:
                o['traits'].append(out_trait)

    def export_scene_traits(self) -> None:
        """Exports the traits of the scene and adds some internal traits
        to the scene depending on the exporter settings.
        """
        wrd = bpy.data.worlds['Arm']

        if wrd.arm_physics != 'Disabled' and ArmoryExporter.export_physics:
            if 'traits' not in self.output:
                self.output['traits'] = []
            phys_pkg = 'bullet' if wrd.arm_physics_engine == 'Bullet' else 'oimo'

            out_trait = {
                'type': 'Script',
                'class_name': 'armory.trait.physics.' + phys_pkg + '.PhysicsWorld'
            }

            rbw = self.scene.rigidbody_world
            if rbw is not None and rbw.enabled:
                out_trait['parameters'] = [str(rbw.time_scale), str(rbw.substeps_per_frame), str(rbw.solver_iterations)]

                if phys_pkg == 'bullet':
                    debug_draw_mode = 1 if wrd.arm_bullet_dbg_draw_wireframe else 0
                    debug_draw_mode |= 2 if wrd.arm_bullet_dbg_draw_aabb else 0
                    debug_draw_mode |= 8 if wrd.arm_bullet_dbg_draw_contact_points else 0
                    debug_draw_mode |= 2048 if wrd.arm_bullet_dbg_draw_constraints else 0
                    debug_draw_mode |= 4096 if wrd.arm_bullet_dbg_draw_constraint_limits else 0
                    debug_draw_mode |= 16384 if wrd.arm_bullet_dbg_draw_normals else 0
                    debug_draw_mode |= 32768 if wrd.arm_bullet_dbg_draw_axis_gizmo else 0
                    out_trait['parameters'].append(str(debug_draw_mode))

            self.output['traits'].append(out_trait)

        if wrd.arm_navigation != 'Disabled' and ArmoryExporter.export_navigation:
            if 'traits' not in self.output:
                self.output['traits'] = []
            out_trait = {'type': 'Script', 'class_name': 'armory.trait.navigation.Navigation'}
            self.output['traits'].append(out_trait)

        if wrd.arm_debug_console:
            if 'traits' not in self.output:
                self.output['traits'] = []
            ArmoryExporter.export_ui = True
            # Position
            debug_console_pos_type = 2
            if wrd.arm_debug_console_position == 'Left':
                debug_console_pos_type = 0
            elif wrd.arm_debug_console_position == 'Center':
                debug_console_pos_type = 1
            else:
                debug_console_pos_type = 2
            # Parameters
            out_trait = {
                'type': 'Script',
                'class_name': 'armory.trait.internal.DebugConsole',
                'parameters': [
                    str(arm.utils.get_ui_scale()),
                    str(wrd.arm_debug_console_scale),
                    str(debug_console_pos_type),
                    str(int(wrd.arm_debug_console_visible)),
                    str(int(wrd.arm_debug_console_trace_pos)),
                    str(int(arm.utils.get_debug_console_visible_sc())),
                    str(int(arm.utils.get_debug_console_scale_in_sc())),
                    str(int(arm.utils.get_debug_console_scale_out_sc()))
                ]
            }
            self.output['traits'].append(out_trait)

        if arm.utils.is_livepatch_enabled():
            if 'traits' not in self.output:
                self.output['traits'] = []
            out_trait = {'type': 'Script', 'class_name': 'armory.trait.internal.LivePatch'}
            self.output['traits'].append(out_trait)

        if len(self.scene.arm_traitlist) > 0:
            if 'traits' not in self.output:
                self.output['traits'] = []
            self.export_traits(self.scene, self.output)

        if 'traits' in self.output:
            for out_trait in self.output['traits']:
                ArmoryExporter.import_traits.append(out_trait['class_name'])

    @staticmethod
    def export_canvas_themes():
        path_themes = os.path.join(arm.utils.get_fp(), 'Bundled', 'canvas')
        file_theme = os.path.join(path_themes, "_themes.json")

        # If there is a canvas but no _themes.json, create it so that
        # CanvasScript.hx works
        if os.path.exists(path_themes) and not os.path.exists(file_theme):
            with open(file_theme, "w+", encoding='utf-8'):
                pass
            assets.add(file_theme)

    @staticmethod
    def add_softbody_mod(o, bobject: bpy.types.Object, modifier: Union[bpy.types.ClothModifier, bpy.types.SoftBodyModifier]):
        """Adds a softbody trait to the given object based on the given
        softbody/cloth modifier.
        """
        ArmoryExporter.export_physics = True
        assets.add_khafile_def('arm_physics_soft')

        phys_pkg = 'bullet' if bpy.data.worlds['Arm'].arm_physics_engine == 'Bullet' else 'oimo'
        out_trait = {'type': 'Script', 'class_name': 'armory.trait.physics.' + phys_pkg + '.SoftBody'}
        # ClothModifier
        if modifier.type == 'CLOTH':
            bend = modifier.settings.bending_stiffness
            soft_type = 0
        # SoftBodyModifier
        elif modifier.type == 'SOFT_BODY':
            bend = (modifier.settings.bend + 1.0) * 10
            soft_type = 1
        else:
            # Wrong modifier type
            return

        out_trait['parameters'] = [str(soft_type), str(bend), str(modifier.settings.mass), str(bobject.arm_soft_body_margin)]
        o['traits'].append(out_trait)

        if soft_type == 0:
            ArmoryExporter.add_hook_mod(o, bobject, '', modifier.settings.vertex_group_mass)

    @staticmethod
    def add_hook_mod(o, bobject: bpy.types.Object, target_name, group_name):
        ArmoryExporter.export_physics = True

        phys_pkg = 'bullet' if bpy.data.worlds['Arm'].arm_physics_engine == 'Bullet' else 'oimo'
        out_trait = {'type': 'Script', 'class_name': 'armory.trait.physics.' + phys_pkg + '.PhysicsHook'}

        verts = []
        if group_name != '':
            group = bobject.vertex_groups[group_name].index
            for v in bobject.data.vertices:
                for g in v.groups:
                    if g.group == group:
                        verts.append(v.co.x)
                        verts.append(v.co.y)
                        verts.append(v.co.z)

        out_trait['parameters'] = [f"'{target_name}'", str(verts)]
        o['traits'].append(out_trait)

    @staticmethod
    def add_rigidbody_constraint(o, bobject, rbc):
        rb1 = rbc.object1
        rb2 = rbc.object2
        if rb1 is None or rb2 is None:
            return
        if rbc.type == "MOTOR":
            return

        ArmoryExporter.export_physics = True
        phys_pkg = 'bullet' if bpy.data.worlds['Arm'].arm_physics_engine == 'Bullet' else 'oimo'
        breaking_threshold = rbc.breaking_threshold if rbc.use_breaking else 0

        trait = {
            'type': 'Script',
            'class_name': 'armory.trait.physics.' + phys_pkg + '.PhysicsConstraintExportHelper',
            'parameters': [
                "'" + rb1.name + "'",
                "'" + rb2.name + "'",
                str(rbc.disable_collisions).lower(),
                str(breaking_threshold),
                str(bobject.arm_relative_physics_constraint).lower()
            ]
        }
        if rbc.type == "FIXED":
            trait['parameters'].insert(2,str(0))
        if rbc.type == "POINT":
            trait['parameters'].insert(2,str(1))
        if rbc.type == "GENERIC":
            limits = [
                1 if rbc.use_limit_lin_x else 0,
                rbc.limit_lin_x_lower,
                rbc.limit_lin_x_upper,
                1 if rbc.use_limit_lin_y else 0,
                rbc.limit_lin_y_lower,
                rbc.limit_lin_y_upper,
                1 if rbc.use_limit_lin_z else 0,
                rbc.limit_lin_z_lower,
                rbc.limit_lin_z_upper,
                1 if rbc.use_limit_ang_x else 0,
                rbc.limit_ang_x_lower,
                rbc.limit_ang_x_upper,
                1 if rbc.use_limit_ang_y else 0,
                rbc.limit_ang_y_lower,
                rbc.limit_ang_y_upper,
                1 if rbc.use_limit_ang_z else 0,
                rbc.limit_ang_z_lower,
                rbc.limit_ang_z_upper
            ]
            trait['parameters'].insert(2,str(5))
            trait['parameters'].append(str(limits))
        if rbc.type == "GENERIC_SPRING":
            limits = [
                1 if rbc.use_limit_lin_x else 0,
                rbc.limit_lin_x_lower,
                rbc.limit_lin_x_upper,
                1 if rbc.use_limit_lin_y else 0,
                rbc.limit_lin_y_lower,
                rbc.limit_lin_y_upper,
                1 if rbc.use_limit_lin_z else 0,
                rbc.limit_lin_z_lower,
                rbc.limit_lin_z_upper,
                1 if rbc.use_limit_ang_x else 0,
                rbc.limit_ang_x_lower,
                rbc.limit_ang_x_upper,
                1 if rbc.use_limit_ang_y else 0,
                rbc.limit_ang_y_lower,
                rbc.limit_ang_y_upper,
                1 if rbc.use_limit_ang_z else 0,
                rbc.limit_ang_z_lower,
                rbc.limit_ang_z_upper,
                1 if rbc.use_spring_x else 0,
                rbc.spring_stiffness_x,
                rbc.spring_damping_x,
                1 if rbc.use_spring_y else 0,
                rbc.spring_stiffness_y,
                rbc.spring_damping_y,
                1 if rbc.use_spring_z else 0,
                rbc.spring_stiffness_z,
                rbc.spring_damping_z,
                1 if rbc.use_spring_ang_x else 0,
                rbc.spring_stiffness_ang_x,
                rbc.spring_damping_ang_x,
                1 if rbc.use_spring_ang_y else 0,
                rbc.spring_stiffness_ang_y,
                rbc.spring_damping_ang_y,
                1 if rbc.use_spring_ang_z else 0,
                rbc.spring_stiffness_ang_z,
                rbc.spring_damping_ang_z
            ]
            trait['parameters'].insert(2,str(6))
            trait['parameters'].append(str(limits))
        if rbc.type == "HINGE":
            limits = [
                1 if rbc.use_limit_ang_z else 0,
                rbc.limit_ang_z_lower,
                rbc.limit_ang_z_upper
            ]
            trait['parameters'].insert(2,str(2))
            trait['parameters'].append(str(limits))
        if rbc.type == "SLIDER":
            limits = [
                1 if rbc.use_limit_lin_x else 0,
                rbc.limit_lin_x_lower,
                rbc.limit_lin_x_upper
            ]
            trait['parameters'].insert(2,str(3))
            trait['parameters'].append(str(limits))
        if rbc.type == "PISTON":
            limits = [
                1 if rbc.use_limit_lin_x else 0,
                rbc.limit_lin_x_lower,
                rbc.limit_lin_x_upper,
                1 if rbc.use_limit_ang_x else 0,
                rbc.limit_ang_x_lower,
                rbc.limit_ang_x_upper
            ]
            trait['parameters'].insert(2,str(4))
            trait['parameters'].append(str(limits))
        o['traits'].append(trait)

    @staticmethod
    def post_export_world(world: bpy.types.World, out_world: Dict):
        wrd = bpy.data.worlds['Arm']

        bgcol = world.arm_envtex_color
        # No compositor used
        if '_LDR' in world.world_defs:
            for i in range(0, 3):
                bgcol[i] = pow(bgcol[i], 1.0 / 2.2)
        out_world['background_color'] = arm.utils.color_to_int(bgcol)

        if '_EnvSky' in world.world_defs:
            # Sky data for probe
            out_world['sun_direction'] = list(world.arm_envtex_sun_direction)
            out_world['turbidity'] = world.arm_envtex_turbidity
            out_world['ground_albedo'] = world.arm_envtex_ground_albedo
            out_world['nishita_density'] = list(world.arm_nishita_density)

        disable_hdr = world.arm_envtex_name.endswith('.jpg')

        if '_EnvTex' in world.world_defs or '_EnvImg' in world.world_defs:
            out_world['envmap'] = world.arm_envtex_name.rsplit('.', 1)[0]
            if disable_hdr:
                out_world['envmap'] += '.jpg'
            else:
                out_world['envmap'] += '.hdr'

        # Main probe
        rpdat = arm.utils.get_rp()
        solid_mat = rpdat.arm_material_model == 'Solid'
        arm_irradiance = rpdat.arm_irradiance and not solid_mat
        arm_radiance = rpdat.arm_radiance
        radtex = world.arm_envtex_name.rsplit('.', 1)[0]  # Remove file extension
        irrsharmonics = world.arm_envtex_irr_name
        num_mips = world.arm_envtex_num_mips
        strength = world.arm_envtex_strength

        mobile_mat = rpdat.arm_material_model in ('Mobile', 'Solid')
        if mobile_mat:
            arm_radiance = False

        out_probe = {'name': world.name}
        if arm_irradiance:
            ext = '' if wrd.arm_minimize else '.json'
            out_probe['irradiance'] = irrsharmonics + '_irradiance' + ext
            if arm_radiance:
                out_probe['radiance'] = radtex + '_radiance'
                out_probe['radiance'] += '.jpg' if disable_hdr else '.hdr'
                out_probe['radiance_mipmaps'] = num_mips
        out_probe['strength'] = strength
        out_world['probe'] = out_probe

    @staticmethod
    def mod_equal(mod1: bpy.types.Modifier, mod2: bpy.types.Modifier) -> bool:
        """Compares whether the given modifiers are equal."""
        # https://blender.stackexchange.com/questions/70629
        return all([getattr(mod1, prop, True) == getattr(mod2, prop, False) for prop in mod1.bl_rna.properties.keys()])

    @staticmethod
    def mod_equal_stack(obj1: bpy.types.Object, obj2: bpy.types.Object) -> bool:
        """Returns `True` if the given objects have the same modifiers."""
        if len(obj1.modifiers) == 0 and len(obj2.modifiers) == 0:
            return True
        if len(obj1.modifiers) == 0 or len(obj2.modifiers) == 0:
            return False
        if len(obj1.modifiers) != len(obj2.modifiers):
            return False
        return all([ArmoryExporter.mod_equal(m, obj2.modifiers[i]) for i, m in enumerate(obj1.modifiers)])
