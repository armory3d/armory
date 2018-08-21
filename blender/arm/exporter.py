#  Armory Scene Exporter
#  http://armory3d.org/
#
#  Based on Open Game Engine Exchange
#  http://opengex.org/
#  Export plugin for Blender by Eric Lengyel
#  Copyright 2015, Terathon Software LLC
#
#  This software is licensed under the Creative Commons
#  Attribution-ShareAlike 3.0 Unported License:
#  http://creativecommons.org/licenses/by-sa/3.0/deed.en_US

import os
import bpy
import math
from mathutils import *
import time
import subprocess
import shutil
import arm.utils
import arm.write_probes as write_probes
import arm.assets as assets
import arm.log as log
import arm.material.make as make_material
import arm.material.mat_batch as mat_batch
import arm.make_renderpath as make_renderpath
import arm.material.cycles as cycles

NodeTypeNode = 0
NodeTypeBone = 1
NodeTypeMesh = 2
NodeTypeLight = 3
NodeTypeCamera = 4
NodeTypeSpeaker = 5
NodeTypeDecal = 6
AnimationTypeSampled = 0
AnimationTypeLinear = 1
AnimationTypeBezier = 2
ExportEpsilon = 1.0e-6

structIdentifier = ["object", "bone_object", "mesh_object", "lamp_object", "camera_object", "speaker_object", "decal_object"]

subtranslationName = ["xloc", "yloc", "zloc"]
subrotationName = ["xrot", "yrot", "zrot"]
subscaleName = ["xscl", "yscl", "zscl"]
deltaSubtranslationName = ["dxloc", "dyloc", "dzloc"]
deltaSubrotationName = ["dxrot", "dyrot", "dzrot"]
deltaSubscaleName = ["dxscl", "dyscl", "dzscl"]
axisName = ["x", "y", "z"]

class Vertex:
    # Based on https://github.com/Kupoman/blendergltf/blob/master/blendergltf.py
    __slots__ = ("co", "normal", "uvs", "col", "loop_indices", "index", "bone_weights", "bone_indices", "bone_count", "vertex_index")
    def __init__(self, mesh, loop):
        self.vertex_index = loop.vertex_index
        loop_idx = loop.index
        self.co = mesh.vertices[self.vertex_index].co[:]
        self.normal = loop.normal[:]
        self.uvs = tuple(layer.data[loop_idx].uv[:] for layer in mesh.uv_layers)
        self.col = [0.0, 0.0, 0.0]
        if len(mesh.vertex_colors) > 0:
            self.col = mesh.vertex_colors[0].data[loop_idx].color[:]
        # self.colors = tuple(layer.data[loop_idx].color[:] for layer in mesh.vertex_colors)
        self.loop_indices = [loop_idx]

        # Take the four most influential groups
        # groups = sorted(mesh.vertices[self.vertex_index].groups, key=lambda group: group.weight, reverse=True)
        # if len(groups) > 4:
            # groups = groups[:4]

        # self.bone_weights = [group.weight for group in groups]
        # self.bone_indices = [group.group for group in groups]
        # self.bone_count = len(self.bone_weights)

        self.index = 0

    def __hash__(self):
        return hash((self.co, self.normal, self.uvs))

    def __eq__(self, other):
        eq = (
            (self.co == other.co) and
            (self.normal == other.normal) and
            (self.uvs == other.uvs) and
            (self.col == other.col)
            )

        if eq:
            indices = self.loop_indices + other.loop_indices
            self.loop_indices = indices
            other.loop_indices = indices
        return eq

