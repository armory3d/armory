from typing import Dict, List

import bpy
from bpy.types import Material
from bpy.types import Object

import arm.material.cycles as cycles
import arm.material.make_shader as make_shader
import arm.material.mat_batch as mat_batch
import arm.node_utils
import arm.utils


def glsl_value(val):
    if str(type(val)) == "<class 'bpy_prop_array'>":
        res = []
        for v in val:
            res.append(v)
        return res
    else:
        return val


def parse(material: Material, mat_data, mat_users: Dict[Material, List[Object]], mat_armusers):
    wrd = bpy.data.worlds['Arm']
    rpdat = arm.utils.get_rp()

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
    elif not wrd.arm_batch_materials or material.name.startswith('armdefault'):
        rpasses, shader_data, shader_data_name, bind_constants, bind_textures = make_shader.build(material, mat_users, mat_armusers)
        sd = shader_data.sd
    else:
        rpasses, shader_data, shader_data_name, bind_constants, bind_textures = mat_batch.get(material)
        sd = shader_data.sd

    # Material
    for rp in rpasses:
        c = {
            'name': rp,
            'bind_constants': [] + bind_constants[rp],
            'bind_textures': [] + bind_textures[rp],
        }
        mat_data['contexts'].append(c)

        if rp == 'mesh':
            c['bind_constants'].append({'name': 'receiveShadow', 'bool': material.arm_receive_shadow})

            if material.arm_material_id != 0:
                c['bind_constants'].append({'name': 'materialID', 'int': material.arm_material_id})

                if material.arm_material_id == 2:
                    wrd.world_defs += '_Hair'

            elif rpdat.rp_sss_state == 'On':
                sss = False
                sss_node = arm.node_utils.get_node_by_type(material.node_tree, 'SUBSURFACE_SCATTERING')
                if sss_node is not None and sss_node.outputs[0].is_linked: # Check linked node
                    sss = True
                sss_node = arm.node_utils.get_node_by_type(material.node_tree, 'BSDF_PRINCIPLED')
                if sss_node is not None and sss_node.outputs[0].is_linked and (sss_node.inputs[1].is_linked or sss_node.inputs[1].default_value != 0.0):
                    sss = True
                sss_node = arm.node_utils.get_node_armorypbr(material.node_tree)
                if sss_node is not None and sss_node.outputs[0].is_linked and (sss_node.inputs[8].is_linked or sss_node.inputs[8].default_value != 0.0):
                    sss = True

                const = {'name': 'materialID'}
                if sss:
                    const['int'] = 2
                else:
                    const['int'] = 0
                c['bind_constants'].append(const)

            # TODO: Mesh only material batching
            if wrd.arm_batch_materials:
                # Set textures uniforms
                if len(c['bind_textures']) > 0:
                    c['bind_textures'] = []
                    for node in material.node_tree.nodes:
                        if node.type == 'TEX_IMAGE':
                            tex_name = arm.utils.safesrc(node.name)
                            tex = cycles.make_texture(node, tex_name)
                            # Empty texture
                            if tex is None:
                                tex = {'name': tex_name, 'file': ''}
                            c['bind_textures'].append(tex)

                # Set marked inputs as uniforms
                for node in material.node_tree.nodes:
                    for inp in node.inputs:
                        if inp.is_uniform:
                            uname = arm.utils.safesrc(inp.node.name) + arm.utils.safesrc(inp.name)  # Merge with cycles module
                            c['bind_constants'].append({'name': uname, cycles.glsl_type(inp.type): glsl_value(inp.default_value)})

        elif rp == 'translucent':
            c['bind_constants'].append({'name': 'receiveShadow', 'bool': material.arm_receive_shadow})

    if wrd.arm_single_data_file:
        mat_data['shader'] = shader_data_name
    else:
        ext = '' if wrd.arm_minimize else '.json'
        mat_data['shader'] = shader_data_name + ext + '/' + shader_data_name

    return sd, rpasses
