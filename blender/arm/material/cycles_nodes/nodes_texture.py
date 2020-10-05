import os
from typing import Union

import bpy

import arm.assets as assets
import arm.make_world as make_world
import arm.material.cycles as cycles
import arm.material.cycles_functions as c_functions
from arm.material.shader import floatstr, vec3str
import arm.utils
import arm.write_probes as write_probes


def parse_tex_brick(node: bpy.types.ShaderNodeTexBrick, out_socket: bpy.types.NodeSocket) -> Union[floatstr, vec3str]:
    cycles.curshader.add_function(c_functions.str_tex_brick)

    if node.inputs[0].is_linked:
        co = cycles.parse_vector_input(node.inputs[0])
    else:
        co = 'bposition'

    # Color
    if out_socket == node.sockets[0]:
        col1 = cycles.parse_vector_input(node.inputs[1])
        col2 = cycles.parse_vector_input(node.inputs[2])
        col3 = cycles.parse_vector_input(node.inputs[3])
        scale = cycles.parse_value_input(node.inputs[4])
        res = f'tex_brick({co} * {scale}, {col1}, {col2}, {col3})'
    # Fac
    else:
        scale = cycles.parse_value_input(node.inputs[4])
        res = 'tex_brick_f({0} * {1})'.format(co, scale)

    if cycles.sample_bump:
        cycles.write_bump(node, res)

    return res


def parse_tex_checker(node: bpy.types.ShaderNodeTexChecker, out_socket: bpy.types.NodeSocket) -> Union[floatstr, vec3str]:
    cycles.curshader.add_function(c_functions.str_tex_checker)

    if node.inputs[0].is_linked:
        co = cycles.parse_vector_input(node.inputs[0])
    else:
        co = 'bposition'

    # Color
    if out_socket == node.sockets[0]:
        col1 = cycles.parse_vector_input(node.inputs[1])
        col2 = cycles.parse_vector_input(node.inputs[2])
        scale = cycles.parse_value_input(node.inputs[3])
        res = f'tex_checker({co}, {col1}, {col2}, {scale})'
    # Fac
    else:
        scale = cycles.parse_value_input(node.inputs[3])
        res = 'tex_checker_f({0}, {1})'.format(co, scale)

    if cycles.sample_bump:
        cycles.write_bump(node, res)

    return res


def parse_tex_environment(node: bpy.types.ShaderNodeTexEnvironment, out_socket: bpy.types.NodeSocket) -> vec3str:
    # Pass through
    return cycles.to_vec3([0.0, 0.0, 0.0])


def parse_tex_gradient(node: bpy.types.ShaderNodeTexGradient, out_socket: bpy.types.NodeSocket) -> Union[floatstr, vec3str]:
    if node.inputs[0].is_linked:
        co = cycles.parse_vector_input(node.inputs[0])
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

    if cycles.sample_bump:
        cycles.write_bump(node, res)

    return res


def parse_tex_image(node: bpy.types.ShaderNodeTexImage, out_socket: bpy.types.NodeSocket) -> Union[floatstr, vec3str]:
    # Color or Alpha output
    use_color_out = out_socket == node.outputs[0]

    # Already fetched
    if cycles.is_parsed(cycles.store_var_name(node)):
        if use_color_out:
            return f'{cycles.store_var_name(node)}.rgb'
        else:
            return f'{cycles.store_var_name(node)}.a'

    tex_name = cycles.node_name(node.name)
    tex = cycles.make_texture(node, tex_name)
    tex_link = node.name if node.arm_material_param else None

    if tex is not None:
        cycles.curshader.write_textures += 1
        if use_color_out:
            to_linear = node.image is not None and node.image.colorspace_settings.name == 'sRGB'
            res = f'{cycles.texture_store(node, tex, tex_name, to_linear, tex_link=tex_link)}.rgb'
        else:
            res = f'{cycles.texture_store(node, tex, tex_name, tex_link=tex_link)}.a'
        cycles.curshader.write_textures -= 1
        return res

    # Empty texture
    elif node.image is None:
        tex = {
            'name': tex_name,
            'file': ''
        }
        if use_color_out:
            return '{0}.rgb'.format(cycles.texture_store(node, tex, tex_name, to_linear=False, tex_link=tex_link))
        return '{0}.a'.format(cycles.texture_store(node, tex, tex_name, to_linear=True, tex_link=tex_link))

    # Pink color for missing texture
    else:
        tex_store = cycles.store_var_name(node)

        if use_color_out:
            cycles.parsed[tex_store] = True
            cycles.curshader.write_textures += 1
            cycles.curshader.write(f'vec4 {tex_store} = vec4(1.0, 0.0, 1.0, 1.0);')
            cycles.curshader.write_textures -= 1
            return f'{tex_store}.rgb'
        else:
            cycles.curshader.write(f'vec4 {tex_store} = vec4(1.0, 0.0, 1.0, 1.0);')
            return f'{tex_store}.a'


