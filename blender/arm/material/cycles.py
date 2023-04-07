#
# This module builds upon Cycles nodes work licensed as
# Copyright 2011-2013 Blender Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import shutil
from typing import Any, Callable, Dict, Optional, Tuple

import bpy

import arm.assets
import arm.log as log
import arm.make_state
import arm.material.cycles_functions as c_functions
from arm.material.cycles_nodes import *
import arm.material.mat_state as mat_state
from arm.material.parser_state import ParserState, ParserContext
from arm.material.shader import Shader, ShaderContext, floatstr, vec3str
import arm.utils

if arm.is_reload(__name__):
    arm.assets = arm.reload_module(arm.assets)
    log = arm.reload_module(log)
    arm.make_state = arm.reload_module(arm.make_state)
    c_functions = arm.reload_module(c_functions)
    arm.material.cycles_nodes = arm.reload_module(arm.material.cycles_nodes)
    from arm.material.cycles_nodes import *
    mat_state = arm.reload_module(mat_state)
    arm.material.parser_state = arm.reload_module(arm.material.parser_state)
    from arm.material.parser_state import ParserState, ParserContext
    arm.material.shader = arm.reload_module(arm.material.shader)
    from arm.material.shader import Shader, ShaderContext, floatstr, vec3str
    arm.utils = arm.reload_module(arm.utils)
else:
    arm.enable_reload(__name__)


# Particle info export
particle_info: Dict[str, bool] = {}

state: Optional[ParserState]


def parse(nodes, con: ShaderContext,
          vert: Shader, frag: Shader, geom: Shader, tesc: Shader, tese: Shader,
          parse_surface=True, parse_opacity=True, parse_displacement=True, basecol_only=False):
    global state

    state = ParserState(ParserContext.OBJECT, mat_state.material.name)

    state.parse_surface = parse_surface
    state.parse_opacity = parse_opacity
    state.parse_displacement = parse_displacement
    state.basecol_only = basecol_only

    state.con = con

    state.vert = vert
    state.frag = frag
    state.geom = geom
    state.tesc = tesc
    state.tese = tese

    output_node = node_by_type(nodes, 'OUTPUT_MATERIAL')
    if output_node is not None:
        custom_particle_node = node_by_name(nodes, 'ArmCustomParticleNode')
        parse_material_output(output_node, custom_particle_node)

    # Make sure that individual functions in this module aren't called with an incorrect/old parser state, set it to
    # None so that it will raise exceptions when not set
    state = None


def parse_material_output(node: bpy.types.Node, custom_particle_node: bpy.types.Node):
    global particle_info

    parse_surface = state.parse_surface
    parse_opacity = state.parse_opacity
    parse_displacement = state.parse_displacement
    particle_info = {
        'index': False,
        'age': False,
        'lifetime': False,
        'location': False,
        'size': False,
        'velocity': False,
        'angular_velocity': False
    }
    state.sample_bump = False
    state.sample_bump_res = ''
    wrd = bpy.data.worlds['Arm']

    mat_state.emission_type = mat_state.EmissionType.NO_EMISSION

    # Surface
    if parse_surface or parse_opacity:
        state.parents = []
        state.parsed = set()
        state.normal_parsed = False
        curshader = state.frag
        state.curshader = curshader

        out_basecol, out_roughness, out_metallic, out_occlusion, out_specular, out_opacity, out_rior, out_emission_col = parse_shader_input(node.inputs[0])
        if parse_surface:
            curshader.write(f'basecol = {out_basecol};')
            curshader.write(f'roughness = {out_roughness};')
            curshader.write(f'metallic = {out_metallic};')
            curshader.write(f'occlusion = {out_occlusion};')
            curshader.write(f'specular = {out_specular};')
            curshader.write(f'emissionCol = {out_emission_col};')

            if mat_state.emission_type == mat_state.EmissionType.SHADELESS:
                if '_EmissionShadeless' not in wrd.world_defs:
                    wrd.world_defs += '_EmissionShadeless'
            elif mat_state.emission_type == mat_state.EmissionType.SHADED:
                if '_EmissionShaded' not in wrd.world_defs:
                    wrd.world_defs += '_EmissionShaded'
                    arm.assets.add_khafile_def('rp_gbuffer_emission')

        if parse_opacity:
            curshader.write('opacity = {0};'.format(out_opacity))
            curshader.write('rior = {0};'.format(out_rior))

    # Volume
    # parse_volume_input(node.inputs[1])

    # Displacement
    if parse_displacement and disp_enabled() and node.inputs[2].is_linked:
        state.parents = []
        state.parsed = set()
        state.normal_parsed = False
        rpdat = arm.utils.get_rp()
        if rpdat.arm_rp_displacement == 'Tessellation' and state.tese is not None:
            state.curshader = state.tese
        else:
            state.curshader = state.vert
        out_disp = parse_displacement_input(node.inputs[2])
        state.curshader.write('vec3 disp = {0};'.format(out_disp))

    if custom_particle_node is not None:
        if not (parse_displacement and disp_enabled() and node.inputs[2].is_linked):
            state.parents = []
            state.parsed = set()
        state.normal_parsed = False

        state.curshader = state.vert
        custom_particle_node.parse(state.curshader, state.con)


