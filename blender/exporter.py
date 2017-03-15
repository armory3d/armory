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
import ast
import write_probes
import assets
import armutils
import subprocess
import log
import armmaterial.make as make_material
import armmaterial.mat_batch as mat_batch
import armmaterial.texture as make_texture
import nodes
import make_renderer
import make_renderpath

NodeTypeNode = 0
NodeTypeBone = 1
NodeTypeMesh = 2
NodeTypeLamp = 3
NodeTypeCamera = 4
NodeTypeSpeaker = 5
AnimationTypeSampled = 0
AnimationTypeLinear = 1
AnimationTypeBezier = 2
ExportEpsilon = 1.0e-6

structIdentifier = ["object", "bone_object", "mesh_object", "lamp_object", "camera_object", "speaker_object"]

subtranslationName = ["xloc", "yloc", "zloc"]
subrotationName = ["xrot", "yrot", "zrot"]
subscaleName = ["xscl", "yscl", "zscl"]
deltaSubtranslationName = ["dxloc", "dyloc", "dzloc"]
deltaSubrotationName = ["dxrot", "dyrot", "dzrot"]
deltaSubscaleName = ["dxscl", "dyscl", "dzscl"]
axisName = ["x", "y", "z"]

class Vertex:
    __slots__ = ("co", "normal", "uvs", "col", "loop_indices", "index", "bone_weights", "bone_indices", "bone_count", "vertexIndex")
    def __init__(self, mesh, loop):
        self.vertexIndex = loop.vertex_index
        i = loop.index
        self.co = mesh.vertices[self.vertexIndex].co.freeze()
        self.normal = loop.normal.freeze()
        self.uvs = tuple(layer.data[i].uv.freeze() for layer in mesh.uv_layers)
        self.col = [0, 0, 0]
        if len(mesh.vertex_colors) > 0:
            self.col = mesh.vertex_colors[0].data[i].color.freeze()
        self.loop_indices = [i]

        # Take the four most influential groups
        # groups = sorted(mesh.vertices[self.vertexIndex].groups, key=lambda group: group.weight, reverse=True)
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
            (self.uvs == other.uvs)
            )

        if eq:
            indices = self.loop_indices + other.loop_indices
            self.loop_indices = indices
            other.loop_indices = indices
        return eq

class ExportVertex:
    __slots__ = ("hash", "vertexIndex", "faceIndex", "position", "normal", "color", "texcoord0", "texcoord1")

    def __init__(self):
        self.color = [1.0, 1.0, 1.0]
        self.texcoord0 = [0.0, 0.0]
        self.texcoord1 = [0.0, 0.0]

    def __eq__(self, v):
        if self.hash != v.hash:
            return False
        if self.position != v.position:
            return False
        if self.normal != v.normal:
            return False
        if self.texcoord0 != v.texcoord0:
            return False
        if self.color != v.color:
            return False
        if self.texcoord1 != v.texcoord1:
            return False
        return True

    def Hash(self):
        h = hash(self.position[0])
        h = h * 21737 + hash(self.position[1])
        h = h * 21737 + hash(self.position[2])
        h = h * 21737 + hash(self.normal[0])
        h = h * 21737 + hash(self.normal[1])
        h = h * 21737 + hash(self.normal[2])
        h = h * 21737 + hash(self.color[0])
        h = h * 21737 + hash(self.color[1])
        h = h * 21737 + hash(self.color[2])
        h = h * 21737 + hash(self.texcoord0[0])
        h = h * 21737 + hash(self.texcoord0[1])
        h = h * 21737 + hash(self.texcoord1[0])
        h = h * 21737 + hash(self.texcoord1[1])
        self.hash = h

