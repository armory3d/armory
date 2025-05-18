from typing import Dict, List

import bpy
from bpy.types import Material
from bpy.types import Object

import arm.log as log
import arm.material.cycles as cycles
import arm.material.make_shader as make_shader
import arm.material.mat_batch as mat_batch
import arm.material.mat_utils as mat_utils
import arm.node_utils
import arm.utils

if arm.is_reload(__name__):
    log = arm.reload_module(log)
    cycles = arm.reload_module(cycles)
    make_shader = arm.reload_module(make_shader)
    mat_batch = arm.reload_module(mat_batch)
    mat_utils = arm.reload_module(mat_utils)
    arm.node_utils = arm.reload_module(arm.node_utils)
    arm.utils = arm.reload_module(arm.utils)
else:
    arm.enable_reload(__name__)


def glsl_value(val):
    if str(type(val)) == "<class 'bpy_prop_array'>":
        res = []
        for v in val:
            res.append(v)
        return res
    else:
        return val


def parse(material: Material, mat_data, mat_users: Dict[Material, List[Object]], mat_armusers) -> tuple:
    wrd = bpy.data.worlds['Arm']
    rpdat = arm.utils.get_rp()

    # Texture caching for material batching
    batch_cached_textures = []

    needs_sss = material_needs_sss(material)
    if needs_sss and rpdat.rp_sss_state != 'Off' and '_SSS' not in wrd.world_defs:
        # Must be set before calling make_shader.build()
        wrd.world_defs += '_SSS'

    # No batch - shader data per material
    if material.arm_custom_material != '':
        rpasses = ['mesh']

        con = {'vertex_elements': []}
        con['vertex_elements'].append({'name': 'pos', 'data': 'short4norm'})
        con['vertex_elements'].append({'name': 'nor', 'data': 'short2norm'})
        con['vertex_elements'].append({'name': 'tex', 'data': 'short2norm'})
        con['vertex_elements'].append({'name': 'tex1', 'data': 'short2norm'})

        sd = {'contexts': [con]}
        shader_data_name = material.arm_custom_material
        bind_constants = {'mesh': []}
        bind_textures = {'mesh': []}

        make_shader.make_instancing_and_skinning(material, mat_users)

        for idx, item in enumerate(material.arm_bind_textures_list):
            if item.uniform_name == '':
                log.warn(f'Material "{material.name}": skipping export of bind texture at slot {idx + 1} with empty uniform name')
                continue

            if item.image is not None:
                tex = cycles.make_texture(item.image, item.uniform_name, material.name, 'Linear', 'REPEAT')
                if tex is None:
                    continue
                bind_textures['mesh'].append(tex)
            else:
                log.warn(f'Material "{material.name}": skipping export of bind texture at slot {idx + 1} ("{item.uniform_name}") with no image selected')

    elif not wrd.arm_batch_materials or material.name.startswith('armdefault'):
        rpasses, shader_data, shader_data_name, bind_constants, bind_textures = make_shader.build(material, mat_users, mat_armusers)
        sd = shader_data.sd
    else:
        rpasses, shader_data, shader_data_name, bind_constants, bind_textures = mat_batch.get(material)
        sd = shader_data.sd

    sss_used = False

    # Material
    for rp in rpasses:
        c = {
            'name': rp,
            'bind_constants': [] + bind_constants[rp],
            'bind_textures': [] + bind_textures[rp],
            'depth_read': material.arm_depth_read,
        }
        mat_data['contexts'].append(c)

        if rp == 'mesh' or rp == 'voxel':
            c['bind_constants'].append({'name': 'receiveShadow', 'boolValue': material.arm_receive_shadow})

            if material.arm_material_id != 0:
                c['bind_constants'].append({'name': 'materialID', 'intValue': material.arm_material_id})

                if material.arm_material_id == 2:
                    wrd.world_defs += '_Hair'

            elif rpdat.rp_sss_state != 'Off':
                const = {'name': 'materialID'}
                if needs_sss:
                    const['intValue'] = 2
                    sss_used = True
                else:
                    const['intValue'] = 0
                c['bind_constants'].append(const)

            # TODO: Mesh only material batching
            if wrd.arm_batch_materials:
                # Set textures uniforms
                if len(c['bind_textures']) > 0:
                    c['bind_textures'] = []
                    for node in material.node_tree.nodes:
                        if node.type == 'TEX_IMAGE':
                            tex_name = arm.utils.safesrc(node.name)
                            tex = cycles.make_texture_from_image_node(node, tex_name)
                            # Empty texture
                            if tex is None:
                                tex = {'name': tex_name, 'file': ''}
                            c['bind_textures'].append(tex)
                    batch_cached_textures = c['bind_textures']

                # Set marked inputs as uniforms
                for node in material.node_tree.nodes:
                    for inp in node.inputs:
                        if inp.is_uniform:
                            uname = arm.utils.safesrc(inp.node.name) + arm.utils.safesrc(inp.name)  # Merge with cycles module
                            c['bind_constants'].append({'name': uname, cycles.glsl_type(inp.type)+'Value': glsl_value(inp.default_value)})

        elif rp == 'translucent' or rp == 'refraction':
            c['bind_constants'].append({'name': 'receiveShadow', 'boolValue': material.arm_receive_shadow})
        
        elif rp == 'shadowmap':
            if wrd.arm_batch_materials:
                if len(c['bind_textures']) > 0:
                    c['bind_textures'] = batch_cached_textures

    if wrd.arm_single_data_file:
        mat_data['shader'] = shader_data_name
    else:
        # Make sure that custom materials are not expected to be in .arm format
        ext = '' if wrd.arm_minimize and material.arm_custom_material == "" else '.json'
        mat_data['shader'] = shader_data_name + ext + '/' + shader_data_name

    return sd, rpasses, sss_used


def material_needs_sss(material: Material) -> bool:
    """Check whether the given material requires SSS."""
    for sss_node in arm.node_utils.iter_nodes_by_type(material.node_tree, 'SUBSURFACE_SCATTERING'):
        if sss_node is not None and sss_node.outputs[0].is_linked:
            return True

    for sss_node in arm.node_utils.iter_nodes_by_type(material.node_tree, 'BSDF_PRINCIPLED'):
        if sss_node is not None and sss_node.outputs[0].is_linked and (sss_node.inputs[1].is_linked or sss_node.inputs[1].default_value != 0.0):
            return True

    for sss_node in mat_utils.iter_nodes_armorypbr(material.node_tree):
        if sss_node is not None and sss_node.outputs[0].is_linked and (sss_node.inputs[8].is_linked or sss_node.inputs[8].default_value != 0.0):
            return True

    return False