def parse_group(node, socket): # Entering group
    index = socket_index(node, socket)
    output_node = node_by_type(node.node_tree.nodes, 'GROUP_OUTPUT')
    if output_node is None:
        return
    inp = output_node.inputs[index]
    state.parents.append(node)
    out_group = parse_input(inp)
    state.parents.pop()
    return out_group


def parse_group_input(node: bpy.types.Node, socket: bpy.types.NodeSocket):
    index = socket_index(node, socket)
    parent = state.parents.pop() # Leaving group
    inp = parent.inputs[index]
    res = parse_input(inp)
    state.parents.append(parent) # Return to group
    return res


def parse_input(inp: bpy.types.NodeSocket):
    if inp.type == 'SHADER':
        return parse_shader_input(inp)
    elif inp.type in ('RGB', 'RGBA', 'VECTOR'):
        return parse_vector_input(inp)
    elif inp.type == 'VALUE':
        return parse_value_input(inp)


def parse_shader_input(inp: bpy.types.NodeSocket) -> Tuple[str, ...]:
    # Follow input
    if inp.is_linked:
        link = inp.links[0]
        if link.from_node.type == 'REROUTE':
            return parse_shader_input(link.from_node.inputs[0])

        if link.from_socket.type != 'SHADER':
            log.warn(f'Node tree "{tree_name()}": socket "{link.from_socket.name}" of node "{link.from_node.name}" cannot be connected to a shader socket')
            state.reset_outs()
            return state.get_outs()

        return parse_shader(link.from_node, link.from_socket)

    else:
        # Return default shader values
        state.reset_outs()
        return state.get_outs()


def parse_shader(node: bpy.types.Node, socket: bpy.types.NodeSocket) -> Tuple[str, ...]:
    # Use switch-like lookup via dictionary
    # (better performance, better code readability)
    # 'NODE_TYPE': parser_function
    node_parser_funcs: Dict[str, Callable] = {
        'MIX_SHADER': nodes_shader.parse_mixshader,
        'ADD_SHADER': nodes_shader.parse_addshader,
        'BSDF_PRINCIPLED': nodes_shader.parse_bsdfprincipled,
        'BSDF_DIFFUSE': nodes_shader.parse_bsdfdiffuse,
        'BSDF_GLOSSY': nodes_shader.parse_bsdfglossy,
        'AMBIENT_OCCLUSION': nodes_shader.parse_ambientocclusion,
        'BSDF_ANISOTROPIC': nodes_shader.parse_bsdfanisotropic,
        'EMISSION': nodes_shader.parse_emission,
        'BSDF_GLASS': nodes_shader.parse_bsdfglass,
        'HOLDOUT': nodes_shader.parse_holdout,
        'SUBSURFACE_SCATTERING': nodes_shader.parse_subsurfacescattering,
        'BSDF_TRANSLUCENT': nodes_shader.parse_bsdftranslucent,
        'BSDF_TRANSPARENT': nodes_shader.parse_bsdftransparent,
        'BSDF_VELVET': nodes_shader.parse_bsdfvelvet,
    }

    state.reset_outs()

    if node.type in node_parser_funcs:
        node_parser_funcs[node.type](node, socket, state)

    elif node.type == 'GROUP':
        if node.node_tree.name.startswith('Armory PBR'):
            if state.parse_surface:
                # Normal
                if node.inputs[5].is_linked and node.inputs[5].links[0].from_node.type == 'NORMAL_MAP':
                    log.warn(tree_name() + ' - Do not use Normal Map node with Armory PBR, connect Image Texture directly')
                parse_normal_map_color_input(node.inputs[5])

                emission_factor = f'clamp({parse_value_input(node.inputs[6])}, 0.0, 1.0)'
                basecol = parse_vector_input(node.inputs[0])

                # Multiply base color with inverse of emission factor to
                # copy behaviour of the Mix Shader node used in the group
                # (less base color -> less shading influence)
                state.out_basecol = f'({basecol} * (1 - {emission_factor}))'

                state.out_occlusion = parse_value_input(node.inputs[2])
                state.out_roughness = parse_value_input(node.inputs[3])
                state.out_metallic = parse_value_input(node.inputs[4])

                # Emission
                if node.inputs[6].is_linked or node.inputs[6].default_value != 0.0:
                    state.out_emission_col = f'({basecol} * {emission_factor})'
                    mat_state.emission_type = mat_state.EmissionType.SHADED
            if state.parse_opacity:
                state.out_opacity = parse_value_input(node.inputs[1])
        else:
            return parse_group(node, socket)

    elif node.type == 'GROUP_INPUT':
        return parse_group_input(node, socket)

    elif node.type == 'CUSTOM':
        if node.bl_idname == 'ArmShaderDataNode':
            return node.parse(state.frag, state.vert)

    else:
        log.warn(f'Node tree "{tree_name()}": material node type {node.type} not supported')

    return state.get_outs()


