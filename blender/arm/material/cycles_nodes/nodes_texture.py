import os
from typing import Union

import bpy

import arm.assets as assets
import arm.make_world as make_world
import arm.material.cycles_functions as c_functions
import arm.material.cycles as c
from arm.material.parser_state import ParserState
from arm.material.shader import floatstr, vec3str
import arm.utils
import arm.write_probes as write_probes


def parse_tex_brick(node: bpy.types.ShaderNodeTexBrick, out_socket: bpy.types.NodeSocket, state: ParserState) -> Union[floatstr, vec3str]:
    state.curshader.add_function(c_functions.str_tex_brick)

    if node.inputs[0].is_linked:
        co = c.parse_vector_input(node.inputs[0])
    else:
        co = 'bposition'

    # Color
    if out_socket == node.sockets[0]:
        col1 = c.parse_vector_input(node.inputs[1])
        col2 = c.parse_vector_input(node.inputs[2])
        col3 = c.parse_vector_input(node.inputs[3])
        scale = c.parse_value_input(node.inputs[4])
        res = f'tex_brick({co} * {scale}, {col1}, {col2}, {col3})'
    # Fac
    else:
        scale = c.parse_value_input(node.inputs[4])
        res = 'tex_brick_f({0} * {1})'.format(co, scale)

    if state.sample_bump:
        c.write_bump(node, res)

    return res


def parse_tex_checker(node: bpy.types.ShaderNodeTexChecker, out_socket: bpy.types.NodeSocket, state: ParserState) -> Union[floatstr, vec3str]:
    state.curshader.add_function(c_functions.str_tex_checker)

    if node.inputs[0].is_linked:
        co = c.parse_vector_input(node.inputs[0])
    else:
        co = 'bposition'

    # Color
    if out_socket == node.sockets[0]:
        col1 = c.parse_vector_input(node.inputs[1])
        col2 = c.parse_vector_input(node.inputs[2])
        scale = c.parse_value_input(node.inputs[3])
        res = f'tex_checker({co}, {col1}, {col2}, {scale})'
    # Fac
    else:
        scale = c.parse_value_input(node.inputs[3])
        res = 'tex_checker_f({0}, {1})'.format(co, scale)

    if state.sample_bump:
        c.write_bump(node, res)

    return res


def parse_tex_environment(node: bpy.types.ShaderNodeTexEnvironment, out_socket: bpy.types.NodeSocket, state: ParserState) -> vec3str:
    # Pass through
    return c.to_vec3([0.0, 0.0, 0.0])


def parse_tex_gradient(node: bpy.types.ShaderNodeTexGradient, out_socket: bpy.types.NodeSocket, state: ParserState) -> Union[floatstr, vec3str]:
    if node.inputs[0].is_linked:
        co = c.parse_vector_input(node.inputs[0])
    else:
        co = 'bposition'

    grad = node.gradient_type
    if grad == 'LINEAR':
        f = f'{co}.x'
    elif grad == 'QUADRATIC':
        f = '0.0'
    elif grad == 'EASING':
        f = '0.0'
    elif grad == 'DIAGONAL':
        f = f'({co}.x + {co}.y) * 0.5'
    elif grad == 'RADIAL':
        f = f'atan({co}.y, {co}.x) / PI2 + 0.5'
    elif grad == 'QUADRATIC_SPHERE':
        f = '0.0'
    else:  # SPHERICAL
        f = f'max(1.0 - sqrt({co}.x * {co}.x + {co}.y * {co}.y + {co}.z * {co}.z), 0.0)'

    # Color
    if out_socket == node.outputs[0]:
        res = f'vec3(clamp({f}, 0.0, 1.0))'
    # Fac
    else:
        res = f'(clamp({f}, 0.0, 1.0))'

    if state.sample_bump:
        c.write_bump(node, res)

    return res