class ArmoryExporter:
    '''Export to Armory format'''

    def write_matrix(self, matrix):
        return [matrix[0][0], matrix[0][1], matrix[0][2], matrix[0][3],
                matrix[1][0], matrix[1][1], matrix[1][2], matrix[1][3],
                matrix[2][0], matrix[2][1], matrix[2][2], matrix[2][3],
                matrix[3][0], matrix[3][1], matrix[3][2], matrix[3][3]]

    def write_vector2d(self, vector):
        return [vector[0], vector[1]]

    def write_vector3d(self, vector):
        return [vector[0], vector[1], vector[2]]

    def write_vertex_array2d(self, vertexArray, attrib):
        va = []
        count = len(vertexArray)
        k = 0

        lineCount = count >> 3
        for i in range(lineCount):
            for j in range(7):
                va += self.write_vector2d(getattr(vertexArray[k], attrib))
                k += 1

            va += self.write_vector2d(getattr(vertexArray[k], attrib))
            k += 1

        count &= 7
        if (count != 0):
            for j in range(count - 1):
                va += self.write_vector2d(getattr(vertexArray[k], attrib))
                k += 1

            va += self.write_vector2d(getattr(vertexArray[k], attrib))

        return va

    def write_vertex_array3d(self, vertex_array, attrib):
        va = []
        count = len(vertex_array)
        k = 0

        lineCount = count >> 3
        for i in range(lineCount):

            for j in range(7):
                va += self.write_vector3d(getattr(vertex_array[k], attrib))
                k += 1

            va += self.write_vector3d(getattr(vertex_array[k], attrib))
            k += 1

        count &= 7
        if count != 0:
            for j in range(count - 1):
                va += self.write_vector3d(getattr(vertex_array[k], attrib))
                k += 1

            va += self.write_vector3d(getattr(vertex_array[k], attrib))

        return va

    def write_triangle(self, triangle_index, index_table):
        i = triangle_index * 3
        return [index_table[i], index_table[i + 1], index_table[i + 2]]

    def write_triangle_array(self, count, index_table):
        va = []
        triangle_index = 0

        line_count = count >> 4
        for i in range(line_count):

            for j in range(15):
                va += self.write_triangle(triangle_index, index_table)
                triangle_index += 1

            va += self.write_triangle(triangle_index, index_table)
            triangle_index += 1

        count &= 15
        if (count != 0):

            for j in range(count - 1):
                va += self.write_triangle(triangle_index, index_table)
                triangle_index += 1

            va += self.write_triangle(triangle_index, index_table)

        return va

    def get_meshes_file_path(self, object_id, compressed=False):
        index = self.filepath.rfind('/')
        mesh_fp = self.filepath[:(index + 1)] + 'meshes/'
        if not os.path.exists(mesh_fp):
            os.makedirs(mesh_fp)
        ext = '.zip' if compressed else '.arm'
        return mesh_fp + object_id + ext

    def get_greasepencils_file_path(self, object_id, compressed=False):
        index = self.filepath.rfind('/')
        gp_fp = self.filepath[:(index + 1)] + 'greasepencils/'
        if not os.path.exists(gp_fp):
            os.makedirs(gp_fp)
        ext = '.zip' if compressed else '.arm'
        return gp_fp + object_id + ext

    @staticmethod
    def get_bobject_type(bobject):
        if bobject.type == "MESH":
            if len(bobject.data.polygons) != 0:
                return NodeTypeMesh
        elif bobject.type == "FONT":
            return NodeTypeMesh
        elif bobject.type == "META": # Metaball
            return NodeTypeMesh
        elif bobject.type == "LAMP":
            return NodeTypeLamp
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

    def find_node(self, name):
        for bobject_ref in self.bobjectArray.items():
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

    @staticmethod
    def animation_keys_different(fcurve):
        key_count = len(fcurve.keyframe_points)
        if key_count > 0:
            key1 = fcurve.keyframe_points[0].co[1]
            for i in range(1, key_count):
                key2 = fcurve.keyframe_points[i].co[1]
                if math.fabs(key2 - key1) > ExportEpsilon:
                    return True
        return False

    @staticmethod
    def animation_tangents_nonzero(fcurve):
        key_count = len(fcurve.keyframe_points)
        if key_count > 0:
            key = fcurve.keyframe_points[0].co[1]
            left = fcurve.keyframe_points[0].handle_left[1]
            right = fcurve.keyframe_points[0].handle_right[1]
            if ((math.fabs(key - left) > ExportEpsilon) or (math.fabs(right - key) > ExportEpsilon)):
                return True
            for i in range(1, key_count):
                key = fcurve.keyframe_points[i].co[1]
                left = fcurve.keyframe_points[i].handle_left[1]
                right = fcurve.keyframe_points[i].handle_right[1]
                if ((math.fabs(key - left) > ExportEpsilon) or (math.fabs(right - key) > ExportEpsilon)):
                    return True
        return False

    @staticmethod
    def matrices_different(m1, m2):
        for i in range(4):
            for j in range(4):
                if math.fabs(m1[i][j] - m2[i][j]) > ExportEpsilon:
                    return True
        return False

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

    @staticmethod
    def animation_present(fcurve, kind):
        if kind != AnimationTypeBezier:
            return ArmoryExporter.animation_keys_different(fcurve)
        return ((ArmoryExporter.animation_keys_different(fcurve)) or (ArmoryExporter.animation_tangents_nonzero(fcurve)))

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

    @staticmethod
    def deindex_mesh(mesh, material_table):
        # This function deindexes all vertex positions, colors, and texcoords.
        # Three separate ExportVertex structures are created for each triangle.
        vertexArray = mesh.vertices
        export_vertex_array = []
        faceIndex = 0

        for face in mesh.tessfaces:
            k1 = face.vertices[0]
            k2 = face.vertices[1]
            k3 = face.vertices[2]

            v1 = vertexArray[k1]
            v2 = vertexArray[k2]
            v3 = vertexArray[k3]

            exportVertex = ExportVertex()
            exportVertex.vertexIndex = k1
            exportVertex.faceIndex = faceIndex
            exportVertex.position = v1.co
            exportVertex.normal = v1.normal if (face.use_smooth) else face.normal
            export_vertex_array.append(exportVertex)

            exportVertex = ExportVertex()
            exportVertex.vertexIndex = k2
            exportVertex.faceIndex = faceIndex
            exportVertex.position = v2.co
            exportVertex.normal = v2.normal if (face.use_smooth) else face.normal
            export_vertex_array.append(exportVertex)

            exportVertex = ExportVertex()
            exportVertex.vertexIndex = k3
            exportVertex.faceIndex = faceIndex
            exportVertex.position = v3.co
            exportVertex.normal = v3.normal if (face.use_smooth) else face.normal
            export_vertex_array.append(exportVertex)

            material_table.append(face.material_index)

            if len(face.vertices) == 4:
                k1 = face.vertices[0]
                k2 = face.vertices[2]
                k3 = face.vertices[3]

                v1 = vertexArray[k1]
                v2 = vertexArray[k2]
                v3 = vertexArray[k3]

                exportVertex = ExportVertex()
                exportVertex.vertexIndex = k1
                exportVertex.faceIndex = faceIndex
                exportVertex.position = v1.co
                exportVertex.normal = v1.normal if (face.use_smooth) else face.normal
                export_vertex_array.append(exportVertex)

                exportVertex = ExportVertex()
                exportVertex.vertexIndex = k2
                exportVertex.faceIndex = faceIndex
                exportVertex.position = v2.co
                exportVertex.normal = v2.normal if (face.use_smooth) else face.normal
                export_vertex_array.append(exportVertex)

                exportVertex = ExportVertex()
                exportVertex.vertexIndex = k3
                exportVertex.faceIndex = faceIndex
                exportVertex.position = v3.co
                exportVertex.normal = v3.normal if (face.use_smooth) else face.normal
                export_vertex_array.append(exportVertex)

                material_table.append(face.material_index)

            faceIndex += 1

        colorCount = len(mesh.tessface_vertex_colors)
        if colorCount > 0:
            colorFace = mesh.tessface_vertex_colors[0].data
            vertexIndex = 0
            faceIndex = 0

            for face in mesh.tessfaces:
                cf = colorFace[faceIndex]
                export_vertex_array[vertexIndex].color = cf.color1
                vertexIndex += 1
                export_vertex_array[vertexIndex].color = cf.color2
                vertexIndex += 1
                export_vertex_array[vertexIndex].color = cf.color3
                vertexIndex += 1

                if len(face.vertices) == 4:
                    export_vertex_array[vertexIndex].color = cf.color1
                    vertexIndex += 1
                    export_vertex_array[vertexIndex].color = cf.color3
                    vertexIndex += 1
                    export_vertex_array[vertexIndex].color = cf.color4
                    vertexIndex += 1

                faceIndex += 1

        texcoordCount = len(mesh.tessface_uv_textures)
        if texcoordCount > 0:
            texcoordFace = mesh.tessface_uv_textures[0].data
            vertexIndex = 0
            faceIndex = 0

            for face in mesh.tessfaces:
                tf = texcoordFace[faceIndex]
                export_vertex_array[vertexIndex].texcoord0 = [tf.uv1[0], 1.0 - tf.uv1[1]] # Reverse TCY
                vertexIndex += 1
                export_vertex_array[vertexIndex].texcoord0 = [tf.uv2[0], 1.0 - tf.uv2[1]]
                vertexIndex += 1
                export_vertex_array[vertexIndex].texcoord0 = [tf.uv3[0], 1.0 - tf.uv3[1]]
                vertexIndex += 1

                if len(face.vertices) == 4:
                    export_vertex_array[vertexIndex].texcoord0 = [tf.uv1[0], 1.0 - tf.uv1[1]]
                    vertexIndex += 1
                    export_vertex_array[vertexIndex].texcoord0 = [tf.uv3[0], 1.0 - tf.uv3[1]]
                    vertexIndex += 1
                    export_vertex_array[vertexIndex].texcoord0 = [tf.uv4[0], 1.0 - tf.uv4[1]]
                    vertexIndex += 1

                faceIndex += 1

            if texcoordCount > 1:
                texcoordFace = mesh.tessface_uv_textures[1].data
                vertexIndex = 0
                faceIndex = 0

                for face in mesh.tessfaces:
                    tf = texcoordFace[faceIndex]
                    export_vertex_array[vertexIndex].texcoord1 = [tf.uv1[0], 1.0 - tf.uv1[1]]
                    vertexIndex += 1
                    export_vertex_array[vertexIndex].texcoord1 = [tf.uv2[0], 1.0 - tf.uv2[1]]
                    vertexIndex += 1
                    export_vertex_array[vertexIndex].texcoord1 = [tf.uv3[0], 1.0 - tf.uv3[1]]
                    vertexIndex += 1

                    if len(face.vertices) == 4:
                        export_vertex_array[vertexIndex].texcoord1 = [tf.uv1[0], 1.0 - tf.uv1[1]]
                        vertexIndex += 1
                        export_vertex_array[vertexIndex].texcoord1 = [tf.uv3[0], 1.0 - tf.uv3[1]]
                        vertexIndex += 1
                        export_vertex_array[vertexIndex].texcoord1 = [tf.uv4[0], 1.0 - tf.uv4[1]]
                        vertexIndex += 1

                    faceIndex += 1

        for ev in export_vertex_array:
            ev.Hash()

        return export_vertex_array

    @staticmethod
    def unify_vertices(export_vertex_array, indexTable):    
        # This function looks for identical vertices having exactly the same position, normal,
        # color, and texcoords. Duplicate vertices are unified, and a new index table is returned.
        bucketCount = len(export_vertex_array) >> 3
        if bucketCount > 1:
            # Round down to nearest power of two.
            while True:
                count = bucketCount & (bucketCount - 1)
                if (count == 0):
                    break
                bucketCount = count
        else:
            bucketCount = 1

        hashTable = [[] for i in range(bucketCount)]
        unifiedVertexArray = []

        for i in range(len(export_vertex_array)):
            ev = export_vertex_array[i]
            bucket = ev.hash & (bucketCount - 1)
            
            index = -1
            for b in hashTable[bucket]:
                if export_vertex_array[b] == ev:
                    index = b
                    break
            
            if index < 0:
                indexTable.append(len(unifiedVertexArray))
                unifiedVertexArray.append(ev)
                hashTable[bucket].append(i)
            else:
                indexTable.append(indexTable[index])

        return unifiedVertexArray

    def export_bone(self, armature, bone, scene, o, action):
        bobjectRef = self.bobjectArray.get(bone)
        
        if bobjectRef:
            o['type'] = structIdentifier[bobjectRef["objectType"]]
            o['name'] = bobjectRef["structName"]
            self.export_bone_transform(armature, bone, scene, o, action)

        o['children'] = []
        for subbobject in bone.children:
            so = {}
            self.export_bone(armature, subbobject, scene, so, action)
            o['children'].append(so)

        # Export any ordinary objects that are parented to this bone
        boneSubbobjectArray = self.boneParentArray.get(bone.name)
        if boneSubbobjectArray:
            poseBone = None
            if not bone.use_relative_parent:
                poseBone = armature.pose.bones.get(bone.name)
            for subbobject in boneSubbobjectArray:
                self.export_object(subbobject, scene, poseBone, o)
        
    def export_object_sampled_animation(self, bobject, scene, o):
        # This function exports animation as full 4x4 matrices for each frame
        currentFrame = scene.frame_current
        currentSubframe = scene.frame_subframe

        animationFlag = False
        m1 = bobject.matrix_local.copy()

        # Font in
        for i in range(self.beginFrame, self.endFrame):
            scene.frame_set(i)
            m2 = bobject.matrix_local
            if ArmoryExporter.matrices_different(m1, m2):
                animationFlag = True
                break
        # Font out
        if animationFlag:
            o['animation'] = {}

            tracko = {}
            tracko['target'] = "transform"

            tracko['time'] = {}
            tracko['time']['values'] = []

            for i in range(self.beginFrame, self.endFrame):
                tracko['time']['values'].append(((i - self.beginFrame) * self.frameTime))

            tracko['time']['values'].append((self.endFrame * self.frameTime))

            tracko['value'] = {}
            tracko['value']['values'] = []

            for i in range(self.beginFrame, self.endFrame):
                scene.frame_set(i)
                tracko['value']['values'].append(self.write_matrix(bobject.matrix_local))

            scene.frame_set(self.endFrame)
            tracko['value']['values'].append(self.write_matrix(bobject.matrix_local))
            o['animation']['tracks'] = [tracko]

        scene.frame_set(currentFrame, currentSubframe)

    def get_action_framerange(self, action):
        begin_frame = int(action.frame_range[0]) # Action frames
        end_frame = int(action.frame_range[1])
        if self.beginFrame > begin_frame: # Cap frames to timeline bounds
            begin_frame = self.beginFrame
        if self.endFrame < end_frame:
            end_frame = self.endFrame
        return begin_frame, end_frame

    def export_bone_sampled_animation(self, poseBone, scene, o, action):
        # This function exports bone animation as full 4x4 matrices for each frame.
        currentFrame = scene.frame_current
        currentSubframe = scene.frame_subframe

        # Frame range
        begin_frame, end_frame = self.get_action_framerange(action)

        animationFlag = False
        m1 = poseBone.matrix.copy()

        for i in range(begin_frame, end_frame):
            scene.frame_set(i)
            m2 = poseBone.matrix
            if (ArmoryExporter.matrices_different(m1, m2)):
                animationFlag = True
                break

        if animationFlag:
            o['animation'] = {}
            tracko = {}
            tracko['target'] = "transform"
            tracko['time'] = {}
            tracko['time']['values'] = []

            for i in range(begin_frame, end_frame):
                tracko['time']['values'].append(((i - begin_frame) * self.frameTime))

            tracko['time']['values'].append((end_frame * self.frameTime))

            tracko['value'] = {}
            tracko['value']['values'] = []

            parent = poseBone.parent
            if parent:
                for i in range(begin_frame, end_frame):
                    scene.frame_set(i)
                    tracko['value']['values'].append(self.write_matrix(parent.matrix.inverted() * poseBone.matrix))

                scene.frame_set(end_frame)
                tracko['value']['values'].append(self.write_matrix(parent.matrix.inverted() * poseBone.matrix))
            else:
                for i in range(begin_frame, end_frame):
                    scene.frame_set(i)
                    tracko['value']['values'].append(self.write_matrix(poseBone.matrix))

                scene.frame_set(end_frame)
                tracko['value']['values'].append(self.write_matrix(poseBone.matrix))
            o['animation']['tracks'] = [tracko]

        scene.frame_set(currentFrame, currentSubframe)


    def export_key_times(self, fcurve):
        keyo = {}
        keyo['values'] = []
        keyCount = len(fcurve.keyframe_points)
        for i in range(keyCount):
            time = fcurve.keyframe_points[i].co[0] - self.beginFrame
            keyo['values'].append(time * self.frameTime)
        return keyo

    def export_key_time_control_points(self, fcurve):
        keyminuso = {}
        keyminuso['values'] = []
        keyCount = len(fcurve.keyframe_points)
        for i in range(keyCount):
            ctrl = fcurve.keyframe_points[i].handle_left[0] - self.beginFrame
            keyminuso['values'].append(ctrl * self.frameTime)
        keypluso = {}
        keypluso['values'] = []
        for i in range(keyCount):
            ctrl = fcurve.keyframe_points[i].handle_right[0] - self.beginFrame
            keypluso['values'].append(ctrl * self.frameTime)

        return keyminuso, keypluso

    def ExportKeyValues(self, fcurve):
        keyo = {}
        keyo['values'] = []
        keyCount = len(fcurve.keyframe_points)
        for i in range(keyCount):
            value = fcurve.keyframe_points[i].co[1]
            keyo['values'].append(value)

        return keyo

    def export_key_value_control_points(self, fcurve):
        keyminuso = {}
        keyminuso['values'] = []
        keyCount = len(fcurve.keyframe_points)
        for i in range(keyCount):
            ctrl = fcurve.keyframe_points[i].handle_left[1]
            keyminuso['values'].append(ctrl)

        keypluso = {}
        keypluso['values'] = []
        for i in range(keyCount):
            ctrl = fcurve.keyframe_points[i].handle_right[1]
            keypluso['values'].append(ctrl)
        return keypluso, keypluso

    def export_animation_track(self, fcurve, kind, target, newline):
        # This function exports a single animation track. The curve types for the
        # Time and Value structures are given by the kind parameter.
        tracko = {}
        tracko['target'] = target
        if (kind != AnimationTypeBezier):
            tracko['time'] = self.export_key_times(fcurve)
            tracko['value'] = self.ExportKeyValues(fcurve)
        else:
            tracko['curve'] = 'bezier'
            tracko['time'] = self.export_key_times(fcurve)
            tracko['time_control_plus'], tracko['time_control_minus'] = self.export_key_time_control_points(fcurve)

            tracko['value'] = self.ExportKeyValues(fcurve)
            tracko['value_control_plus'], tracko['value_control_minus'] = self.export_key_value_control_points(fcurve)
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
        sampledAnimation = ((ArmoryExporter.sampleAnimationFlag) or (mode == "QUATERNION") or (mode == "AXIS_ANGLE"))

        if ((not sampledAnimation) and (bobject.animation_data)):
            action = bobject.animation_data.action
            if action:
                for fcurve in action.fcurves:
                    kind = ArmoryExporter.classify_animation_curve(fcurve)
                    if kind != AnimationTypeSampled:
                        if fcurve.data_path == "location":
                            for i in range(3):
                                if ((fcurve.array_index == i) and (not locAnimCurve[i])):
                                    locAnimCurve[i] = fcurve
                                    locAnimKind[i] = kind
                                    if ArmoryExporter.animation_present(fcurve, kind):
                                        locAnimated[i] = True
                        elif fcurve.data_path == "delta_location":
                            for i in range(3):
                                if ((fcurve.array_index == i) and (not deltaPosAnimCurve[i])):
                                    deltaPosAnimCurve[i] = fcurve
                                    deltaPosAnimKind[i] = kind
                                    if ArmoryExporter.animation_present(fcurve, kind):
                                        deltaPosAnimated[i] = True
                        elif fcurve.data_path == "rotation_euler":
                            for i in range(3):
                                if ((fcurve.array_index == i) and (not rotAnimCurve[i])):
                                    rotAnimCurve[i] = fcurve
                                    rotAnimKind[i] = kind
                                    if ArmoryExporter.animation_present(fcurve, kind):
                                        rotAnimated[i] = True
                        elif fcurve.data_path == "delta_rotation_euler":
                            for i in range(3):
                                if ((fcurve.array_index == i) and (not deltaRotAnimCurve[i])):
                                    deltaRotAnimCurve[i] = fcurve
                                    deltaRotAnimKind[i] = kind
                                    if ArmoryExporter.animation_present(fcurve, kind):
                                        deltaRotAnimated[i] = True
                        elif fcurve.data_path == "scale":
                            for i in range(3):
                                if ((fcurve.array_index == i) and (not sclAnimCurve[i])):
                                    sclAnimCurve[i] = fcurve
                                    sclAnimKind[i] = kind
                                    if ArmoryExporter.animation_present(fcurve, kind):
                                        sclAnimated[i] = True
                        elif fcurve.data_path == "delta_scale":
                            for i in range(3):
                                if ((fcurve.array_index == i) and (not deltaSclAnimCurve[i])):
                                    deltaSclAnimCurve[i] = fcurve
                                    deltaSclAnimKind[i] = kind
                                    if ArmoryExporter.animation_present(fcurve, kind):
                                        deltaSclAnimated[i] = True
                        elif ((fcurve.data_path == "rotation_axis_angle") or (fcurve.data_path == "rotation_quaternion") or (fcurve.data_path == "delta_rotation_quaternion")):
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

        if ((sampledAnimation) or ((not locationAnimated) and (not rotationAnimated) and (not scaleAnimated) and (not deltaPositionAnimated) and (not deltaRotationAnimated) and (not deltaScaleAnimated))):
            # If there's no keyframe animation at all, then write the object transform as a single 4x4 matrix.
            # We might still be exporting sampled animation below.
            o['transform'] = {}

            if sampledAnimation:
                o['transform']['target'] = "transform"

            o['transform']['values'] = self.write_matrix(bobject.matrix_local)

            if sampledAnimation:
                self.export_object_sampled_animation(bobject, scene, o)
        else:
            structFlag = False

            o['transform'] = {}
            o['transform']['values'] = self.write_matrix(bobject.matrix_local)

            o['animation_transforms'] = []

            deltaTranslation = bobject.delta_location
            if deltaPositionAnimated:
                # When the delta location is animated, write the x, y, and z components separately
                # so they can be targeted by different tracks having different sets of keys.
                for i in range(3):
                    pos = deltaTranslation[i]
                    if ((deltaPosAnimated[i]) or (math.fabs(pos) > ExportEpsilon)):
                        animo = {}
                        o['animation_transforms'].append(animo)
                        animo['type'] = 'translation_' + axisName[i]
                        animo['name'] = deltaSubtranslationName[i]
                        animo['value'] = pos
                        # self.IndentWrite(B"Translation %", 0, structFlag)
                        # self.Write(deltaSubtranslationName[i])
                        # self.Write(B" (kind = \"")
                        # self.Write(axisName[i])
                        # self.Write(B"\")\n")
                        # self.IndentWrite(B"{\n")
                        # self.IndentWrite(B"float {", 1)
                        # self.WriteFloat(pos)
                        # self.Write(B"}")
                        # self.IndentWrite(B"}\n", 0, True)
                        structFlag = True

            elif ((math.fabs(deltaTranslation[0]) > ExportEpsilon) or (math.fabs(deltaTranslation[1]) > ExportEpsilon) or (math.fabs(deltaTranslation[2]) > ExportEpsilon)):
                animo = {}
                o['animation_transforms'].append(animo)
                animo['type'] = 'translation'
                animo['values'] = self.write_vector3d(deltaTranslation)
                structFlag = True

            translation = bobject.location
            if locationAnimated:
                # When the location is animated, write the x, y, and z components separately
                # so they can be targeted by different tracks having different sets of keys.
                for i in range(3):
                    pos = translation[i]
                    if ((locAnimated[i]) or (math.fabs(pos) > ExportEpsilon)):
                        animo = {}
                        o['animation_transforms'].append(animo)
                        animo['type'] = 'translation_' + axisName[i]
                        animo['name'] = subtranslationName[i]
                        animo['value'] = pos
                        structFlag = True

            elif ((math.fabs(translation[0]) > ExportEpsilon) or (math.fabs(translation[1]) > ExportEpsilon) or (math.fabs(translation[2]) > ExportEpsilon)):
                animo = {}
                o['animation_transforms'].append(animo)
                animo['type'] = 'translation'
                animo['values'] = self.write_vector3d(translation)
                structFlag = True

            if deltaRotationAnimated:
                # When the delta rotation is animated, write three separate Euler angle rotations
                # so they can be targeted by different tracks having different sets of keys.
                for i in range(3):
                    axis = ord(mode[2 - i]) - 0x58
                    angle = bobject.delta_rotation_euler[axis]
                    if ((deltaRotAnimated[axis]) or (math.fabs(angle) > ExportEpsilon)):
                        animo = {}
                        o['animation_transforms'].append(animo)
                        animo['type'] = 'rotation_' + axisName[axis]
                        animo['name'] = deltaSubrotationName[axis]
                        animo['value'] = angle
                        structFlag = True

            else:
                # When the delta rotation is not animated, write it in the representation given by
                # the object's current rotation mode. (There is no axis-angle delta rotation.)
                if mode == "QUATERNION":
                    quaternion = bobject.delta_rotation_quaternion
                    if ((math.fabs(quaternion[0] - 1.0) > ExportEpsilon) or (math.fabs(quaternion[1]) > ExportEpsilon) or (math.fabs(quaternion[2]) > ExportEpsilon) or (math.fabs(quaternion[3]) > ExportEpsilon)):
                        animo = {}
                        o['animation_transforms'].append(animo)
                        animo['type'] = 'rotation_quaternion'
                        animo['values'] = self.WriteQuaternion(quaternion)
                        structFlag = True

                else:
                    for i in range(3):
                        axis = ord(mode[2 - i]) - 0x58
                        angle = bobject.delta_rotation_euler[axis]
                        if math.fabs(angle) > ExportEpsilon:
                            animo = {}
                            o['animation_transforms'].append(animo)
                            animo['type'] = 'rotation_' + axisName[axis]
                            animo['value'] = angle
                            structFlag = True

            if rotationAnimated:
                # When the rotation is animated, write three separate Euler angle rotations
                # so they can be targeted by different tracks having different sets of keys.
                for i in range(3):
                    axis = ord(mode[2 - i]) - 0x58
                    angle = bobject.rotation_euler[axis]
                    if ((rotAnimated[axis]) or (math.fabs(angle) > ExportEpsilon)):
                        animo = {}
                        o['animation_transforms'].append(animo)
                        animo['type'] = 'rotation_' + axisName[axis]
                        animo['name'] = subrotationName[axis]
                        animo['value'] = angle
                        structFlag = True

            else:
                # When the rotation is not animated, write it in the representation given by
                # the object's current rotation mode.
                if (mode == "QUATERNION"):
                    quaternion = bobject.rotation_quaternion
                    if ((math.fabs(quaternion[0] - 1.0) > ExportEpsilon) or (math.fabs(quaternion[1]) > ExportEpsilon) or (math.fabs(quaternion[2]) > ExportEpsilon) or (math.fabs(quaternion[3]) > ExportEpsilon)):
                        animo = {}
                        o['animation_transforms'].append(animo)
                        animo['type'] = 'rotation_quaternion'
                        animo['values'] = self.WriteQuaternion(quaternion)
                        structFlag = True

                elif (mode == "AXIS_ANGLE"):
                    if (math.fabs(bobject.rotation_axis_angle[0]) > ExportEpsilon):
                        animo = {}
                        o['animation_transforms'].append(animo)
                        animo['type'] = 'rotation_axis'
                        animo['values'] = self.WriteVector4D(bobject.rotation_axis_angle)
                        structFlag = True

                else:
                    for i in range(3):
                        axis = ord(mode[2 - i]) - 0x58
                        angle = bobject.rotation_euler[axis]
                        if (math.fabs(angle) > ExportEpsilon):
                            animo = {}
                            o['animation_transforms'].append(animo)
                            animo['type'] = 'rotation_' + axisName[axis]
                            animo['value'] = angle
                            structFlag = True

            deltaScale = bobject.delta_scale
            if (deltaScaleAnimated):
                # When the delta scale is animated, write the x, y, and z components separately
                # so they can be targeted by different tracks having different sets of keys.
                for i in range(3):
                    scl = deltaScale[i]
                    if ((deltaSclAnimated[i]) or (math.fabs(scl) > ExportEpsilon)):
                        animo = {}
                        o['animation_transforms'].append(animo)
                        animo['type'] = 'scale_' + axisName[i]
                        animo['name'] = deltaSubscaleName[i]
                        animo['value'] = scl
                        structFlag = True

            elif ((math.fabs(deltaScale[0] - 1.0) > ExportEpsilon) or (math.fabs(deltaScale[1] - 1.0) > ExportEpsilon) or (math.fabs(deltaScale[2] - 1.0) > ExportEpsilon)):
                animo = {}
                o['animation_transforms'].append(animo)
                animo['type'] = 'scale'
                animo['values'] = self.write_vector3d(deltaScale)
                structFlag = True

            scale = bobject.scale
            if (scaleAnimated):
                # When the scale is animated, write the x, y, and z components separately
                # so they can be targeted by different tracks having different sets of keys.
                for i in range(3):
                    scl = scale[i]
                    if ((sclAnimated[i]) or (math.fabs(scl) > ExportEpsilon)):
                        animo = {}
                        o['animation_transforms'].append(animo)
                        animo['type'] = 'scale_' + axisName[i]
                        animo['name'] = subscaleName[i]
                        animo['value'] = scl
                        structFlag = True

            elif ((math.fabs(scale[0] - 1.0) > ExportEpsilon) or (math.fabs(scale[1] - 1.0) > ExportEpsilon) or (math.fabs(scale[2] - 1.0) > ExportEpsilon)):
                animo = {}
                o['animation_transforms'].append(animo)
                animo['type'] = 'scale'
                animo['values'] = self.write_vector3d(scale)
                structFlag = True

            # Export the animation tracks.      
            o['animation'] = {}
            o['animation']['begin'] = (action.frame_range[0] - self.beginFrame) * self.frameTime
            o['animation']['end'] = (action.frame_range[1] - self.beginFrame) * self.frameTime
            o['animation']['tracks'] = []

            if locationAnimated:
                for i in range(3):
                    if (locAnimated[i]):
                        tracko = self.export_animation_track(locAnimCurve[i], locAnimKind[i], subtranslationName[i], structFlag)
                        o['animation']['tracks'].append(tracko)
                        structFlag = True

            if rotationAnimated:
                for i in range(3):
                    if (rotAnimated[i]):
                        tracko = self.export_animation_track(rotAnimCurve[i], rotAnimKind[i], subrotationName[i], structFlag)
                        o['animation']['tracks'].append(tracko)
                        structFlag = True

            if scaleAnimated:
                for i in range(3):
                    if (sclAnimated[i]):
                        tracko = self.export_animation_track(sclAnimCurve[i], sclAnimKind[i], subscaleName[i], structFlag)
                        o['animation']['tracks'].append(tracko)
                        structFlag = True

            if deltaPositionAnimated:
                for i in range(3):
                    if (deltaPosAnimated[i]):
                        tracko = self.export_animation_track(deltaPosAnimCurve[i], deltaPosAnimKind[i], deltaSubtranslationName[i], structFlag)
                        o['animation']['tracks'].append(tracko)
                        structFlag = True

            if deltaRotationAnimated:
                for i in range(3):
                    if (deltaRotAnimated[i]):
                        tracko = self.export_animation_track(deltaRotAnimCurve[i], deltaRotAnimKind[i], deltaSubrotationName[i], structFlag)
                        o['animation']['tracks'].append(tracko)
                        structFlag = True

            if deltaScaleAnimated:
                for i in range(3):
                    if (deltaSclAnimated[i]):
                        tracko = self.export_animation_track(deltaSclAnimCurve[i], deltaSclAnimKind[i], deltaSubscaleName[i], structFlag)
                        o['animation']['tracks'].append(tracko)
                        structFlag = True
            
    def process_bone(self, bone):
        if ((ArmoryExporter.exportAllFlag) or (bone.select)):
            self.bobjectArray[bone] = {"objectType" : NodeTypeBone, "structName" : bone.name}

        for subbobject in bone.children:
            self.process_bone(subbobject)

    def process_bobject(self, bobject):
        if ArmoryExporter.exportAllFlag or bobject.select:
            btype = ArmoryExporter.get_bobject_type(bobject)

            if ArmoryExporter.option_mesh_only and btype != NodeTypeMesh:
                return

            self.bobjectArray[bobject] = {"objectType" : btype, "structName" : self.asset_name(bobject)}

            if bobject.parent_type == "BONE":
                boneSubbobjectArray = self.boneParentArray.get(bobject.parent_bone)
                if boneSubbobjectArray:
                    boneSubbobjectArray.append(bobject)
                else:
                    self.boneParentArray[bobject.parent_bone] = [bobject]

            if bobject.type == "ARMATURE":
                skeleton = bobject.data
                if (skeleton):
                    for bone in skeleton.bones:
                        if (not bone.parent):
                            self.process_bone(bone)

        if bobject.type != 'MESH' or bobject.instanced_children == False:
            for subbobject in bobject.children:
                self.process_bobject(subbobject)

    def process_skinned_meshes(self):
        for bobjectRef in self.bobjectArray.items():
            if bobjectRef[1]["objectType"] == NodeTypeMesh:
                armature = bobjectRef[0].find_armature()
                if armature:
                    for bone in armature.data.bones:
                        boneRef = self.find_node(bone.name)
                        if boneRef:
                            # If an object is used as a bone, then we force its type to be a bone
                            boneRef[1]["objectType"] = NodeTypeBone

    def export_bone_transform(self, armature, bone, scene, o, action):
        curveArray = self.collect_bone_animation(armature, bone.name)
        animation = ((len(curveArray) != 0) or (ArmoryExporter.sampleAnimationFlag))

        transform = bone.matrix_local.copy()
        parentBone = bone.parent
        if parentBone:
            transform = parentBone.matrix_local.inverted() * transform

        poseBone = armature.pose.bones.get(bone.name)
        if poseBone:
            transform = poseBone.matrix.copy()
            parentPoseBone = poseBone.parent
            if parentPoseBone:
                transform = parentPoseBone.matrix.inverted() * transform

        o['transform'] = {}
        o['transform']['values'] = self.write_matrix(transform)

        if animation and poseBone:
            self.export_bone_sampled_animation(poseBone, scene, o, action)

    def asset_name(self, bdata):
        s = bdata.name
        # Append library name if linked
        if bdata.library != None:
            s += '_' + bdata.library.name
        return s

    def use_default_material(self, bobject, o):
        if bobject.find_armature() and armutils.is_bone_animation_enabled(bobject):
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
            self.materialArray[material] = {"structName" : self.asset_name(material)}
        o['material_refs'].append(self.materialArray[material]["structName"])

    def export_particle_system_ref(self, psys, index, o):
        if not psys.settings in self.particleSystemArray:
            self.particleSystemArray[psys.settings] = {"structName" : psys.settings.name}

        pref = {}
        pref['name'] = psys.name
        pref['seed'] = psys.seed
        pref['particle'] = self.particleSystemArray[psys.settings]["structName"]
        o['particle_refs'].append(pref)

    def get_viewport_view_matrix(self):
        screen = bpy.context.window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        return space.region_3d.view_matrix
        return None

    def get_viewport_projection_matrix(self):
        screen = bpy.context.window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        return space.region_3d.perspective_matrix
        return None

    def make_fake_omni_lamps(self, o, bobject):
        # Look down
        o['transform']['values'] = [1.0, 0.0, 0.0, bobject.location.x, 0.0, 1.0, 0.0, bobject.location.y, 0.0, 0.0, 1.0, bobject.location.z, 0.0, 0.0, 0.0, 1.0]
        if not hasattr(o, 'children'):
            o['children'] = []
        # Make child lamps
        for i in range(0, 5):
            child_lamp = {}
            child_lamp['name'] = o['name'] + '__' + str(i)
            child_lamp['data_ref'] = o['data_ref']
            child_lamp['type'] = 'lamp_object'
            if i == 0:
                mat = [0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]
            elif i == 1:
                mat = [0.0, 0.0, -1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]
            elif i == 2:
                mat = [0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]
            elif i == 3:
                mat = [0.0, -1.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]
            elif i == 4:
                mat = [-1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0]
            child_lamp['transform'] = {}
            child_lamp['transform']['values'] = mat
            o['children'].append(child_lamp)

    def export_object(self, bobject, scene, poseBone = None, parento = None):
        # This function exports a single object in the scene and includes its name,
        # object reference, material references (for meshes), and transform.
        # Subobjects are then exported recursively.
        if self.preprocess_object(bobject) == False:
            return

        bobjectRef = self.bobjectArray.get(bobject)
        if bobjectRef:
            type = bobjectRef["objectType"]

            o = {}
            o['type'] = structIdentifier[type]
            o['name'] = bobjectRef["structName"]

            if bobject.hide_render or not bobject.game_visible:
                o['visible'] = False

            if not bobject.cycles_visibility.camera:
                o['visible_mesh'] = False

            if not bobject.cycles_visibility.shadow:
                o['visible_shadow'] = False

            if bobject.spawn == False:
                o['spawn'] = False

            if bobject.mobile == False:
                o['mobile'] = False

            if bobject.dupli_type == 'GROUP' and bobject.dupli_group != None:
                o['group_ref'] = bobject.dupli_group.name

            if ArmoryExporter.option_spawn_all_layers == False:
                layer_found = False
                for l in self.active_layers:
                    if bobject.layers[l] == True:
                        layer_found = True
                        break
                if layer_found == False:
                    o['spawn'] = False

            # Export the object reference and material references
            objref = bobject.data

            # Lods
            if bobject.type == 'MESH' and hasattr(objref, 'my_lodlist') and len(objref.my_lodlist) > 0:
                o['lods'] = []
                for l in objref.my_lodlist:
                    if l.enabled_prop == False:
                        continue
                    lod = {}
                    lod['object_ref'] = l.name
                    lod['screen_size'] = l.screen_size_prop
                    o['lods'].append(lod)
                if objref.lod_material:
                    o['lod_material'] = True
            
            # Remove unsafe chars from data names
            if objref != None:
                safe = armutils.safefilename(objref.name)
                if objref.name != safe:
                    objref.name = safe

                objname = self.asset_name(objref)

            if type == NodeTypeMesh:
                if not objref in self.meshArray:
                    self.meshArray[objref] = {"structName" : objname, "objectTable" : [bobject]}
                else:
                    self.meshArray[objref]["objectTable"].append(bobject)

                oid = armutils.safe_filename(self.meshArray[objref]["structName"])
                if ArmoryExporter.option_mesh_per_file:
                    ext = ''
                    if self.is_compress(objref):
                        ext = '.zip'
                    o['data_ref'] = 'mesh_' + oid + ext + '/' + oid
                else:
                    o['data_ref'] = oid
                
                o['material_refs'] = []
                for i in range(len(bobject.material_slots)):
                    if bobject.override_material: # Overwrite material slot
                        o['material_refs'].append(bobject.override_material_name)
                    else: # Export assigned material
                        self.export_material_ref(bobject, bobject.material_slots[i].material, i, o)
                # No material, mimic cycles and assign default
                if len(o['material_refs']) == 0:
                    self.use_default_material(bobject, o)

                num_psys = len(bobject.particle_systems)
                if num_psys > 0:
                    o['particle_refs'] = []
                    for i in range(0, num_psys):
                        self.export_particle_system_ref(bobject.particle_systems[i], i, o)
                    
                o['dimensions'] = [bobject.dimensions[0], bobject.dimensions[1], bobject.dimensions[2]] 
                # Origin not in geometry center
                if hasattr(bobject.data, 'mesh_aabb'):
                    dx = bobject.data.mesh_aabb[0] * bobject.scale[0]
                    dy = bobject.data.mesh_aabb[1] * bobject.scale[1]
                    dz = bobject.data.mesh_aabb[2] * bobject.scale[2]
                    if dx > o['dimensions'][0]:
                        o['dimensions'][0] = dx
                    if dy > o['dimensions'][1]:
                        o['dimensions'][1] = dy
                    if dz > o['dimensions'][2]:
                        o['dimensions'][2] = dz

                #shapeKeys = ArmoryExporter.get_shape_keys(objref)
                #if (shapeKeys):
                #   self.ExportMorphWeights(bobject, shapeKeys, scene, o)
                # TODO

            elif type == NodeTypeLamp:
                if not objref in self.lampArray:
                    self.lampArray[objref] = {"structName" : objname, "objectTable" : [bobject]}
                else:
                    self.lampArray[objref]["objectTable"].append(bobject)
                o['data_ref'] = self.lampArray[objref]["structName"]

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

            if poseBone:
                # If the object is parented to a bone and is not relative, then undo the bone's transform
                o['transform'] = {}
                o['transform']['values'] = self.write_matrix(poseBone.matrix.inverted())

            # Export the transform. If object is animated, then animation tracks are exported here
            self.export_object_transform(bobject, scene, o)

            # 6 directional lamps
            if type == NodeTypeLamp and objref.type == 'POINT' and objref.lamp_omni_shadows:
                self.make_fake_omni_lamps(o, bobject)

            # Viewport Camera - overwrite active camera matrix with viewport matrix
            if type == NodeTypeCamera and bpy.data.worlds['Arm'].arm_play_viewport_camera and self.scene.camera != None and bobject.name == self.scene.camera.name:
                viewport_matrix = self.get_viewport_view_matrix()
                if viewport_matrix != None:
                    o['transform']['values'] = self.write_matrix(viewport_matrix.inverted())
                    # Do not apply parent matrix
                    o['local_transform_only'] = True

            if bobject.type == "ARMATURE":
                bdata = bobject.data # Armature data
                action = None # Reference start action
                if bobject.edit_actions_prop:
                    action = bpy.data.actions[bobject.start_action_name_prop]
                elif bobject.animation_data != None: # Use default
                    action = bobject.animation_data.action
                    
                if bdata and action != None:
                    armatureid = self.asset_name(bdata)
                    armatureid = armutils.safe_filename(armatureid)
                    ext = ''
                    if self.is_compress(bdata):
                       ext = '.zip'
                    o['bones_ref'] = 'bones_' + armatureid + '_' + action.name + ext

                    # Write bones
                    if bdata.edit_actions:
                        export_actions = []
                        for t in bdata.my_actiontraitlist:
                            export_actions.append(bpy.data.actions[t.name])
                    else: # Use default
                        export_actions = [action]

                    orig_action = bobject.animation_data.action
                    for action in export_actions:
                        # if bdata.animation_data == None:
                            # continue # bdata.animation_data_create()
                        # bdata.animation_data.action = action
                        bobject.animation_data.action = action
                        fp = self.get_meshes_file_path('bones_' + armatureid + '_' + action.name, compressed=self.is_compress(bdata))
                        assets.add(fp)
                        if bdata.data_cached == False or not os.path.exists(fp):
                            bones = []
                            for bone in bdata.bones:
                                if not bone.parent:
                                    boneo = {}
                                    self.export_bone(bobject, bone, scene, boneo, action)
                                    #o.objects.append(boneo)
                                    bones.append(boneo)
                            # Save bones separately
                            bones_obj = {}
                            bones_obj['objects'] = bones
                            armutils.write_arm(fp, bones_obj)
                    bobject.animation_data.action = orig_action
                    bdata.data_cached = True

            if parento == None:
                self.output['objects'].append(o)
            else:
                parento['children'].append(o)

            self.post_export_object(bobject, o, type)

            if not hasattr(o, 'children') and len(bobject.children) > 0:
                o['children'] = []

        if bobject.type != 'MESH' or bobject.instanced_children == False:
            for subbobject in bobject.children:
                if subbobject.parent_type != "BONE":
                    self.export_object(subbobject, scene, None, o)

    def export_skin_quality(self, bobject, armature, export_vertex_array, om):
        # This function exports all skinning data, which includes the skeleton
        # and per-vertex bone influence data
        oskin = {}
        om['skin'] = oskin

        # Write the skin bind pose transform
        otrans = {}
        oskin['transform'] = otrans
        otrans['values'] = self.write_matrix(bobject.matrix_world)

        # Export the skeleton, which includes an array of bone object references
        # and and array of per-bone bind pose transforms
        oskel = {}
        oskin['skeleton'] = oskel

        # Write the bone object reference array
        oskel['bone_ref_array'] = []

        boneArray = armature.data.bones
        boneCount = len(boneArray)

        for i in range(boneCount):
            boneRef = self.find_node(boneArray[i].name)
            if (boneRef):
                oskel['bone_ref_array'].append(boneRef[1]["structName"])
            else:
                oskel['bone_ref_array'].append("null")

        # Write the bind pose transform array
        oskel['transforms'] = []
        for i in range(boneCount):
            oskel['transforms'].append(self.write_matrix(armature.matrix_world * boneArray[i].matrix_local))

        # Export the per-vertex bone influence data
        groupRemap = []

        for group in bobject.vertex_groups:
            groupName = group.name
            for i in range(boneCount):
                if boneArray[i].name == groupName:
                    groupRemap.append(i)
                    break
            else:
                groupRemap.append(-1)

        boneCountArray = []
        boneIndexArray = []
        boneWeightArray = []

        mesh_vertex_array = bobject.data.vertices
        for ev in export_vertex_array:
            boneCount = 0
            totalWeight = 0.0
            for element in mesh_vertex_array[ev.vertexIndex].groups:
                boneIndex = groupRemap[element.group]
                boneWeight = element.weight
                if boneIndex >= 0 and boneWeight != 0.0:
                    boneCount += 1
                    totalWeight += boneWeight
                    boneIndexArray.append(boneIndex)
                    boneWeightArray.append(boneWeight)
                    if boneCount == 4: # Four bones max - TODO: take biggest weights
                        break
            boneCountArray.append(boneCount)

            if totalWeight != 0.0:
                normalizer = 1.0 / totalWeight
                for i in range(-boneCount, 0):
                    boneWeightArray[i] *= normalizer

        # Write the bone count array. There is one entry per vertex.
        oskin['bone_count_array'] = boneCountArray

        # Write the bone index array. The number of entries is the sum of the bone counts for all vertices.
        oskin['bone_index_array'] = boneIndexArray

        # Write the bone weight array. The number of entries is the sum of the bone counts for all vertices.
        oskin['bone_weight_array'] = boneWeightArray

    # def export_skin_fast(self, bobject, armature, vert_list, om):
    #     oskin = {}
    #     om['skin'] = oskin

    #     otrans = {}
    #     oskin['transform'] = otrans
    #     otrans['values'] = self.write_matrix(bobject.matrix_world)

    #     oskel = {}
    #     oskin['skeleton'] = oskel
    #     oskel['bone_ref_array'] = []

    #     boneArray = armature.data.bones
    #     boneCount = len(boneArray)
    #     for i in range(boneCount):
    #         boneRef = self.find_node(boneArray[i].name)
    #         if (boneRef):
    #             oskel['bone_ref_array'].append(boneRef[1]["structName"])
    #         else:
    #             oskel['bone_ref_array'].append("null")

    #     oskel['transforms'] = []
    #     for i in range(boneCount):
    #         oskel['transforms'].append(self.write_matrix(armature.matrix_world * boneArray[i].matrix_local))

    #     boneCountArray = []
    #     boneIndexArray = []
    #     boneWeightArray = []
    #     for vtx in vert_list:
    #         boneCountArray.append(vtx.bone_count)
    #         boneIndexArray += vtx.bone_indices
    #         boneWeightArray += vtx.bone_weights
    #     oskin['bone_count_array'] = boneCountArray
    #     oskin['bone_index_array'] = boneIndexArray
    #     oskin['bone_weight_array'] = boneWeightArray

    def calc_tangents(self, posa, nora, uva, ia):
        triangle_count = int(len(ia) / 3)
        vertex_count = int(len(posa) / 3)
        tangents = [0] * vertex_count * 3
        # bitangents = [0] * vertex_count * 3
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
            armutils.write_arm(fp, mesh_obj)

            bobject.data.mesh_cached = True
            if bobject.type != 'FONT' and bobject.type != 'META':
                bobject.data.mesh_cached_verts = len(bobject.data.vertices)
                bobject.data.mesh_cached_edges = len(bobject.data.edges)
        else:
            self.output['mesh_datas'].append(o)

    def export_mesh_fast(self, exportMesh, bobject, fp, o, om):
        # Much faster export but produces slightly less efficient data
        exportMesh.calc_normals_split()
        exportMesh.calc_tessface()
        vert_list = { Vertex(exportMesh, loop) : 0 for loop in exportMesh.loops}.keys()
        num_verts = len(vert_list)
        num_uv_layers = len(exportMesh.uv_layers)
        num_colors = len(exportMesh.vertex_colors)
        vdata = [0] * num_verts * 3
        ndata = [0] * num_verts * 3
        if num_uv_layers > 0:
            t0data = [0] * num_verts * 2
            if num_uv_layers > 1:
                t1data = [0] * num_verts * 2
        if num_colors > 0:
            cdata = [0] * num_verts * 3
        # Make arrays
        for i, vtx in enumerate(vert_list):
            vtx.index = i

            co = vtx.co
            normal = vtx.normal
            for j in range(3):
                vdata[(i * 3) + j] = co[j]
                ndata[(i * 3) + j] = normal[j]
            if num_uv_layers > 0:
                t0data[i * 2] = vtx.uvs[0].x
                t0data[i * 2 + 1] = 1.0 - vtx.uvs[0].y # Reverse TCY
                if num_uv_layers > 1:
                    t1data[i * 2] = vtx.uvs[1].x
                    t1data[i * 2 + 1] = 1.0 - vtx.uvs[1].y
            if num_colors > 0:
                cdata[i * 3] = vtx.col[0]
                cdata[i * 3 + 1] = vtx.col[1]
                cdata[i * 3 + 2] = vtx.col[2]
        # Output
        om['vertex_arrays'] = []
        pa = {}
        pa['attrib'] = "position"
        pa['size'] = 3
        pa['values'] = vdata
        om['vertex_arrays'].append(pa)
        na = {}
        na['attrib'] = "normal"
        na['size'] = 3
        na['values'] = ndata
        om['vertex_arrays'].append(na)
        
        if self.get_export_uvs(exportMesh) == True and num_uv_layers > 0:
            ta = {}
            ta['attrib'] = "texcoord"
            ta['size'] = 2
            ta['values'] = t0data
            om['vertex_arrays'].append(ta)
            if num_uv_layers > 1:
                ta1 = {}
                ta1['attrib'] = "texcoord1"
                ta1['size'] = 2
                ta1['values'] = t1data
                om['vertex_arrays'].append(ta1)
        
        if self.get_export_vcols(exportMesh) == True and num_colors > 0:
            ca = {}
            ca['attrib'] = "color"
            ca['size'] = 3
            ca['values'] = cdata
            om['vertex_arrays'].append(ca)
        
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
                mat = exportMesh.materials[poly.material_index]
                prim = prims[mat.name if mat else '']
            indices = [vert_dict[i].index for i in range(first, first+poly.loop_total)]

            if poly.loop_total == 3:
                prim += indices
            elif poly.loop_total > 3:
                for i in range(poly.loop_total-2):
                    prim += (indices[-1], indices[i], indices[i + 1])
        
        # Write indices
        om['index_arrays'] = []
        for mat, prim in prims.items():
            idata = [0] * len(prim)
            for i, v in enumerate(prim):
                idata[i] = v
            ia = {}
            ia['size'] = 3
            ia['values'] = idata
            ia['material'] = 0
            # Find material index for multi-mat mesh
            if len(exportMesh.materials) > 1:
                for i in range(0, len(exportMesh.materials)):
                    if (exportMesh.materials[i] != None and mat == exportMesh.materials[i].name) or \
                       (exportMesh.materials[i] == None and mat == ''): # Default material for empty slots
                        ia['material'] = i
                        break
            om['index_arrays'].append(ia)
        
        # Make tangents
        if self.get_export_uvs(exportMesh) == True and self.get_export_tangents(exportMesh) == True and num_uv_layers > 0:
            tanga = {}
            tanga['attrib'] = "tangent"
            tanga['size'] = 3
            tanga['values'] = self.calc_tangents(pa['values'], na['values'], ta['values'], om['index_arrays'][0]['values'])  
            om['vertex_arrays'].append(tanga)

        return vert_list

    def do_export_mesh(self, objectRef, scene):
        # This function exports a single mesh object
        bobject = objectRef[1]["objectTable"][0]
        oid = armutils.safe_filename(objectRef[1]["structName"])

        # Check if mesh is using instanced rendering
        is_instanced, instance_offsets = self.object_process_instancing(bobject, objectRef[1]["objectTable"])

        # No export necessary
        if ArmoryExporter.option_mesh_per_file:
            fp = self.get_meshes_file_path('mesh_' + oid, compressed=self.is_compress(bobject.data))
            assets.add(fp)
            if self.object_is_mesh_cached(bobject) == True and os.path.exists(fp):
                return

        print('Exporting mesh ' + self.asset_name(bobject.data))

        o = {}
        o['name'] = oid
        mesh = objectRef[0]
        structFlag = False;

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

                    # if ((relative) and (morphCount != baseIndex)):
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

        om = {}
        # Triangles is default
        # om['primitive'] = "triangles"

        armature = bobject.find_armature()
        applyModifiers = not armature

        # Apply all modifiers to create a new mesh with tessfaces.

        # We don't apply modifiers for a skinned mesh because we need the vertex positions
        # before they are deformed by the armature modifier in order to export the proper
        # bind pose. This does mean that modifiers preceding the armature modifier are ignored,
        # but the Blender API does not provide a reasonable way to retrieve the mesh at an
        # arbitrary stage in the modifier stack.
        exportMesh = bobject.to_mesh(scene, applyModifiers, "RENDER", True, False)

        if exportMesh == None:
            print('Armory Warning: ' + oid + ' was not exported')
            return

        if len(exportMesh.uv_layers) > 2:
            print('Armory Warning: ' + oid + ' exceeds maximum of 2 UV Maps supported')

        # Process meshes
        if ArmoryExporter.option_optimize_mesh:
            unifiedVertexArray = self.export_mesh_quality(exportMesh, bobject, fp, o, om)
            if armature:
                self.export_skin_quality(bobject, armature, unifiedVertexArray, om)
        else:
            vert_list = self.export_mesh_fast(exportMesh, bobject, fp, o, om)
            if armature:
                self.export_skin_quality(bobject, armature, vert_list, om)
                # self.export_skin_fast(bobject, armature, vert_list, om)

        # Save aabb
        for va in om['vertex_arrays']:
            if va['attrib'] == 'position':
                positions = va['values']
                aabb_min = [-0.01, -0.01, -0.01]
                aabb_max = [0.01, 0.01, 0.01]
                i = 0
                while i < len(positions):
                    if positions[i] > aabb_max[0]:
                        aabb_max[0] = positions[i];
                    if positions[i + 1] > aabb_max[1]:
                        aabb_max[1] = positions[i + 1];
                    if positions[i + 2] > aabb_max[2]:
                        aabb_max[2] = positions[i + 2];
                    if positions[i] < aabb_min[0]:
                        aabb_min[0] = positions[i];
                    if positions[i + 1] < aabb_min[1]:
                        aabb_min[1] = positions[i + 1];
                    if positions[i + 2] < aabb_min[2]:
                        aabb_min[2] = positions[i + 2];
                    i += 3;
                if hasattr(bobject.data, 'mesh_aabb'):
                    bobject.data.mesh_aabb = [abs(aabb_min[0]) + abs(aabb_max[0]), abs(aabb_min[1]) + abs(aabb_max[1]), abs(aabb_min[2]) + abs(aabb_max[2])]
                break

        # Restore the morph state
        if shapeKeys:
            bobject.active_shape_key_index = activeShapeKeyIndex
            bobject.show_only_shape_key = showOnlyShapeKey

            for m in range(len(currentMorphValue)):
                shapeKeys.key_blocks[m].value = currentMorphValue[m]

            mesh.update()

        # Save offset data for instanced rendering
        if is_instanced == True:
            om['instance_offsets'] = instance_offsets

        # Export usage
        if bobject.data.dynamic_usage:
            om['dynamic_usage'] = bobject.data.dynamic_usage

        o['mesh'] = om
        self.write_mesh(bobject, fp, o)

    def export_mesh_quality(self, exportMesh, bobject, fp, o, om):
        # Triangulate mesh and remap vertices to eliminate duplicates
        material_table = []
        export_vertex_array = ArmoryExporter.deindex_mesh(exportMesh, material_table)
        triangleCount = len(material_table)

        indexTable = []
        unifiedVertexArray = ArmoryExporter.unify_vertices(export_vertex_array, indexTable)

        # Write the position array
        om['vertex_arrays'] = []
        pa = {}
        pa['attrib'] = "position"
        pa['size'] = 3
        pa['values'] = self.write_vertex_array3d(unifiedVertexArray, "position")
        om['vertex_arrays'].append(pa)
        
        # Write the normal array
        na = {}
        na['attrib'] = "normal"
        na['size'] = 3
        na['values'] = self.write_vertex_array3d(unifiedVertexArray, "normal")
        om['vertex_arrays'].append(na)

        # Write the color array if it exists
        colorCount = len(exportMesh.tessface_vertex_colors)
        if self.get_export_vcols(exportMesh) == True and colorCount > 0:
            ca = {}
            ca['attrib'] = "color"
            ca['size'] = 3
            ca['values'] = self.write_vertex_array3d(unifiedVertexArray, "color")
            om['vertex_arrays'].append(ca)

        # Write the texcoord arrays
        texcoordCount = len(exportMesh.tessface_uv_textures)
        if self.get_export_uvs(exportMesh) == True and texcoordCount > 0:
            ta = {}
            ta['attrib'] = "texcoord"
            ta['size'] = 2
            ta['values'] = self.write_vertex_array2d(unifiedVertexArray, "texcoord0")
            om['vertex_arrays'].append(ta)

            if (texcoordCount > 1):
                ta2 = {}
                ta2['attrib'] = "texcoord1"
                ta2['size'] = 2
                ta2['values'] = self.write_vertex_array2d(unifiedVertexArray, "texcoord1")
                om['vertex_arrays'].append(ta2)

        # If there are multiple morph targets, export them here
        # if (shapeKeys):
        #   shapeKeys.key_blocks[0].value = 0.0
        #   for m in range(1, len(currentMorphValue)):
        #       shapeKeys.key_blocks[m].value = 1.0
        #       mesh.update()

        #       bobject.active_shape_key_index = m
        #       morphMesh = bobject.to_mesh(scene, applyModifiers, "RENDER", True, False)

        #       # Write the morph target position array.

        #       self.IndentWrite(B"VertexArray (attrib = \"position\", morph = ", 0, True)
        #       self.WriteInt(m)
        #       self.Write(B")\n")
        #       self.IndentWrite(B"{\n")
        #       self.indentLevel += 1

        #       self.IndentWrite(B"float[3]\t\t// ")
        #       self.IndentWrite(B"{\n", 0, True)
        #       self.WriteMorphPositionArray3D(unifiedVertexArray, morphMesh.vertices)
        #       self.IndentWrite(B"}\n")

        #       self.indentLevel -= 1
        #       self.IndentWrite(B"}\n\n")

        #       # Write the morph target normal array.

        #       self.IndentWrite(B"VertexArray (attrib = \"normal\", morph = ")
        #       self.WriteInt(m)
        #       self.Write(B")\n")
        #       self.IndentWrite(B"{\n")
        #       self.indentLevel += 1

        #       self.IndentWrite(B"float[3]\t\t// ")
        #       self.IndentWrite(B"{\n", 0, True)
        #       self.WriteMorphNormalArray3D(unifiedVertexArray, morphMesh.vertices, morphMesh.tessfaces)
        #       self.IndentWrite(B"}\n")

        #       self.indentLevel -= 1
        #       self.IndentWrite(B"}\n")

        #       bpy.data.meshes.remove(morphMesh)

        # Write the index arrays
        om['index_arrays'] = []

        maxMaterialIndex = 0
        for i in range(len(material_table)):
            index = material_table[i]
            if index > maxMaterialIndex:
                maxMaterialIndex = index

        if maxMaterialIndex == 0:
            # There is only one material, so write a single index array.
            ia = {}
            ia['size'] = 3
            ia['values'] = self.write_triangle_array(triangleCount, indexTable)
            ia['material'] = 0
            om['index_arrays'].append(ia)
        else:
            # If there are multiple material indexes, then write a separate index array for each one.
            materialTriangleCount = [0 for i in range(maxMaterialIndex + 1)]
            for i in range(len(material_table)):
                materialTriangleCount[material_table[i]] += 1

            for m in range(maxMaterialIndex + 1):
                if (materialTriangleCount[m] != 0):
                    materialIndexTable = []
                    for i in range(len(material_table)):
                        if (material_table[i] == m):
                            k = i * 3
                            materialIndexTable.append(indexTable[k])
                            materialIndexTable.append(indexTable[k + 1])
                            materialIndexTable.append(indexTable[k + 2])

                    ia = {}
                    ia['size'] = 3
                    ia['values'] = self.write_triangle_array(materialTriangleCount[m], materialIndexTable)
                    ia['material'] = m
                    om['index_arrays'].append(ia)   

        # Export tangents
        if self.get_export_tangents(exportMesh) == True and len(exportMesh.uv_textures) > 0:
            tanga = {}
            tanga['attrib'] = "tangent"
            tanga['size'] = 3
            tanga['values'] = self.calc_tangents(pa['values'], na['values'], ta['values'], om['index_arrays'][0]['values'])  
            om['vertex_arrays'].append(tanga)

        # Delete the new mesh that we made earlier
        bpy.data.meshes.remove(exportMesh)
        return unifiedVertexArray

    def export_lamp(self, objectRef):
        # This function exports a single lamp object
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
        o['near_plane'] = objref.lamp_clip_start
        o['far_plane'] = objref.lamp_clip_end
        o['fov'] = objref.lamp_fov
        o['shadows_bias'] = objref.lamp_shadows_bias
        if bpy.data.cameras[0].rp_shadowmap == 'None':
            o['shadowmap_size'] = 0
        else:
            o['shadowmap_size'] = int(bpy.data.cameras[0].rp_shadowmap)
        if o['type'] == 'sun': # Scale bias for ortho light matrix
            o['shadows_bias'] *= 10.0
        if (objtype == 'POINT' or objtype == 'SPOT') and objref.shadow_soft_size > 0.1: # No sun for now
            lamp_size = objref.shadow_soft_size
            # Slightly higher bias for high sizes
            if lamp_size > 1:
                o['shadows_bias'] += 0.00001 * lamp_size
            o['lamp_size'] = lamp_size * 10 # Match to Cycles

        # Parse nodes
        # Emission only for now
        tree = objref.node_tree
        for n in tree.nodes:
            if n.type == 'EMISSION':
                col = n.inputs[0].default_value
                o['color'] = [col[0], col[1], col[2]]
                o['strength'] = n.inputs[1].default_value
                # Normalize lamp strength
                if o['type'] == 'point' or o['type'] == 'spot':
                    o['strength'] *= 0.025
                elif o['type'] == 'area':
                    o['strength'] *= 0.025
                elif o['type'] == 'sun':
                    o['strength'] *= 0.4
                # TODO: Lamp texture test..
                if n.inputs[0].is_linked:
                    color_node = n.inputs[0].links[0].from_node
                    if color_node.type == 'TEX_IMAGE':
                        o['color_texture'] = color_node.image.name
                break

        # Fake omni shadows
        if objref.lamp_omni_shadows:
            o['fov'] = 1.5708 # 90 deg
            o['strength'] /= 6

        self.output['lamp_datas'].append(o)

    def export_camera(self, objectRef):
        # This function exports a single camera object
        o = {}
        o['name'] = objectRef[1]["structName"]

        #self.WriteNodeTable(objectRef)

        objref = objectRef[0]

        o['near_plane'] = objref.clip_start
        o['far_plane'] = objref.clip_end
        o['fov'] = objref.angle

        # Viewport Camera - override fov for every camera for now
        # if bpy.data.worlds['Arm'].arm_play_viewport_camera and ArmoryExporter.in_viewport:
        #     # Extract fov from projection
        #     mat = self.get_viewport_projection_matrix()
        #     if mat != None:
        #         yscale = mat[1][1]
        #         if yscale < 0:
        #             yscale *= -1 # Reverse
        #         fov = math.atan(1.0 / yscale) * 0.9
        #         o['fov'] = fov
        
        if objref.type == 'PERSP':
            o['type'] = 'perspective'
        else:
            o['type'] = 'orthographic'

        if objref.is_mirror:
            o['is_mirror'] = True
            o['mirror_resolution_x'] = int(objref.mirror_resolution_x)
            o['mirror_resolution_y'] = int(objref.mirror_resolution_y)

        o['frustum_culling'] = objref.frustum_culling
        o['render_path'] = objref.renderpath_path + '/' + objref.renderpath_path # Same file name and id
        
        if self.scene.world != None and 'Background' in self.scene.world.node_tree.nodes: # TODO: parse node tree
            background_node = self.scene.world.node_tree.nodes['Background']
            col = background_node.inputs[0].default_value
            strength = background_node.inputs[1].default_value
            o['clear_color'] = [col[0] * strength, col[1] * strength, col[2] * strength, col[3]]
        else:
            o['clear_color'] = [0.0, 0.0, 0.0, 1.0]

        self.output['camera_datas'].append(o)

    def export_speaker(self, objectRef):
        # This function exports a single speaker object
        o = {}
        o['name'] = objectRef[1]["structName"]
        objref = objectRef[0]
        if objref.sound:
            # Packed
            if objref.sound.packed_file != None:
                unpack_path = armutils.get_fp() + '/build/compiled/Assets/unpacked'
                if not os.path.exists(unpack_path):
                    os.makedirs(unpack_path)
                unpack_filepath = unpack_path + '/' + objref.sound.name
                if os.path.isfile(unpack_filepath) == False or os.path.getsize(unpack_filepath) != objref.sound.packed_file.size:
                    with open(unpack_filepath, 'wb') as f:
                        f.write(objref.sound.packed_file.data)
                assets.add(unpack_filepath)
            # External
            else:
                assets.add(armutils.safe_assetpath(objref.sound.filepath)) # Link sound to assets
            
            o['sound'] = armutils.extract_filename(objref.sound.filepath)
            o['sound'] = armutils.safe_filename(o['sound'])
        else:
            o['sound'] = ''
        o['muted'] = objref.muted
        o['loop'] = objref.loop
        o['stream'] = objref.stream
        o['volume'] = objref.volume
        o['pitch'] = objref.pitch
        o['attenuation'] = objref.attenuation
        self.output['speaker_datas'].append(o)

    def make_default_mat(self, mat_name, mat_objs):
        if mat_name in bpy.data.materials:
            return
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        o = {}
        o['name'] = mat.name
        o['contexts'] = []
        mat_users = dict()
        mat_users[mat] = mat_objs
        mat_armusers = dict()
        mat_armusers[mat] = [o]
        make_material.parse(mat, o, mat_users, mat_armusers, ArmoryExporter.renderpath_id)
        self.output['material_datas'].append(o)
        bpy.data.materials.remove(mat)

    def export_materials(self):
        wrd = bpy.data.worlds['Arm']

        if wrd.arm_batch_materials:
            mat_users = self.materialToObjectDict
            mat_armusers = self.materialToArmObjectDict
            rid = ArmoryExporter.renderpath_id
            mat_batch.build(self.materialArray, mat_users, mat_armusers, rid)

        transluc_used = False
        overlays_used = False
        decals_used = False
        for materialRef in self.materialArray.items():
            material = materialRef[0]
            # If the material is unlinked, material becomes None
            if material == None:
                continue
            
            o = {}
            o['name'] = materialRef[1]["structName"]

            if material.skip_context != '':
                o['skip_context'] = material.skip_context
            
            if material.override_cull or wrd.force_no_culling:
                o['override_context'] = {}
                if wrd.force_no_culling:
                    o['override_context']['cull_mode'] = 'none'
                else:
                    o['override_context']['cull_mode'] = material.override_cull_mode

            o['contexts'] = []

            if not material.use_nodes:
                material.use_nodes = True

            mat_users = self.materialToObjectDict
            mat_armusers = self.materialToArmObjectDict
            rid = ArmoryExporter.renderpath_id
            sd, rpasses = make_material.parse(material, o, mat_users, mat_armusers, rid)

            if 'translucent' in rpasses:
                transluc_used = True
            if 'overlay' in rpasses:
                overlays_used = True
            if 'decal' in rpasses:
                decals_used = True

            uv_export = False
            tang_export = False
            vcol_export = False
            vs_str = ''
            for elem in sd['vertex_structure']:
                if len(vs_str) > 0:
                    vs_str += ','
                vs_str += elem['name']

                if elem['name'] == 'tang':
                    tang_export = True
                elif elem['name'] == 'tex':
                    uv_export = True
                elif elem['name'] == 'col':
                    vcol_export = True
            material.vertex_structure = vs_str

            if (material.export_tangents != tang_export) or \
               (material.export_uvs != uv_export) or \
               (material.export_vcols != vcol_export):

                material.export_uvs = uv_export
                material.export_vcols = vcol_export
                material.export_tangents = tang_export
                mat_users = self.materialToObjectDict[material]
                for ob in mat_users:
                    ob.data.mesh_cached = False

            self.output['material_datas'].append(o)
            material.is_cached = True

        # Object with no material assigned in the scene
        if len(self.defaultMaterialObjects) > 0:
            self.make_default_mat('armdefault', self.defaultMaterialObjects)
        if len(self.defaultSkinMaterialObjects) > 0:
            self.make_default_mat('armdefaultskin', self.defaultSkinMaterialObjects)

        # Auto-enable render-path featues
        if len(bpy.data.cameras) > 0:
            rebuild_rp = False
            cam = bpy.data.cameras[0]
            if cam.rp_translucency_state == 'Auto' and cam.rp_translucency != transluc_used:
                cam.rp_translucency = transluc_used
                rebuild_rp = True
            if cam.rp_overlays_state == 'Auto' and cam.rp_overlays != overlays_used:
                cam.rp_overlays = overlays_used
                rebuild_rp = True
            if cam.rp_decals_state == 'Auto' and cam.rp_decals != decals_used:
                cam.rp_decals = decals_used
                rebuild_rp = True
            if rebuild_rp:
                self.rebuild_render_path(cam)

    def rebuild_render_path(self, cam):
        # No shader invalidate required?
        make_renderer.make_renderer(cam)
        # Rebuild modified path
        assets_path = armutils.get_sdk_path() + 'armory/Assets/'
        make_renderpath.build_node_trees(assets_path)

    def export_particle_systems(self):
        for particleRef in self.particleSystemArray.items():
            o = {}
            psettings = particleRef[0]

            if psettings == None:
                continue

            o['name'] = particleRef[1]["structName"]
            o['count'] = psettings.count
            o['lifetime'] = psettings.lifetime
            o['normal_factor'] = psettings.normal_factor;
            o['object_align_factor'] = [psettings.object_align_factor[0], psettings.object_align_factor[1], psettings.object_align_factor[2]]
            o['factor_random'] = psettings.factor_random
            self.output['particle_datas'].append(o)
            
    def export_worlds(self):
        worldRef = self.scene.world
        if worldRef != None:
            o = {}
            w = worldRef
            o['name'] = w.name
            self.post_export_world(w, o)
            self.output['world_datas'].append(o)

    def export_grease_pencils(self):
        return # Disabled for now
        
        gpRef = self.scene.grease_pencil
        if gpRef == None or self.scene.gp_export == False:
            return
        
        # ArmoryExporter.option_mesh_per_file # Currently always exports to separate file
        fp = self.get_greasepencils_file_path('greasepencil_' + gpRef.name, compressed=self.is_compress(gpRef))
        assets.add(fp)
        ext = ''
        if self.is_compress(gpRef):
            ext = '.zip'
        self.output['grease_pencil_ref'] = 'greasepencil_' + gpRef.name + ext + '/' + gpRef.name

        assets.add_shader_data('build/compiled/Shaders/grease_pencil/grease_pencil.arm')
        assets.add_shader('build/compiled/Shaders/grease_pencil/grease_pencil.frag.glsl')
        assets.add_shader('build/compiled/Shaders/grease_pencil/grease_pencil.vert.glsl')
        assets.add_shader('build/compiled/Shaders/grease_pencil/grease_pencil_shadows.frag.glsl')
        assets.add_shader('build/compiled/Shaders/grease_pencil/grease_pencil_shadows.vert.glsl')

        if gpRef.data_cached == True and os.path.exists(fp):
            return

        gpo = self.post_export_grease_pencil(gpRef)
        gp_obj = {}
        gp_obj['grease_pencil_datas'] = [gpo]
        armutils.write_arm(fp, gp_obj)
        gpRef.data_cached = True

    def is_compress(self, obj):
        return ArmoryExporter.compress_enabled and obj.data_compressed

    def export_objects(self, scene):
        if not ArmoryExporter.option_mesh_only:
            self.output['lamp_datas'] = []
            self.output['camera_datas'] = []
            self.output['speaker_datas'] = []
            for objectRef in self.lampArray.items():
                self.export_lamp(objectRef)
            for objectRef in self.cameraArray.items():
                self.export_camera(objectRef)
            for objectRef in self.speakerArray.items():
                self.export_speaker(objectRef)
        for objectRef in self.meshArray.items():
            self.output['mesh_datas'] = [];
            self.do_export_mesh(objectRef, scene)

    def execute(self, context, filepath):
        profile_time = time.time()
        
        self.output = {}
        self.filepath = filepath

        self.scene = context.scene
        originalFrame = self.scene.frame_current
        originalSubframe = self.scene.frame_subframe
        self.restoreFrame = False

        self.beginFrame = self.scene.frame_start
        self.endFrame = self.scene.frame_end
        self.frameTime = 1.0 / (self.scene.render.fps_base * self.scene.render.fps)

        self.bobjectArray = {}
        self.meshArray = {}
        self.lampArray = {}
        self.cameraArray = {}
        self.camera_spawned = False
        self.speakerArray = {}
        self.materialArray = {}
        self.particleSystemArray = {}
        self.worldArray = {} # Export all worlds
        self.boneParentArray = {}
        self.materialToObjectDict = dict()
        self.defaultMaterialObjects = [] # If no material is assigned, provide default to mimick cycles
        self.defaultSkinMaterialObjects = []
        self.materialToArmObjectDict = dict()
        self.objectToArmObjectDict = dict()
        self.uvprojectUsersArray = [] # For processing decals
        self.active_layers = []
        for i in range(0, len(self.scene.layers)):
            if self.scene.layers[i] == True:
                self.active_layers.append(i)

        self.preprocess()

        for bobject in self.scene.objects:
            if not bobject.parent:
                self.process_bobject(bobject)

        self.process_skinned_meshes()

        self.output['name'] = armutils.safe_filename(self.scene.name)
        if (self.filepath.endswith('.zip')):
            self.output['name'] += '.zip'

        self.output['objects'] = []
        for obj in self.scene.objects:
            if not obj.parent:
                self.export_object(obj, self.scene)

        if len(bpy.data.groups) > 0:
            self.output['groups'] = []
            for group in bpy.data.groups:
                o = {}
                o['name'] = group.name
                o['object_refs'] = []
                for obj in group.objects:
                    o['object_refs'].append(obj.name)
                self.output['groups'].append(o)

        if not ArmoryExporter.option_mesh_only:
            if self.scene.camera != None:
                self.output['camera_ref'] = self.scene.camera.name
            else:
                if armutils.safe_filename(self.scene.name) == armutils.get_project_scene_name():
                    print('Armory Warning: No camera found in active scene')

            self.output['material_datas'] = []
            self.export_materials()

            # Ensure same vertex structure for object materials
            for bobject in self.scene.objects:
                if len(bobject.material_slots) > 1:
                    mat = bobject.material_slots[0].material
                    if mat == None:
                        continue
                    vs = mat.vertex_structure
                    for i in range(len(bobject.material_slots)):
                        nmat = bobject.material_slots[i].material
                        if nmat == None:
                            continue
                        if vs != nmat.vertex_structure:
                            log.warn('Object ' + bobject.name + ' - unable to bind materials to vertex data, please separate object by material for now (select object - edit mode - P - By Material)')
                            break

            self.output['particle_datas'] = []
            self.export_particle_systems()
            
            self.output['world_datas'] = []
            self.export_worlds()

            self.output['grease_pencil_datas'] = []
            self.export_grease_pencils()

            if self.scene.world != None:
                self.output['world_ref'] = self.scene.world.name

            self.output['gravity'] = [self.scene.gravity[0], self.scene.gravity[1], self.scene.gravity[2]]

        self.export_objects(self.scene)
        
        if not self.camera_spawned:
            log.warn('No camera found in active scene layers')

        self.postprocess()

        if self.restoreFrame:
            self.scene.frame_set(originalFrame, originalSubframe)

        # Scene root traits
        if bpy.data.worlds['Arm'].arm_physics != 'Disabled' and ArmoryExporter.export_physics:
            if not 'traits' in self.output:
                self.output['traits'] = []
            x = {}
            x['type'] = 'Script'
            x['class_name'] = 'armory.trait.internal.PhysicsWorld'
            self.output['traits'].append(x)
        if bpy.data.worlds['Arm'].arm_navigation != 'Disabled' and ArmoryExporter.export_navigation:
            if not 'traits' in self.output:
                self.output['traits'] = []
            x = {}
            x['type'] = 'Script'
            x['class_name'] = 'armory.trait.internal.Navigation'
            self.output['traits'].append(x)

        # Write embedded data references
        if len(assets.embedded_data) > 0:
            self.output['embedded_datas'] = []
            for file in assets.embedded_data:
                self.output['embedded_datas'].append(file)

        # Write scene file
        armutils.write_arm(self.filepath, self.output)

        print('Scene built in ' + str(time.time() - profile_time))
        return {'FINISHED'}

    # Callbacks
    def object_is_mesh_cached(self, bobject):
        if bobject.type == 'FONT' or bobject.type == 'META': # No verts
            return bobject.data.mesh_cached
        if bobject.data.mesh_cached_verts != len(bobject.data.vertices):
            return False
        if bobject.data.mesh_cached_edges != len(bobject.data.edges):
            return False
        return bobject.data.mesh_cached

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
            if n.instanced_children == True:
                is_instanced = True
                # Save offset data
                instance_offsets = [0, 0, 0] # Include parent
                for sn in n.children:
                    # Child hidden
                    if sn.game_export == False or (sn.hide_render and ArmoryExporter.option_export_hide_render == False):
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
        ArmoryExporter.exportAllFlag = True
        ArmoryExporter.export_physics = False # Indicates whether rigid body is exported
        ArmoryExporter.export_navigation = False
        if not hasattr(ArmoryExporter, 'compress_enabled'):
            ArmoryExporter.compress_enabled = False
        if not hasattr(ArmoryExporter, 'in_viewport'):
            ArmoryExporter.in_viewport = False
        ArmoryExporter.option_mesh_only = False
        ArmoryExporter.option_mesh_per_file = True
        ArmoryExporter.option_optimize_mesh = bpy.data.worlds['Arm'].arm_optimize_mesh
        ArmoryExporter.option_export_hide_render = bpy.data.worlds['Arm'].arm_export_hide_render
        ArmoryExporter.option_spawn_all_layers = bpy.data.worlds['Arm'].arm_spawn_all_layers
        ArmoryExporter.option_minimize = bpy.data.worlds['Arm'].arm_minimize
        ArmoryExporter.option_sample_animation = bpy.data.worlds['Arm'].arm_sampled_animation
        ArmoryExporter.sampleAnimationFlag = ArmoryExporter.option_sample_animation

        # Only one render path for scene for now
        # Used for material shader export and khafile
        if len(bpy.data.cameras) > 0:
            ArmoryExporter.renderpath_id = bpy.data.cameras[0].renderpath_id
            ArmoryExporter.renderpath_passes = bpy.data.cameras[0].renderpath_passes.split('_')
            ArmoryExporter.mesh_context = 'mesh'
            ArmoryExporter.mesh_context_empty = ''
            ArmoryExporter.shadows_context = 'shadowmap'
            ArmoryExporter.translucent_context = 'translucent'
            ArmoryExporter.overlay_context = 'overlay'

    def preprocess_object(self, bobject): # Returns false if object should not be exported
        export_object = True

        # Disabled object   
        if bobject.game_export == False or (bobject.hide_render and ArmoryExporter.option_export_hide_render == False):
            return False
        
        for m in bobject.modifiers:
            if m.type == 'OCEAN':
                # Do not export ocean mesh, just take specified constants
                export_object = False
                wrd = bpy.data.worlds['Arm']
                wrd.generate_ocean = True
                # Take position and bounds
                wrd.generate_ocean_level = bobject.location.z
            elif m.type == 'UV_PROJECT' and m.show_render:
                self.uvprojectUsersArray.append(bobject)
                
        return export_object

    def postprocess(self):
        # Check uv project users
        for bobject in self.uvprojectUsersArray:
            for m in bobject.modifiers:
                if m.type == 'UV_PROJECT':
                    # Mark all projectors as decals
                    for pnode in m.projectors:
                        o = self.objectToArmObjectDict[bobject]
                        po = self.objectToArmObjectDict[pnode.object]
                        po['type'] = 'decal_object'
                        po['material_refs'] = [o['material_refs'][0] + '_decal'] # Will fetch a proper context used in render path
                    break

    def post_export_object(self, bobject, o, type):
        # Animation setup
        if armutils.is_bone_animation_enabled(bobject) or armutils.is_object_animation_enabled(bobject):
            x = {}
            if len(bobject.my_cliptraitlist) > 0:
                # Edit clips enabled
                x['names'] = []
                x['starts'] = []
                x['ends'] = []
                x['speeds'] = []
                x['loops'] = []
                x['reflects'] = []
                for at in bobject.my_cliptraitlist:
                    if at.enabled_prop:
                        x['names'].append(at.name)
                        x['starts'].append(at.start_prop)
                        x['ends'].append(at.end_prop)
                        x['speeds'].append(at.speed_prop)
                        x['loops'].append(at.loop_prop)
                        x['reflects'].append(at.reflect_prop)
                start_track = bobject.start_track_name_prop
                if start_track == '' and len(bobject.my_cliptraitlist) > 0: # Start track undefined
                    start_track = bobject.my_cliptraitlist[0].name
                x['start_track'] = start_track
                x['max_bones'] = bpy.data.worlds['Arm'].generate_gpu_skin_max_bones
            else:
                # Export default clip, taking full action
                if armutils.is_bone_animation_enabled(bobject):
                    begin_frame, end_frame = self.get_action_framerange(bobject.parent.animation_data.action)
                else:
                    begin_frame, end_frame = self.get_action_framerange(bobject.animation_data.action)
                x['start_track'] = 'default'
                x['names'] = ['default']
                x['starts'] = [begin_frame]
                x['ends'] = [end_frame]
                x['speeds'] = [1.0]
                x['loops'] = [True]
                x['reflects'] = [False]
                x['max_bones'] = bpy.data.worlds['Arm'].generate_gpu_skin_max_bones
            o['animation_setup'] = x

        # Export traits
        o['traits'] = []
        for t in bobject.my_traitlist:
            if t.enabled_prop == False:
                continue
            x = {}
            if t.type_prop == 'Logic Nodes' and t.nodes_name_prop != '':
                x['type'] = 'Script'
                x['class_name'] = bpy.data.worlds['Arm'].arm_project_package + '.node.' + armutils.safe_source_name(t.nodes_name_prop)
            elif t.type_prop == 'JS Script' or t.type_prop == 'Python Script':
                basename = t.jsscript_prop.split('.')[0]
                x['type'] = 'Script'
                x['class_name'] = 'armory.trait.internal.JSScript'
                x['parameters'] = [armutils.safe_filename(basename)]
                scriptspath = armutils.get_fp() + '/build/compiled/scripts/'
                if not os.path.exists(scriptspath):
                    os.makedirs(scriptspath)
                # Compile to JS
                if t.type_prop == 'Python Script':
                    # Write py to file
                    basename_ext = basename + '.py'
                    targetpath = scriptspath + basename_ext
                    with open(targetpath, 'w') as f:
                        f.write(bpy.data.texts[t.jsscript_prop].as_string())
                    sdk_path = armutils.get_sdk_path()
                    python_path = bpy.app.binary_path_python
                    cwd = os.getcwd()
                    os.chdir(scriptspath)
                    # Disable minification for now, too slow
                    transproc = subprocess.Popen([python_path + ' ' + sdk_path + '/lib/transcrypt/__main__.py' + ' ' + basename_ext + ' --nomin'], shell=True)
                    transproc.wait()
                    if transproc.poll() != 0:
                        log.print_info('Compiling ' + t.jsscript_prop + ' failed, check console')
                    os.chdir(cwd)
                    # Compiled file
                    assets.add('build/compiled/scripts/__javascript__/' + basename + '.js')
                else:
                    # Write js to file
                    assetpath = 'build/compiled/scripts/' + t.jsscript_prop + '.js'
                    targetpath = armutils.get_fp() + '/' + assetpath
                    with open(targetpath, 'w') as f:
                        f.write(bpy.data.texts[t.jsscript_prop].as_string())
                    assets.add(assetpath)
            else: # Haxe/Bundled Script
                if t.class_name_prop == '': # Empty class name, skip
                    continue
                x['type'] = 'Script'
                if t.type_prop == 'Bundled Script':
                    trait_prefix = 'armory.trait.'
                    # TODO: temporary, export single mesh navmesh as obj
                    if t.class_name_prop == 'NavMesh' and bobject.type == 'MESH' and bpy.data.worlds['Arm'].arm_navigation != 'Disabled':
                        ArmoryExporter.export_navigation = True
                        nav_path = armutils.get_fp() + '/build/compiled/Assets/navigation'
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
                    trait_prefix = bpy.data.worlds['Arm'].arm_project_package + '.'
                x['class_name'] = trait_prefix + t.class_name_prop
                if len(t.my_paramstraitlist) > 0:
                    x['parameters'] = []
                    for pt in t.my_paramstraitlist: # Append parameters
                        x['parameters'].append(ast.literal_eval(pt.name))
            o['traits'].append(x)

        # Rigid body trait
        if bobject.rigid_body != None:
            ArmoryExporter.export_physics = True
            rb = bobject.rigid_body
            shape = 0 # BOX
            if rb.collision_shape == 'SPHERE':
                shape = 1
            elif rb.collision_shape == 'CONVEX_HULL':
                shape = 2
            elif rb.collision_shape == 'MESH':
                if rb.enabled:
                    shape = 3 # Mesh
                else:
                    shape = 8 # Static Mesh
            elif rb.collision_shape == 'CONE':
                shape = 4
            elif rb.collision_shape == 'CYLINDER':
                shape = 5
            elif rb.collision_shape == 'CAPSULE':
                shape = 6
            body_mass = 0
            if rb.enabled:
                body_mass = rb.mass
            x = {}
            x['type'] = 'Script'
            x['class_name'] = 'armory.trait.internal.RigidBody'
            x['parameters'] = [body_mass, shape, rb.friction]
            if rb.use_margin:
                x['parameters'].append(rb.collision_margin)
            else:
                x['parameters'].append(0.0)
            x['parameters'].append(rb.linear_damping)
            x['parameters'].append(rb.angular_damping)
            x['parameters'].append(rb.type == 'PASSIVE')
            o['traits'].append(x)
        
        # Soft bodies modifier
        soft_type = -1
        soft_mod = None
        for m in bobject.modifiers:
            if m.type == 'CLOTH':
                soft_type = 0
                soft_mod = m
                break
            elif m.type == 'SOFT_BODY':
                soft_type = 1 # Volume
                soft_mod = m
                break
        if soft_type >= 0:
            ArmoryExporter.export_physics = True
            assets.add_khafile_def('arm_physics_soft')
            cloth_trait = {}
            cloth_trait['type'] = 'Script'
            cloth_trait['class_name'] = 'armory.trait.internal.SoftBody'
            if soft_type == 0:
                bend = soft_mod.settings.bending_stiffness
            elif soft_type == 1:
                bend = (soft_mod.settings.bend + 1.0) * 10
            cloth_trait['parameters'] = [soft_type, bend, soft_mod.settings.mass, bobject.soft_body_margin]
            o['traits'].append(cloth_trait)

        if type == NodeTypeCamera:
            # Debug console enabled, attach console overlay to each camera
            if bpy.data.worlds['Arm'].arm_play_console:
                console_trait = {}
                console_trait['type'] = 'Script'
                console_trait['class_name'] = 'armory.trait.internal.Console'
                console_trait['parameters'] = []
                o['traits'].append(console_trait)
            # Viewport camera enabled, attach navigation to active camera if enabled
            if self.scene.camera != None and bobject.name == self.scene.camera.name and bpy.data.worlds['Arm'].arm_play_viewport_camera and bpy.data.worlds['Arm'].arm_play_viewport_navigation == 'Walk':
                navigation_trait = {}
                navigation_trait['type'] = 'Script'
                navigation_trait['class_name'] = 'armory.trait.WalkNavigation'
                navigation_trait['parameters'] = []
                o['traits'].append(navigation_trait)

        # Map objects to game objects
        self.objectToArmObjectDict[bobject] = o
        
        # Map objects to materials, can be used in later stages
        for i in range(len(bobject.material_slots)):
            mat = bobject.material_slots[i].material
            if mat in self.materialToObjectDict:
                self.materialToObjectDict[mat].append(bobject)
                self.materialToArmObjectDict[mat].append(o)
            else:
                self.materialToObjectDict[mat] = [bobject]
                self.materialToArmObjectDict[mat] = [o]

        # Export constraints
        if len(bobject.constraints) > 0:
            o['constraints'] = []
            for constr in bobject.constraints:
                if constr.mute:
                    continue
                co = {}
                co['name'] = constr.name
                co['type'] = constr.type
                if constr.type == 'COPY_LOCATION':
                    co['target'] = constr.target.name
                    co['use_x'] = constr.use_x
                    co['use_y'] = constr.use_y
                    co['use_z'] = constr.use_z
                    co['invert_x'] = constr.invert_x
                    co['invert_y'] = constr.invert_y
                    co['invert_z'] = constr.invert_z
                    co['use_offset'] = constr.use_offset
                    co['influence'] = constr.influence
                o['constraints'].append(co)
    
    def post_export_world(self, world, o):
        defs = bpy.data.worlds['Arm'].world_defs + bpy.data.worlds['Arm'].rp_defs
        bgcol = world.world_envtex_color
        if '_LDR' in defs: # No compositor used
            for i in range(0, 3):
                bgcol[i] = pow(bgcol[i], 1.0 / 2.2)
        o['background_color'] = armutils.color_to_int(bgcol)

        wmat_name = armutils.safe_filename(world.name) + '_material'
        o['material_ref'] = wmat_name + '/' + wmat_name + '/world'
        o['probes'] = []
        # Main probe
        world_generate_radiance = False
        generate_irradiance = True #'_EnvTex' in defs or '_EnvSky' in defs or '_EnvCon' in defs
        disable_hdr = world.world_envtex_name.endswith('.jpg')
        radtex = world.world_envtex_name.rsplit('.', 1)[0]
        irrsharmonics = world.world_envtex_irr_name

        # Radiance
        if '_EnvTex' in defs:
            world_generate_radiance = bpy.data.worlds['Arm'].generate_radiance
        elif '_EnvSky' in defs and bpy.data.worlds['Arm'].generate_radiance_sky:
            world_generate_radiance = bpy.data.worlds['Arm'].generate_radiance
            radtex = 'hosek'

        num_mips = world.world_envtex_num_mips
        strength = world.world_envtex_strength
        po = self.make_probe(world.name, irrsharmonics, radtex, num_mips, strength, 1.0, [0, 0, 0], [0, 0, 0], world_generate_radiance, generate_irradiance, disable_hdr)
        o['probes'].append(po)
        
        if '_EnvSky' in defs:
            # Sky data for probe
            po['sun_direction'] =  list(world.world_envtex_sun_direction)
            po['turbidity'] = world.world_envtex_turbidity
            po['ground_albedo'] = world.world_envtex_ground_albedo
        
        # Probe cameras attached in scene
        for cam in bpy.data.cameras:
            if cam.is_probe:
                # Generate probe straight here for now
                volume_object = bpy.data.objects[cam.probe_volume]
                # Assume empty box of size 2, multiply by scale and dividy by 2 to get half extents
                volume = [2 * volume_object.scale[0] / 2, 2 * volume_object.scale[1] / 2, 2 * volume_object.scale[2] / 2] 
                volume_center = [volume_object.location[0], volume_object.location[1], volume_object.location[2]]
                
                disable_hdr = cam.probe_texture.endswith('.jpg')
                generate_radiance = cam.probe_generate_radiance
                if world_generate_radiance == False:
                    generate_radiance = False
                
                texture_path = '//' + cam.probe_texture
                cam.probe_num_mips = write_probes.write_probes(texture_path, disable_hdr, cam.probe_num_mips, generate_radiance=generate_radiance)
                base_name = cam.probe_texture.rsplit('.', 1)[0]
                po = self.make_probe(cam.name, base_name, base_name, cam.probe_num_mips, cam.probe_strength, cam.probe_blending, volume, volume_center, generate_radiance, generate_irradiance, disable_hdr)
                o['probes'].append(po)
    
    def post_export_grease_pencil(self, gp):
        o = {}
        o['name'] = gp.name
        o['layers'] = []
        # originalFrame = self.scene.frame_current
        for layer in gp.layers:
            o['layers'].append(self.export_grease_pencil_layer(layer))
        # self.scene.frame_set(originalFrame)
        # o['palettes'] = []
        # for palette in gp.palettes:
            # o['palettes'].append(self.export_grease_pencil_palette(palette))
        o['shader'] = 'grease_pencil/grease_pencil'
        return o

    def export_grease_pencil_layer(self, layer):
        lo = {}
        lo['name'] = layer.info
        lo['opacity'] = layer.opacity
        lo['frames'] = []
        for frame in layer.frames:
            if frame.frame_number > self.scene.frame_end:
                break
            # TODO: load GP frame data
            # self.scene.frame_set(frame.frame_number)
            lo['frames'].append(self.export_grease_pencil_frame(frame))
        return lo

    def export_grease_pencil_frame(self, frame):
        va = []
        cola = []
        colfilla = []
        indices = []
        num_stroke_points = []
        index_offset = 0
        for stroke in frame.strokes:
            for point in stroke.points:
                va.append(point.co[0])
                va.append(point.co[1])
                va.append(point.co[2])
                # TODO: store index to color pallete only, this is extremely wasteful
                if stroke.color != None:
                    cola.append(stroke.color.color[0])
                    cola.append(stroke.color.color[1])
                    cola.append(stroke.color.color[2])
                    cola.append(stroke.color.alpha)
                    colfilla.append(stroke.color.fill_color[0])
                    colfilla.append(stroke.color.fill_color[1])
                    colfilla.append(stroke.color.fill_color[2])
                    colfilla.append(stroke.color.fill_alpha)
                else:
                    cola.append(0.0)
                    cola.append(0.0)
                    cola.append(0.0)
                    cola.append(0.0)
                    colfilla.append(0.0)
                    colfilla.append(0.0)
                    colfilla.append(0.0)
                    colfilla.append(0.0)        
            for triangle in stroke.triangles:
                indices.append(triangle.v1 + index_offset)
                indices.append(triangle.v2 + index_offset)
                indices.append(triangle.v3 + index_offset)
            num_stroke_points.append(len(stroke.points))
            index_offset += len(stroke.points)
        fo = {}
        # TODO: merge into array of vertex arrays
        fo['vertex_array'] = {}
        fo['vertex_array']['attrib'] = 'pos'
        fo['vertex_array']['size'] = 3
        fo['vertex_array']['values'] = va
        fo['col_array'] = {}
        fo['col_array']['attrib'] = 'col'
        fo['col_array']['size'] = 4
        fo['col_array']['values'] = cola
        fo['colfill_array'] = {}
        fo['colfill_array']['attrib'] = 'colfill'
        fo['colfill_array']['size'] = 4
        fo['colfill_array']['values'] = colfilla
        fo['index_array'] = {}
        fo['index_array']['material'] = 0
        fo['index_array']['size'] = 3
        fo['index_array']['values'] = indices
        fo['num_stroke_points'] = num_stroke_points
        fo['frame_number'] = frame.frame_number
        return fo

    def export_grease_pencil_palette(self, palette):
        po = {}
        po['name'] = palette.info
        po['colors'] = []
        for color in palette.colors:
            po['colors'].append(self.export_grease_pencil_palette_color(color))
        return po

    def export_grease_pencil_palette_color(self, color):
        co = {}
        co['name'] = color.name
        co['color'] = [color.color[0], color.color[1], color.color[2]]
        co['alpha'] = color.alpha
        co['fill_color'] = [color.fill_color[0], color.fill_color[1], color.fill_color[2]]
        co['fill_alpha'] = color.fill_alpha
        return co

    def make_probe(self, id, irrsharmonics, radtex, mipmaps, strength, blending, volume, volume_center, generate_radiance, generate_irradiance, disable_hdr):
        po = {}
        po['name'] = id
        if generate_radiance:
            po['radiance'] = radtex + '_radiance'
            if disable_hdr:
                po['radiance'] += '.jpg'
            else:
                po['radiance'] += '.hdr'
            po['radiance_mipmaps'] = mipmaps
        if generate_irradiance:
            po['irradiance'] = irrsharmonics + '_irradiance'
        else:
            po['irradiance'] = '' # No irradiance data, fallback to default at runtime
        po['strength'] = strength
        po['blending'] = blending
        po['volume'] = volume
        po['volume_center'] = volume_center
        return po