def parse_displacement_input(inp):
    if inp.is_linked:
        l = inp.links[0]
        if l.from_node.type == 'REROUTE':
            return parse_displacement_input(l.from_node.inputs[0])
        return parse_vector_input(inp)
    else:
        return None


def parse_vector_input(inp: bpy.types.NodeSocket) -> vec3str:
    """Return the parsed result of the given input socket."""
    # Follow input
    if inp.is_linked:
        link = inp.links[0]
        if link.from_node.type == 'REROUTE':
            return parse_vector_input(link.from_node.inputs[0])
        res_var = write_result(link)
        st = link.from_socket.type
        if st in ('RGB', 'RGBA', 'VECTOR'):
            return res_var
        elif st in ('VALUE', 'INT'):
            return f'vec3({res_var})'
        else:
            log.warn(f'Node tree "{tree_name()}": socket "{link.from_socket.name}" of node "{link.from_node.name}" cannot be connected to a vector-like socket')
            return to_vec3([0.0, 0.0, 0.0])

    # Unlinked reroute
    elif inp.type == 'VALUE':
        return to_vec3([0.0, 0.0, 0.0])

    # Use direct socket value
    else:
        if mat_batch() and inp.is_uniform:
            return to_uniform(inp)
        else:
            return to_vec3(inp.default_value)


def parse_vector(node: bpy.types.Node, socket: bpy.types.NodeSocket) -> str:
    """Parses the vector/color output value from the given node and socket."""
    node_parser_funcs: Dict[str, Callable] = {
        'ATTRIBUTE': nodes_input.parse_attribute,

        # RGB outputs
        'RGB': nodes_input.parse_rgb,
        'TEX_BRICK': nodes_texture.parse_tex_brick,
        'TEX_CHECKER': nodes_texture.parse_tex_checker,
        'TEX_ENVIRONMENT': nodes_texture.parse_tex_environment,
        'TEX_GRADIENT': nodes_texture.parse_tex_gradient,
        'TEX_IMAGE': nodes_texture.parse_tex_image,
        'TEX_MAGIC': nodes_texture.parse_tex_magic,
        'TEX_MUSGRAVE': nodes_texture.parse_tex_musgrave,
        'TEX_NOISE': nodes_texture.parse_tex_noise,
        'TEX_POINTDENSITY': nodes_texture.parse_tex_pointdensity,
        'TEX_SKY': nodes_texture.parse_tex_sky,
        'TEX_VORONOI': nodes_texture.parse_tex_voronoi,
        'TEX_WAVE': nodes_texture.parse_tex_wave,
        'VERTEX_COLOR': nodes_input.parse_vertex_color,
        'BRIGHTCONTRAST': nodes_color.parse_brightcontrast,
        'GAMMA': nodes_color.parse_gamma,
        'HUE_SAT': nodes_color.parse_huesat,
        'INVERT': nodes_color.parse_invert,
        'MIX_RGB': nodes_color.parse_mixrgb,
        'BLACKBODY': nodes_converter.parse_blackbody,
        'VALTORGB': nodes_converter.parse_valtorgb,  # ColorRamp
        'CURVE_VEC': nodes_vector.parse_curvevec,  # Vector Curves
        'CURVE_RGB': nodes_color.parse_curvergb,
        'COMBINE_COLOR': nodes_converter.parse_combine_color,
        'COMBHSV': nodes_converter.parse_combhsv,
        'COMBRGB': nodes_converter.parse_combrgb,
        'WAVELENGTH': nodes_converter.parse_wavelength,

        # Vector outputs
        'CAMERA': nodes_input.parse_camera,
        'NEW_GEOMETRY': nodes_input.parse_geometry,
        'HAIR_INFO': nodes_input.parse_hairinfo,
        'OBJECT_INFO': nodes_input.parse_objectinfo,
        'PARTICLE_INFO': nodes_input.parse_particleinfo,
        'TANGENT': nodes_input.parse_tangent,
        'TEX_COORD': nodes_input.parse_texcoord,
        'UVMAP': nodes_input.parse_uvmap,
        'BUMP': nodes_vector.parse_bump,
        'MAPPING': nodes_vector.parse_mapping,
        'NORMAL': nodes_vector.parse_normal,
        'NORMAL_MAP': nodes_vector.parse_normalmap,
        'VECT_TRANSFORM': nodes_vector.parse_vectortransform,
        'COMBXYZ': nodes_converter.parse_combxyz,
        'VECT_MATH': nodes_converter.parse_vectormath,
        'DISPLACEMENT': nodes_vector.parse_displacement,
        'VECTOR_ROTATE': nodes_vector.parse_vectorrotate,
    }

    if node.type in node_parser_funcs:
        return node_parser_funcs[node.type](node, socket, state)

    elif node.type == 'GROUP':
        return parse_group(node, socket)

    elif node.type == 'GROUP_INPUT':
        return parse_group_input(node, socket)

    elif node.type == 'CUSTOM':
        if node.bl_idname == 'ArmShaderDataNode':
            return node.parse(state.frag, state.vert)

    log.warn(f'Node tree "{tree_name()}": material node type {node.type} not supported')
    return "vec3(0, 0, 0)"