def parse_tex_image(node: bpy.types.ShaderNodeTexImage, out_socket: bpy.types.NodeSocket, state: ParserState) -> Union[floatstr, vec3str]:
    # Color or Alpha output
    use_color_out = out_socket == node.outputs[0]

    # Already fetched
    if c.is_parsed(c.store_var_name(node)):
        if use_color_out:
            return f'{c.store_var_name(node)}.rgb'
        else:
            return f'{c.store_var_name(node)}.a'

    tex_name = c.node_name(node.name)
    tex = c.make_texture(node, tex_name)
    tex_link = node.name if node.arm_material_param else None

    if tex is not None:
        state.curshader.write_textures += 1
        if use_color_out:
            to_linear = node.image is not None and node.image.colorspace_settings.name == 'sRGB'
            res = f'{c.texture_store(node, tex, tex_name, to_linear, tex_link=tex_link)}.rgb'
        else:
            res = f'{c.texture_store(node, tex, tex_name, tex_link=tex_link)}.a'
        state.curshader.write_textures -= 1
        return res

    # Empty texture
    elif node.image is None:
        tex = {
            'name': tex_name,
            'file': ''
        }
        if use_color_out:
            return '{0}.rgb'.format(c.texture_store(node, tex, tex_name, to_linear=False, tex_link=tex_link))
        return '{0}.a'.format(c.texture_store(node, tex, tex_name, to_linear=True, tex_link=tex_link))

    # Pink color for missing texture
    else:
        tex_store = c.store_var_name(node)

        if use_color_out:
            state.parsed[tex_store] = True
            state.curshader.write_textures += 1
            state.curshader.write(f'vec4 {tex_store} = vec4(1.0, 0.0, 1.0, 1.0);')
            state.curshader.write_textures -= 1
            return f'{tex_store}.rgb'
        else:
            state.curshader.write(f'vec4 {tex_store} = vec4(1.0, 0.0, 1.0, 1.0);')
            return f'{tex_store}.a'


def parse_tex_magic(node: bpy.types.ShaderNodeTexMagic, out_socket: bpy.types.NodeSocket, state: ParserState) -> Union[floatstr, vec3str]:
    state.curshader.add_function(c_functions.str_tex_magic)

    if node.inputs[0].is_linked:
        co = c.parse_vector_input(node.inputs[0])
    else:
        co = 'bposition'

    scale = c.parse_value_input(node.inputs[1])

    # Color
    if out_socket == node.outputs[0]:
        res = f'tex_magic({co} * {scale} * 4.0)'
    # Fac
    else:
        res = f'tex_magic_f({co} * {scale} * 4.0)'

    if state.sample_bump:
        c.write_bump(node, res, 0.1)

    return res


def parse_tex_musgrave(node: bpy.types.ShaderNodeTexMusgrave, out_socket: bpy.types.NodeSocket, state: ParserState) -> Union[floatstr, vec3str]:
    state.curshader.add_function(c_functions.str_tex_musgrave)

    if node.inputs[0].is_linked:
        co = c.parse_vector_input(node.inputs[0])
    else:
        co = 'bposition'

    scale = c.parse_value_input(node.inputs[1])
    # detail = c.parse_value_input(node.inputs[2])
    # distortion = c.parse_value_input(node.inputs[3])

    # Color
    if out_socket == node.outputs[0]:
        res = f'vec3(tex_musgrave_f({co} * {scale} * 0.5))'
    # Fac
    else:
        res = 'tex_musgrave_f({0} * {1} * 0.5)'.format(co, scale)

    if state.sample_bump:
        c.write_bump(node, res)

    return res


def parse_tex_noise(node: bpy.types.ShaderNodeTexNoise, out_socket: bpy.types.NodeSocket, state: ParserState) -> Union[floatstr, vec3str]:
    c.write_procedurals()
    state.curshader.add_function(c_functions.str_tex_noise)
    c.assets_add(os.path.join(c.get_sdk_path(), 'armory', 'Assets', 'noise256.png'))
    c.assets_add_embedded_data('noise256.png')
    state.curshader.add_uniform('sampler2D snoise256', link='$noise256.png')

    if node.inputs[0].is_linked:
        co = c.parse_vector_input(node.inputs[0])
    else:
        co = 'bposition'

    scale = c.parse_value_input(node.inputs[2])
    detail = c.parse_value_input(node.inputs[3])
    distortion = c.parse_value_input(node.inputs[4])#

    # Color
    if out_socket == node.outputs[0]:
        res = 'vec3(tex_noise({0} * {1},{2},{3}), tex_noise({0} * {1} + 120.0,{2},{3}), tex_noise({0} * {1} + 168.0,{2},{3}))'.format(co, scale, detail, distortion)
    # Fac
    else:
        res = 'tex_noise({0} * {1},{2},{3})'.format(co, scale, detail, distortion)

    if state.sample_bump:
        c.write_bump(node, res, 0.1)

    return res