class ArmoryExporter:
    '''Export to Armory format'''

    def write_matrix(self, matrix):
        return [matrix[0][0], matrix[0][1], matrix[0][2], matrix[0][3],
                matrix[1][0], matrix[1][1], matrix[1][2], matrix[1][3],
                matrix[2][0], matrix[2][1], matrix[2][2], matrix[2][3],
                matrix[3][0], matrix[3][1], matrix[3][2], matrix[3][3]]

    # def write_vector3d(self, vector):
        # return [vector[0], vector[1], vector[2]]

    def get_meshes_file_path(self, object_id, compressed=False):
        index = self.filepath.rfind('/')
        mesh_fp = self.filepath[:(index + 1)] + 'meshes/'
        if not os.path.exists(mesh_fp):
            os.makedirs(mesh_fp)
        ext = '.zip' if compressed else '.arm'
        return mesh_fp + object_id + ext

    @staticmethod
    def get_bobject_type(bobject):
        if bobject.type == "MESH":
            if len(bobject.data.polygons) != 0:
                return NodeTypeMesh
        elif bobject.type == "FONT":
            return NodeTypeMesh
        elif bobject.type == "META": # Metaball
            return NodeTypeMesh
        elif bobject.type == "LIGHT" or bobject.type == "LAMP": # TODO: LAMP is deprecated
            return NodeTypeLight
        elif bobject.type == "CAMERA":
            return NodeTypeCamera
        elif bobject.type == "SPEAKER":
            return NodeTypeSpeaker
        return NodeTypeNode

    @staticmethod
    def get_shape_keys(mesh):
        if not hasattr(mesh, 'shape_keys'): # Metaball
            return None
        shape_keys = mesh.shape_keys
        if shape_keys and len(shape_keys.key_blocks) > 1:
            return shape_keys
        return None

    def find_bone(self, name):
        for bobject_ref in self.bobjectBoneArray.items():
            if bobject_ref[0].name == name:
                return bobject_ref
        return None

    @staticmethod
    def classify_animation_curve(fcurve):
        linear_count = 0
        bezier_count = 0

        for key in fcurve.keyframe_points:
            interp = key.interpolation
            if interp == "LINEAR":
                linear_count += 1
            elif interp == "BEZIER":
                bezier_count += 1
            else:
                return AnimationTypeSampled

        if bezier_count == 0:
            return AnimationTypeLinear
        elif linear_count == 0:
            return AnimationTypeBezier
        return AnimationTypeSampled

    # @staticmethod
    # def animation_keys_different(fcurve):
    #     key_count = len(fcurve.keyframe_points)
    #     if key_count > 0:
    #         key1 = fcurve.keyframe_points[0].co[1]
    #         for i in range(1, key_count):
    #             key2 = fcurve.keyframe_points[i].co[1]
    #             if math.fabs(key2 - key1) > ExportEpsilon:
    #                 return True
    #     return False

    # @staticmethod
    # def animation_tangents_nonzero(fcurve):
    #     key_count = len(fcurve.keyframe_points)
    #     if key_count > 0:
    #         key = fcurve.keyframe_points[0].co[1]
    #         left = fcurve.keyframe_points[0].handle_left[1]
    #         right = fcurve.keyframe_points[0].handle_right[1]
    #         if (math.fabs(key - left) > ExportEpsilon) or (math.fabs(right - key) > ExportEpsilon):
    #             return True
    #         for i in range(1, key_count):
    #             key = fcurve.keyframe_points[i].co[1]
    #             left = fcurve.keyframe_points[i].handle_left[1]
    #             right = fcurve.keyframe_points[i].handle_right[1]
    #             if (math.fabs(key - left) > ExportEpsilon) or (math.fabs(right - key) > ExportEpsilon):
    #                 return True
    #     return False

    # @staticmethod
    # def matrices_different(m1, m2):
    #     for i in range(4):
    #         for j in range(4):
    #             if math.fabs(m1[i][j] - m2[i][j]) > ExportEpsilon:
    #                 return True
    #     return False

    @staticmethod
    def collect_bone_animation(armature, name):
        path = "pose.bones[\"" + name + "\"]."
        curve_array = []

        if armature.animation_data:
            action = armature.animation_data.action
            if action:
                for fcurve in action.fcurves:
                    if fcurve.data_path.startswith(path):
                        curve_array.append(fcurve)
        return curve_array

    # @staticmethod
    # def animation_present(fcurve, kind):
        # if kind != AnimationTypeBezier:
            # return ArmoryExporter.animation_keys_different(fcurve)
        # return ((ArmoryExporter.animation_keys_different(fcurve)) or (ArmoryExporter.animation_tangents_nonzero(fcurve)))

    @staticmethod
    def calc_tangent(v0, v1, v2, uv0, uv1, uv2):
        deltaPos1 = v1 - v0
        deltaPos2 = v2 - v0
        deltaUV1 = uv1 - uv0
        deltaUV2 = uv2 - uv0

        d = (deltaUV1.x * deltaUV2.y - deltaUV1.y * deltaUV2.x)
        if d != 0:
            r = 1.0 / d
        else:
            r = 1.0
        tangent = (deltaPos1 * deltaUV2.y - deltaPos2 * deltaUV1.y) * r
        # bitangent = (deltaPos2 * deltaUV1.x - deltaPos1 * deltaUV2.x) * r
        return tangent

    def export_bone(self, armature, bone, scene, o, action):
        bobjectRef = self.bobjectBoneArray.get(bone)

        if bobjectRef:
            o['type'] = structIdentifier[bobjectRef["objectType"]]
            o['name'] = bobjectRef["structName"]
            self.export_bone_transform(armature, bone, scene, o, action)

        o['children'] = []
        for subbobject in bone.children:
            so = {}
            self.export_bone(armature, subbobject, scene, so, action)
            o['children'].append(so)

    def export_pose_markers(self, oanim, action):
        if action.pose_markers == None or len(action.pose_markers) == 0:
            return
        oanim['marker_frames'] = []
        oanim['marker_names'] = []
        for m in action.pose_markers:
            oanim['marker_frames'].append(int(m.frame))
            oanim['marker_names'].append(m.name)

    def export_object_sampled_animation(self, bobject, scene, o):
        # This function exports animation as full 4x4 matrices for each frame
        animation_flag = False
        # m1 = bobject.matrix_local.copy()
        # Font in
        # for i in range(self.beginFrame, self.endFrame):
        #     scene.frame_set(i)
        #     m2 = bobject.matrix_local
        #     if ArmoryExporter.matrices_different(m1, m2):
        #         animation_flag = True
        #         break
        animation_flag = bobject.animation_data != None and bobject.animation_data.action != None and bobject.type != 'ARMATURE'

        # Font out
        if animation_flag:
            if not 'object_actions' in o:
                o['object_actions'] = []

            action = bobject.animation_data.action
            aname = arm.utils.safestr(arm.utils.asset_name(action))
            fp = self.get_meshes_file_path('action_' + aname, compressed=self.is_compress(bobject.data))
            assets.add(fp)
            ext = '.zip' if self.is_compress(bobject.data) else ''
            if ext == '' and not bpy.data.worlds['Arm'].arm_minimize:
                ext = '.json'
            o['object_actions'].append('action_' + aname + ext)

            oaction = {}
            oaction['sampled'] = True
            oaction['name'] = action.name
            oanim = {}
            oaction['anim'] = oanim

            tracko = {}
            tracko['target'] = "transform"

            tracko['frames'] = []

            begin_frame, end_frame = int(action.frame_range[0]), int(action.frame_range[1])
            end_frame += 1

            for i in range(begin_frame, end_frame):
                tracko['frames'].append(int(i - begin_frame))

            tracko['frames'].append(int(end_frame))

            tracko['values'] = []

            for i in range(begin_frame, end_frame):
                scene.frame_set(i)
                tracko['values'] += self.write_matrix(bobject.matrix_local) # Continuos array of matrix transforms

            oanim['tracks'] = [tracko]
            self.export_pose_markers(oanim, action)

            if True: #action.arm_cached == False or not os.path.exists(fp):
                print('Exporting object action ' + aname)
                actionf = {}
                actionf['objects'] = []
                actionf['objects'].append(oaction)
                oaction['type'] = 'object'
                oaction['name'] = aname
                oaction['data_ref'] = ''
                oaction['transform'] = []
                arm.utils.write_arm(fp, actionf)

    def export_key_frames(self, fcurve):
        keyo = []
        key_count = len(fcurve.keyframe_points)
        for i in range(key_count):
            frame = fcurve.keyframe_points[i].co[0] - self.beginFrame
            keyo.append(int(frame))
        return keyo

    def export_key_frame_control_points(self, fcurve):
        keyminuso = []
        key_count = len(fcurve.keyframe_points)
        for i in range(key_count):
            ctrl = fcurve.keyframe_points[i].handle_left[0] - self.beginFrame
            keyminuso.append(ctrl)
        keypluso = []
        for i in range(key_count):
            ctrl = fcurve.keyframe_points[i].handle_right[0] - self.beginFrame
            keypluso.append(ctrl)

        return keyminuso, keypluso

    def export_key_values(self, fcurve):
        keyo = []
        key_count = len(fcurve.keyframe_points)
        for i in range(key_count):
            value = fcurve.keyframe_points[i].co[1]
            keyo.append(value)

        return keyo

    def export_key_value_control_points(self, fcurve):
        keyminuso = []
        key_count = len(fcurve.keyframe_points)
        for i in range(key_count):
            ctrl = fcurve.keyframe_points[i].handle_left[1]
            keyminuso.append(ctrl)

        keypluso = []
        for i in range(key_count):
            ctrl = fcurve.keyframe_points[i].handle_right[1]
            keypluso.append(ctrl)
        return keyminuso, keypluso

    def export_animation_track(self, fcurve, kind, target, newline):
        # This function exports a single animation track. The curve types for the
        # Frame and Value structures are given by the kind parameter.
        tracko = {}
        tracko['target'] = target
        if kind != AnimationTypeBezier:
            tracko['frames'] = self.export_key_frames(fcurve)
            tracko['values'] = self.export_key_values(fcurve)
        else:
            tracko['curve'] = 'bezier'
            tracko['frames'] = self.export_key_frames(fcurve)
            tracko['values'] = self.export_key_values(fcurve)
            tracko['frames_control_minus'], tracko['frames_control_plus'] = self.export_key_frame_control_points(fcurve)
            tracko['values_control_minus'], tracko['values_control_plus'] = self.export_key_value_control_points(fcurve)
        return tracko

    def export_object_transform(self, bobject, scene, o):
        locAnimCurve = [None, None, None]
        rotAnimCurve = [None, None, None]
        sclAnimCurve = [None, None, None]
        locAnimKind = [0, 0, 0]
        rotAnimKind = [0, 0, 0]
        sclAnimKind = [0, 0, 0]

        deltaPosAnimCurve = [None, None, None]
        deltaRotAnimCurve = [None, None, None]
        deltaSclAnimCurve = [None, None, None]
        deltaPosAnimKind = [0, 0, 0]
        deltaRotAnimKind = [0, 0, 0]
        deltaSclAnimKind = [0, 0, 0]

        locationAnimated = False
        rotationAnimated = False
        scaleAnimated = False
        locAnimated = [False, False, False]
        rotAnimated = [False, False, False]
        sclAnimated = [False, False, False]

        deltaPositionAnimated = False
        deltaRotationAnimated = False
        deltaScaleAnimated = False
        deltaPosAnimated = [False, False, False]
        deltaRotAnimated = [False, False, False]
        deltaSclAnimated = [False, False, False]

        mode = bobject.rotation_mode
        sampledAnimation = ArmoryExporter.sample_animation_flag or mode == "QUATERNION" or mode == "AXIS_ANGLE"

        if not sampledAnimation and bobject.animation_data and bobject.type != 'ARMATURE':
            action = bobject.animation_data.action
            if action:
                for fcurve in action.fcurves:
                    kind = ArmoryExporter.classify_animation_curve(fcurve)
                    if kind != AnimationTypeSampled:
                        if fcurve.data_path == "location":
                            for i in range(3):
                                if (fcurve.array_index == i) and (not locAnimCurve[i]):
                                    locAnimCurve[i] = fcurve
                                    locAnimKind[i] = kind
                                    locAnimated[i] = True
                        elif fcurve.data_path == "delta_location":
                            for i in range(3):
                                if (fcurve.array_index == i) and (not deltaPosAnimCurve[i]):
                                    deltaPosAnimCurve[i] = fcurve
                                    deltaPosAnimKind[i] = kind
                                    deltaPosAnimated[i] = True
                        elif fcurve.data_path == "rotation_euler":
                            for i in range(3):
                                if (fcurve.array_index == i) and (not rotAnimCurve[i]):
                                    rotAnimCurve[i] = fcurve
                                    rotAnimKind[i] = kind
                                    rotAnimated[i] = True
                        elif fcurve.data_path == "delta_rotation_euler":
                            for i in range(3):
                                if (fcurve.array_index == i) and (not deltaRotAnimCurve[i]):
                                    deltaRotAnimCurve[i] = fcurve
                                    deltaRotAnimKind[i] = kind
                                    deltaRotAnimated[i] = True
                        elif fcurve.data_path == "scale":
                            for i in range(3):
                                if (fcurve.array_index == i) and (not sclAnimCurve[i]):
                                    sclAnimCurve[i] = fcurve
                                    sclAnimKind[i] = kind
                                    sclAnimated[i] = True
                        elif fcurve.data_path == "delta_scale":
                            for i in range(3):
                                if (fcurve.array_index == i) and (not deltaSclAnimCurve[i]):
                                    deltaSclAnimCurve[i] = fcurve
                                    deltaSclAnimKind[i] = kind
                                    deltaSclAnimated[i] = True
                        elif (fcurve.data_path == "rotation_axis_angle") or (fcurve.data_path == "rotation_quaternion") or (fcurve.data_path == "delta_rotation_quaternion"):
                            sampledAnimation = True
                            break
                    else:
                        sampledAnimation = True
                        break

        locationAnimated = locAnimated[0] | locAnimated[1] | locAnimated[2]
        rotationAnimated = rotAnimated[0] | rotAnimated[1] | rotAnimated[2]
        scaleAnimated = sclAnimated[0] | sclAnimated[1] | sclAnimated[2]

        deltaPositionAnimated = deltaPosAnimated[0] | deltaPosAnimated[1] | deltaPosAnimated[2]
        deltaRotationAnimated = deltaRotAnimated[0] | deltaRotAnimated[1] | deltaRotAnimated[2]
        deltaScaleAnimated = deltaSclAnimated[0] | deltaSclAnimated[1] | deltaSclAnimated[2]

        if (sampledAnimation) or ((not locationAnimated) and (not rotationAnimated) and (not scaleAnimated) and (not deltaPositionAnimated) and (not deltaRotationAnimated) and (not deltaScaleAnimated)):
            # If there's no keyframe animation at all, then write the object transform as a single 4x4 matrix.
            # We might still be exporting sampled animation below.
            o['transform'] = {}

            if sampledAnimation:
                o['transform']['target'] = "transform"

            o['transform']['values'] = self.write_matrix(bobject.matrix_local)

            if sampledAnimation:
                self.export_object_sampled_animation(bobject, scene, o)
        else: # Animated
            structFlag = False

            o['transform'] = {}
            o['transform']['values'] = self.write_matrix(bobject.matrix_local)

            if not 'object_actions' in o:
                o['object_actions'] = []

            action = bobject.animation_data.action
            aname = arm.utils.safestr(arm.utils.asset_name(action))
            fp = self.get_meshes_file_path('action_' + aname, compressed=self.is_compress(bobject.data))
            assets.add(fp)
            ext = '.zip' if self.is_compress(bobject.data) else ''
            if ext == '' and not bpy.data.worlds['Arm'].arm_minimize:
                ext = '.json'
            o['object_actions'].append('action_' + aname + ext)

            oaction = {}
            oaction['name'] = action.name

            # Export the animation tracks
            oanim = {}
            oaction['anim'] = oanim
            oanim['begin'] = int(action.frame_range[0] - self.beginFrame)
            oanim['end'] = int(action.frame_range[1] - self.beginFrame)
            oanim['tracks'] = []
            self.export_pose_markers(oanim, action)

            if locationAnimated:
                for i in range(3):
                    if locAnimated[i]:
                        tracko = self.export_animation_track(locAnimCurve[i], locAnimKind[i], subtranslationName[i], structFlag)
                        oanim['tracks'].append(tracko)
                        structFlag = True

            if rotationAnimated:
                for i in range(3):
                    if rotAnimated[i]:
                        tracko = self.export_animation_track(rotAnimCurve[i], rotAnimKind[i], subrotationName[i], structFlag)
                        oanim['tracks'].append(tracko)
                        structFlag = True

            if scaleAnimated:
                for i in range(3):
                    if sclAnimated[i]:
                        tracko = self.export_animation_track(sclAnimCurve[i], sclAnimKind[i], subscaleName[i], structFlag)
                        oanim['tracks'].append(tracko)
                        structFlag = True

            if deltaPositionAnimated:
                for i in range(3):
                    if deltaPosAnimated[i]:
                        tracko = self.export_animation_track(deltaPosAnimCurve[i], deltaPosAnimKind[i], deltaSubtranslationName[i], structFlag)
                        oanim['tracks'].append(tracko)
                        oanim['has_delta'] = True
                        structFlag = True

            if deltaRotationAnimated:
                for i in range(3):
                    if deltaRotAnimated[i]:
                        tracko = self.export_animation_track(deltaRotAnimCurve[i], deltaRotAnimKind[i], deltaSubrotationName[i], structFlag)
                        oanim['tracks'].append(tracko)
                        oanim['has_delta'] = True
                        structFlag = True

            if deltaScaleAnimated:
                for i in range(3):
                    if deltaSclAnimated[i]:
                        tracko = self.export_animation_track(deltaSclAnimCurve[i], deltaSclAnimKind[i], deltaSubscaleName[i], structFlag)
                        oanim['tracks'].append(tracko)
                        oanim['has_delta'] = True
                        structFlag = True

            if True: #action.arm_cached == False or not os.path.exists(fp):
                print('Exporting object action ' + aname)
                actionf = {}
                actionf['objects'] = []
                actionf['objects'].append(oaction)
                oaction['type'] = 'object'
                oaction['name'] = aname
                oaction['data_ref'] = ''
                oaction['transform'] = []
                arm.utils.write_arm(fp, actionf)

    def process_bone(self, bone):
        if ArmoryExporter.export_all_flag or bone.select:
            self.bobjectBoneArray[bone] = {"objectType" : NodeTypeBone, "structName" : bone.name}

        for subbobject in bone.children:
            self.process_bone(subbobject)

    def process_bobject(self, bobject):
        if ArmoryExporter.export_all_flag or bobject.select:
            btype = ArmoryExporter.get_bobject_type(bobject)

            if ArmoryExporter.option_mesh_only and btype != NodeTypeMesh:
                return

            self.bobjectArray[bobject] = {"objectType" : btype, "structName" : arm.utils.asset_name(bobject)}

            if bobject.type == "ARMATURE":
                skeleton = bobject.data
                if skeleton:
                    for bone in skeleton.bones:
                        if not bone.parent:
                            self.process_bone(bone)

        if bobject.type != 'MESH' or bobject.arm_instanced == False:
            for subbobject in bobject.children:
                self.process_bobject(subbobject)

    def process_skinned_meshes(self):
        for bobjectRef in self.bobjectArray.items():
            if bobjectRef[1]["objectType"] == NodeTypeMesh:
                armature = bobjectRef[0].find_armature()
                if armature:
                    for bone in armature.data.bones:
                        boneRef = self.find_bone(bone.name)
                        if boneRef:
                            # If an object is used as a bone, then we force its type to be a bone
                            boneRef[1]["objectType"] = NodeTypeBone

    def export_bone_transform(self, armature, bone, scene, o, action):
        
        pose_bone = armature.pose.bones.get(bone.name)
        # if pose_bone != None:
        #     transform = pose_bone.matrix.copy()
        #     if pose_bone.parent != None:
        #         transform = pose_bone.parent.matrix.inverted_safe() * transform
        # else:
        transform = bone.matrix_local.copy()
        if bone.parent != None:
            transform = self.mulmat(bone.parent.matrix_local.inverted_safe(), transform)

        o['transform'] = {}
        o['transform']['values'] = self.write_matrix(transform)

        curve_array = self.collect_bone_animation(armature, bone.name)
        animation = len(curve_array) != 0 or ArmoryExporter.sample_animation_flag

        if animation and pose_bone:
            begin_frame, end_frame = int(action.frame_range[0]), int(action.frame_range[1])

            # animation_flag = False
            # m1 = pose_bone.matrix.copy()
            # for i in range(begin_frame, end_frame):
            #     scene.frame_set(i)
            #     m2 = pose_bone.matrix
            #     if ArmoryExporter.matrices_different(m1, m2):
            #         animation_flag = True
            #         break
            # if animation_flag:

            o['anim'] = {}
            tracko = {}
            o['anim']['tracks'] = [tracko]
            tracko['target'] = "transform"
            tracko['frames'] = []
            for i in range(begin_frame, end_frame + 1):
                tracko['frames'].append(i - begin_frame)

            tracko['values'] = []
            self.bone_tracks.append((tracko['values'], pose_bone))

    def use_default_material(self, bobject, o):
        if arm.utils.export_bone_data(bobject):
            o['material_refs'].append('armdefaultskin')
            self.defaultSkinMaterialObjects.append(bobject)
        else:
            o['material_refs'].append('armdefault')
            self.defaultMaterialObjects.append(bobject)

    def export_material_ref(self, bobject, material, index, o):
        if material == None: # Use default for empty mat slots
            self.use_default_material(bobject, o)
            return
        if not material in self.materialArray:
            self.materialArray.append(material)
        o['material_refs'].append(arm.utils.asset_name(material))

    def export_particle_system_ref(self, psys, index, o):
        if psys.settings in self.particleSystemArray: # or not modifier.show_render:
            return

        if psys.settings.dupli_object == None or psys.settings.render_type != 'OBJECT':
             return

        self.particleSystemArray[psys.settings] = {"structName" : psys.settings.name}
        pref = {}
        pref['name'] = psys.name
        pref['seed'] = psys.seed
        pref['particle'] = psys.settings.name
        o['particle_refs'].append(pref)

    def get_view3d_area(self):
        screen = bpy.context.window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                return area
        return None

    def get_viewport_view_matrix(self):
        play_area = self.get_view3d_area()
        if play_area == None:
            return None
        for space in play_area.spaces:
            if space.type == 'VIEW_3D':
                return space.region_3d.view_matrix
        return None

    def get_viewport_projection_matrix(self):
        play_area = self.get_view3d_area()
        if play_area == None:
            return None, False
        for space in play_area.spaces:
            if space.type == 'VIEW_3D':
                # return space.region_3d.perspective_matrix # pesp = window * view
                return space.region_3d.window_matrix, space.region_3d.is_perspective
        return None, False

    def get_viewport_panels_w(self):
        w = 0
        screen = bpy.context.window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'TOOLS' or region.type == 'UI':
                        if region.width > 1:
                            w += region.width
        return w

    def get_viewport_w(self):
        screen = bpy.context.window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'HEADER': # Use header to report full width, panels included
                        return region.width
        return 0

    def write_bone_matrices(self, scene, action):
        begin_frame, end_frame = int(action.frame_range[0]), int(action.frame_range[1])
        if len(self.bone_tracks) > 0:
            for i in range(begin_frame, end_frame + 1):
                scene.frame_set(i)
                for track in self.bone_tracks:
                    values, pose_bone = track[0], track[1]
                    parent = pose_bone.parent
                    if parent:
                        values += self.write_matrix(self.mulmat(parent.matrix.inverted_safe(), pose_bone.matrix))
                    else:
                        values += self.write_matrix(pose_bone.matrix)

    def has_baked_material(self, bobject, materials):
        for mat in materials:
            if mat == None:
                continue
            baked_mat = mat.name + '_' + bobject.name + '_baked'
            if baked_mat in bpy.data.materials:
                return True
        return False

    def slot_to_material(self, bobject, slot):
        mat = slot.material
        # Pick up backed material if present
        if mat != None:
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
        #     self.WriteFloat((action.frame_range[0] - self.beginFrame) * self.frameTime)
        #     self.Write(B", end = ")
        #     self.WriteFloat((action.frame_range[1] - self.beginFrame) * self.frameTime)
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

    def export_object(self, bobject, scene, parento=None):
        # This function exports a single object in the scene and includes its name,
        # object reference, material references (for meshes), and transform.
        # Subobjects are then exported recursively.
        if self.preprocess_object(bobject) == False:
            return

        bobjectRef = self.bobjectArray.get(bobject)
        if bobjectRef:
            type = bobjectRef["objectType"]

            # Linked object, not present in scene
            if bobject not in self.objectToArmObjectDict:
                o = {}
                o['traits'] = []
                o['spawn'] = False
                self.objectToArmObjectDict[bobject] = o

            o = self.objectToArmObjectDict[bobject]
            o['type'] = structIdentifier[type]
            o['name'] = bobjectRef["structName"]

            if bobject.parent_type == "BONE":
                o['parent_bone'] = bobject.parent_bone

            if bobject.hide_render or bobject.arm_visible == False:
                o['visible'] = False

            if not bobject.cycles_visibility.camera:
                o['visible_mesh'] = False

            if not bobject.cycles_visibility.shadow:
                o['visible_shadow'] = False

            if bobject.arm_spawn == False:
                o['spawn'] = False

            if bobject.arm_mobile == False:
                o['mobile'] = False

            if bobject.dupli_type == 'GROUP' and bobject.dupli_group != None:
                o['group_ref'] = bobject.dupli_group.name

            if hasattr(bobject, 'users_group') and bobject.users_group != None and len(bobject.users_group) > 0:
                o['groups'] = []
                for g in bobject.users_group:
                    if g.name.startswith('RigidBodyWorld') or g.name.startswith('Trait|'):
                        continue
                    o['groups'].append(g.name)

            if bobject.arm_tilesheet != '':
                o['tilesheet_ref'] = bobject.arm_tilesheet
                o['tilesheet_action_ref'] = bobject.arm_tilesheet_action

            layer_found = False
            if bpy.app.version >= (2, 80, 1):
                layer_found = True
            else:
                for l in self.active_layers:
                    if bobject.layers[l] == True:
                        layer_found = True
                        break
            if layer_found == False:
                o['spawn'] = False

            # Export the object reference and material references
            objref = bobject.data
            if objref != None:
                objname = arm.utils.asset_name(objref)

            # Lods
            if bobject.type == 'MESH' and hasattr(objref, 'arm_lodlist') and len(objref.arm_lodlist) > 0:
                o['lods'] = []
                for l in objref.arm_lodlist:
                    if l.enabled_prop == False:
                        continue
                    lod = {}
                    lod['object_ref'] = l.name
                    lod['screen_size'] = l.screen_size_prop
                    o['lods'].append(lod)
                if objref.arm_lod_material:
                    o['lod_material'] = True

            if type == NodeTypeMesh:
                if not objref in self.meshArray:
                    self.meshArray[objref] = {"structName" : objname, "objectTable" : [bobject]}
                else:
                    self.meshArray[objref]["objectTable"].append(bobject)

                oid = arm.utils.safestr(self.meshArray[objref]["structName"])
                if ArmoryExporter.option_mesh_per_file:
                    ext = '' if not self.is_compress(objref) else '.zip'
                    if ext == '' and not bpy.data.worlds['Arm'].arm_minimize:
                        ext = '.json'
                    o['data_ref'] = 'mesh_' + oid + ext + '/' + oid
                else:
                    o['data_ref'] = oid

                o['material_refs'] = []
                for i in range(len(bobject.material_slots)):
                    mat = self.slot_to_material(bobject, bobject.material_slots[i])
                    # Export ref
                    self.export_material_ref(bobject, mat, i, o)
                    # Decal flag
                    if mat != None and mat.arm_decal:
                        o['type'] = 'decal_object'
                # No material, mimic cycles and assign default
                if len(o['material_refs']) == 0:
                    self.use_default_material(bobject, o)

                num_psys = len(bobject.particle_systems)
                if num_psys > 0:
                    o['particle_refs'] = []
                    for i in range(0, num_psys):
                        self.export_particle_system_ref(bobject.particle_systems[i], i, o)

                o['dimensions'] = [0.0, 0.0, 0.0]
                for i in range(0, 3):
                    if bobject.scale[i] != 0:
                        o['dimensions'][i] = bobject.dimensions[i] / bobject.scale[i]
                # Origin not in geometry center
                if hasattr(bobject.data, 'arm_aabb'):
                    dx = bobject.data.arm_aabb[0]
                    dy = bobject.data.arm_aabb[1]
                    dz = bobject.data.arm_aabb[2]
                    if dx > o['dimensions'][0]:
                        o['dimensions'][0] = dx
                    if dy > o['dimensions'][1]:
                        o['dimensions'][1] = dy
                    if dz > o['dimensions'][2]:
                        o['dimensions'][2] = dz

                #shapeKeys = ArmoryExporter.get_shape_keys(objref)
                #if shapeKeys:
                #   self.ExportMorphWeights(bobject, shapeKeys, scene, o)

            elif type == NodeTypeLight:
                if not objref in self.lightArray:
                    self.lightArray[objref] = {"structName" : objname, "objectTable" : [bobject]}
                else:
                    self.lightArray[objref]["objectTable"].append(bobject)
                o['data_ref'] = self.lightArray[objref]["structName"]

            elif type == NodeTypeCamera:
                if 'spawn' in o and o['spawn'] == False:
                    self.camera_spawned = False
                else:
                    self.camera_spawned = True
                if not objref in self.cameraArray:
                    self.cameraArray[objref] = {"structName" : objname, "objectTable" : [bobject]}
                else:
                    self.cameraArray[objref]["objectTable"].append(bobject)
                o['data_ref'] = self.cameraArray[objref]["structName"]

            elif type == NodeTypeSpeaker:
                if not objref in self.speakerArray:
                    self.speakerArray[objref] = {"structName" : objname, "objectTable" : [bobject]}
                else:
                    self.speakerArray[objref]["objectTable"].append(bobject)
                o['data_ref'] = self.speakerArray[objref]["structName"]

            # Export the transform. If object is animated, then animation tracks are exported here
            if bobject.type != 'ARMATURE' and bobject.animation_data != None:
                action = bobject.animation_data.action
                export_actions = [action]
                for track in bobject.animation_data.nla_tracks:
                    if track.strips == None:
                        continue
                    for strip in track.strips:
                        if strip.action == None or strip.action in export_actions:
                            continue
                        export_actions.append(strip.action)
                orig_action = action
                for a in export_actions:
                    bobject.animation_data.action = a
                    self.export_object_transform(bobject, scene, o)
                if len(export_actions) >= 2 and export_actions[0] == None: # No action assigned
                    o['object_actions'].insert(0, 'null')
                bobject.animation_data.action = orig_action
            else:
                self.export_object_transform(bobject, scene, o)

            # If the object is parented to a bone and is not relative, then undo the bone's transform
            if bobject.parent_type == "BONE":
                armature = bobject.parent.data
                bone = armature.bones[bobject.parent_bone]
                # if not bone.use_relative_parent:
                o['parent_bone_connected'] = bone.use_connect
                if bone.use_connect:
                    bone_translation = Vector((0, bone.length, 0)) + bone.head
                    o['parent_bone_tail'] = [bone_translation[0], bone_translation[1], bone_translation[2]]
                else:
                    bone_translation = bone.tail - bone.head
                    o['parent_bone_tail'] = [bone_translation[0], bone_translation[1], bone_translation[2]]
                    pose_bone = bobject.parent.pose.bones[bobject.parent_bone]
                    bone_translation_pose = pose_bone.tail - pose_bone.head
                    o['parent_bone_tail_pose'] = [bone_translation_pose[0], bone_translation_pose[1], bone_translation_pose[2]]

            # Viewport Camera - overwrite active camera matrix with viewport matrix
            if type == NodeTypeCamera and bpy.data.worlds['Arm'].arm_play_camera != 'Scene' and self.scene.camera != None and bobject.name == self.scene.camera.name:
                viewport_matrix = self.get_viewport_view_matrix()
                if viewport_matrix != None:
                    o['transform']['values'] = self.write_matrix(viewport_matrix.inverted_safe())
                    # Do not apply parent matrix
                    o['local_only'] = True

            if bobject.type == 'ARMATURE' and bobject.data != None:
                bdata = bobject.data # Armature data
                action = None # Reference start action
                adata = bobject.animation_data

                # Active action
                if adata != None:
                    action = adata.action
                if action == None:
                    log.warn('Object ' + bobject.name + ' - No action assigned, setting to pose')
                    bobject.animation_data_create()
                    actions = bpy.data.actions
                    action = actions.get('armorypose')
                    if action == None:
                        action = actions.new(name='armorypose')

                # Export actions
                export_actions = [action]
                # hasattr - armature modifier may reference non-parent armature object to deform with
                if hasattr(adata, 'nla_tracks') and adata.nla_tracks != None:
                    for track in adata.nla_tracks:
                        if track.strips == None:
                            continue
                        for strip in track.strips:
                            if strip.action == None:
                                continue
                            if strip.action.name == action.name:
                                continue
                            export_actions.append(strip.action)

                armatureid = arm.utils.safestr(arm.utils.asset_name(bdata))
                ext = '.zip' if self.is_compress(bdata) else ''
                if ext == '' and not bpy.data.worlds['Arm'].arm_minimize:
                    ext = '.json'
                o['bone_actions'] = []
                for action in export_actions:
                    aname = arm.utils.safestr(arm.utils.asset_name(action))
                    o['bone_actions'].append('action_' + armatureid + '_' + aname + ext)

                orig_action = bobject.animation_data.action
                for action in export_actions:
                    aname = arm.utils.safestr(arm.utils.asset_name(action))
                    bobject.animation_data.action = action
                    fp = self.get_meshes_file_path('action_' + armatureid + '_' + aname, compressed=self.is_compress(bdata))
                    assets.add(fp)
                    if bdata.arm_cached == False or not os.path.exists(fp):
                        print('Exporting armature action ' + aname)
                        bones = []
                        self.bone_tracks = []
                        for bone in bdata.bones:
                            if not bone.parent:
                                boneo = {}
                                self.export_bone(bobject, bone, scene, boneo, action)
                                bones.append(boneo)
                        self.write_bone_matrices(scene, action)
                        if len(bones) > 0 and 'anim' in bones[0]:
                            self.export_pose_markers(bones[0]['anim'], action)
                        # Save action separately
                        action_obj = {}
                        action_obj['name'] = aname
                        action_obj['objects'] = bones
                        arm.utils.write_arm(fp, action_obj)
                bobject.animation_data.action = orig_action
                # TODO: cache per action
                bdata.arm_cached = True

            if parento == None:
                self.output['objects'].append(o)
            else:
                parento['children'].append(o)

            self.post_export_object(bobject, o, type)

            if not hasattr(o, 'children') and len(bobject.children) > 0:
                o['children'] = []

        if bobject.type != 'MESH' or bobject.arm_instanced == False:
            for subbobject in bobject.children:
                self.export_object(subbobject, scene, o)

    def export_skin(self, bobject, armature, vert_list, o):
        # This function exports all skinning data, which includes the skeleton
        # and per-vertex bone influence data
        oskin = {}
        o['skin'] = oskin

        # Write the skin bind pose transform
        otrans = {}
        oskin['transform'] = otrans
        otrans['values'] = self.write_matrix(bobject.matrix_world)

        # Write the bone object reference array
        oskin['bone_ref_array'] = []
        oskin['bone_len_array'] = []

        bone_array = armature.data.bones
        bone_count = len(bone_array)
        rpdat = arm.utils.get_rp()
        max_bones = rpdat.arm_skin_max_bones
        if bone_count > max_bones:
            log.warn(bobject.name + ' - ' + str(bone_count) + ' bones found, exceeds maximum of ' + str(max_bones) + ' bones defined - raise the value in Camera Data - Armory Render Props - Max Bones')

        for i in range(bone_count):
            boneRef = self.find_bone(bone_array[i].name)
            if boneRef:
                oskin['bone_ref_array'].append(boneRef[1]["structName"])
                oskin['bone_len_array'].append(bone_array[i].length)
            else:
                oskin['bone_ref_array'].append("null")
                oskin['bone_len_array'].append(0.0)

        # Write the bind pose transform array
        oskin['transformsI'] = []
        if rpdat.arm_skin == 'CPU':
            for i in range(bone_count):
                skeletonI = self.mulmat(armature.matrix_world, bone_array[i].matrix_local).inverted_safe()
                oskin['transformsI'].append(self.write_matrix(skeletonI))
        else:
            for i in range(bone_count):
                skeletonI = self.mulmat(armature.matrix_world, bone_array[i].matrix_local).inverted_safe()
                skeletonI = self.mulmat(skeletonI, bobject.matrix_world)
                oskin['transformsI'].append(self.write_matrix(skeletonI))

        # Export the per-vertex bone influence data
        group_remap = []
        for group in bobject.vertex_groups:
            group_name = group.name
            for i in range(bone_count):
                if bone_array[i].name == group_name:
                    group_remap.append(i)
                    break
            else:
                group_remap.append(-1)

        bone_count_array = []
        bone_index_array = []
        bone_weight_array = []

        warn_bones = False
        vertices = bobject.data.vertices
        for v in vert_list:
            bone_count = 0
            total_weight = 0.0
            bone_values = []
            for g in vertices[v.vertex_index].groups:
                bone_index = group_remap[g.group]
                bone_weight = g.weight
                if bone_index >= 0 and bone_weight != 0.0:
                    bone_values.append((bone_weight, bone_index))
                    total_weight += bone_weight
                    bone_count += 1

            # Take highest weights
            bone_values.sort()
            bone_values.reverse()

            if bone_count > 4: # Four bones max
                bone_count = 4
                bone_values = bone_values[:4]
                warn_bones = True
            bone_count_array.append(bone_count)

            for bv in bone_values:
                bone_weight_array.append(bv[0])
                bone_index_array.append(bv[1])

            if total_weight != 0.0:
                normalizer = 1.0 / total_weight
                for i in range(-bone_count, 0):
                    bone_weight_array[i] *= normalizer

        if warn_bones:
            log.warn(bobject.name + ' - more than 4 bones influence single vertex - taking highest weights')

        # Write the bone count array. There is one entry per vertex.
        oskin['bone_count_array'] = bone_count_array

        # Write the bone index array. The number of entries is the sum of the bone counts for all vertices.
        oskin['bone_index_array'] = bone_index_array

        # Write the bone weight array. The number of entries is the sum of the bone counts for all vertices.
        oskin['bone_weight_array'] = bone_weight_array

        # Bone constraints
        for bone in armature.pose.bones:
            if len(bone.constraints) > 0:
                if 'constraints' not in oskin:
                    oskin['constraints'] = []
                self.add_constraints(bone, oskin, bone=True)

    # def export_skin_fast(self, bobject, armature, vert_list, o):
    #     oskin = {}
    #     o['skin'] = oskin

    #     otrans = {}
    #     oskin['transform'] = otrans
    #     otrans['values'] = self.write_matrix(bobject.matrix_world)

    #     oskin['bone_ref_array'] = []

    #     bone_array = armature.data.bones
    #     bone_count = len(bone_array)
    #     for i in range(bone_count):
    #         boneRef = self.find_bone(bone_array[i].name)
    #         if boneRef:
    #             oskin['bone_ref_array'].append(boneRef[1]["structName"])
    #         else:
    #             oskin['bone_ref_array'].append("null")

    #     oskin['transforms'] = []
    #     for i in range(bone_count):
    #         oskin['transforms'].append(self.write_matrix(armature.matrix_world * bone_array[i].matrix_local))

    #     bone_count_array = []
    #     bone_index_array = []
    #     bone_weight_array = []
    #     for vtx in vert_list:
    #         bone_count_array.append(vtx.bone_count)
    #         bone_index_array += vtx.bone_indices
    #         bone_weight_array += vtx.bone_weights
    #     oskin['bone_count_array'] = bone_count_array
    #     oskin['bone_index_array'] = bone_index_array
    #     oskin['bone_weight_array'] = bone_weight_array

    def calc_tangents(self, posa, nora, uva, ias):
        vertex_count = int(len(posa) / 3)
        tangents = [0] * vertex_count * 3
        # bitangents = [0] * vertex_count * 3
        for ar in ias:
            ia = ar['values']
            triangle_count = int(len(ia) / 3)
            for i in range(0, triangle_count):
                i0 = ia[i * 3 + 0]
                i1 = ia[i * 3 + 1]
                i2 = ia[i * 3 + 2]
                # TODO: Slow
                v0 = Vector((posa[i0 * 3 + 0], posa[i0 * 3 + 1], posa[i0 * 3 + 2]))
                v1 = Vector((posa[i1 * 3 + 0], posa[i1 * 3 + 1], posa[i1 * 3 + 2]))
                v2 = Vector((posa[i2 * 3 + 0], posa[i2 * 3 + 1], posa[i2 * 3 + 2]))
                uv0 = Vector((uva[i0 * 2 + 0], uva[i0 * 2 + 1]))
                uv1 = Vector((uva[i1 * 2 + 0], uva[i1 * 2 + 1]))
                uv2 = Vector((uva[i2 * 2 + 0], uva[i2 * 2 + 1]))

                tangent = ArmoryExporter.calc_tangent(v0, v1, v2, uv0, uv1, uv2)

                tangents[i0 * 3 + 0] += tangent.x
                tangents[i0 * 3 + 1] += tangent.y
                tangents[i0 * 3 + 2] += tangent.z
                tangents[i1 * 3 + 0] += tangent.x
                tangents[i1 * 3 + 1] += tangent.y
                tangents[i1 * 3 + 2] += tangent.z
                tangents[i2 * 3 + 0] += tangent.x
                tangents[i2 * 3 + 1] += tangent.y
                tangents[i2 * 3 + 2] += tangent.z
                # bitangents[i0 * 3 + 0] += bitangent.x
                # bitangents[i0 * 3 + 1] += bitangent.y
                # bitangents[i0 * 3 + 2] += bitangent.z
                # bitangents[i1 * 3 + 0] += bitangent.x
                # bitangents[i1 * 3 + 1] += bitangent.y
                # bitangents[i1 * 3 + 2] += bitangent.z
                # bitangents[i2 * 3 + 0] += bitangent.x
                # bitangents[i2 * 3 + 1] += bitangent.y
                # bitangents[i2 * 3 + 2] += bitangent.z

        # Orthogonalize
        for i in range(0, vertex_count):
            # Slow
            t = Vector((tangents[i * 3], tangents[i * 3 + 1], tangents[i * 3 + 2]))
            # b = Vector((bitangents[i * 3], bitangents[i * 3 + 1], bitangents[i * 3 + 2]))
            n = Vector((nora[i * 3], nora[i * 3 + 1], nora[i * 3 + 2]))
            v = t - n * n.dot(t)
            v.normalize()
            # Calculate handedness
            # cnv = n.cross(v)
            # if cnv.dot(b) < 0.0:
                # v = v * -1.0
            tangents[i * 3] = v.x
            tangents[i * 3 + 1] = v.y
            tangents[i * 3 + 2] = v.z
        return tangents

    def write_mesh(self, bobject, fp, o):
        # One mesh data per file
        if ArmoryExporter.option_mesh_per_file:
            mesh_obj = {}
            mesh_obj['mesh_datas'] = [o]
            arm.utils.write_arm(fp, mesh_obj)
            bobject.data.arm_cached = True
            bobject.arm_cached = True
            # if bobject.type != 'FONT' and bobject.type != 'META':
                # bobject.data.arm_cached_verts = len(bobject.data.vertices)
                # bobject.data.arm_cached_edges = len(bobject.data.edges)
        else:
            self.output['mesh_datas'].append(o)

    def make_va(self, attrib, size, values):
        va = {}
        va['attrib'] = attrib
        va['size'] = size
        va['values'] = values
        return va

    def export_mesh_data(self, exportMesh, bobject, fp, o):
        exportMesh.calc_normals_split()
        exportMesh.calc_tessface() # free_mpoly=True
        vert_list = { Vertex(exportMesh, loop) : 0 for loop in exportMesh.loops}.keys()
        num_verts = len(vert_list)
        num_uv_layers = len(exportMesh.uv_layers)
        has_tex = self.get_export_uvs(exportMesh) == True and num_uv_layers > 0
        if self.has_baked_material(bobject, exportMesh.materials):
            has_tex = True
        has_tex1 = has_tex == True and num_uv_layers > 1
        num_colors = len(exportMesh.vertex_colors)
        has_col = self.get_export_vcols(exportMesh) == True and num_colors > 0
        has_tang = self.has_tangents(exportMesh)

        vdata = [0] * num_verts * 3
        ndata = [0] * num_verts * 3
        if has_tex:
            # Get active uvmap
            t0map = 0
            if bpy.app.version >= (2, 80, 1):
                uv_layers = exportMesh.uv_layers
            else:
                uv_layers = exportMesh.uv_textures
            if uv_layers != None:
                if 'UVMap_baked' in uv_layers:
                    for i in range(0, len(uv_layers)):
                        if uv_layers[i].name == 'UVMap_baked':
                            t0map = i
                            break
                else:
                    for i in range(0, len(uv_layers)):
                        if uv_layers[i].active_render:
                            t0map = i
                            break
            t1map = 1 if t0map == 0 else 0
            # Alloc data
            t0data = [0] * num_verts * 2
            if has_tex1:
                t1data = [0] * num_verts * 2
        if has_col:
            cdata = [0] * num_verts * 3


        # va_stride = 3 + 3 # pos + nor
        # va_name = 'pos_nor'
        # if has_tex:
        #     va_stride += 2
        #     va_name += '_tex'
        #     if has_tex1:
        #         va_stride += 2
        #         va_name += '_tex1'
        # if has_col > 0:
        #     va_stride += 3
        #     va_name += '_col'
        # if has_tang:
        #     va_stride += 3
        #     va_name += '_tang'
        # vdata = [0] * num_verts * va_stride

        # Make arrays
        for i, vtx in enumerate(vert_list):
            vtx.index = i
            co = vtx.co
            normal = vtx.normal
            for j in range(3):
                vdata[(i * 3) + j] = co[j]
                ndata[(i * 3) + j] = normal[j]
            if has_tex:
                t0data[i * 2] = vtx.uvs[t0map][0]
                t0data[i * 2 + 1] = 1.0 - vtx.uvs[t0map][1] # Reverse TCY
                if has_tex1:
                    t1data[i * 2] = vtx.uvs[t1map][0]
                    t1data[i * 2 + 1] = 1.0 - vtx.uvs[t1map][1]
            if has_col > 0:
                cdata[i * 3] = pow(vtx.col[0], 2.2)
                cdata[i * 3 + 1] = pow(vtx.col[1], 2.2)
                cdata[i * 3 + 2] = pow(vtx.col[2], 2.2)

        # Output
        o['vertex_arrays'] = []
        pa = self.make_va('pos', 3, vdata)
        o['vertex_arrays'].append(pa)
        na = self.make_va('nor', 3, ndata)
        o['vertex_arrays'].append(na)

        if has_tex:
            ta = self.make_va('tex', 2, t0data)
            o['vertex_arrays'].append(ta)
            if has_tex1:
                ta1 = self.make_va('tex1', 2, t1data)
                o['vertex_arrays'].append(ta1)

        if has_col:
            ca = self.make_va('col', 3, cdata)
            o['vertex_arrays'].append(ca)

        # Indices
        prims = {ma.name if ma else '': [] for ma in exportMesh.materials}
        if not prims:
            prims = {'': []}

        vert_dict = {i : v for v in vert_list for i in v.loop_indices}
        for poly in exportMesh.polygons:
            first = poly.loop_start
            if len(exportMesh.materials) == 0:
                prim = prims['']
            else:
                mat = exportMesh.materials[min(poly.material_index, len(exportMesh.materials) - 1)]
                prim = prims[mat.name if mat else '']
            indices = [vert_dict[i].index for i in range(first, first+poly.loop_total)]

            if poly.loop_total == 3:
                prim += indices
            elif poly.loop_total > 3:
                for i in range(poly.loop_total-2):
                    prim += (indices[-1], indices[i], indices[i + 1])

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

        # Write indices
        o['index_arrays'] = []
        for mat, prim in prims.items():
            idata = [0] * len(prim)
            for i, v in enumerate(prim):
                idata[i] = v
            if len(idata) == 0: # No face assigned
                continue
            ia = {}
            ia['values'] = idata
            ia['material'] = 0
            # Find material index for multi-mat mesh
            if len(exportMesh.materials) > 1:
                for i in range(0, len(exportMesh.materials)):
                    if (exportMesh.materials[i] != None and mat == exportMesh.materials[i].name) or \
                       (exportMesh.materials[i] == None and mat == ''): # Default material for empty slots
                        ia['material'] = i
                        break
            o['index_arrays'].append(ia)
        # Sort by material index
        # o['index_arrays'] = sorted(o['index_arrays'], key=lambda k: k['material']) 

        # Make tangents
        if has_tang:
            tanga_vals = self.calc_tangents(pa['values'], na['values'], ta['values'], o['index_arrays'])
            tanga = self.make_va('tang', 3, tanga_vals)
            o['vertex_arrays'].append(tanga)

        return vert_list

    def has_tangents(self, exportMesh):
        return self.get_export_uvs(exportMesh) == True and self.get_export_tangents(exportMesh) == True and len(exportMesh.uv_layers) > 0

    def export_mesh(self, objectRef, scene):
        # This function exports a single mesh object
        table = objectRef[1]["objectTable"]
        bobject = table[0]
        oid = arm.utils.safestr(objectRef[1]["structName"])

        # No export necessary
        if ArmoryExporter.option_mesh_per_file:
            fp = self.get_meshes_file_path('mesh_' + oid, compressed=self.is_compress(bobject.data))
            assets.add(fp)
            # if hasattr(bobject.data, 'arm_sdfgen') and bobject.data.arm_sdfgen:
                # sdf_path = fp.replace('/mesh_', '/sdf_')
                # assets.add(sdf_path)
            if self.is_mesh_cached(bobject) == True and os.path.exists(fp):
                return

        # Check if mesh is using instanced rendering
        is_instanced, instance_offsets = self.object_process_instancing(bobject, objectRef[1]["objectTable"])

        # Mesh users have different modifier stack
        for i in range(1, len(table)):
            if not self.mod_equal_stack(bobject, table[i]):
                log.warn('{0} users {1} and {2} differ in modifier stack - use Make Single User(U) - Object & Data for now'.format(oid, bobject.name, table[i].name))
                break

        print('Exporting mesh ' + arm.utils.asset_name(bobject.data))

        o = {}
        o['name'] = oid
        mesh = objectRef[0]
        structFlag = False

        # Save the morph state if necessary
        activeShapeKeyIndex = bobject.active_shape_key_index
        showOnlyShapeKey = bobject.show_only_shape_key
        currentMorphValue = []

        shapeKeys = ArmoryExporter.get_shape_keys(mesh)
        if shapeKeys:
            bobject.active_shape_key_index = 0
            bobject.show_only_shape_key = True

            baseIndex = 0
            relative = shapeKeys.use_relative
            if relative:
                morphCount = 0
                baseName = shapeKeys.reference_key.name
                for block in shapeKeys.key_blocks:
                    if block.name == baseName:
                        baseIndex = morphCount
                        break
                    morphCount += 1

            morphCount = 0
            for block in shapeKeys.key_blocks:
                currentMorphValue.append(block.value)
                block.value = 0.0

                if block.name != "":
                    # self.IndentWrite(B"Morph (index = ", 0, structFlag)
                    # self.WriteInt(morphCount)

                    # if (relative) and (morphCount != baseIndex):
                    #   self.Write(B", base = ")
                    #   self.WriteInt(baseIndex)

                    # self.Write(B")\n")
                    # self.IndentWrite(B"{\n")
                    # self.IndentWrite(B"Name {string {\"", 1)
                    # self.Write(bytes(block.name, "UTF-8"))
                    # self.Write(B"\"}}\n")
                    # self.IndentWrite(B"}\n")
                    # TODO
                    structFlag = True

                morphCount += 1

            shapeKeys.key_blocks[0].value = 1.0
            mesh.update()

        armature = bobject.find_armature()
        apply_modifiers = not armature

        # Apply all modifiers to create a new mesh with tessfaces
        if bpy.app.version >= (2, 80, 1):
            exportMesh = bobject.to_mesh(bpy.context.depsgraph, apply_modifiers, True, False)
        else:
            exportMesh = bobject.to_mesh(scene, apply_modifiers, "RENDER", True, False)

        if exportMesh == None:
            log.warn(oid + ' was not exported')
            return

        if len(exportMesh.uv_layers) > 2:
            log.warn(oid + ' exceeds maximum of 2 UV Maps supported')

        # Process meshes
        vert_list = self.export_mesh_data(exportMesh, bobject, fp, o)
        if armature:
            self.export_skin(bobject, armature, vert_list, o)

        # Save aabb
        for va in o['vertex_arrays']:
            if va['attrib'].startswith('pos'):
                positions = va['values']
                stride = 0
                ar = va['attrib'].split('_')
                for a in ar:
                    if a == 'pos' or a == 'nor' or a == 'col' or a == 'tang':
                        stride += 3
                    elif a == 'tex' or a == 'tex1':
                        stride += 2
                    elif a == 'bone' or a == 'weight':
                        stride += 4
                aabb_min = [-0.01, -0.01, -0.01]
                aabb_max = [0.01, 0.01, 0.01]
                i = 0
                while i < len(positions):
                    if positions[i] > aabb_max[0]:
                        aabb_max[0] = positions[i]
                    if positions[i + 1] > aabb_max[1]:
                        aabb_max[1] = positions[i + 1]
                    if positions[i + 2] > aabb_max[2]:
                        aabb_max[2] = positions[i + 2]
                    if positions[i] < aabb_min[0]:
                        aabb_min[0] = positions[i]
                    if positions[i + 1] < aabb_min[1]:
                        aabb_min[1] = positions[i + 1]
                    if positions[i + 2] < aabb_min[2]:
                        aabb_min[2] = positions[i + 2]
                    i += stride
                if hasattr(bobject.data, 'arm_aabb'):
                    bobject.data.arm_aabb = [abs(aabb_min[0]) + abs(aabb_max[0]), abs(aabb_min[1]) + abs(aabb_max[1]), abs(aabb_min[2]) + abs(aabb_max[2])]
                break
        # Not axis-aligned
        # arm_aabb = [bobject.matrix_world * Vector(v) for v in bobject.bound_box]

        # Restore the morph state
        if shapeKeys:
            bobject.active_shape_key_index = activeShapeKeyIndex
            bobject.show_only_shape_key = showOnlyShapeKey

            for m in range(len(currentMorphValue)):
                shapeKeys.key_blocks[m].value = currentMorphValue[m]

            mesh.update()

        # Save offset data for instanced rendering
        if is_instanced == True:
            o['instance_offsets'] = instance_offsets

        # Export usage
        if bobject.data.arm_dynamic_usage:
            o['dynamic_usage'] = bobject.data.arm_dynamic_usage

        self.write_mesh(bobject, fp, o)

    def export_light(self, objectRef):
        # This function exports a single light object
        o = {}
        o['name'] = objectRef[1]["structName"]
        objref = objectRef[0]
        objtype = objref.type

        if objtype == 'SUN':
            o['type'] = 'sun'
        elif objtype == 'POINT':
            o['type'] = 'point'
        elif objtype == 'SPOT':
            o['type'] = 'spot'
            o['spot_size'] = math.cos(objref.spot_size / 2)
            o['spot_blend'] = objref.spot_blend / 10 # Cycles defaults to 0.15
        elif objtype == 'AREA':
            o['type'] = 'area'
            o['size'] = objref.size
            o['size_y'] = objref.size_y
        else: # Hemi
            o['type'] = 'sun'

        o['cast_shadow'] = objref.cycles.cast_shadow
        o['near_plane'] = objref.arm_clip_start
        o['far_plane'] = objref.arm_clip_end
        o['fov'] = objref.arm_fov
        o['shadows_bias'] = objref.arm_shadows_bias * 0.0001
        rpdat = arm.utils.get_rp()
        if rpdat.rp_shadowmap == 'Off':
            o['shadowmap_size'] = 0
        else:
            o['shadowmap_size'] = int(rpdat.rp_shadowmap)
        if o['type'] == 'sun': # Scale bias for ortho light matrix
            o['shadows_bias'] *= 25.0
            if o['shadowmap_size'] > 1024:
                o['shadows_bias'] *= 1 / (o['shadowmap_size'] / 1024) # Less bias for bigger maps
        if (objtype == 'POINT' or objtype == 'SPOT') and objref.shadow_soft_size > 0.1:
            o['lamp_size'] = objref.shadow_soft_size * 10 # Match to Cycles
        gapi = arm.utils.get_gapi()
        mobile_mat = rpdat.arm_material_model == 'Mobile' or rpdat.arm_material_model == 'Solid'
        if objtype == 'POINT' and not mobile_mat:
            o['fov'] = 1.5708 # 90 deg
            o['shadowmap_cube'] = True
            o['shadows_bias'] *= 2.0

        if bpy.app.version >= (2, 80, 1) and (self.scene.render.engine == 'BLENDER_EEVEE' or self.scene.render.engine == 'ARMORY'):
            o['color'] = [objref.color[0], objref.color[1], objref.color[2]]
            o['strength'] = objref.energy
            if o['type'] == 'point' or o['type'] == 'spot':
                o['strength'] *= 2.6
            elif o['type'] == 'sun':
                o['strength'] *= 0.325
        elif objref.node_tree != None: # Cycles
            tree = objref.node_tree
            for n in tree.nodes:
                # Emission only for now
                if n.type == 'EMISSION':
                    col = n.inputs[0].default_value
                    o['color'] = [col[0], col[1], col[2]]
                    o['strength'] = n.inputs[1].default_value
                    # Normalize light strength
                    if o['type'] == 'point' or o['type'] == 'spot':
                        o['strength'] *= 0.026
                    elif o['type'] == 'area':
                        o['strength'] *= 0.26
                    elif o['type'] == 'sun':
                        o['strength'] *= 0.325
                    # TODO: Light texture test..
                    if n.inputs[0].is_linked:
                        color_node = n.inputs[0].links[0].from_node
                        if color_node.type == 'TEX_IMAGE':
                            o['color_texture'] = color_node.image.name
                    break
        else:
            o['color'] = [objref.color[0], objref.color[1], objref.color[2]]
            o['strength'] = 1000.0 * 0.026
            o['type'] = 'point'

        self.output['lamp_datas'].append(o)

    def get_camera_clear_color(self):
        if self.scene.world == None:
            return [0.051, 0.051, 0.051, 1.0]

        if self.scene.world.node_tree == None:
            c = self.scene.world.color if bpy.app.version >= (2, 80, 1) else self.scene.world.horizon_color
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
        else:
            return [0.051, 0.051, 0.051, 1.0]
            
    def extract_projection(self, o, proj, with_planes=True):
        a = proj[0][0]
        b = proj[1][1]
        c = proj[2][2]
        d = proj[2][3]
        k = (c - 1.0) / (c + 1.0)
        o['fov'] = 2.0 * math.atan(1.0 / b)
        if with_planes:
            o['near_plane'] = (d * (1.0 - k)) / (2.0 * k)
            o['far_plane'] = k * o['near_plane']

    def export_camera(self, objectRef):
        o = {}
        o['name'] = objectRef[1]["structName"]
        objref = objectRef[0]

        camera = objectRef[1]["objectTable"][0]
        render = self.scene.render
        if bpy.app.version >= (2, 80, 1):
            proj = camera.calc_matrix_camera(
                self.scene.view_layers[0].depsgraph,
                render.resolution_x,
                render.resolution_y,
                render.pixel_aspect_x,
                render.pixel_aspect_y)
        else:
                proj = camera.calc_matrix_camera(
                render.resolution_x,
                render.resolution_y,
                render.pixel_aspect_x,
                render.pixel_aspect_y)
        self.extract_projection(o, proj)

        wrd = bpy.data.worlds['Arm']
        if wrd.arm_play_camera != 'Scene':
            proj, is_persp = self.get_viewport_projection_matrix()
            if proj != None and is_persp:
                self.extract_projection(o, proj, with_planes=False)

        if objref.type != 'PERSP':
            o['ortho_scale'] = objref.ortho_scale / (7.31429 / 2)
            o['near_plane'] = objref.clip_start
            o['far_plane'] = objref.clip_end

        if objref.arm_render_to_texture:
            o['render_to_texture'] = True
            o['texture_resolution_x'] = int(objref.arm_texture_resolution_x)
            o['texture_resolution_y'] = int(objref.arm_texture_resolution_y)

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
            if objref.sound.packed_file != None:
                unpack_path = arm.utils.get_fp_build() + '/compiled/Assets/unpacked'
                if not os.path.exists(unpack_path):
                    os.makedirs(unpack_path)
                unpack_filepath = unpack_path + '/' + objref.sound.name
                if os.path.isfile(unpack_filepath) == False or os.path.getsize(unpack_filepath) != objref.sound.packed_file.size:
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
        o['loop'] = objref.arm_loop
        o['stream'] = objref.arm_stream
        o['volume'] = objref.volume
        o['pitch'] = objref.pitch
        o['attenuation'] = objref.attenuation
        o['play_on_start'] = objref.arm_play_on_start
        self.output['speaker_datas'].append(o)

    def make_default_mat(self, mat_name, mat_objs):
        if mat_name in bpy.data.materials:
            return
        mat = bpy.data.materials.new(name=mat_name)
        # if default_exists:
            # mat.is_cached = True
        mat.use_nodes = True
        o = {}
        o['name'] = mat.name
        o['contexts'] = []
        mat_users = dict()
        mat_users[mat] = mat_objs
        mat_armusers = dict()
        mat_armusers[mat] = [o]
        make_material.parse(mat, o, mat_users, mat_armusers)
        self.output['material_datas'].append(o)
        bpy.data.materials.remove(mat)
        rpdat = arm.utils.get_rp()
        if rpdat.arm_culling == False:
            o['override_context'] = {}
            o['override_context']['cull_mode'] = 'none'

    def signature_traverse(self, node, sign):
        sign += node.type + '-'
        if node.type == 'TEX_IMAGE' and node.image != None:
            sign += node.image.filepath + '-'
        for inp in node.inputs:
            if inp.is_linked:
                sign = self.signature_traverse(inp.links[0].from_node, sign)
            else:
                # Unconnected socket
                if not hasattr(inp, 'default_value'):
                    sign += 'o'
                elif inp.type == 'RGB' or inp.type == 'RGBA' or inp.type == 'VECTOR':
                    sign += str(inp.default_value[0])
                    sign += str(inp.default_value[1])
                    sign += str(inp.default_value[2])
                else:
                    sign += str(inp.default_value)
        return sign

    def get_signature(self, mat):
        nodes = mat.node_tree.nodes
        output_node = cycles.node_by_type(nodes, 'OUTPUT_MATERIAL')
        if output_node != None:
            sign = self.signature_traverse(output_node, '')
            return sign
        return None

    def export_materials(self):
        wrd = bpy.data.worlds['Arm']

        # Keep materials with fake user
        for m in bpy.data.materials:
            if m.use_fake_user and m not in self.materialArray:
                self.materialArray.append(m)
        # Ensure the same order for merging materials
        self.materialArray.sort(key=lambda x: x.name)

        if wrd.arm_batch_materials:
            mat_users = self.materialToObjectDict
            mat_armusers = self.materialToArmObjectDict
            mat_batch.build(self.materialArray, mat_users, mat_armusers)

        transluc_used = False
        overlays_used = False
        blending_used = False
        decals_used = False
        # sss_used = False
        for material in self.materialArray:
            # If the material is unlinked, material becomes None
            if material == None:
                continue

            if not material.use_nodes:
                material.use_nodes = True

            # Recache material
            signature = self.get_signature(material)
            if signature != material.signature:
                material.is_cached = False
            if signature != None:
           		material.signature = signature

            o = {}
            o['name'] = arm.utils.asset_name(material)

            if material.arm_skip_context != '':
                o['skip_context'] = material.arm_skip_context

            rpdat = arm.utils.get_rp()
            if material.arm_two_sided or rpdat.arm_culling == False:
                o['override_context'] = {}
                o['override_context']['cull_mode'] = 'none'
            elif material.arm_cull_mode != 'clockwise':
                o['override_context'] = {}
                o['override_context']['cull_mode'] = material.arm_cull_mode

            o['contexts'] = []

            mat_users = self.materialToObjectDict
            mat_armusers = self.materialToArmObjectDict
            sd, rpasses = make_material.parse(material, o, mat_users, mat_armusers)

            if 'translucent' in rpasses:
                transluc_used = True
            if 'overlay' in rpasses:
                overlays_used = True
            if 'mesh' in rpasses and material.arm_blending:
                blending_used = True
            if 'decal' in rpasses:
                decals_used = True

            uv_export = False
            tang_export = False
            vcol_export = False
            vs_str = ''
            for con in sd['contexts']:
                for elem in con['vertex_structure']:
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

                if material in self.materialToObjectDict:
                    mat_users = self.materialToObjectDict[material]
                    for ob in mat_users:
                        ob.data.arm_cached = False

            self.output['material_datas'].append(o)
            material.is_cached = True

        # Object with no material assigned in the scene
        if len(self.defaultMaterialObjects) > 0:
            self.make_default_mat('armdefault', self.defaultMaterialObjects)
        if len(self.defaultSkinMaterialObjects) > 0:
            self.make_default_mat('armdefaultskin', self.defaultSkinMaterialObjects)

        # Auto-enable render-path featues
        rebuild_rp = False
        rpdat = arm.utils.get_rp()
        if rpdat.rp_translucency_state == 'Auto' and rpdat.rp_translucency != transluc_used:
            rpdat.rp_translucency = transluc_used
            rebuild_rp = True
        if rpdat.rp_overlays_state == 'Auto' and rpdat.rp_overlays != overlays_used:
            rpdat.rp_overlays = overlays_used
            rebuild_rp = True
        if rpdat.rp_blending_state == 'On' and rpdat.rp_blending == False: # TODO: deprecated
            rpdat.rp_blending = True
            rebuild_rp = True
        if rpdat.rp_blending_state == 'Auto' and rpdat.rp_blending != blending_used:
            rpdat.rp_blending = blending_used
            rebuild_rp = True
        if rpdat.rp_decals_state == 'Auto' and rpdat.rp_decals != decals_used:
            rpdat.rp_decals = decals_used
            rebuild_rp = True
        # if rpdat.rp_sss_state == 'Auto' and rpdat.rp_sss != sss_used:
            # rpdat.rp_sss = sss_used
            # rebuild_rp = True
        if rebuild_rp:
            make_renderpath.build()

    def export_particle_systems(self):
        if len(self.particleSystemArray) > 0:
            self.output['particle_datas'] = []
        for particleRef in self.particleSystemArray.items():
            o = {}
            psettings = particleRef[0]

            if psettings == None:
                continue

            if psettings.dupli_object == None or psettings.render_type != 'OBJECT':
                continue

            o['name'] = particleRef[1]["structName"]
            o['type'] = 0 if psettings.type == 'EMITTER' else 1 # HAIR
            o['loop'] = psettings.arm_loop
            if bpy.app.version >= (2, 80, 1):
                o['render_emitter'] = False
            else:
                o['render_emitter'] = psettings.use_render_emitter
            # Emission
            o['count'] = psettings.count * psettings.arm_count_mult
            o['frame_start'] = int(psettings.frame_start)
            o['frame_end'] = int(psettings.frame_end)
            o['lifetime'] = psettings.lifetime
            o['lifetime_random'] = psettings.lifetime_random
            o['emit_from'] = 1 if psettings.emit_from == 'VOLUME' else 0 # VERT, FACE
            # Velocity
            # o['normal_factor'] = psettings.normal_factor
            # o['tangent_factor'] = psettings.tangent_factor
            # o['tangent_phase'] = psettings.tangent_phase
            o['object_align_factor'] = [psettings.object_align_factor[0], psettings.object_align_factor[1], psettings.object_align_factor[2]]
            # o['object_factor'] = psettings.object_factor
            o['factor_random'] = psettings.factor_random
            # Physics
            o['physics_type'] = 1 if psettings.physics_type == 'NEWTON' else 0
            o['particle_size'] = psettings.particle_size
            o['size_random'] = psettings.size_random
            o['mass'] = psettings.mass
            # Render
            o['dupli_object'] = psettings.dupli_object.name
            self.objectToArmObjectDict[psettings.dupli_object]['is_particle'] = True
            # Field weights
            o['weight_gravity'] = psettings.effector_weights.gravity
            self.output['particle_datas'].append(o)

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

    def export_worlds(self):
        worldRef = self.scene.world
        if worldRef != None:
            o = {}
            w = worldRef
            o['name'] = w.name
            self.post_export_world(w, o)
            self.output['world_datas'].append(o)

    def is_compress(self, obj):
        return ArmoryExporter.compress_enabled and obj.arm_compress

    def export_objects(self, scene):
        if not ArmoryExporter.option_mesh_only:
            self.output['lamp_datas'] = []
            self.output['camera_datas'] = []
            self.output['speaker_datas'] = []
            for objectRef in self.lightArray.items():
                self.export_light(objectRef)
            for objectRef in self.cameraArray.items():
                self.export_camera(objectRef)
            # Keep sounds with fake user
            for sound in bpy.data.sounds:
                if sound.use_fake_user:
                    assets.add(arm.utils.asset_path(sound.filepath))
            for objectRef in self.speakerArray.items():
                self.export_speaker(objectRef)
        for objectRef in self.meshArray.items():
            self.output['mesh_datas'] = []
            self.export_mesh(objectRef, scene)

    def execute(self, context, filepath, scene=None):
        profile_time = time.time()

        self.output = {}
        self.filepath = filepath

        self.scene = context.scene if scene == None else scene
        print('Exporting ' + arm.utils.asset_name(self.scene))

        current_frame, current_subframe = scene.frame_current, scene.frame_subframe
        self.beginFrame = self.scene.frame_start
        self.output['frame_time'] = 1.0 / (self.scene.render.fps / self.scene.render.fps_base)

        self.bobjectArray = {}
        self.bobjectBoneArray = {}
        self.meshArray = {}
        self.lightArray = {}
        self.cameraArray = {}
        self.camera_spawned = False
        self.speakerArray = {}
        self.materialArray = []
        self.particleSystemArray = {}
        self.worldArray = {} # Export all worlds
        self.boneParentArray = {}
        self.materialToObjectDict = dict()
        self.defaultMaterialObjects = [] # If no material is assigned, provide default to mimick cycles
        self.defaultSkinMaterialObjects = []
        self.materialToArmObjectDict = dict()
        self.objectToArmObjectDict = dict()
        self.active_layers = []
        self.bone_tracks = []
        for i in range(0, len(self.scene.layers)):
            if self.scene.layers[i] == True:
                self.active_layers.append(i)

        self.preprocess()

        if bpy.app.version >= (2, 80, 1):
            def mulmat(a, b):
                return a @ b
            self.mulmat = mulmat
        else:
            def mulmat(a, b):
                return a * b
            self.mulmat = mulmat

        if bpy.app.version >= (2, 80, 1):
            # scene_objects = self.scene.objects
            scene_objects = []
            for lay in self.scene.view_layers:
                scene_objects += lay.objects
        else:
            scene_objects = self.scene.objects
        for bobject in scene_objects:
            # Map objects to game objects
            o = {}
            o['traits'] = []
            self.objectToArmObjectDict[bobject] = o
            # Process
            if not bobject.parent:
                self.process_bobject(bobject)

        self.process_skinned_meshes()

        self.output['name'] = arm.utils.safestr(self.scene.name)
        if self.filepath.endswith('.zip'):
            self.output['name'] += '.zip'
        elif not bpy.data.worlds['Arm'].arm_minimize:
            self.output['name'] += '.json'

        # Fix material variants
        # Skinned and non-skined objects can not share material
        matvars = []
        matslots = []
        for bo in scene_objects:
            if arm.utils.export_bone_data(bo):
                for slot in bo.material_slots:
                    if slot.material == None or slot.material.library != None:
                        continue
                    if slot.material.name.endswith('_armskin'):
                        continue
                    matslots.append(slot)
                    mat_name = slot.material.name + '_armskin'
                    mat = bpy.data.materials.get(mat_name)
                    if mat == None:
                        mat = slot.material.copy()
                        mat.name = mat_name
                        matvars.append(mat)
                    slot.material = mat
        # Particle and non-particle objects can not share material
        for psys in bpy.data.particles:
            bo = psys.dupli_object
            if bo == None or psys.render_type != 'OBJECT':
                continue
            for slot in bo.material_slots:
                if slot.material == None or slot.material.library != None:
                    continue
                if slot.material.name.endswith('_armpsys'):
                    continue
                matslots.append(slot)
                mat_name = slot.material.name + '_armpsys'
                mat = bpy.data.materials.get(mat_name)
                if mat == None:
                    mat = slot.material.copy()
                    mat.name = mat_name
                    mat.arm_particle_flag = True
                    matvars.append(mat)
                slot.material = mat

        # Auto-bones
        wrd = bpy.data.worlds['Arm']
        rpdat = arm.utils.get_rp()
        if rpdat.arm_skin_max_bones_auto:
            max_bones = 8
            for armature in bpy.data.armatures:
                if max_bones < len(armature.bones):
                    max_bones = len(armature.bones)
            rpdat.arm_skin_max_bones = max_bones

        self.output['objects'] = []
        for bo in scene_objects:
            if not bo.parent:
                self.export_object(bo, self.scene)

        if hasattr(bpy.data, 'groups') and len(bpy.data.groups) > 0:
            self.output['groups'] = []
            for group in bpy.data.groups:
                # Blender automatically stores physics objects in this group,
                # can cause stuck unused objects, skip for now
                if group.name.startswith('RigidBodyWorld') or group.name.startswith('Trait|'):
                    continue
                o = {}
                o['name'] = group.name
                o['object_refs'] = []
                # Add unparented objects only, then instantiate full object child tree
                for bobject in group.objects:
                    if bobject.parent == None and bobject.arm_export:
                        # This object is controlled by proxy
                        has_proxy_user = False
                        for bo in bpy.data.objects:
                            if bo.proxy == bobject:
                                has_proxy_user = True
                                break
                        if has_proxy_user:
                            continue
                        # Add external linked objects
                        if bobject.name not in scene_objects: # and bobject.ls_linked
                            self.process_bobject(bobject)
                            self.export_object(bobject, self.scene)
                            o['object_refs'].append(arm.utils.asset_name(bobject))
                        else:
                            o['object_refs'].append(bobject.name)
                self.output['groups'].append(o)

        if not ArmoryExporter.option_mesh_only:
            if self.scene.camera != None:
                self.output['camera_ref'] = self.scene.camera.name
            else:
                if self.scene.name == arm.utils.get_project_scene_name():
                    log.warn('No camera found in active scene')

            self.output['material_datas'] = []
            self.export_materials()
            self.export_particle_systems()
            self.output['world_datas'] = []
            self.export_worlds()
            self.export_tilesheets()

            if self.scene.world != None:
                self.output['world_ref'] = self.scene.world.name

            if self.scene.use_gravity:
                self.output['gravity'] = [self.scene.gravity[0], self.scene.gravity[1], self.scene.gravity[2]]
            else:
                self.output['gravity'] = [0.0, 0.0, 0.0]

        self.export_objects(self.scene)

        if not self.camera_spawned:
            log.warn('No camera found in active scene layers')

        if (len(self.output['camera_datas']) == 0 and len(bpy.data.cameras) == 0) or not self.camera_spawned:
            log.warn('Creating default camera')
            o = {}
            o['name'] = 'DefaultCamera'
            o['near_plane'] = 0.1
            o['far_plane'] = 100.0
            o['fov'] = 0.85
            o['type'] = 'perspective'
            o['frustum_culling'] = True
            o['clear_color'] = self.get_camera_clear_color()
            self.output['camera_datas'].append(o)
            o = {}
            o['name'] = 'DefaultCamera'
            o['type'] = 'camera_object'
            o['data_ref'] = 'DefaultCamera'
            o['material_refs'] = []
            o['transform'] = {}
            viewport_matrix = self.get_viewport_view_matrix()
            if viewport_matrix != None:
                o['transform']['values'] = self.write_matrix(viewport_matrix.inverted_safe())
                o['local_only'] = True
            else:
                o['transform']['values'] = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]
            o['traits'] = []
            trait = {}
            trait['type'] = 'Script'
            trait['class_name'] = 'armory.trait.WalkNavigation'
            trait['parameters'] = ['true'] # ease
            o['traits'].append(trait)
            ArmoryExporter.import_traits.append(trait['class_name'])
            self.output['objects'].append(o)
            self.output['camera_ref'] = 'DefaultCamera'

        # Scene root traits
        if wrd.arm_physics != 'Disabled' and ArmoryExporter.export_physics:
            if not 'traits' in self.output:
                self.output['traits'] = []
            x = {}
            x['type'] = 'Script'
            phys_pkg = 'bullet' if wrd.arm_physics_engine == 'Bullet' else 'oimo'
            x['class_name'] = 'armory.trait.physics.' + phys_pkg + '.PhysicsWorld'
            rbw = self.scene.rigidbody_world
            if rbw != None and rbw.enabled:
                x['parameters'] = [str(rbw.time_scale), str(1 / rbw.steps_per_second)]
            self.output['traits'].append(x)
        if wrd.arm_navigation != 'Disabled' and ArmoryExporter.export_navigation:
            if not 'traits' in self.output:
                self.output['traits'] = []
            x = {}
            x['type'] = 'Script'
            x['class_name'] = 'armory.trait.navigation.Navigation'
            self.output['traits'].append(x)
        if wrd.arm_play_console:
            if not 'traits' in self.output:
                self.output['traits'] = []
            ArmoryExporter.export_ui = True
            x = {}
            x['type'] = 'Script'
            x['class_name'] = 'armory.trait.internal.DebugConsole'
            x['parameters'] = []
            self.output['traits'].append(x)
        if len(self.scene.arm_traitlist) > 0:
            if not 'traits' in self.output:
                self.output['traits'] = []
            self.export_traits(self.scene, self.output)
        if 'traits' in self.output:
            for x in self.output['traits']:
                ArmoryExporter.import_traits.append(x['class_name'])

        # Write embedded data references
        if len(assets.embedded_data) > 0:
            self.output['embedded_datas'] = []
            for file in assets.embedded_data:
                self.output['embedded_datas'].append(file)

        # Write scene file
        arm.utils.write_arm(self.filepath, self.output)

        # Remove created material variants
        for slot in matslots: # Set back to original material
            orig_mat = bpy.data.materials[slot.material.name[:-8]] # _armskin or _armpsys
            orig_mat.export_uvs = slot.material.export_uvs
            orig_mat.export_vcols = slot.material.export_vcols
            orig_mat.export_tangents = slot.material.export_tangents
            orig_mat.is_cached = slot.material.is_cached
            slot.material = orig_mat
        for mat in matvars:
            bpy.data.materials.remove(mat, do_unlink=True)

        # Restore frame
        if scene.frame_current != current_frame:
            scene.frame_set(current_frame, current_subframe)

        print('Scene built in ' + str(time.time() - profile_time))
        return {'FINISHED'}

    # Callbacks
    def is_mesh_cached(self, bobject):
        if bobject.type == 'FONT' or bobject.type == 'META': # No verts
            return bobject.data.arm_cached
        # if bobject.data.arm_cached_verts != len(bobject.data.vertices):
            # return False
        # if bobject.data.arm_cached_edges != len(bobject.data.edges):
            # return False
        if not bobject.arm_cached:
            return False
        return bobject.data.arm_cached

    def get_export_tangents(self, mesh):
        for m in mesh.materials:
            if m != None and m.export_tangents == True:
                return True
        return False

    def get_export_vcols(self, mesh):
        for m in mesh.materials:
            if m != None and m.export_vcols == True:
                return True
        return False

    def get_export_uvs(self, mesh):
        for m in mesh.materials:
            if m != None and m.export_uvs == True:
                return True
        return False

    def object_process_instancing(self, bobject, refs):
        is_instanced = False
        instance_offsets = None
        for n in refs:
            if n.arm_instanced == True:
                is_instanced = True
                # Save offset data
                instance_offsets = [0.0, 0.0, 0.0] # Include parent
                for sn in n.children:
                    # Child hidden
                    if sn.arm_export == False:
                        continue
                    # Do not take parent matrix into account
                    loc = sn.matrix_local.to_translation()
                    instance_offsets.append(loc.x)
                    instance_offsets.append(loc.y)
                    instance_offsets.append(loc.z)
                    # m = sn.matrix_local
                    # instance_offsets.append(m[0][3]) #* m[0][0]) # Scale
                    # instance_offsets.append(m[1][3]) #* m[1][1])
                    # instance_offsets.append(m[2][3]) #* m[2][2])
                break
            # Instance render groups with same children?
            # elif n.dupli_type == 'GROUP' and n.dupli_group != None:
            #     is_instanced = True
            #     instance_offsets = []
            #     for sn in bpy.data.groups[n.dupli_group].objects:
            #         loc = sn.matrix_local.to_translation()
            #         instance_offsets.append(loc.x)
            #         instance_offsets.append(loc.y)
            #         instance_offsets.append(loc.z)
            #     break

        return is_instanced, instance_offsets

    def preprocess(self):
        wrd = bpy.data.worlds['Arm']
        ArmoryExporter.export_all_flag = True
        ArmoryExporter.export_physics = False # Indicates whether rigid body is exported
        if wrd.arm_physics == 'Enabled':
            ArmoryExporter.export_physics = True
        ArmoryExporter.export_navigation = False
        if wrd.arm_navigation == 'Enabled':
            ArmoryExporter.export_navigation = True
        ArmoryExporter.export_ui = False
        if not hasattr(ArmoryExporter, 'compress_enabled'):
            ArmoryExporter.compress_enabled = False
        if not hasattr(ArmoryExporter, 'import_traits'):
            ArmoryExporter.import_traits = [] # Referenced traits
        ArmoryExporter.option_mesh_only = False
        ArmoryExporter.option_mesh_per_file = True
        ArmoryExporter.sample_animation_flag = wrd.arm_sampled_animation

        # Used for material shader export and khafile
        ArmoryExporter.mesh_context = 'mesh'
        ArmoryExporter.mesh_context_empty = ''
        ArmoryExporter.shadows_context = 'shadowmap'
        ArmoryExporter.translucent_context = 'translucent'
        ArmoryExporter.overlay_context = 'overlay'

    def preprocess_object(self, bobject): # Returns false if object should not be exported
        export_object = True

        # Disabled object
        if bobject.arm_export == False:
            return False

        return export_object

    def post_export_object(self, bobject, o, type):
        # Export traits
        self.export_traits(bobject, o)

        wrd = bpy.data.worlds['Arm']
        phys_enabled = wrd.arm_physics != 'Disabled'
        phys_pkg = 'bullet' if wrd.arm_physics_engine == 'Bullet' else 'oimo'

        # Rigid body trait
        if bobject.rigid_body != None and phys_enabled:
            ArmoryExporter.export_physics = True
            rb = bobject.rigid_body
            shape = 0 # BOX
            if bobject.arm_rb_terrain: # Override selected shape as terrain..
                shape = 7
            elif rb.collision_shape == 'SPHERE':
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
            is_static = not rb.enabled or (rb.type == 'PASSIVE' and not rb.kinematic)
            if is_static:
                body_mass = 0
            x = {}
            x['type'] = 'Script'
            x['class_name'] = 'armory.trait.physics.' + phys_pkg + '.RigidBody'
            x['parameters'] = [str(body_mass), str(shape), str(rb.friction), str(rb.restitution)]
            if rb.use_margin:
                x['parameters'].append(str(rb.collision_margin))
            else:
                x['parameters'].append('0.0')
            x['parameters'].append(str(rb.linear_damping))
            x['parameters'].append(str(rb.angular_damping))
            x['parameters'].append(str(rb.kinematic).lower())
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
            lin_fac = '[{0}, {1}, {2}]'.format(str(lx), str(ly), str(lz))
            ang_fac = '[{0}, {1}, {2}]'.format(str(ax), str(ay), str(az))
            x['parameters'].append(lin_fac)
            x['parameters'].append(ang_fac)
            col_group = ''
            for b in rb.collision_groups:
                col_group = ('1' if b else '0') + col_group
            x['parameters'].append(str(int(col_group, 2)))
            x['parameters'].append(str(bobject.arm_rb_trigger).lower())
            if rb.use_deactivation or bobject.arm_rb_force_deactivation:
                deact_params = lin_fac = '[{0}, {1}, {2}]'.format(str(rb.deactivate_linear_velocity), str(rb.deactivate_angular_velocity), str(bobject.arm_rb_deactivation_time))
                x['parameters'].append(deact_params)
            else:
                x['parameters'].append('null')
            o['traits'].append(x)

        # Phys traits
        if phys_enabled:
            for m in bobject.modifiers:
                if m.type == 'CLOTH':
                    self.add_softbody_mod(o, bobject, m, 0) # SoftShape.Cloth
                elif m.type == 'SOFT_BODY':
                    self.add_softbody_mod(o, bobject, m, 1) # SoftShape.Volume
                elif m.type == 'HOOK':
                    self.add_hook_mod(o, bobject, m.object.name, m.vertex_group)
            # Rigid body constraint
            rbc = bobject.rigid_body_constraint
            if rbc != None and rbc.enabled:
                self.add_rigidbody_constraint(o, rbc)

        # Camera traits
        if type == NodeTypeCamera:
            # Viewport camera enabled, attach navigation to active camera
            if self.scene.camera != None and bobject.name == self.scene.camera.name and bpy.data.worlds['Arm'].arm_play_camera != 'Scene':
                navigation_trait = {}
                navigation_trait['type'] = 'Script'
                navigation_trait['class_name'] = 'armory.trait.WalkNavigation'
                navigation_trait['parameters'] = ['true'] # ease
                o['traits'].append(navigation_trait)

        # Map objects to materials, can be used in later stages
        for i in range(len(bobject.material_slots)):
            mat = self.slot_to_material(bobject, bobject.material_slots[i])
            if mat in self.materialToObjectDict:
                self.materialToObjectDict[mat].append(bobject)
                self.materialToArmObjectDict[mat].append(o)
            else:
                self.materialToObjectDict[mat] = [bobject]
                self.materialToArmObjectDict[mat] = [o]

        # Export constraints
        if len(bobject.constraints) > 0:
            o['constraints'] = []
            self.add_constraints(bobject, o)

        for x in o['traits']:
            ArmoryExporter.import_traits.append(x['class_name'])

    def add_constraints(self, bobject, o, bone=False):
        for con in bobject.constraints:
            if con.mute:
                continue
            co = {}
            co['name'] = con.name
            co['type'] = con.type
            if bone:
                co['bone'] = bobject.name
            if hasattr(con, 'target') and con.target != None:
                if con.type == 'COPY_LOCATION':
                    co['target'] = con.target.name
                    co['use_x'] = con.use_x
                    co['use_y'] = con.use_y
                    co['use_z'] = con.use_z
                    co['invert_x'] = con.invert_x
                    co['invert_y'] = con.invert_y
                    co['invert_z'] = con.invert_z
                    co['use_offset'] = con.use_offset
                    co['influence'] = con.influence
                elif con.type == 'CHILD_OF':
                    co['target'] = con.target.name
                    co['influence'] = con.influence
            o['constraints'].append(co)

    def export_traits(self, bobject, o):
        if hasattr(bobject, 'arm_traitlist'):
            for t in bobject.arm_traitlist:
                if t.enabled_prop == False:
                    continue
                x = {}
                if t.type_prop == 'Logic Nodes' and t.nodes_name_prop != '':
                    x['type'] = 'Script'
                    group_name = arm.utils.safesrc(t.nodes_name_prop[0].upper() + t.nodes_name_prop[1:])
                    x['class_name'] = arm.utils.safestr(bpy.data.worlds['Arm'].arm_project_package) + '.node.' + group_name
                elif t.type_prop == 'WebAssembly':
                    wpath = arm.utils.get_fp() + '/Bundled/' + t.webassembly_prop + '.wasm'
                    if not os.path.exists(wpath):
                        log.warn('Wasm "' + t.webassembly_prop + '" not found, skipping')
                        continue
                    x['type'] = 'Script'
                    x['class_name'] = 'armory.trait.internal.WasmScript'
                    x['parameters'] = ["'" + t.webassembly_prop + "'"]
                elif t.type_prop == 'UI Canvas':
                    cpath = arm.utils.get_fp() + '/Bundled/canvas/' + t.canvas_name_prop + '.json'
                    if not os.path.exists(cpath):
                        log.warn('Canvas "' + t.canvas_name_prop + '" not found, skipping')
                        continue
                    ArmoryExporter.export_ui = True
                    x['type'] = 'Script'
                    x['class_name'] = 'armory.trait.internal.CanvasScript'
                    x['parameters'] = ["'" + t.canvas_name_prop + "'"]
                    # assets.add(assetpath) # Bundled is auto-added
                    # Read file list and add canvas assets
                    assetpath = arm.utils.get_fp() + '/Bundled/canvas/' + t.canvas_name_prop + '.files'
                    if os.path.exists(assetpath):
                        with open(assetpath) as f:
                            fileList = f.read().splitlines()
                            for asset in fileList:
                                # Relative to the root/Bundled/canvas path
                                asset = asset[6:] # Strip ../../ to start in project root
                                assets.add(asset)
                else: # Haxe/Bundled Script
                    if t.class_name_prop == '': # Empty class name, skip
                        continue
                    x['type'] = 'Script'
                    if t.type_prop == 'Bundled Script':
                        trait_prefix = 'armory.trait.'
                        # TODO: temporary, export single mesh navmesh as obj
                        if t.class_name_prop == 'NavMesh' and bobject.type == 'MESH' and bpy.data.worlds['Arm'].arm_navigation != 'Disabled':
                            ArmoryExporter.export_navigation = True
                            nav_path = arm.utils.get_fp_build() + '/compiled/Assets/navigation'
                            if not os.path.exists(nav_path):
                                os.makedirs(nav_path)
                            nav_filepath = nav_path + '/nav_' + bobject.data.name + '.arm'
                            assets.add(nav_filepath)
                            # TODO: Implement cache
                            #if os.path.isfile(nav_filepath) == False:
                            override = {'selected_objects': [bobject]}
                            # bobject.scale.y *= -1
                            # mesh = obj.data
                            # for face in mesh.faces:
                                # face.v.reverse()
                            # bpy.ops.export_scene.obj(override, use_selection=True, filepath=nav_filepath, check_existing=False, use_normals=False, use_uvs=False, use_materials=False)
                            # bobject.scale.y *= -1
                            with open(nav_filepath, 'w') as f:
                                for v in bobject.data.vertices:
                                    f.write("v %.4f " % (v.co[0] * bobject.scale.x))
                                    f.write("%.4f " % (v.co[2] * bobject.scale.z))
                                    f.write("%.4f\n" % (v.co[1] * bobject.scale.y)) # Flipped
                                for p in bobject.data.polygons:
                                    f.write("f")
                                    for i in reversed(p.vertices): # Flipped normals
                                        f.write(" %d" % (i + 1))
                                    f.write("\n")
                    else:
                        trait_prefix = arm.utils.safestr(bpy.data.worlds['Arm'].arm_project_package) + '.'
                    x['class_name'] = trait_prefix + t.class_name_prop
                    if len(t.arm_traitparamslist) > 0:
                        x['parameters'] = []
                        for pt in t.arm_traitparamslist: # Append parameters
                            x['parameters'].append(pt.name)
                    if len(t.arm_traitpropslist) > 0:
                        x['props'] = []
                        for pt in t.arm_traitpropslist: # Append props
                            prop = pt.name.replace(')', '').split('(')
                            x['props'].append(prop[0])
                            if(len(prop) > 1):
                                if prop[1] == 'String':
                                    value = "'" + pt.value + "'"
                                else:
                                    value = pt.value
                            else:
                                value = pt.value
                            x['props'].append(value)
                o['traits'].append(x)

    def add_softbody_mod(self, o, bobject, soft_mod, soft_type):
        ArmoryExporter.export_physics = True
        phys_pkg = 'bullet' if bpy.data.worlds['Arm'].arm_physics_engine == 'Bullet' else 'oimo'
        assets.add_khafile_def('arm_physics_soft')
        trait = {}
        trait['type'] = 'Script'
        trait['class_name'] = 'armory.trait.physics.' + phys_pkg + '.SoftBody'
        if soft_type == 0:
            bend = soft_mod.settings.bending_stiffness
        elif soft_type == 1:
            bend = (soft_mod.settings.bend + 1.0) * 10
        trait['parameters'] = [str(soft_type), str(bend), str(soft_mod.settings.mass), str(bobject.arm_soft_body_margin)]
        o['traits'].append(trait)
        if soft_type == 0 and soft_mod.settings.use_pin_cloth:
            self.add_hook_mod(o, bobject, '', soft_mod.settings.vertex_group_mass)

    def add_hook_mod(self, o, bobject, target_name, group_name):
        ArmoryExporter.export_physics = True
        phys_pkg = 'bullet' if bpy.data.worlds['Arm'].arm_physics_engine == 'Bullet' else 'oimo'
        trait = {}
        trait['type'] = 'Script'
        trait['class_name'] = 'armory.trait.physics.' + phys_pkg + '.PhysicsHook'
        verts = []
        if group_name != '':
            group = bobject.vertex_groups[group_name].index
            for v in bobject.data.vertices:
                for g in v.groups:
                    if g.group == group:
                        verts.append(v.co.x)
                        verts.append(v.co.y)
                        verts.append(v.co.z)
        trait['parameters'] = ["'" + target_name + "'", str(verts)]
        o['traits'].append(trait)

    def add_rigidbody_constraint(self, o, rbc):
        rb1 = rbc.object1
        rb2 = rbc.object2
        if rb1 == None or rb2 == None:
            return
        ArmoryExporter.export_physics = True
        phys_pkg = 'bullet' if bpy.data.worlds['Arm'].arm_physics_engine == 'Bullet' else 'oimo'
        breaking_threshold = rbc.breaking_threshold if rbc.use_breaking else 0
        trait = {}
        trait['type'] = 'Script'
        trait['class_name'] = 'armory.trait.physics.' + phys_pkg + '.PhysicsConstraint'
        trait['parameters'] = [\
            "'" + rb1.name + "'", \
            "'" + rb2.name + "'", \
            "'" + rbc.type + "'", \
            str(rbc.disable_collisions).lower(), \
            str(breaking_threshold)]
        if rbc.type == "GENERIC":
            limits = []
            limits.append(1 if rbc.use_limit_lin_x else 0)
            limits.append(rbc.limit_lin_x_lower)
            limits.append(rbc.limit_lin_x_upper)
            limits.append(1 if rbc.use_limit_lin_y else 0)
            limits.append(rbc.limit_lin_y_lower)
            limits.append(rbc.limit_lin_y_upper)
            limits.append(1 if rbc.use_limit_lin_z else 0)
            limits.append(rbc.limit_lin_z_lower)
            limits.append(rbc.limit_lin_z_upper)
            limits.append(1 if rbc.use_limit_ang_x else 0)
            limits.append(rbc.limit_ang_x_lower)
            limits.append(rbc.limit_ang_x_upper)
            limits.append(1 if rbc.use_limit_ang_y else 0)
            limits.append(rbc.limit_ang_y_lower)
            limits.append(rbc.limit_ang_y_upper)
            limits.append(1 if rbc.use_limit_ang_z else 0)
            limits.append(rbc.limit_ang_z_lower)
            limits.append(rbc.limit_ang_z_upper)
            trait['parameters'].append(str(limits))
        o['traits'].append(trait)

    def post_export_world(self, world, o):
        wrd = bpy.data.worlds['Arm']
        bgcol = world.arm_envtex_color
        if '_LDR' in wrd.world_defs: # No compositor used
            for i in range(0, 3):
                bgcol[i] = pow(bgcol[i], 1.0 / 2.2)
        o['background_color'] = arm.utils.color_to_int(bgcol)

        if '_EnvSky' in wrd.world_defs:
            # Sky data for probe
            o['sun_direction'] =  list(world.arm_envtex_sun_direction)
            o['turbidity'] = world.arm_envtex_turbidity
            o['ground_albedo'] = world.arm_envtex_ground_albedo

        disable_hdr = world.arm_envtex_name.endswith('.jpg')
        if '_EnvTex' in wrd.world_defs or '_EnvImg' in wrd.world_defs:
            o['envmap'] = world.arm_envtex_name.rsplit('.', 1)[0]
            if disable_hdr:
                o['envmap'] += '.jpg'
            else:
                o['envmap'] += '.hdr'

        o['probes'] = []

        # Main probe
        rpdat = arm.utils.get_rp()
        solid_mat = rpdat.arm_material_model == 'Solid'
        arm_irradiance = rpdat.arm_irradiance and not solid_mat
        arm_radiance = False
        radtex = world.arm_envtex_name.rsplit('.', 1)[0]
        irrsharmonics = world.arm_envtex_irr_name
        # Radiance
        if '_EnvTex' in wrd.world_defs:
            arm_radiance = rpdat.arm_radiance
        elif '_EnvSky' in wrd.world_defs and rpdat.arm_radiance_sky:
            arm_radiance = rpdat.arm_radiance
            radtex = 'hosek'
        num_mips = world.arm_envtex_num_mips
        strength = world.arm_envtex_strength

        mobile_mat = rpdat.arm_material_model == 'Mobile' or rpdat.arm_material_model == 'Solid'
        if mobile_mat:
            arm_radiance = False

        po = {}
        po['name'] = world.name
        if arm_irradiance:
            ext = '' if wrd.arm_minimize else '.json'
            po['irradiance'] = irrsharmonics + '_irradiance' + ext
            if arm_radiance:
                po['radiance'] = radtex + '_radiance'
                if disable_hdr:
                    po['radiance'] += '.jpg'
                else:
                    po['radiance'] += '.hdr'
                po['radiance_mipmaps'] = num_mips
        else:
            po['irradiance'] = '' # No irradiance data, fallback to default at runtime
        po['strength'] = strength
        po['blending'] = 1.0
        po['volume'] = [0.0, 0.0, 0.0]
        po['volume_center'] = [0.0, 0.0, 0.0]
        o['probes'].append(po)

    # https://blender.stackexchange.com/questions/70629
    def mod_equal(self, mod1, mod2):
        return all([getattr(mod1, prop, True) == getattr(mod2, prop, False) for prop in mod1.bl_rna.properties.keys()])

    def mod_equal_stack(self, obj1, obj2):
        if len(obj1.modifiers) == 0 and len(obj2.modifiers) == 0:
            return True
        if len(obj1.modifiers) == 0 or len(obj2.modifiers) == 0:
            return False
        if len(obj1.modifiers) != len(obj2.modifiers):
            return False
        return all([self.mod_equal(m, obj2.modifiers[i]) for i,m in enumerate(obj1.modifiers)])