def parse_normal_map_color_input(inp, strength_input=None):
    frag = state.frag

    if state.basecol_only or not inp.is_linked or state.normal_parsed:
        return

    state.normal_parsed = True
    frag.write_normal += 1
    if not get_arm_export_tangents() or mat_get_material().arm_decal: # Compute TBN matrix
        frag.write('vec3 texn = ({0}) * 2.0 - 1.0;'.format(parse_vector_input(inp)))
        frag.write('texn.y = -texn.y;')
        frag.add_include('std/normals.glsl')
        frag.write('mat3 TBN = cotangentFrame(n, -vVec, texCoord);')
        frag.write('n = TBN * normalize(texn);')
    else:
        frag.write('n = ({0}) * 2.0 - 1.0;'.format(parse_vector_input(inp)))
        if strength_input is not None:
            strength = parse_value_input(strength_input)
            if strength != '1.0':
                frag.write('n.xy *= {0};'.format(strength))
        frag.write('n = normalize(TBN * n);')
        state.con.add_elem('tang', 'short4norm')
    frag.write_normal -= 1


def parse_value_input(inp: bpy.types.NodeSocket) -> floatstr:
    # Follow input
    if inp.is_linked:
        link = inp.links[0]

        if link.from_node.type == 'REROUTE':
            return parse_value_input(link.from_node.inputs[0])

        res_var = write_result(link)
        socket_type = link.from_socket.type
        if socket_type in ('RGB', 'RGBA', 'VECTOR'):
            # RGB to BW
            return rgb_to_bw(res_var)
        elif socket_type in ('VALUE', 'INT'):
            return res_var
        else:
            log.warn(f'Node tree "{tree_name()}": socket "{link.from_socket.name}" of node "{link.from_node.name}" cannot be connected to a scalar value socket')
            return '0.0'

    # Use value from socket
    else:
        if mat_batch() and inp.is_uniform:
            return to_uniform(inp)
        else:
            return to_vec1(inp.default_value)


