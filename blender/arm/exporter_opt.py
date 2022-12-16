"""
Exports smaller geometry but is slower.
To be replaced with https://github.com/zeux/meshoptimizer
"""
from typing import Optional

import bpy
from mathutils import Vector
import numpy as np

import arm.utils
from arm import log

if arm.is_reload(__name__):
    log = arm.reload_module(log)
    arm.utils = arm.reload_module(arm.utils)
else:
    arm.enable_reload(__name__)


class Vertex:
    __slots__ = ("co", "normal", "uvs", "col", "loop_indices", "index", "bone_weights", "bone_indices", "bone_count", "vertex_index")

    def __init__(self, mesh: bpy.types.Mesh, loop: bpy.types.MeshLoop, vcol0: Optional[bpy.types.Attribute]):
        self.vertex_index = loop.vertex_index
        loop_idx = loop.index
        self.co = mesh.vertices[self.vertex_index].co[:]
        self.normal = loop.normal[:]
        self.uvs = tuple(layer.data[loop_idx].uv[:] for layer in mesh.uv_layers)
        self.col = [0.0, 0.0, 0.0] if vcol0 is None else vcol0.data[loop_idx].color[:]
        self.loop_indices = [loop_idx]
        self.index = 0
        print("******************************************************************")
        print(self.vertex_index)
        print(loop_idx)
        print(self.co)
        print(self.normal)
        print(self.uvs)
        print(self.col)
        print(self.loop_indices)

    def __hash__(self):
        print("000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")
        print(hash((self.co, self.normal, self.uvs)))
        return hash((self.co, self.normal, self.uvs))

    def __eq__(self, other):
        print("111111111111111111111111111111111111111111111111111111111111111111111111111111111111111")
        eq = (
            (self.co == other.co) and
            (self.normal == other.normal) and
            (self.uvs == other.uvs) and
            (self.col == other.col)
            )
        if eq:
            print("EQUAL")
            indices = self.loop_indices + other.loop_indices
            self.loop_indices = indices
            other.loop_indices = indices
        return eq


def calc_tangents(posa, nora, uva, ias, scale_pos):
    num_verts = int(len(posa) / 4)
    tangents = np.empty(num_verts * 3, dtype='<f4')
    # bitangents = np.empty(num_verts * 3, dtype='<f4')
    for ar in ias:
        ia = ar['values']
        num_tris = int(len(ia) / 3)
        for i in range(0, num_tris):
            i0 = ia[i * 3    ]
            i1 = ia[i * 3 + 1]
            i2 = ia[i * 3 + 2]
            v0 = Vector((posa[i0 * 4], posa[i0 * 4 + 1], posa[i0 * 4 + 2]))
            v1 = Vector((posa[i1 * 4], posa[i1 * 4 + 1], posa[i1 * 4 + 2]))
            v2 = Vector((posa[i2 * 4], posa[i2 * 4 + 1], posa[i2 * 4 + 2]))
            uv0 = Vector((uva[i0 * 2], uva[i0 * 2 + 1]))
            uv1 = Vector((uva[i1 * 2], uva[i1 * 2 + 1]))
            uv2 = Vector((uva[i2 * 2], uva[i2 * 2 + 1]))

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

            tangents[i0 * 3    ] += tangent.x
            tangents[i0 * 3 + 1] += tangent.y
            tangents[i0 * 3 + 2] += tangent.z
            tangents[i1 * 3    ] += tangent.x
            tangents[i1 * 3 + 1] += tangent.y
            tangents[i1 * 3 + 2] += tangent.z
            tangents[i2 * 3    ] += tangent.x
            tangents[i2 * 3 + 1] += tangent.y
            tangents[i2 * 3 + 2] += tangent.z
            # bitangents[i0 * 3    ] += bitangent.x
            # bitangents[i0 * 3 + 1] += bitangent.y
            # bitangents[i0 * 3 + 2] += bitangent.z
            # bitangents[i1 * 3    ] += bitangent.x
            # bitangents[i1 * 3 + 1] += bitangent.y
            # bitangents[i1 * 3 + 2] += bitangent.z
            # bitangents[i2 * 3    ] += bitangent.x
            # bitangents[i2 * 3 + 1] += bitangent.y
            # bitangents[i2 * 3 + 2] += bitangent.z
    # Orthogonalize
    for i in range(0, num_verts):
        t = Vector((tangents[i * 3], tangents[i * 3 + 1], tangents[i * 3 + 2]))
        # b = Vector((bitangents[i * 3], bitangents[i * 3 + 1], bitangents[i * 3 + 2]))
        n = Vector((nora[i * 2], nora[i * 2 + 1], posa[i * 4 + 3] / scale_pos))
        v = t - n * n.dot(t)
        v.normalize()
        # Calculate handedness
        # cnv = n.cross(v)
        # if cnv.dot(b) < 0.0:
            # v = v * -1.0
        tangents[i * 3    ] = v.x
        tangents[i * 3 + 1] = v.y
        tangents[i * 3 + 2] = v.z
    return tangents


