"""
Armory Scene Exporter
http://armory3d.org/

Based on Open Game Engine Exchange
http://opengex.org/
Export plugin for Blender by Eric Lengyel
Copyright 2015, Terathon Software LLC

This software is licensed under the Creative Commons
Attribution-ShareAlike 3.0 Unported License:
http://creativecommons.org/licenses/by-sa/3.0/deed.en_US
"""
import math
import os
import time

import numpy as np

from mathutils import *
import bpy

import arm.assets as assets
import arm.exporter_opt as exporter_opt
import arm.log as log
import arm.make_renderpath as make_renderpath
import arm.material.cycles as cycles
import arm.material.make as make_material
import arm.material.mat_batch as mat_batch
import arm.utils

NodeTypeEmpty = 0
NodeTypeBone = 1
NodeTypeMesh = 2
NodeTypeLight = 3
NodeTypeCamera = 4
NodeTypeSpeaker = 5
NodeTypeDecal = 6
NodeTypeProbe = 7
AnimationTypeSampled = 0
AnimationTypeLinear = 1
AnimationTypeBezier = 2
AnimationTypeConstant = 3
ExportEpsilon = 1.0e-6

structIdentifier = ["object", "bone_object", "mesh_object", "light_object", "camera_object", "speaker_object", "decal_object", "probe_object"]
current_output = None