def parse_value(node, socket):
    node_parser_funcs: Dict[str, Callable] = {
        'ATTRIBUTE': nodes_input.parse_attribute,
        'CAMERA': nodes_input.parse_camera,
        'FRESNEL': nodes_input.parse_fresnel,
        'NEW_GEOMETRY': nodes_input.parse_geometry,
        'HAIR_INFO': nodes_input.parse_hairinfo,
        'LAYER_WEIGHT': nodes_input.parse_layerweight,
        'LIGHT_PATH': nodes_input.parse_lightpath,
        'OBJECT_INFO': nodes_input.parse_objectinfo,
        'PARTICLE_INFO': nodes_input.parse_particleinfo,
        'VALUE': nodes_input.parse_value,
        'WIREFRAME': nodes_input.parse_wireframe,
        'TEX_BRICK': nodes_texture.parse_tex_brick,
        'TEX_CHECKER': nodes_texture.parse_tex_checker,
        'TEX_GRADIENT': nodes_texture.parse_tex_gradient,
        'TEX_IMAGE': nodes_texture.parse_tex_image,
        'TEX_MAGIC': nodes_texture.parse_tex_magic,
        'TEX_MUSGRAVE': nodes_texture.parse_tex_musgrave,
        'TEX_NOISE': nodes_texture.parse_tex_noise,
        'TEX_POINTDENSITY': nodes_texture.parse_tex_pointdensity,
        'TEX_VORONOI': nodes_texture.parse_tex_voronoi,
        'TEX_WAVE': nodes_texture.parse_tex_wave,
        'LIGHT_FALLOFF': nodes_color.parse_lightfalloff,
        'NORMAL': nodes_vector.parse_normal,
        'CLAMP': nodes_converter.parse_clamp,
        'VALTORGB': nodes_converter.parse_valtorgb,
        'MATH': nodes_converter.parse_math,
        'RGBTOBW': nodes_converter.parse_rgbtobw,
        'SEPARATE_COLOR': nodes_converter.parse_separate_color,
        'SEPHSV': nodes_converter.parse_sephsv,
        'SEPRGB': nodes_converter.parse_seprgb,
        'SEPXYZ': nodes_converter.parse_sepxyz,
        'VECT_MATH': nodes_converter.parse_vectormath,
        'MAP_RANGE': nodes_converter.parse_maprange,
    }

    if node.type in node_parser_funcs:
        return node_parser_funcs[node.type](node, socket, state)

    elif node.type == 'GROUP':
        if node.node_tree.name.startswith('Armory PBR'):
            # Displacement
            if socket == node.outputs[1]:
                return parse_value_input(node.inputs[7])
            else:
                return None
        else:
            return parse_group(node, socket)

    elif node.type == 'GROUP_INPUT':
        return parse_group_input(node, socket)

    elif node.type == 'CUSTOM':
        if node.bl_idname == 'ArmShaderDataNode':
            return node.parse(state.frag, state.vert)

    log.warn(f'Node tree "{tree_name()}": material node type {node.type} not supported')
    return '0.0'


def vector_curve(name, fac, points):
    curshader = state.curshader

    # Write Ys array
    ys_var = name + '_ys'
    curshader.write('float {0}[{1}];'.format(ys_var, len(points))) # TODO: Make const
    for i in range(0, len(points)):
        curshader.write('{0}[{1}] = {2};'.format(ys_var, i, points[i].location[1]))
    # Get index
    fac_var = name + '_fac'
    curshader.write('float {0} = {1};'.format(fac_var, fac))
    index = '0'
    for i in range(1, len(points)):
        index += ' + ({0} > {1} ? 1 : 0)'.format(fac_var, points[i].location[0])
    # Write index
    index_var = name + '_i'
    curshader.write('int {0} = {1};'.format(index_var, index))
    # Linear
    # Write Xs array
    facs_var = name + '_xs'
    curshader.write('float {0}[{1}];'.format(facs_var, len(points))) # TODO: Make const
    for i in range(0, len(points)):
        curshader.write('{0}[{1}] = {2};'.format(facs_var, i, points[i].location[0]))
    # Map vector
    return 'mix({0}[{1}], {0}[{1} + 1], ({2} - {3}[{1}]) * (1.0 / ({3}[{1} + 1] - {3}[{1}]) ))'.format(ys_var, index_var, fac_var, facs_var)

def write_normal(inp):
    if inp.is_linked and inp.links[0].from_node.type != 'GROUP_INPUT':
        normal_res = parse_vector_input(inp)
        if normal_res != None:
            state.curshader.write('n = {0};'.format(normal_res))


def is_parsed(node_store_name: str):
    return node_store_name in state.parsed


def res_var_name(node: bpy.types.Node, socket: bpy.types.NodeSocket) -> str:
    """Return the name of the variable that stores the parsed result
    from the given node and socket."""
    return node_name(node.name) + '_' + safesrc(socket.name) + '_res'


def write_result(link: bpy.types.NodeLink) -> Optional[str]:
    """Write the parsed result of the given node link to the shader."""
    res_var = res_var_name(link.from_node, link.from_socket)

    # Unparsed node
    if not is_parsed(res_var):
        state.parsed.add(res_var)
        st = link.from_socket.type

        if st in ('RGB', 'RGBA', 'VECTOR'):
            res = parse_vector(link.from_node, link.from_socket)
            if res is None:
                log.error(f'{link.from_node.name} returned `None` while parsing!')
                return None
            state.curshader.write(f'vec3 {res_var} = {res};')

        elif st == 'VALUE':
            res = parse_value(link.from_node, link.from_socket)
            if res is None:
                log.error(f'{link.from_node.name} returned `None` while parsing!')
                return None
            if link.from_node.type == "VALUE" and not link.from_node.arm_material_param:
                state.curshader.add_const('float', res_var, res)
            else:
                state.curshader.write(f'float {res_var} = {res};')

    # Normal map already parsed, return
    elif link.from_node.type == 'NORMAL_MAP':
        return None

    return res_var