def parse_tex_magic(node: bpy.types.ShaderNodeTexMagic, out_socket: bpy.types.NodeSocket) -> Union[floatstr, vec3str]:
    cycles.curshader.add_function(c_functions.str_tex_magic)

    if node.inputs[0].is_linked:
        co = cycles.parse_vector_input(node.inputs[0])
    else:
        co = 'bposition'

    scale = cycles.parse_value_input(node.inputs[1])

    # Color
    if out_socket == node.outputs[0]:
        res = f'tex_magic({co} * {scale} * 4.0)'
    # Fac
    else:
        res = f'tex_magic_f({co} * {scale} * 4.0)'

    if cycles.sample_bump:
        cycles.write_bump(node, res, 0.1)

    return res


def parse_tex_musgrave(node: bpy.types.ShaderNodeTexMusgrave, out_socket: bpy.types.NodeSocket) -> Union[floatstr, vec3str]:
    cycles.curshader.add_function(c_functions.str_tex_musgrave)

    if node.inputs[0].is_linked:
        co = cycles.parse_vector_input(node.inputs[0])
    else:
        co = 'bposition'

    scale = cycles.parse_value_input(node.inputs[1])
    # detail = cycles.parse_value_input(node.inputs[2])
    # distortion = cycles.parse_value_input(node.inputs[3])

    # Color
    if out_socket == node.outputs[0]:
        res = f'vec3(tex_musgrave_f({co} * {scale} * 0.5))'
    # Fac
    else:
        res = 'tex_musgrave_f({0} * {1} * 0.5)'.format(co, scale)

    if cycles.sample_bump:
        cycles.write_bump(node, res)

    return res


def parse_tex_noise(node: bpy.types.ShaderNodeTexNoise, out_socket: bpy.types.NodeSocket) -> Union[floatstr, vec3str]:
    cycles.write_procedurals()
    cycles.curshader.add_function(c_functions.str_tex_noise)
    cycles.assets_add(os.path.join(cycles.get_sdk_path(), 'armory', 'Assets', 'noise256.png'))
    cycles.assets_add_embedded_data('noise256.png')
    cycles.curshader.add_uniform('sampler2D snoise256', link='$noise256.png')

    if node.inputs[0].is_linked:
        co = cycles.parse_vector_input(node.inputs[0])
    else:
        co = 'bposition'

    scale = cycles.parse_value_input(node.inputs[2])
    detail = cycles.parse_value_input(node.inputs[3])
    distortion = cycles.parse_value_input(node.inputs[4])#

    # Color
    if out_socket == node.outputs[0]:
        res = 'vec3(tex_noise({0} * {1},{2},{3}), tex_noise({0} * {1} + 120.0,{2},{3}), tex_noise({0} * {1} + 168.0,{2},{3}))'.format(co, scale, detail, distortion)
    # Fac
    else:
        res = 'tex_noise({0} * {1},{2},{3})'.format(co, scale, detail, distortion)

    if cycles.sample_bump:
        cycles.write_bump(node, res, 0.1)

    return res


def parse_tex_pointdensity(node: bpy.types.ShaderNodeTexPointDensity, out_socket: bpy.types.NodeSocket) -> Union[floatstr, vec3str]:
    # Pass through

    # Color
    if out_socket == node.outputs[0]:
        return cycles.to_vec3([0.0, 0.0, 0.0])
    # Density
    else:
        return '0.0'


def parse_tex_sky(node: bpy.types.ShaderNodeTexSky, out_socket: bpy.types.NodeSocket) -> vec3str:
    # Pass through
    return cycles.to_vec3([0.0, 0.0, 0.0])


def parse_tex_voronoi(node: bpy.types.ShaderNodeTexVoronoi, out_socket: bpy.types.NodeSocket) -> Union[floatstr, vec3str]:
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

    cycles.write_procedurals()
    cycles.curshader.add_function(c_functions.str_tex_voronoi)

    if node.inputs[0].is_linked:
        co = cycles.parse_vector_input(node.inputs[0])
    else:
        co = 'bposition'

    scale = cycles.parse_value_input(node.inputs[2])
    exp = cycles.parse_value_input(node.inputs[4])
    randomness = cycles.parse_value_input(node.inputs[5])

    # Color or Position
    if out_socket == node.outputs[1] or out_socket == node.outputs[2]:
        res = 'tex_voronoi({0}, {1}, {2}, {3}, {4}, {5})'.format(co, randomness, m, outp, scale, exp)
    # Distance
    else:
        res = 'tex_voronoi({0}, {1}, {2}, {3}, {4}, {5}).x'.format(co, randomness, m, outp, scale, exp)

    if cycles.sample_bump:
        cycles.write_bump(node, res)

    return res


def parse_tex_wave(node: bpy.types.ShaderNodeTexWave, out_socket: bpy.types.NodeSocket) -> Union[floatstr, vec3str]:
    cycles.write_procedurals()
    cycles.curshader.add_function(c_functions.str_tex_wave)
    if node.inputs[0].is_linked:
        co = cycles.parse_vector_input(node.inputs[0])
    else:
        co = 'bposition'
    scale = cycles.parse_value_input(node.inputs[1])
    distortion = cycles.parse_value_input(node.inputs[2])
    detail = cycles.parse_value_input(node.inputs[3])
    detail_scale = cycles.parse_value_input(node.inputs[4])
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

    if cycles.sample_bump:
        cycles.write_bump(node, res)

    return res