class ArmoryExporter:
    '''Export to Armory format'''

    def write_matrix(self, matrix):
        return [matrix[0][0], matrix[0][1], matrix[0][2], matrix[0][3],
                matrix[1][0], matrix[1][1], matrix[1][2], matrix[1][3],
                matrix[2][0], matrix[2][1], matrix[2][2], matrix[2][3],
                matrix[3][0], matrix[3][1], matrix[3][2], matrix[3][3]]

    def get_meshes_file_path(self, object_id, compressed=False):
        index = self.filepath.rfind('/')
        mesh_fp = self.filepath[:(index + 1)] + 'meshes/'
        if not os.path.exists(mesh_fp):
            os.makedirs(mesh_fp)
        ext = '.lz4' if compressed else '.arm'
        return mesh_fp + object_id + ext

    @staticmethod
    def get_bobject_type(bobject):
        if bobject.type == "MESH":
            if len(bobject.data.polygons) != 0:
                return NodeTypeMesh
        elif bobject.type == "FONT":
            return NodeTypeMesh
        elif bobject.type == "META":
            return NodeTypeMesh
        elif bobject.type == "LIGHT":
            return NodeTypeLight
        elif bobject.type == "CAMERA":
            return NodeTypeCamera
        elif bobject.type == "SPEAKER":
            return NodeTypeSpeaker
        elif bobject.type == "LIGHT_PROBE":
            return NodeTypeProbe
        return NodeTypeEmpty

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

        animation_flag = bobject.animation_data != None and bobject.animation_data.action != None and bobject.type != 'ARMATURE'

        # Font out
        if animation_flag:
            if not 'object_actions' in o:
                o['object_actions'] = []

            action = bobject.animation_data.action
            aname = arm.utils.safestr(arm.utils.asset_name(action))
            fp = self.get_meshes_file_path('action_' + aname, compressed=self.is_compress())
            assets.add(fp)
            ext = '.lz4' if self.is_compress() else ''
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
                oaction['transform'] = None
                arm.utils.write_arm(fp, actionf)

    def calculate_animation_length(self, action):
        """Calculates the length of the given action."""
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

        return (int(start), int(end))

    def export_animation_track(self, fcurve, frame_range, target):
        """This function exports a single animation track."""
        data_ttrack = {}

        data_ttrack['target'] = target
        data_ttrack['frames'] = []
        data_ttrack['values'] = []

        start = frame_range[0]
        end = frame_range[1]

        for frame in range(start, end + 1):
            data_ttrack['frames'].append(frame)
            data_ttrack['values'].append(fcurve.evaluate(frame))

        return data_ttrack

    def export_object_transform(self, bobject, o):
        # Internal target names for single FCurve data paths
        target_names = {
            "location": ("xloc", "yloc", "zloc"),
            "rotation_euler": ("xrot", "yrot", "zrot"),
            "rotation_quaternion": ("qwrot", "qxrot", "qyrot", "qzrot"),
            "scale": ("xscl", "yscl", "zscl"),
            "delta_location": ("dxloc", "dyloc", "dzloc"),
            "delta_rotation_euler": ("dxrot", "dyrot", "dzrot"),
            "delta_rotation_quaternion": ("dqwrot", "dqxrot", "dqyrot", "dqzrot"),
            "delta_scale": ("dxscl", "dyscl", "dzscl"),
        }

        # Static transform
        o['transform'] = {}
        o['transform']['values'] = self.write_matrix(bobject.matrix_local)

        # Animated transform
        if bobject.animation_data is not None and bobject.type != "ARMATURE":
            action = bobject.animation_data.action

            if action is not None:
                action_name = arm.utils.safestr(arm.utils.asset_name(action))

                if 'object_actions' not in o:
                    o['object_actions'] = []

                fp = self.get_meshes_file_path('action_' + action_name, compressed=self.is_compress())
                assets.add(fp)
                ext = '.lz4' if self.is_compress() else ''
                if ext == '' and not bpy.data.worlds['Arm'].arm_minimize:
                    ext = '.json'
                o['object_actions'].append('action_' + action_name + ext)

                oaction = {}
                oaction['name'] = action.name

                # Export the animation tracks
                oanim = {}
                oaction['anim'] = oanim

                frame_range = self.calculate_animation_length(action)
                oanim['begin'] = frame_range[0]
                oanim['end'] = frame_range[1]

                oanim['tracks'] = []
                self.export_pose_markers(oanim, action)

                for fcurve in action.fcurves:
                    data_path = fcurve.data_path

                    try:
                        data_ttrack = self.export_animation_track(fcurve, frame_range, target_names[data_path][fcurve.array_index])

                    except KeyError:
                        if data_path not in target_names:
                            print(f"Action {action_name}: The data path '{data_path}' is not supported (yet)!")
                            continue

                        # Missing target entry for array_index or something else
                        else:
                            raise

                    oanim['tracks'].append(data_ttrack)

                if True:  #action.arm_cached == False or not os.path.exists(fp):
                    print('Exporting object action ' + action_name)
                    actionf = {}
                    actionf['objects'] = []
                    actionf['objects'].append(oaction)
                    oaction['type'] = 'object'
                    oaction['name'] = action_name
                    oaction['data_ref'] = ''
                    oaction['transform'] = None
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

        if bobject.arm_instanced == 'Off':
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
        # if pose_bone is not None:
        #     transform = pose_bone.matrix.copy()
        #     if pose_bone.parent is not None:
        #         transform = pose_bone.parent.matrix.inverted_safe() * transform
        # else:
        transform = bone.matrix_local.copy()
        if bone.parent is not None:
            transform = (bone.parent.matrix_local.inverted_safe() @ transform)

        o['transform'] = {}
        o['transform']['values'] = self.write_matrix(transform)

        curve_array = self.collect_bone_animation(armature, bone.name)
        animation = len(curve_array) != 0

        if animation and pose_bone:
            begin_frame, end_frame = int(action.frame_range[0]), int(action.frame_range[1])

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

    def use_default_material_part(self):
        # Particle object with no material assigned
        for ps in bpy.data.particles:
            if ps.render_type != 'OBJECT' or ps.instance_object is None:
                continue
            po = ps.instance_object
            if po not in self.objectToArmObjectDict:
                continue
            o = self.objectToArmObjectDict[po]
            if len(o['material_refs']) > 0 and o['material_refs'][0] == 'armdefault' and po not in self.defaultPartMaterialObjects:
                self.defaultPartMaterialObjects.append(po)
                o['material_refs'] = ['armdefaultpart'] # Replace armdefault

    def export_material_ref(self, bobject, material, index, o):
        if material is None: # Use default for empty mat slots
            self.use_default_material(bobject, o)
            return
        if not material in self.materialArray:
            self.materialArray.append(material)
        o['material_refs'].append(arm.utils.asset_name(material))

    def export_particle_system_ref(self, psys, index, o):
        if psys.settings in self.particleSystemArray: # or not modifier.show_render:
            return

        if psys.settings.instance_object == None or psys.settings.render_type != 'OBJECT':
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
        if play_area is None:
            return None
        for space in play_area.spaces:
            if space.type == 'VIEW_3D':
                return space.region_3d.view_matrix
        return None

    def get_viewport_projection_matrix(self):
        play_area = self.get_view3d_area()
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
                        values += self.write_matrix((parent.matrix.inverted_safe() @ pose_bone.matrix))
                    else:
                        values += self.write_matrix(pose_bone.matrix)
        # print('Bone matrices exported in ' + str(time.time() - profile_time))

    def has_baked_material(self, bobject, materials):
        for mat in materials:
            if mat is None:
                continue
            baked_mat = mat.name + '_' + bobject.name + '_baked'
            if baked_mat in bpy.data.materials:
                return True
        return False

    def slot_to_material(self, bobject, slot):
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

            o['mobile'] = bobject.arm_mobile

            if bobject.instance_type == 'COLLECTION' and bobject.instance_collection is not None:
                o['group_ref'] = bobject.instance_collection.name

            if bobject.arm_tilesheet != '':
                o['tilesheet_ref'] = bobject.arm_tilesheet
                o['tilesheet_action_ref'] = bobject.arm_tilesheet_action

            if len(bobject.arm_propertylist) > 0:
                o['properties'] = []
                for p in bobject.arm_propertylist:
                    po = {}
                    po['name'] = p.name_prop
                    po['value'] = getattr(p, p.type_prop + '_prop')
                    o['properties'].append(po)

            # TODO:
            layer_found = True
            if layer_found == False:
                o['spawn'] = False

            # Export the object reference and material references
            objref = bobject.data
            if objref is not None:
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

                wrd = bpy.data.worlds['Arm']
                if wrd.arm_single_data_file:
                    o['data_ref'] = oid
                else:
                    ext = '' if not self.is_compress() else '.lz4'
                    if ext == '' and not bpy.data.worlds['Arm'].arm_minimize:
                        ext = '.json'
                    o['data_ref'] = 'mesh_' + oid + ext + '/' + oid

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

                aabb = bobject.data.arm_aabb
                if aabb[0] == 0 and aabb[1] == 0 and aabb[2] == 0:
                    self.calc_aabb(bobject)
                o['dimensions'] = [aabb[0], aabb[1], aabb[2]]

                #shapeKeys = ArmoryExporter.get_shape_keys(objref)
                #if shapeKeys:
                #   self.ExportMorphWeights(bobject, shapeKeys, scene, o)

            elif type == NodeTypeLight:
                if not objref in self.lightArray:
                    self.lightArray[objref] = {"structName" : objname, "objectTable" : [bobject]}
                else:
                    self.lightArray[objref]["objectTable"].append(bobject)
                o['data_ref'] = self.lightArray[objref]["structName"]

            elif type == NodeTypeProbe:
                if not objref in self.probeArray:
                    self.probeArray[objref] = {"structName" : objname, "objectTable" : [bobject]}
                else:
                    self.probeArray[objref]["objectTable"].append(bobject)
                dist = bobject.data.influence_distance
                if objref.type == "PLANAR":
                    o['dimensions'] = [1.0, 1.0, dist]
                else: # GRID, CUBEMAP
                    o['dimensions'] = [dist, dist, dist]
                o['data_ref'] = self.probeArray[objref]["structName"]

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
            if bobject.type != 'ARMATURE' and bobject.animation_data is not None:
                action = bobject.animation_data.action
                export_actions = [action]
                for track in bobject.animation_data.nla_tracks:
                    if track.strips is None:
                        continue
                    for strip in track.strips:
                        if strip.action == None or strip.action in export_actions:
                            continue
                        export_actions.append(strip.action)
                orig_action = action
                for a in export_actions:
                    bobject.animation_data.action = a
                    self.export_object_transform(bobject, o)
                if len(export_actions) >= 2 and export_actions[0] is None: # No action assigned
                    o['object_actions'].insert(0, 'null')
                bobject.animation_data.action = orig_action
            else:
                self.export_object_transform(bobject, o)

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

            if bobject.type == 'ARMATURE' and bobject.data is not None:
                bdata = bobject.data # Armature data
                action = None # Reference start action
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
                # hasattr - armature modifier may reference non-parent armature object to deform with
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
                ext = '.lz4' if self.is_compress() else ''
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
                    fp = self.get_meshes_file_path('action_' + armatureid + '_' + aname, compressed=self.is_compress())
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

            if parento is None:
                self.output['objects'].append(o)
            else:
                parento['children'].append(o)

            self.post_export_object(bobject, o, type)

            if not hasattr(o, 'children') and len(bobject.children) > 0:
                o['children'] = []

        if bobject.arm_instanced == 'Off':
            for subbobject in bobject.children:
                self.export_object(subbobject, scene, o)

    def export_skin(self, bobject, armature, exportMesh, o):
        # This function exports all skinning data, which includes the skeleton
        # and per-vertex bone influence data
        oskin = {}
        o['skin'] = oskin

        # Write the skin bind pose transform
        otrans = {}
        oskin['transform'] = otrans
        otrans['values'] = self.write_matrix(bobject.matrix_world)

        bone_array = armature.data.bones
        bone_count = len(bone_array)
        rpdat = arm.utils.get_rp()
        max_bones = rpdat.arm_skin_max_bones
        if bone_count > max_bones:
            bone_count = max_bones

        # Write the bone object reference array
        oskin['bone_ref_array'] = np.empty(bone_count, dtype=object)
        oskin['bone_len_array'] = np.empty(bone_count, dtype='<f4')

        for i in range(bone_count):
            boneRef = self.find_bone(bone_array[i].name)
            if boneRef:
                oskin['bone_ref_array'][i] = boneRef[1]["structName"]
                oskin['bone_len_array'][i] = bone_array[i].length
            else:
                oskin['bone_ref_array'][i] = ""
                oskin['bone_len_array'][i] = 0.0

        # Write the bind pose transform array
        oskin['transformsI'] = []
        for i in range(bone_count):
            skeletonI = (armature.matrix_world @ bone_array[i].matrix_local).inverted_safe()
            skeletonI = (skeletonI @ bobject.matrix_world)
            oskin['transformsI'].append(self.write_matrix(skeletonI))

        # Export the per-vertex bone influence data
        group_remap = []
        for group in bobject.vertex_groups:
            for i in range(bone_count):
                if bone_array[i].name == group.name:
                    group_remap.append(i)
                    break
            else:
                group_remap.append(-1)

        bone_count_array = np.empty(len(exportMesh.loops), dtype='<i2')
        bone_index_array = np.empty(len(exportMesh.loops) * 4, dtype='<i2')
        bone_weight_array = np.empty(len(exportMesh.loops) * 4, dtype='<f4')

        vertices = bobject.data.vertices
        count = 0
        for index, l in enumerate(exportMesh.loops):
            bone_count = 0
            total_weight = 0.0
            bone_values = []
            for g in vertices[l.vertex_index].groups:
                bone_index = group_remap[g.group]
                bone_weight = g.weight
                if bone_index >= 0: #and bone_weight != 0.0:
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

            if total_weight != 0.0 and total_weight != 1.0:
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
        for bone in armature.pose.bones:
            if len(bone.constraints) > 0:
                if 'constraints' not in oskin:
                    oskin['constraints'] = []
                self.add_constraints(bone, oskin, bone=True)

    def write_mesh(self, bobject, fp, o):
        wrd = bpy.data.worlds['Arm']
        if wrd.arm_single_data_file:
            self.output['mesh_datas'].append(o)
        else: # One mesh data per file
            mesh_obj = {}
            mesh_obj['mesh_datas'] = [o]
            arm.utils.write_arm(fp, mesh_obj)
            bobject.data.arm_cached = True

    def calc_aabb(self, bobject):
        aabb_center = 0.125 * sum((Vector(b) for b in bobject.bound_box), Vector())
        bobject.data.arm_aabb = [ \
            abs((bobject.bound_box[6][0] - bobject.bound_box[0][0]) / 2 + abs(aabb_center[0])) * 2, \
            abs((bobject.bound_box[6][1] - bobject.bound_box[0][1]) / 2 + abs(aabb_center[1])) * 2, \
            abs((bobject.bound_box[6][2] - bobject.bound_box[0][2]) / 2 + abs(aabb_center[2])) * 2  \
        ]

    def export_mesh_data(self, exportMesh, bobject, o, has_armature=False):
        exportMesh.calc_normals_split()
        # exportMesh.calc_loop_triangles()

        loops = exportMesh.loops
        num_verts = len(loops)
        num_uv_layers = len(exportMesh.uv_layers)
        is_baked = self.has_baked_material(bobject, exportMesh.materials)
        has_tex = (self.get_export_uvs(exportMesh) and num_uv_layers > 0) or is_baked
        has_tex1 = has_tex and num_uv_layers > 1
        num_colors = len(exportMesh.vertex_colors)
        has_col = self.get_export_vcols(exportMesh) and num_colors > 0
        has_tang = self.has_tangents(exportMesh)

        pdata = np.empty(num_verts * 4, dtype='<f4') # p.xyz, n.z
        ndata = np.empty(num_verts * 2, dtype='<f4') # n.xy
        if has_tex:
            t0map = 0 # Get active uvmap
            t0data = np.empty(num_verts * 2, dtype='<f4')
            uv_layers = exportMesh.uv_layers
            if uv_layers is not None:
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
            if has_tex1:
                t1map = 1 if t0map == 0 else 0
                t1data = np.empty(num_verts * 2, dtype='<f4')
            # Scale for packed coords
            maxdim = 1.0
            lay0 = uv_layers[t0map]
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
                    if abs(v.uv[1]) > maxdim:
                        maxdim = abs(v.uv[1])
            if maxdim > 1:
                o['scale_tex'] = maxdim
                invscale_tex = (1 / o['scale_tex']) * 32767
            else:
                invscale_tex = 1 * 32767
            if has_tang:
                exportMesh.calc_tangents(uvmap=lay0.name)
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

        verts = exportMesh.vertices
        if has_tex:
            lay0 = exportMesh.uv_layers[t0map]
            if has_tex1:
                lay1 = exportMesh.uv_layers[t1map]
        if has_col:
            vcol0 = exportMesh.vertex_colors[0].data

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
            if has_col:
                col = vcol0[loop.index].color
                i3 = i * 3
                cdata[i3    ] = col[0]
                cdata[i3 + 1] = col[1]
                cdata[i3 + 2] = col[2]

        mats = exportMesh.materials
        poly_map = []
        for i in range(max(len(mats), 1)):
            poly_map.append([])
        for poly in exportMesh.polygons:
            poly_map[poly.material_index].append(poly)

        o['index_arrays'] = []
        for index, polys in enumerate(poly_map):
            tris = 0
            for poly in polys:
                tris += poly.loop_total - 2
            if tris == 0: # No face assigned
                continue
            prim = np.empty(tris * 3, dtype='<i4')

            i = 0
            for poly in polys:
                first = poly.loop_start
                total = poly.loop_total
                if total == 3:
                    prim[i    ] = loops[first    ].index
                    prim[i + 1] = loops[first + 1].index
                    prim[i + 2] = loops[first + 2].index
                    i += 3
                else:
                    for j in range(total - 2):
                        prim[i    ] = loops[first + total - 1].index
                        prim[i + 1] = loops[first + j        ].index
                        prim[i + 2] = loops[first + j + 1    ].index
                        i += 3

            ia = {}
            ia['values'] = prim
            ia['material'] = 0
            if len(mats) > 1:
                for i in range(len(mats)): # Multi-mat mesh
                    if (mats[i] == mats[index]): # Default material for empty slots
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
        if has_col:
            cdata *= 32767
            cdata = np.array(cdata, dtype='<i2')
        if has_tang:
            tangdata *= 32767
            tangdata = np.array(tangdata, dtype='<i2')

        # Output
        o['vertex_arrays'] = []
        o['vertex_arrays'].append({ 'attrib': 'pos', 'values': pdata })
        o['vertex_arrays'].append({ 'attrib': 'nor', 'values': ndata })
        if has_tex:
            o['vertex_arrays'].append({ 'attrib': 'tex', 'values': t0data })
            if has_tex1:
                o['vertex_arrays'].append({ 'attrib': 'tex1', 'values': t1data })
        if has_col:
            o['vertex_arrays'].append({ 'attrib': 'col', 'values': cdata })
        if has_tang:
            o['vertex_arrays'].append({ 'attrib': 'tang', 'values': tangdata })

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
        return self.get_export_uvs(exportMesh) == True and self.get_export_tangents(exportMesh) == True and len(exportMesh.uv_layers) > 0

    def export_mesh(self, objectRef, scene):
        # profile_time = time.time()
        # This function exports a single mesh object
        table = objectRef[1]["objectTable"]
        bobject = table[0]
        oid = arm.utils.safestr(objectRef[1]["structName"])

        wrd = bpy.data.worlds['Arm']
        if wrd.arm_single_data_file:
            fp = None
        else:
            fp = self.get_meshes_file_path('mesh_' + oid, compressed=self.is_compress())
            assets.add(fp)
            # No export necessary
            if bobject.data.arm_cached and os.path.exists(fp):
                return

        # Mesh users have different modifier stack
        for i in range(1, len(table)):
            if not self.mod_equal_stack(bobject, table[i]):
                log.warn('{0} users {1} and {2} differ in modifier stack - use Make Single User - Object & Data for now'.format(oid, bobject.name, table[i].name))
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

        bobject_eval = bobject.evaluated_get(self.depsgraph) if apply_modifiers else bobject
        exportMesh = bobject_eval.to_mesh()

        if exportMesh is None:
            log.warn(oid + ' was not exported')
            return

        if len(exportMesh.uv_layers) > 2:
            log.warn(oid + ' exceeds maximum of 2 UV Maps supported')

        # Update aabb
        self.calc_aabb(bobject)

        # Process meshes
        if ArmoryExporter.optimize_enabled:
            vert_list = exporter_opt.export_mesh_data(self, exportMesh, bobject, o, has_armature=armature != None)
            if armature:
                exporter_opt.export_skin(self, bobject, armature, vert_list, o)
        else:
            self.export_mesh_data(exportMesh, bobject, o, has_armature=armature != None)
            if armature:
                self.export_skin(bobject, armature, exportMesh, o)

        # Restore the morph state
        if shapeKeys:
            bobject.active_shape_key_index = activeShapeKeyIndex
            bobject.show_only_shape_key = showOnlyShapeKey

            for m in range(len(currentMorphValue)):
                shapeKeys.key_blocks[m].value = currentMorphValue[m]

            mesh.update()

        # Check if mesh is using instanced rendering
        instanced_type, instanced_data = self.object_process_instancing(table, o['scale_pos'])

        # Save offset data for instanced rendering
        if instanced_type > 0:
            o['instanced_data'] = instanced_data
            o['instanced_type'] = instanced_type

        # Export usage
        if bobject.data.arm_dynamic_usage:
            o['dynamic_usage'] = bobject.data.arm_dynamic_usage

        self.write_mesh(bobject, fp, o)
        # print('Mesh exported in ' + str(time.time() - profile_time))

        if hasattr(bobject, 'evaluated_get'):
            bobject_eval.to_mesh_clear()

    def export_light(self, objectRef):
        # This function exports a single light object
        rpdat = arm.utils.get_rp()
        objref = objectRef[0]
        objtype = objref.type
        o = {}
        o['name'] = objectRef[1]["structName"]
        o['type'] = objtype.lower()
        o['cast_shadow'] = objref.use_shadow
        o['near_plane'] = objref.arm_clip_start
        o['far_plane'] = objref.arm_clip_end
        o['fov'] = objref.arm_fov
        o['color'] = [objref.color[0], objref.color[1], objref.color[2]]
        o['strength'] = objref.energy
        o['shadows_bias'] = objref.arm_shadows_bias * 0.0001
        if rpdat.rp_shadows:
            if objtype == 'POINT':
                o['shadowmap_size'] = int(rpdat.rp_shadowmap_cube)
            else:
                o['shadowmap_size'] = arm.utils.get_cascade_size(rpdat)
        else:
            o['shadowmap_size'] = 0

        if objtype == 'SUN':
            o['strength'] *= 0.325
            o['shadows_bias'] *= 20.0 # Scale bias for ortho light matrix
            if o['shadowmap_size'] > 1024:
                o['shadows_bias'] *= 1 / (o['shadowmap_size'] / 1024) # Less bias for bigger maps
        elif objtype == 'POINT':
            o['strength'] *= 2.6
            if bpy.app.version >= (2, 80, 72):
                o['strength'] *= 0.01
            o['fov'] = 1.5708 # pi/2
            o['shadowmap_cube'] = True
            if objref.shadow_soft_size > 0.1:
                o['light_size'] = objref.shadow_soft_size * 10
        elif objtype == 'SPOT':
            o['strength'] *= 2.6
            if bpy.app.version >= (2, 80, 72):
                o['strength'] *= 0.01
            o['spot_size'] = math.cos(objref.spot_size / 2)
            o['spot_blend'] = objref.spot_blend / 10 # Cycles defaults to 0.15
        elif objtype == 'AREA':
            o['strength'] *= 80.0 / (objref.size * objref.size_y)
            if bpy.app.version >= (2, 80, 72):
                o['strength'] *= 0.01
            o['size'] = objref.size
            o['size_y'] = objref.size_y

        self.output['light_datas'].append(o)

    def export_probe(self, objectRef):
        o = {}
        o['name'] = objectRef[1]["structName"]
        bo = objectRef[0]

        if bo.type == 'GRID':
            o['type'] = 'grid'
        elif bo.type == 'PLANAR':
            o['type'] = 'planar'
        else: # CUBEMAP
            o['type'] = 'cubemap'

        self.output['probe_datas'].append(o)

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

    def extract_ortho(self, o, proj):
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
        mat.node_tree.nodes['Principled BSDF'].inputs[7].default_value = 0.25
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
        if node.type == 'TEX_IMAGE' and node.image is not None:
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
        if output_node is not None:
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
            if 'mesh' in rpasses and material.arm_blending:
                blending_used = True
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

                if material in self.materialToObjectDict:
                    mat_users = self.materialToObjectDict[material]
                    for ob in mat_users:
                        ob.data.arm_cached = False

            self.output['material_datas'].append(o)
            material.arm_cached = True

        # Auto-enable render-path featues
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

            if psettings is None:
                continue

            if psettings.instance_object == None or psettings.render_type != 'OBJECT':
                continue

            o['name'] = particleRef[1]["structName"]
            o['type'] = 0 if psettings.type == 'EMITTER' else 1 # HAIR
            o['loop'] = psettings.arm_loop
            o['render_emitter'] = False # TODO
            # Emission
            o['count'] = int(psettings.count * psettings.arm_count_mult)
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
            o['instance_object'] = psettings.instance_object.name
            self.objectToArmObjectDict[psettings.instance_object]['is_particle'] = True
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
        if worldRef is not None:
            o = {}
            w = worldRef
            o['name'] = w.name
            self.post_export_world(w, o)
            self.output['world_datas'].append(o)

    def is_compress(self):
        return ArmoryExporter.compress_enabled

    def export_objects(self, scene):
        if not ArmoryExporter.option_mesh_only:
            self.output['light_datas'] = []
            self.output['camera_datas'] = []
            self.output['speaker_datas'] = []
            for o in self.lightArray.items():
                self.export_light(o)
            for o in self.cameraArray.items():
                self.export_camera(o)
            for sound in bpy.data.sounds: # Keep sounds with fake user
                if sound.use_fake_user:
                    assets.add(arm.utils.asset_path(sound.filepath))
            for o in self.speakerArray.items():
                self.export_speaker(o)
            if len(bpy.data.lightprobes) > 0:
                self.output['probe_datas'] = []
                for o in self.probeArray.items():
                    self.export_probe(o)
        self.output['mesh_datas'] = []
        for o in self.meshArray.items():
            self.export_mesh(o, scene)

    def execute(self, context, filepath, scene=None):
        global current_output
        profile_time = time.time()

        self.scene = context.scene if scene == None else scene
        current_frame, current_subframe = self.scene.frame_current, self.scene.frame_subframe

        print('Exporting ' + arm.utils.asset_name(self.scene))

        self.output = {}
        current_output = self.output
        self.output['frame_time'] = 1.0 / (self.scene.render.fps / self.scene.render.fps_base)
        self.filepath = filepath
        self.bobjectArray = {}
        self.bobjectBoneArray = {}
        self.meshArray = {}
        self.lightArray = {}
        self.probeArray = {}
        self.cameraArray = {}
        self.camera_spawned = False
        self.speakerArray = {}
        self.materialArray = []
        self.particleSystemArray = {}
        self.worldArray = {} # Export all worlds
        self.boneParentArray = {}
        self.materialToObjectDict = dict()
        self.defaultMaterialObjects = [] # If no material is assigned, provide default to mimic cycles
        self.defaultSkinMaterialObjects = []
        self.defaultPartMaterialObjects = []
        self.materialToArmObjectDict = dict()
        self.objectToArmObjectDict = dict()
        self.bone_tracks = []
        # self.active_layers = []
        # for i in range(0, len(self.scene.view_layers)):
            # if self.scene.view_layers[i] == True:
                # self.active_layers.append(i)
        self.depsgraph = context.evaluated_depsgraph_get()
        self.preprocess()

        # scene_objects = []
        # for lay in self.scene.view_layers:
            # scene_objects += lay.objects
        scene_objects = self.scene.collection.all_objects

        for bobject in scene_objects:
            # Map objects to game objects
            o = {}
            o['traits'] = []
            self.objectToArmObjectDict[bobject] = o
            # Process
            if not bobject.parent:
                self.process_bobject(bobject)
                # Softbody needs connected triangles, use optimized geometry export
                for mod in bobject.modifiers:
                    if mod.type == 'CLOTH' or mod.type == 'SOFT_BODY':
                        ArmoryExporter.optimize_enabled = True

        self.process_skinned_meshes()

        self.output['name'] = arm.utils.safestr(self.scene.name)
        if self.filepath.endswith('.lz4'):
            self.output['name'] += '.lz4'
        elif not bpy.data.worlds['Arm'].arm_minimize:
            self.output['name'] += '.json'

        # Create unique material variants for skinning, tilesheets, particles
        matvars = []
        matslots = []
        for bo in scene_objects:
            if arm.utils.export_bone_data(bo):
                for slot in bo.material_slots:
                    if slot.material == None or slot.material.library is not None:
                        continue
                    if slot.material.name.endswith('_armskin'):
                        continue
                    matslots.append(slot)
                    mat_name = slot.material.name + '_armskin'
                    mat = bpy.data.materials.get(mat_name)
                    if mat is None:
                        mat = slot.material.copy()
                        mat.name = mat_name
                        matvars.append(mat)
                    slot.material = mat
            elif bo.arm_tilesheet != '':
                for slot in bo.material_slots:
                    if slot.material == None or slot.material.library is not None:
                        continue
                    if slot.material.name.endswith('_armtile'):
                        continue
                    matslots.append(slot)
                    mat_name = slot.material.name + '_armtile'
                    mat = bpy.data.materials.get(mat_name)
                    if mat is None:
                        mat = slot.material.copy()
                        mat.name = mat_name
                        mat.arm_tilesheet_flag = True
                        matvars.append(mat)
                    slot.material = mat
        # Particle and non-particle objects can not share material
        for psys in bpy.data.particles:
            bo = psys.instance_object
            if bo == None or psys.render_type != 'OBJECT':
                continue
            for slot in bo.material_slots:
                if slot.material == None or slot.material.library is not None:
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

        # Auto-bones
        wrd = bpy.data.worlds['Arm']
        rpdat = arm.utils.get_rp()
        if rpdat.arm_skin_max_bones_auto:
            max_bones = 8
            for armature in bpy.data.armatures:
                if max_bones < len(armature.bones):
                    max_bones = len(armature.bones)
            rpdat.arm_skin_max_bones = max_bones

        # Terrain
        if self.scene.arm_terrain_object is not None:
            # Append trait
            if not 'traits' in self.output:
                self.output['traits'] = []
            trait = {}
            trait['type'] = 'Script'
            trait['class_name'] = 'armory.trait.internal.TerrainPhysics'
            self.output['traits'].append(trait)
            ArmoryExporter.import_traits.append(trait['class_name'])
            ArmoryExporter.export_physics = True
            assets.add_khafile_def('arm_terrain')
            # Export material
            mat = self.scene.arm_terrain_object.children[0].data.materials[0]
            self.materialArray.append(mat)
            # Terrain data
            terrain = {}
            terrain['name'] = 'Terrain'
            terrain['sectors_x'] = self.scene.arm_terrain_sectors[0]
            terrain['sectors_y'] = self.scene.arm_terrain_sectors[1]
            terrain['sector_size'] = self.scene.arm_terrain_sector_size
            terrain['height_scale'] = self.scene.arm_terrain_height_scale
            terrain['material_ref'] = mat.name
            self.output['terrain_datas'] = [terrain]
            self.output['terrain_ref'] = 'Terrain'

        self.output['objects'] = []
        for bo in scene_objects:
            if not bo.parent:
                self.export_object(bo, self.scene)

        if len(bpy.data.collections) > 0:
            self.output['groups'] = []
            for collection in bpy.data.collections:
                if collection.name.startswith('RigidBodyWorld') or collection.name.startswith('Trait|'):
                    continue
                o = {}
                o['name'] = collection.name
                o['object_refs'] = []
                # Add unparented objects only, then instantiate full object child tree
                for bobject in collection.objects:
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
                        if bobject.name not in scene_objects and collection.library is not None:
                            self.process_bobject(bobject)
                            self.export_object(bobject, self.scene)
                            o['object_refs'].append(arm.utils.asset_name(bobject))
                        else:
                            o['object_refs'].append(bobject.name)
                self.output['groups'].append(o)

        if not ArmoryExporter.option_mesh_only:
            if self.scene.camera is not None:
                self.output['camera_ref'] = self.scene.camera.name
            else:
                if self.scene.name == arm.utils.get_project_scene_name():
                    log.warn('No camera found in active scene')

            self.output['material_datas'] = []

            # Object with no material assigned in the scene
            if len(self.defaultMaterialObjects) > 0:
                self.make_default_mat('armdefault', self.defaultMaterialObjects)
            if len(self.defaultSkinMaterialObjects) > 0:
                self.make_default_mat('armdefaultskin', self.defaultSkinMaterialObjects)
            if len(bpy.data.particles) > 0:
                self.use_default_material_part()
            if len(self.defaultPartMaterialObjects) > 0:
                self.make_default_mat('armdefaultpart', self.defaultPartMaterialObjects, is_particle=True)

            self.export_materials()
            self.export_particle_systems()
            self.output['world_datas'] = []
            self.export_worlds()
            self.export_tilesheets()

            if self.scene.world is not None:
                self.output['world_ref'] = self.scene.world.name

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
            self.camera_spawned = True

        # No camera found
        if not self.camera_spawned:
            log.warn('No camera found in active scene layers')

        # No camera found, create a default one
        if (len(self.output['camera_datas']) == 0 or len(bpy.data.cameras) == 0) or not self.camera_spawned:
            self.create_default_camera()

        # Scene traits
        if wrd.arm_physics != 'Disabled' and ArmoryExporter.export_physics:
            if not 'traits' in self.output:
                self.output['traits'] = []
            x = {}
            x['type'] = 'Script'
            phys_pkg = 'bullet' if wrd.arm_physics_engine == 'Bullet' else 'oimo'
            x['class_name'] = 'armory.trait.physics.' + phys_pkg + '.PhysicsWorld'
            rbw = self.scene.rigidbody_world
            if rbw != None and rbw.enabled:
                x['parameters'] = [str(rbw.time_scale), str(1 / rbw.steps_per_second), str(rbw.solver_iterations)]
            self.output['traits'].append(x)
        if wrd.arm_navigation != 'Disabled' and ArmoryExporter.export_navigation:
            if not 'traits' in self.output:
                self.output['traits'] = []
            x = {}
            x['type'] = 'Script'
            x['class_name'] = 'armory.trait.navigation.Navigation'
            self.output['traits'].append(x)
        if wrd.arm_debug_console:
            if not 'traits' in self.output:
                self.output['traits'] = []
            ArmoryExporter.export_ui = True
            x = {}
            x['type'] = 'Script'
            x['class_name'] = 'armory.trait.internal.DebugConsole'
            x['parameters'] = [str(arm.utils.get_ui_scale())]
            self.output['traits'].append(x)
        if wrd.arm_live_patch:
            if not 'traits' in self.output:
                self.output['traits'] = []
            x = {}
            x['type'] = 'Script'
            x['class_name'] = 'armory.trait.internal.LivePatch'
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
            orig_mat = bpy.data.materials[slot.material.name[:-8]] # _armskin, _armpart, _armtile
            orig_mat.export_uvs = slot.material.export_uvs
            orig_mat.export_vcols = slot.material.export_vcols
            orig_mat.export_tangents = slot.material.export_tangents
            orig_mat.arm_cached = slot.material.arm_cached
            slot.material = orig_mat
        for mat in matvars:
            bpy.data.materials.remove(mat, do_unlink=True)

        # Restore frame
        if scene.frame_current != current_frame:
            scene.frame_set(current_frame, subframe=current_subframe)

        print('Scene exported in ' + str(time.time() - profile_time))
        return {'FINISHED'}

    def create_default_camera(self, is_viewport_camera=False):
        o = {}
        o['name'] = 'DefaultCamera'
        o['near_plane'] = 0.1
        o['far_plane'] = 100.0
        o['fov'] = 0.85
        o['frustum_culling'] = True
        o['clear_color'] = self.get_camera_clear_color()
        # Set viewport camera projection
        if is_viewport_camera:
            proj, is_persp = self.get_viewport_projection_matrix()
            if proj is not None:
                if is_persp:
                    self.extract_projection(o, proj, with_planes=False)
                else:
                    self.extract_ortho(o, proj)
        self.output['camera_datas'].append(o)

        o = {}
        o['name'] = 'DefaultCamera'
        o['type'] = 'camera_object'
        o['data_ref'] = 'DefaultCamera'
        o['material_refs'] = []
        o['transform'] = {}
        viewport_matrix = self.get_viewport_view_matrix()
        if viewport_matrix is not None:
            o['transform']['values'] = self.write_matrix(viewport_matrix.inverted_safe())
            o['local_only'] = True
        else:
            o['transform']['values'] = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]
        o['traits'] = []
        trait = {}
        trait['type'] = 'Script'
        trait['class_name'] = 'armory.trait.WalkNavigation'
        o['traits'].append(trait)
        ArmoryExporter.import_traits.append(trait['class_name'])
        self.output['objects'].append(o)
        self.output['camera_ref'] = 'DefaultCamera'

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

    def object_process_instancing(self, refs, scale_pos):
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
                    if child.arm_export == False or child.hide_render:
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
                    if 'Scale'in inst:
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
        if not hasattr(ArmoryExporter, 'optimize_enabled'):
            ArmoryExporter.optimize_enabled = False
        if not hasattr(ArmoryExporter, 'import_traits'):
            ArmoryExporter.import_traits = [] # Referenced traits
        ArmoryExporter.option_mesh_only = False

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
            is_static = not rb.enabled or (rb.type == 'PASSIVE' and not rb.kinematic)
            if is_static:
                body_mass = 0
            x = {}
            x['type'] = 'Script'
            x['class_name'] = 'armory.trait.physics.' + phys_pkg + '.RigidBody'
            col_group = ''
            for b in rb.collision_collections:
                col_group = ('1' if b else '0') + col_group
            x['parameters'] = [str(shape), str(body_mass), str(rb.friction), str(rb.restitution), str(int(col_group, 2))]
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
            col_margin = str(rb.collision_margin) if rb.use_margin else '0.0'
            if rb.use_deactivation or bobject.arm_rb_force_deactivation:
                deact_lv = str(rb.deactivate_linear_velocity)
                deact_av = str(rb.deactivate_angular_velocity)
                deact_time = str(bobject.arm_rb_deactivation_time)
            else:
                deact_lv = '0.0'
                deact_av = '0.0'
                deact_time = '0.0'
            body_params = '[{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}]'.format(
                str(rb.linear_damping),
                str(rb.angular_damping),
                str(lx), str(ly), str(lz),
                str(ax), str(ay), str(az),
                col_margin,
                deact_lv, deact_av, deact_time
            )
            body_flags = '[{0}, {1}, {2}]'.format(
                str(rb.kinematic).lower(),
                str(bobject.arm_rb_trigger).lower(),
                str(bobject.arm_rb_ccd).lower()
            )
            x['parameters'].append(body_params)
            x['parameters'].append(body_flags)
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
            if hasattr(con, 'target') and con.target is not None:
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
                if t.type_prop == 'Logic Nodes' and t.node_tree_prop != None and t.node_tree_prop.name != '':
                    x['type'] = 'Script'
                    group_name = arm.utils.safesrc(t.node_tree_prop.name[0].upper() + t.node_tree_prop.name[1:])
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
                        log.warn('Scene "' + self.scene.name + '" - Object "' + bobject.name + '" - Referenced canvas "' + t.canvas_name_prop + '" not found, skipping')
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
                            # override = {'selected_objects': [bobject]}
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
                    else: # Haxe
                        trait_prefix = arm.utils.safestr(bpy.data.worlds['Arm'].arm_project_package) + '.'
                        hxfile = '/Sources/' + (trait_prefix + t.class_name_prop).replace('.', '/') + '.hx'
                        if not os.path.exists(arm.utils.get_fp() + hxfile):
                            # TODO: Halt build here once this check is tested
                            print('Armory Error: Scene "' + self.scene.name + '" - Object "' + bobject.name + '" : Referenced trait file "' + hxfile + '" not found')

                    x['class_name'] = trait_prefix + t.class_name_prop
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
        if soft_type == 0:
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
        if rb1 == None or rb2 is None:
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
        elif '_EnvSky' in wrd.world_defs:
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
                po['radiance'] += '.jpg' if disable_hdr else '.hdr'
                po['radiance_mipmaps'] = num_mips
        po['strength'] = strength
        o['probe'] = po

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