def write_procedurals():
    if state.curshader not in state.procedurals_written:
        state.curshader.add_function(c_functions.str_tex_proc)
        state.procedurals_written.add(state.curshader)


def glsl_type(socket_type: str):
    """Socket to glsl type."""
    if socket_type in ('RGB', 'RGBA', 'VECTOR'):
        return 'vec3'
    else:
        return 'float'

def to_uniform(inp: bpy.types.NodeSocket):
    uname = safesrc(inp.node.name) + safesrc(inp.name)
    state.curshader.add_uniform(glsl_type(inp.type) + ' ' + uname)
    return uname

def store_var_name(node: bpy.types.Node):
    return node_name(node.name) + '_store'

def texture_store(node, tex, tex_name, to_linear=False, tex_link=None, default_value=None, is_arm_mat_param=None):
    curshader = state.curshader

    tex_store = store_var_name(node)
    if is_parsed(tex_store):
        return tex_store
    state.parsed.add(tex_store)
    if is_arm_mat_param is None:
        mat_bind_texture(tex)
    state.con.add_elem('tex', 'short2norm')
    curshader.add_uniform('sampler2D {0}'.format(tex_name), link=tex_link, default_value=default_value, is_arm_mat_param=is_arm_mat_param)
    triplanar = node.projection == 'BOX'
    if node.inputs[0].is_linked:
        uv_name = parse_vector_input(node.inputs[0])
        if triplanar:
            uv_name = 'vec3({0}.x, 1.0 - {0}.y, {0}.z)'.format(uv_name)
        else:
            uv_name = 'vec2({0}.x, 1.0 - {0}.y)'.format(uv_name)
    else:
        uv_name = 'vec3(texCoord.xy, 0.0)' if triplanar else 'texCoord'
    if triplanar:
        if not curshader.has_include('std/mapping.glsl'):
            curshader.add_include('std/mapping.glsl')
        if state.normal_parsed:
            nor = 'TBN[2]'
        else:
            nor = 'n'
        curshader.write('vec4 {0} = vec4(triplanarMapping({1}, {2}, {3}), 0.0);'.format(tex_store, tex_name, nor, uv_name))
    else:
        if mat_state.texture_grad:
            curshader.write('vec4 {0} = textureGrad({1}, {2}.xy, g2.xy, g2.zw);'.format(tex_store, tex_name, uv_name))
        else:
            curshader.write('vec4 {0} = texture({1}, {2}.xy);'.format(tex_store, tex_name, uv_name))
    if state.sample_bump:
        state.sample_bump_res = tex_store
        curshader.write('float {0}_1 = textureOffset({1}, {2}.xy, ivec2(-2, 0)).r;'.format(tex_store, tex_name, uv_name))
        curshader.write('float {0}_2 = textureOffset({1}, {2}.xy, ivec2(2, 0)).r;'.format(tex_store, tex_name, uv_name))
        curshader.write('float {0}_3 = textureOffset({1}, {2}.xy, ivec2(0, -2)).r;'.format(tex_store, tex_name, uv_name))
        curshader.write('float {0}_4 = textureOffset({1}, {2}.xy, ivec2(0, 2)).r;'.format(tex_store, tex_name, uv_name))
        state.sample_bump = False
    if to_linear:
        curshader.write('{0}.rgb = pow({0}.rgb, vec3(2.2));'.format(tex_store))
    return tex_store


def write_bump(node: bpy.types.Node, out_socket: bpy.types.NodeSocket, res: str, scl=0.001):
    """Sample texture values around the current texture coordinate for bump mapping. The result of the sampling is
    stored in 4 variables named after state.sample_bump_res with _[0-3] appended."""
    state.sample_bump_res = store_var_name(node) + '_bump'

    # Testing.. get function parts..
    ar = res.split('(', 1)
    pre = ar[0] + '('
    if ',' in ar[1]:
        ar2 = ar[1].split(',', 1)
        co = ar2[0]
        post = ',' + ar2[1]
    else:
        co = ar[1][:-1]
        post = ')'

    coordinate_offsets = (
        f'vec3(-{scl}, 0.0, 0.0)',
        f'vec3({scl}, 0.0, {scl})',
        f'vec3(0.0, -{scl}, 0.0)',
        f'vec3(0.0, {scl}, -{scl})'
    )

    needs_conversion_bw = glsl_type(out_socket.type) == "vec3"
    curshader = state.curshader
    for i in range(1, 5):
        if needs_conversion_bw:
            vec_var = f'{state.sample_bump_res}_vec{i}'
            curshader.write(f'vec3 {vec_var} = {pre}{co} + {coordinate_offsets[i - 1]}{post};')
            curshader.write(f'float {state.sample_bump_res}_{i} = {rgb_to_bw(vec_var)};')
        else:
            curshader.write(f'float {state.sample_bump_res}_{i} = {pre}{co} + {coordinate_offsets[i - 1]}{post};')

    state.sample_bump = False


