import bpy

import arm
import arm.log as log
import arm.material.cycles as c
import arm.material.cycles_functions as c_functions
from arm.material.parser_state import ParserState
from arm.material.shader import floatstr, vec3str

if arm.is_reload(__name__):
    log = arm.reload_module(log)
    c = arm.reload_module(c)
    c_functions = arm.reload_module(c_functions)
    arm.material.parser_state = arm.reload_module(arm.material.parser_state)
    from arm.material.parser_state import ParserState
    arm.material.shader = arm.reload_module(arm.material.shader)
    from arm.material.shader import floatstr, vec3str
else:
    arm.enable_reload(__name__)


def parse_brightcontrast(node: bpy.types.ShaderNodeBrightContrast, out_socket: bpy.types.NodeSocket, state: ParserState) -> vec3str:
    out_col = c.parse_vector_input(node.inputs[0])
    bright = c.parse_value_input(node.inputs[1])
    contr = c.parse_value_input(node.inputs[2])

    state.curshader.add_function(c_functions.str_brightcontrast)

    return 'brightcontrast({0}, {1}, {2})'.format(out_col, bright, contr)


def parse_gamma(node: bpy.types.ShaderNodeGamma, out_socket: bpy.types.NodeSocket, state: ParserState) -> vec3str:
    out_col = c.parse_vector_input(node.inputs[0])
    gamma = c.parse_value_input(node.inputs[1])

    return 'pow({0}, vec3({1}))'.format(out_col, gamma)


def parse_huesat(node: bpy.types.ShaderNodeHueSaturation, out_socket: bpy.types.NodeSocket, state: ParserState) -> vec3str:
    state.curshader.add_function(c_functions.str_hue_sat)
    hue = c.parse_value_input(node.inputs[0])
    sat = c.parse_value_input(node.inputs[1])
    val = c.parse_value_input(node.inputs[2])
    fac = c.parse_value_input(node.inputs[3])
    col = c.parse_vector_input(node.inputs[4])

    return f'hue_sat({col}, vec4({hue}-0.5, {sat}, {val}, 1.0-{fac}))'


def parse_invert(node: bpy.types.ShaderNodeInvert, out_socket: bpy.types.NodeSocket, state: ParserState) -> vec3str:
    fac = c.parse_value_input(node.inputs[0])
    out_col = c.parse_vector_input(node.inputs[1])

    return f'mix({out_col}, vec3(1.0) - ({out_col}), {fac})'


def parse_mixrgb(node: bpy.types.ShaderNodeMixRGB, out_socket: bpy.types.NodeSocket, state: ParserState) -> vec3str:
    col1 = c.parse_vector_input(node.inputs[1])
    col2 = c.parse_vector_input(node.inputs[2])

    # Store factor in variable for linked factor input
    if node.inputs[0].is_linked:
        fac = c.node_name(node.name) + '_fac' + state.get_parser_pass_suffix()
        state.curshader.write('float {0} = {1};'.format(fac, c.parse_value_input(node.inputs[0])))
    else:
        fac = c.parse_value_input(node.inputs[0])

    # TODO: Do not mix if factor is constant 0.0 or 1.0?

    blend = node.blend_type
    if blend == 'MIX':
        out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac)
    elif blend == 'ADD':
        out_col = 'mix({0}, {0} + {1}, {2})'.format(col1, col2, fac)
    elif blend == 'MULTIPLY':
        out_col = 'mix({0}, {0} * {1}, {2})'.format(col1, col2, fac)
    elif blend == 'SUBTRACT':
        out_col = 'mix({0}, {0} - {1}, {2})'.format(col1, col2, fac)
    elif blend == 'SCREEN':
        out_col = '(vec3(1.0) - (vec3(1.0 - {2}) + {2} * (vec3(1.0) - {1})) * (vec3(1.0) - {0}))'.format(col1, col2, fac)
    elif blend == 'DIVIDE':
        out_col = '(vec3((1.0 - {2}) * {0} + {2} * {0} / {1}))'.format(col1, col2, fac)
    elif blend == 'DIFFERENCE':
        out_col = 'mix({0}, abs({0} - {1}), {2})'.format(col1, col2, fac)
    elif blend == 'DARKEN':
        out_col = 'min({0}, {1} * {2})'.format(col1, col2, fac)
    elif blend == 'LIGHTEN':
        out_col = 'max({0}, {1} * {2})'.format(col1, col2, fac)
    elif blend == 'OVERLAY':
        out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac) # Revert to mix
    elif blend == 'DODGE':
        out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac) # Revert to mix
    elif blend == 'BURN':
        out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac) # Revert to mix
    elif blend == 'HUE':
        out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac) # Revert to mix
    elif blend == 'SATURATION':
        out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac) # Revert to mix
    elif blend == 'VALUE':
        out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac) # Revert to mix
    elif blend == 'COLOR':
        out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac) # Revert to mix
    elif blend == 'SOFT_LIGHT':
        out_col = '((1.0 - {2}) * {0} + {2} * ((vec3(1.0) - {0}) * {1} * {0} + {0} * (vec3(1.0) - (vec3(1.0) - {1}) * (vec3(1.0) - {0}))))'.format(col1, col2, fac)
    elif blend == 'LINEAR_LIGHT':
        out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac) # Revert to mix
        # out_col = '({0} + {2} * (2.0 * ({1} - vec3(0.5))))'.format(col1, col2, fac_var)
    else:
        log.warn(f'MixRGB node: unsupported blend type {node.blend_type}.')
        return col1

    if node.use_clamp:
        return 'clamp({0}, vec3(0.0), vec3(1.0))'.format(out_col)
    return out_col


def parse_curvergb(node: bpy.types.ShaderNodeRGBCurve, out_socket: bpy.types.NodeSocket, state: ParserState) -> vec3str:
    fac = c.parse_value_input(node.inputs[0])
    vec = c.parse_vector_input(node.inputs[1])
    curves = node.mapping.curves
    name = c.node_name(node.name)
    # mapping.curves[0].points[0].handle_type
    return '(sqrt(vec3({0}, {1}, {2}) * vec3({4}, {5}, {6})) * {3})'.format(
        c.vector_curve(name + '0', vec + '.x', curves[0].points), c.vector_curve(name + '1', vec + '.y', curves[1].points), c.vector_curve(name + '2', vec + '.z', curves[2].points), fac,
        c.vector_curve(name + '3a', vec + '.x', curves[3].points), c.vector_curve(name + '3b', vec + '.y', curves[3].points), c.vector_curve(name + '3c', vec + '.z', curves[3].points))


def parse_lightfalloff(node: bpy.types.ShaderNodeLightFalloff, out_socket: bpy.types.NodeSocket, state: ParserState) -> floatstr:
    # https://github.com/blender/blender/blob/master/source/blender/gpu/shaders/material/gpu_shader_material_light_falloff.glsl
    return c.parse_value_input(node.inputs['Strength'])
