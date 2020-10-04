import bpy

import arm.material.cycles as cycles
import arm.material.cycles_functions as c_functions
from arm.material.shader import vec3str


def parse_brightcontrast(node: bpy.types.ShaderNodeBrightContrast, out_socket: bpy.types.NodeSocket) -> vec3str:
    out_col = cycles.parse_vector_input(node.inputs[0])
    bright = cycles.parse_value_input(node.inputs[1])
    contr = cycles.parse_value_input(node.inputs[2])

    cycles.curshader.add_function(c_functions.str_brightcontrast)

    return 'brightcontrast({0}, {1}, {2})'.format(out_col, bright, contr)


def parse_gamma(node: bpy.types.ShaderNodeGamma, out_socket: bpy.types.NodeSocket) -> vec3str:
    out_col = cycles.parse_vector_input(node.inputs[0])
    gamma = cycles.parse_value_input(node.inputs[1])

    return 'pow({0}, vec3({1}))'.format(out_col, gamma)


def parse_huesat(node: bpy.types.ShaderNodeHueSaturation, out_socket: bpy.types.NodeSocket) -> vec3str:
    cycles.curshader.add_function(c_functions.str_hue_sat)
    hue = cycles.parse_value_input(node.inputs[0])
    sat = cycles.parse_value_input(node.inputs[1])
    val = cycles.parse_value_input(node.inputs[2])
    fac = cycles.parse_value_input(node.inputs[3])
    col = cycles.parse_vector_input(node.inputs[4])

    return f'hue_sat({col}, vec4({hue}-0.5, {sat}, {val}, 1.0-{fac}))'


def parse_invert(node: bpy.types.ShaderNodeInvert, out_socket: bpy.types.NodeSocket) -> vec3str:
    fac = cycles.parse_value_input(node.inputs[0])
    out_col = cycles.parse_vector_input(node.inputs[1])

    return f'mix({out_col}, vec3(1.0) - ({out_col}), {fac})'


def parse_mixrgb(node: bpy.types.ShaderNodeMixRGB, out_socket: bpy.types.NodeSocket) -> vec3str:
    fac = cycles.parse_value_input(node.inputs[0])
    fac_var = cycles.node_name(node.name) + '_fac'
    cycles.curshader.write('float {0} = {1};'.format(fac_var, fac))
    col1 = cycles.parse_vector_input(node.inputs[1])
    col2 = cycles.parse_vector_input(node.inputs[2])
    blend = node.blend_type
    if blend == 'MIX':
        out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac_var)
    elif blend == 'ADD':
        out_col = 'mix({0}, {0} + {1}, {2})'.format(col1, col2, fac_var)
    elif blend == 'MULTIPLY':
        out_col = 'mix({0}, {0} * {1}, {2})'.format(col1, col2, fac_var)
    elif blend == 'SUBTRACT':
        out_col = 'mix({0}, {0} - {1}, {2})'.format(col1, col2, fac_var)
    elif blend == 'SCREEN':
        out_col = '(vec3(1.0) - (vec3(1.0 - {2}) + {2} * (vec3(1.0) - {1})) * (vec3(1.0) - {0}))'.format(col1, col2, fac_var)
    elif blend == 'DIVIDE':
        out_col = '(vec3((1.0 - {2}) * {0} + {2} * {0} / {1}))'.format(col1, col2, fac_var)
    elif blend == 'DIFFERENCE':
        out_col = 'mix({0}, abs({0} - {1}), {2})'.format(col1, col2, fac_var)
    elif blend == 'DARKEN':
        out_col = 'min({0}, {1} * {2})'.format(col1, col2, fac_var)
    elif blend == 'LIGHTEN':
        out_col = 'max({0}, {1} * {2})'.format(col1, col2, fac_var)
    elif blend == 'OVERLAY':
        out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac_var) # Revert to mix
    elif blend == 'DODGE':
        out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac_var) # Revert to mix
    elif blend == 'BURN':
        out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac_var) # Revert to mix
    elif blend == 'HUE':
        out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac_var) # Revert to mix
    elif blend == 'SATURATION':
        out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac_var) # Revert to mix
    elif blend == 'VALUE':
        out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac_var) # Revert to mix
    elif blend == 'COLOR':
        out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac_var) # Revert to mix
    elif blend == 'SOFT_LIGHT':
        out_col = '((1.0 - {2}) * {0} + {2} * ((vec3(1.0) - {0}) * {1} * {0} + {0} * (vec3(1.0) - (vec3(1.0) - {1}) * (vec3(1.0) - {0}))));'.format(col1, col2, fac)
    elif blend == 'LINEAR_LIGHT':
        out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac_var) # Revert to mix
        # out_col = '({0} + {2} * (2.0 * ({1} - vec3(0.5))))'.format(col1, col2, fac_var)
    if node.use_clamp:
        return 'clamp({0}, vec3(0.0), vec3(1.0))'.format(out_col)
    return out_col


def parse_curvergb(node: bpy.types.ShaderNodeRGBCurve, out_socket: bpy.types.NodeSocket) -> vec3str:
    fac = cycles.parse_value_input(node.inputs[0])
    vec = cycles.parse_vector_input(node.inputs[1])
    curves = node.mapping.curves
    name = cycles.node_name(node.name)
    # mapping.curves[0].points[0].handle_type
    return '(sqrt(vec3({0}, {1}, {2}) * vec3({4}, {5}, {6})) * {3})'.format(
        cycles.vector_curve(name + '0', vec + '.x', curves[0].points), cycles.vector_curve(name + '1', vec + '.y', curves[1].points), cycles.vector_curve(name + '2', vec + '.z', curves[2].points), fac,
        cycles.vector_curve(name + '3a', vec + '.x', curves[3].points), cycles.vector_curve(name + '3b', vec + '.y', curves[3].points), cycles.vector_curve(name + '3c', vec + '.z', curves[3].points))