def to_vec1(v):
    return str(v)


def to_vec2(v):
    return f'vec2({v[0]}, {v[1]})'


def to_vec3(v):
    return f'vec3({v[0]}, {v[1]}, {v[2]})'


def cast_value(val: str, from_type: str, to_type: str) -> str:
    """Casts a value that is already parsed in a glsl string to another
    value in a string.

    vec2 types are not supported (not used in the node editor) and there
    is no cast towards int types. If casting from vec3 to vec4, the w
    coordinate/alpha channel is filled with a 1.

    If this function is called with invalid parameters, a TypeError is
    raised.
    """
    if from_type == to_type:
        return val

    if from_type in ('int', 'float'):
        if to_type in ('int', 'float'):
            return val
        elif to_type in ('vec2', 'vec3', 'vec4'):
            return f'{to_type}({val})'

    elif from_type == 'vec3':
        if to_type == 'float':
            return rgb_to_bw(val)
        elif to_type == 'vec4':
            return f'vec4({val}, 1.0)'

    elif from_type == 'vec4':
        if to_type == 'float':
            return rgb_to_bw(val)
        elif to_type == 'vec3':
            return f'{val}.xyz'

    raise TypeError("Invalid type cast in shader!")


def rgb_to_bw(res_var: vec3str) -> floatstr:
    # Blender uses the default OpenColorIO luma coefficients which
    # originally come from the Rec. 709 standard (see ITU-R BT.709-6 Item 3.3)
    return f'dot({res_var}, vec3(0.2126, 0.7152, 0.0722))'


def node_by_type(nodes, ntype: str) -> bpy.types.Node:
    for n in nodes:
        if n.type == ntype:
            return n

def node_by_name(nodes, name: str) -> bpy.types.Node:
    for n in nodes:
        if n.bl_idname == name:
            return n

def socket_index(node: bpy.types.Node, socket: bpy.types.NodeSocket) -> int:
    for i in range(0, len(node.outputs)):
        if node.outputs[i] == socket:
            return i


def node_name(s: str) -> str:
    """Return a unique and safe name for a node for shader code usage."""
    for p in state.parents:
        s = p.name + '_' + s
    if state.curshader.write_textures > 0:
        s += '_texread'
    s = safesrc(s)
    if '__' in s: # Consecutive _ are reserved
        s = s.replace('_', '_x')
    return s

##