def export_mesh_data(self, export_mesh: bpy.types.Mesh, bobject: bpy.types.Object, o, has_armature=False):
    export_mesh.calc_normals_split()
    # exportMesh.calc_loop_triangles()
    vcol0 = self.get_nth_vertex_colors(export_mesh, 0)
    vert_list = {Vertex(export_mesh, loop, vcol0): 0 for loop in export_mesh.loops}.keys()
    print("EXPORT")
    print({Vertex(export_mesh, loop, vcol0): 0 for loop in export_mesh.loops})
    print(vert_list)
    num_verts = len(vert_list)
    print(num_verts)
    num_uv_layers = len(export_mesh.uv_layers)
    # Check if shape keys were exported
    has_morph_target = self.get_shape_keys(bobject.data)
    if has_morph_target:
        # Shape keys UV are exported separately, so reduce UV count by 1
        num_uv_layers -= 1
        morph_uv_index = self.get_morph_uv_index(bobject.data)
    has_tex = self.get_export_uvs(export_mesh) and num_uv_layers > 0
    if self.has_baked_material(bobject, export_mesh.materials):
        has_tex = True
    has_tex1 = has_tex and num_uv_layers > 1
    num_colors = self.get_num_vertex_colors(export_mesh)
    has_col = self.get_export_vcols(export_mesh) and num_colors > 0
    has_tang = self.has_tangents(export_mesh)

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

    if has_col:
        cdata = np.empty(num_verts * 3, dtype='<f4')

    # Save aabb
    self.calc_aabb(bobject)

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

    # Make arrays
    for i, v in enumerate(vert_list):
        v.index = i
        co = v.co
        normal = v.normal
        i4 = i * 4
        i2 = i * 2
        pdata[i4    ] = co[0]
        pdata[i4 + 1] = co[1]
        pdata[i4 + 2] = co[2]
        pdata[i4 + 3] = normal[2] * scale_pos # Cancel scale
        ndata[i2    ] = normal[0]
        ndata[i2 + 1] = normal[1]
        if has_tex:
            uv = v.uvs[t0map]
            t0data[i2    ] = uv[0]
            t0data[i2 + 1] = 1.0 - uv[1] # Reverse Y
            if has_tex1:
                uv = v.uvs[t1map]
                t1data[i2    ] = uv[0]
                t1data[i2 + 1] = 1.0 - uv[1]
        if has_morph_target:
               uv = v.uvs[morph_uv_index]
               morph_data[i2    ] = uv[0]
               morph_data[i2 + 1] = 1.0 - uv[1]
        if has_col:
            i3 = i * 3
            cdata[i3    ] = v.col[0]
            cdata[i3 + 1] = v.col[1]
            cdata[i3 + 2] = v.col[2]

    # Indices
    prims = {ma.name if ma else '': [] for ma in export_mesh.materials}
    if not prims:
        prims = {'': []}

    vert_dict = {i : v for v in vert_list for i in v.loop_indices}
    for poly in export_mesh.polygons:
        first = poly.loop_start
        if len(export_mesh.materials) == 0:
            prim = prims['']
        else:
            mat = export_mesh.materials[min(poly.material_index, len(export_mesh.materials) - 1)]
            prim = prims[mat.name if mat else '']
        indices = [vert_dict[i].index for i in range(first, first+poly.loop_total)]

        if poly.loop_total == 3:
            prim += indices
        elif poly.loop_total > 3:
            for i in range(poly.loop_total-2):
                prim += (indices[-1], indices[i], indices[i + 1])

    # Write indices
    o['index_arrays'] = []
    for mat, prim in prims.items():
        idata = [0] * len(prim)
        for i, v in enumerate(prim):
            idata[i] = v
        if len(idata) == 0: # No face assigned
            continue
        ia = {'values': idata, 'material': 0}
        # Find material index for multi-mat mesh
        if len(export_mesh.materials) > 1:
            for i in range(0, len(export_mesh.materials)):
                if (export_mesh.materials[i] is not None and mat == export_mesh.materials[i].name) or \
                   (export_mesh.materials[i] is None and mat == ''):  # Default material for empty slots
                    ia['material'] = i
                    break
        o['index_arrays'].append(ia)

    if has_tang:
        tangdata = calc_tangents(pdata, ndata, t0data, o['index_arrays'], scale_pos)

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

    return vert_list

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
            oskin['bone_ref_array'].append("")
            oskin['bone_len_array'].append(0.0)

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

    bone_count_array = np.empty(len(vert_list), dtype='<i2')
    bone_index_array = np.empty(len(vert_list) * 4, dtype='<i2')
    bone_weight_array = np.empty(len(vert_list) * 4, dtype='<i2')

    vertices = bobject.data.vertices
    count = 0
    for index, v in enumerate(vert_list):
        bone_count = 0
        total_weight = 0.0
        bone_values = []
        for g in vertices[v.vertex_index].groups:
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
            bone_weight_array[count] = bv[0] * 32767
            bone_index_array[count] = bv[1]
            count += 1
        
        if total_weight not in (0.0, 1.0):
            normalizer = 1.0 / total_weight
            for i in range(bone_count):
                bone_weight_array[count - i - 1] *= normalizer

    oskin['bone_count_array'] = bone_count_array
    oskin['bone_index_array'] = bone_index_array[:count]
    oskin['bone_weight_array'] = bone_weight_array[:count]

    # Bone constraints
    for bone in armature.pose.bones:
        if len(bone.constraints) > 0:
            if 'constraints' not in oskin:
                oskin['constraints'] = []
            self.add_constraints(bone, oskin, bone=True)