def parse_tex_pointdensity(node: bpy.types.ShaderNodeTexPointDensity, out_socket: bpy.types.NodeSocket, state: ParserState) -> Union[floatstr, vec3str]:
    # Pass through

    # Color
    if out_socket == node.outputs[0]:
        return c.to_vec3([0.0, 0.0, 0.0])
    # Density
    else:
        return '0.0'


def parse_tex_sky(node: bpy.types.ShaderNodeTexSky, out_socket: bpy.types.NodeSocket, state: ParserState) -> vec3str:
    # Pass through
    return c.to_vec3([0.0, 0.0, 0.0])


def parse_tex_voronoi(node: bpy.types.ShaderNodeTexVoronoi, out_socket: bpy.types.NodeSocket, state: ParserState) -> Union[floatstr, vec3str]:
    outp = 0
    if out_socket.type == 'RGBA':
        outp = 1
    elif out_socket.type == 'VECTOR':
        outp = 2
    m = 0
    if node.distance == 'MANHATTAN':
        m = 1
    elif node.distance == 'CHEBYCHEV':
        m = 2
    elif node.distance == 'MINKOWSKI':
        m = 3

    c.write_procedurals()
    state.curshader.add_function(c_functions.str_tex_voronoi)

    if node.inputs[0].is_linked:
        co = c.parse_vector_input(node.inputs[0])
    else:
        co = 'bposition'

    scale = c.parse_value_input(node.inputs[2])
    exp = c.parse_value_input(node.inputs[4])
    randomness = c.parse_value_input(node.inputs[5])

    # Color or Position
    if out_socket == node.outputs[1] or out_socket == node.outputs[2]:
        res = 'tex_voronoi({0}, {1}, {2}, {3}, {4}, {5})'.format(co, randomness, m, outp, scale, exp)
    # Distance
    else:
        res = 'tex_voronoi({0}, {1}, {2}, {3}, {4}, {5}).x'.format(co, randomness, m, outp, scale, exp)

    if state.sample_bump:
        c.write_bump(node, res)

    return res


def parse_tex_wave(node: bpy.types.ShaderNodeTexWave, out_socket: bpy.types.NodeSocket, state: ParserState) -> Union[floatstr, vec3str]:
    c.write_procedurals()
    state.curshader.add_function(c_functions.str_tex_wave)
    if node.inputs[0].is_linked:
        co = c.parse_vector_input(node.inputs[0])
    else:
        co = 'bposition'
    scale = c.parse_value_input(node.inputs[1])
    distortion = c.parse_value_input(node.inputs[2])
    detail = c.parse_value_input(node.inputs[3])
    detail_scale = c.parse_value_input(node.inputs[4])
    if node.wave_profile == 'SIN':
        wave_profile = 0
    else:
        wave_profile = 1
    if node.wave_type == 'BANDS':
        wave_type = 0
    else:
        wave_type = 1

    # Color
    if out_socket == node.outputs[0]:
        res = 'vec3(tex_wave_f({0} * {1},{2},{3},{4},{5},{6}))'.format(co, scale, wave_type, wave_profile, distortion, detail, detail_scale)
    # Fac
    else:
        res = 'tex_wave_f({0} * {1},{2},{3},{4},{5},{6})'.format(co, scale, wave_type, wave_profile, distortion, detail, detail_scale)

    if state.sample_bump:
        c.write_bump(node, res)

    return res