def make_texture(
        image: bpy.types.Image, tex_name: str, matname: str,
        interpolation: str, extension: str,
) -> Optional[Dict[str, Any]]:
    """Creates a texture binding entry for the scene's export data
    ('bind_textures') for a given texture image.
    """
    tex = {'name': tex_name}

    if image is None:
        return None

    if matname is None:
        matname = mat_state.material.name

    # Get filepath
    filepath = image.filepath
    if filepath == '':
        if image.packed_file is not None:
            filepath = './' + image.name
            has_ext = filepath.endswith(('.jpg', '.png', '.hdr'))
            if not has_ext:
                # Raw bytes, write converted .jpg to /unpacked
                filepath += '.raw'

        elif image.source == "GENERATED":
            unpack_path = os.path.join(arm.utils.get_fp_build(), 'compiled', 'Assets', 'unpacked')
            if not os.path.exists(unpack_path):
                os.makedirs(unpack_path)

            filepath = os.path.join(unpack_path, image.name + ".jpg")
            arm.utils.convert_image(image, filepath, "JPEG")

        else:
            log.warn(matname + '/' + image.name + ' - invalid file path')
            return None
    else:
        filepath = arm.utils.to_absolute_path(filepath, image.library)

    # Reference image name
    texpath = arm.utils.asset_path(filepath)
    texfile = arm.utils.extract_filename(filepath)
    tex['file'] = arm.utils.safestr(texfile)
    s = tex['file'].rsplit('.', 1)

    if len(s) == 1:
        log.warn(matname + '/' + image.name + ' - file extension required for image name')
        return None

    ext = s[1].lower()
    do_convert = ext not in ('jpg', 'png', 'hdr', 'mp4') # Convert image
    if do_convert:
        new_ext = 'png' if (ext in ('tga', 'dds')) else 'jpg'
        tex['file'] = tex['file'].rsplit('.', 1)[0] + '.' + new_ext

    if image.packed_file is not None or not is_ascii(texfile):
        # Extract packed data / copy non-ascii texture
        unpack_path = os.path.join(arm.utils.get_fp_build(), 'compiled', 'Assets', 'unpacked')
        if not os.path.exists(unpack_path):
            os.makedirs(unpack_path)
        unpack_filepath = os.path.join(unpack_path, tex['file'])

        if do_convert:
            if not os.path.isfile(unpack_filepath):
                fmt = 'PNG' if new_ext == 'png' else 'JPEG'
                arm.utils.convert_image(image, unpack_filepath, file_format=fmt)
        else:

            # Write bytes if size is different or file does not exist yet
            if image.packed_file is not None:
                if not os.path.isfile(unpack_filepath) or os.path.getsize(unpack_filepath) != image.packed_file.size:
                    with open(unpack_filepath, 'wb') as f:
                        f.write(image.packed_file.data)
            # Copy non-ascii texture
            else:
                if not os.path.isfile(unpack_filepath) or os.path.getsize(unpack_filepath) != os.path.getsize(texpath):
                    shutil.copy(texpath, unpack_filepath)

        arm.assets.add(unpack_filepath)

    else:
        if not os.path.isfile(arm.utils.asset_path(filepath)):
            log.warn('Material ' + matname + '/' + image.name + ' - file not found(' + filepath + ')')
            return None

        if do_convert:
            unpack_path = os.path.join(arm.utils.get_fp_build(), 'compiled', 'Assets', 'unpacked')
            if not os.path.exists(unpack_path):
                os.makedirs(unpack_path)
            converted_path = os.path.join(unpack_path, tex['file'])
            # TODO: delete cache when file changes
            if not os.path.isfile(converted_path):
                fmt = 'PNG' if new_ext == 'png' else 'JPEG'
                arm.utils.convert_image(image, converted_path, file_format=fmt)
            arm.assets.add(converted_path)
        else:
            # Link image path to assets
            # TODO: Khamake converts .PNG to .jpg? Convert ext to lowercase on windows
            if arm.utils.get_os() == 'win':
                s = filepath.rsplit('.', 1)
                arm.assets.add(arm.utils.asset_path(s[0] + '.' + s[1].lower()))
            else:
                arm.assets.add(arm.utils.asset_path(filepath))

    # if image_format != 'RGBA32':
        # tex['format'] = image_format

    rpdat = arm.utils.get_rp()
    texfilter = rpdat.arm_texture_filter
    if texfilter == 'Anisotropic':
        interpolation = 'Smart'
    elif texfilter == 'Linear':
        interpolation = 'Linear'
    elif texfilter == 'Point':
        interpolation = 'Closest'

    if interpolation == 'Cubic': # Mipmap linear
        tex['mipmap_filter'] = 'linear'
        tex['generate_mipmaps'] = True
    elif interpolation == 'Smart': # Mipmap anisotropic
        tex['min_filter'] = 'anisotropic'
        tex['mipmap_filter'] = 'linear'
        tex['generate_mipmaps'] = True
    elif interpolation == 'Closest':
        tex['min_filter'] = 'point'
        tex['mag_filter'] = 'point'
    # else defaults to linear

    if extension != 'REPEAT': # Extend or clip
        tex['u_addressing'] = 'clamp'
        tex['v_addressing'] = 'clamp'

    if image.source == 'MOVIE':
        tex['source'] = 'movie'
        tex['min_filter'] = 'linear'
        tex['mag_filter'] = 'linear'
        tex['mipmap_filter'] = 'no'
        tex['generate_mipmaps'] = False

    return tex


def make_texture_from_image_node(image_node: bpy.types.ShaderNodeTexImage, tex_name: str, matname: str = None) -> Optional[Dict[str, Any]]:
    if matname is None:
        matname = mat_state.material.name

    return make_texture(image_node.image, tex_name, matname, image_node.interpolation, image_node.extension)


def is_pow(num):
    return ((num & (num - 1)) == 0) and num != 0

def is_ascii(s):
    return len(s) == len(s.encode())

##

def get_arm_export_tangents():
    return bpy.data.worlds['Arm'].arm_export_tangents

def safesrc(name):
    return arm.utils.safesrc(name)

def disp_enabled():
    return arm.utils.disp_enabled(arm.make_state.target)

def assets_add(path):
    arm.assets.add(path)

def assets_add_embedded_data(path):
    arm.assets.add_embedded_data(path)

def tree_name() -> str:
    return state.tree_name

def mat_batch():
    return mat_state.batch

def mat_bind_texture(tex):
    mat_state.bind_textures.append(tex)

def mat_get_material():
    return mat_state.material

def mat_get_material_users():
    return mat_state.mat_users
