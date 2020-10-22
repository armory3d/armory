from typing import Union

import bpy

import arm.log as log
import arm.material.cycles as c
import arm.material.cycles_functions as c_functions
from arm.material.parser_state import ParserState
from arm.material.shader import floatstr, vec3str


def parse_blackbody(node: bpy.types.ShaderNodeBlackbody, out_socket: bpy.types.NodeSocket, state: ParserState) -> vec3str:
    t = float(c.parse_value_input(node.inputs[0]))

    rgb = [0, 0, 0]
    blackbody_table_r = [
        [2.52432244e+03, -1.06185848e-03, 3.11067539e+00],
        [3.37763626e+03, -4.34581697e-04, 1.64843306e+00],
        [4.10671449e+03, -8.61949938e-05, 6.41423749e-01],
        [4.66849800e+03, 2.85655028e-05, 1.29075375e-01],
        [4.60124770e+03, 2.89727618e-05, 1.48001316e-01],
        [3.78765709e+03, 9.36026367e-06, 3.98995841e-01]
    ]
    blackbody_table_g = [
        [-7.50343014e+02, 3.15679613e-04, 4.73464526e-01],
        [-1.00402363e+03, 1.29189794e-04, 9.08181524e-01],
        [-1.22075471e+03, 2.56245413e-05, 1.20753416e+00],
        [-1.42546105e+03, -4.01730887e-05, 1.44002695e+00],
        [-1.18134453e+03, -2.18913373e-05, 1.30656109e+00],
        [-5.00279505e+02, -4.59745390e-06, 1.09090465e+00]
    ]
    blackbody_table_b = [
        [0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0],
        [-2.02524603e-11, 1.79435860e-07, -2.60561875e-04, -1.41761141e-02],
        [-2.22463426e-13, -1.55078698e-08, 3.81675160e-04, -7.30646033e-01],
        [6.72595954e-13, -2.73059993e-08, 4.24068546e-04, -7.52204323e-01]
    ]

    if t >= 12000:
        rgb[0] = 0.826270103
        rgb[1] = 0.994478524
        rgb[2] = 1.56626022

    elif t < 965.0:
        rgb[0] = 4.70366907
        rgb[1] = 0.0
        rgb[2] = 0.0

    else:
        if t >= 6365.0:
            i = 5
        elif t >= 3315.0:
            i = 4
        elif t >= 1902.0:
            i = 3
        elif t >= 1449.0:
            i = 2
        elif t >= 1167.0:
            i = 1
        else:
            i = 0

        r = blackbody_table_r[i]
        g = blackbody_table_g[i]
        b = blackbody_table_b[i]

        t_inv = 1.0 / t

        rgb[0] = r[0] * t_inv + r[1] * t + r[2]
        rgb[1] = g[0] * t_inv + g[1] * t + g[2]
        rgb[2] = ((b[0] * t + b[1]) * t + b[2]) * t + b[3]

    # Pass constant
    return c.to_vec3([rgb[0], rgb[1], rgb[2]])


def parse_valtorgb(node: bpy.types.ShaderNodeValToRGB, out_socket: bpy.types.NodeSocket, state: ParserState) -> Union[floatstr, vec3str]:
    # Alpha (TODO: make ColorRamp calculation vec4-based and split afterwards)
    if out_socket == node.outputs[1]:
        return '1.0'

    input_fac: bpy.types.NodeSocket = node.inputs[0]

    fac: str = c.parse_value_input(input_fac) if input_fac.is_linked else c.to_vec1(input_fac.default_value)
    interp = node.color_ramp.interpolation
    elems = node.color_ramp.elements

    if len(elems) == 1:
        return c.to_vec3(elems[0].color)

    # Write color array
    # The last entry is included twice so that the interpolation
    # between indices works (no out of bounds error)
    cols_var = c.node_name(node.name).upper() + '_COLS'
    cols_entries = ', '.join(f'vec3({elem.color[0]}, {elem.color[1]}, {elem.color[2]})' for elem in elems)
    cols_entries += f', vec3({elems[len(elems) - 1].color[0]}, {elems[len(elems) - 1].color[1]}, {elems[len(elems) - 1].color[2]})'
    state.curshader.add_const("vec3", cols_var, cols_entries, array_size=len(elems) + 1)

    fac_var = c.node_name(node.name) + '_fac'
    state.curshader.write(f'float {fac_var} = {fac};')

    # Get index of the nearest left element relative to the factor
    index = '0 + '
    index += ' + '.join([f'(({fac_var} > {elems[i].position}) ? 1 : 0)' for i in range(1, len(elems))])

    # Write index
    index_var = c.node_name(node.name) + '_i'
    state.curshader.write(f'int {index_var} = {index};')

    if interp == 'CONSTANT':
        return f'{cols_var}[{index_var}]'

    # Linear interpolation
    else:
        # Write factor array
        facs_var = c.node_name(node.name).upper() + '_FACS'
        facs_entries = ', '.join(str(elem.position) for elem in elems)
        # Add one more entry at the rightmost position so that the
        # interpolation between indices works (no out of bounds error)
        facs_entries += ', 1.0'
        state.curshader.add_const("float", facs_var, facs_entries, array_size=len(elems) + 1)

        # Mix color
        # float f = (pos - start) * (1.0 / (finish - start))
        return 'mix({0}[{1}], {0}[{1} + 1], ({2} - {3}[{1}]) * (1.0 / ({3}[{1} + 1] - {3}[{1}]) ))'.format(cols_var, index_var, fac_var, facs_var)


def parse_combhsv(node: bpy.types.ShaderNodeCombineHSV, out_socket: bpy.types.NodeSocket, state: ParserState) -> vec3str:
    state.curshader.add_function(c_functions.str_hue_sat)
    h = c.parse_value_input(node.inputs[0])
    s = c.parse_value_input(node.inputs[1])
    v = c.parse_value_input(node.inputs[2])
    return f'hsv_to_rgb(vec3({h}, {s}, {v}))'


def parse_combrgb(node: bpy.types.ShaderNodeCombineRGB, out_socket: bpy.types.NodeSocket, state: ParserState) -> vec3str:
    r = c.parse_value_input(node.inputs[0])
    g = c.parse_value_input(node.inputs[1])
    b = c.parse_value_input(node.inputs[2])
    return f'vec3({r}, {g}, {b})'


def parse_combxyz(node: bpy.types.ShaderNodeCombineXYZ, out_socket: bpy.types.NodeSocket, state: ParserState) -> vec3str:
    x = c.parse_value_input(node.inputs[0])
    y = c.parse_value_input(node.inputs[1])
    z = c.parse_value_input(node.inputs[2])
    return f'vec3({x}, {y}, {z})'


def parse_wavelength(node: bpy.types.ShaderNodeWavelength, out_socket: bpy.types.NodeSocket, state: ParserState) -> vec3str:
    state.curshader.add_function(c_functions.str_wavelength_to_rgb)
    wl = c.parse_value_input(node.inputs[0])
    # Roughly map to cycles - 450 to 600 nanometers
    return f'wavelength_to_rgb(({wl} - 450.0) / 150.0)'


def parse_vectormath(node: bpy.types.ShaderNodeVectorMath, out_socket: bpy.types.NodeSocket, state: ParserState) -> Union[floatstr, vec3str]:
    op = node.operation

    vec1 = c.parse_vector_input(node.inputs[0])
    vec2 = c.parse_vector_input(node.inputs[1])

    if out_socket.type == 'VECTOR':
        if op == 'ADD':
            return f'({vec1} + {vec2})'
        elif op == 'SUBTRACT':
            return f'({vec1} - {vec2})'
        elif op == 'MULTIPLY':
            return f'({vec1} * {vec2})'
        elif op == 'DIVIDE':
            state.curshader.add_function(c_functions.str_safe_divide)
            return f'safe_divide({vec1}, {vec2}'

        elif op == 'NORMALIZE':
            return f'normalize({vec1})'
        elif op == 'SCALE':
            # Scale is input 3 despite being visually on another position (see the python tooltip in Blender)
            scale = c.parse_value_input(node.inputs[3])
            return f'{vec1} * {scale}'

        elif op == 'REFLECT':
            return f'reflect({vec1}, normalize({vec2}))'
        elif op == 'PROJECT':
            state.curshader.add_function(c_functions.str_project)
            return f'project({vec1}, {vec2})'
        elif op == 'CROSS_PRODUCT':
            return f'cross({vec1}, {vec2})'

        elif op == 'SINE':
            return f'sin({vec1})'
        elif op == 'COSINE':
            return f'cos({vec1})'
        elif op == 'TANGENT':
            return f'tan({vec1})'

        elif op == 'MODULO':
            return f'mod({vec1}, {vec2})'
        elif op == 'FRACTION':
            return f'fract({vec1})'

        elif op == 'SNAP':
            state.curshader.add_function(c_functions.str_safe_divide)
            return f'floor(safe_divide({vec1}, {vec2})) * {vec2}'
        elif op == 'WRAP':
            vec3 = c.parse_vector_input(node.inputs[2])
            state.curshader.add_function(c_functions.str_wrap)
            return f'wrap({vec1}, {vec2}, {vec3})'
        elif op == 'CEIL':
            return f'ceil({vec1})'
        elif op == 'FLOOR':
            return f'floor({vec1})'
        elif op == 'MAXIMUM':
            return f'max({vec1}, {vec2})'
        elif op == 'MINIMUM':
            return f'min({vec1}, {vec2})'
        elif op == 'ABSOLUTE':
            return f'abs({vec1})'

        log.warn(f'Vectormath node: unsupported operation {node.operation}.')
        return vec1

    # Float output
    if op == 'DOT_PRODUCT':
        return f'dot({vec1}, {vec2})'
    elif op == 'DISTANCE':
        return f'distance({vec1}, {vec2})'
    elif op == 'LENGTH':
        return f'length({vec1})'

    log.warn(f'Vectormath node: unsupported operation {node.operation}.')
    return '0.0'


def parse_math(node: bpy.types.ShaderNodeMath, out_socket: bpy.types.NodeSocket, state: ParserState) -> floatstr:
    val1 = c.parse_value_input(node.inputs[0])
    val2 = c.parse_value_input(node.inputs[1])
    op = node.operation
    if op == 'ADD':
        out_val = '({0} + {1})'.format(val1, val2)
    elif op == 'SUBTRACT':
        out_val = '({0} - {1})'.format(val1, val2)
    elif op == 'MULTIPLY':
        out_val = '({0} * {1})'.format(val1, val2)
    elif op == 'DIVIDE':
        out_val = '({0} / {1})'.format(val1, val2)
    elif op == 'POWER':
        out_val = 'pow({0}, {1})'.format(val1, val2)
    elif op == 'LOGARITHM':
        out_val = 'log({0})'.format(val1)
    elif op == 'SQRT':
        out_val = 'sqrt({0})'.format(val1)
    elif op == 'ABSOLUTE':
        out_val = 'abs({0})'.format(val1)
    elif op == 'MINIMUM':
        out_val = 'min({0}, {1})'.format(val1, val2)
    elif op == 'MAXIMUM':
        out_val = 'max({0}, {1})'.format(val1, val2)
    elif op == 'LESS_THAN':
        out_val = 'float({0} < {1})'.format(val1, val2)
    elif op == 'GREATER_THAN':
        out_val = 'float({0} > {1})'.format(val1, val2)
    elif op == 'ROUND':
        # out_val = 'round({0})'.format(val1)
        out_val = 'floor({0} + 0.5)'.format(val1)
    elif op == 'FLOOR':
        out_val = 'floor({0})'.format(val1)
    elif op == 'CEIL':
        out_val = 'ceil({0})'.format(val1)
    elif op == 'FRACT':
        out_val = 'fract({0})'.format(val1)
    elif op == 'MODULO':
        # out_val = 'float({0} % {1})'.format(val1, val2)
        out_val = 'mod({0}, {1})'.format(val1, val2)
    elif op == 'SINE':
        out_val = 'sin({0})'.format(val1)
    elif op == 'COSINE':
        out_val = 'cos({0})'.format(val1)
    elif op == 'TANGENT':
        out_val = 'tan({0})'.format(val1)
    elif op == 'ARCSINE':
        out_val = 'asin({0})'.format(val1)
    elif op == 'ARCCOSINE':
        out_val = 'acos({0})'.format(val1)
    elif op == 'ARCTANGENT':
        out_val = 'atan({0})'.format(val1)
    elif op == 'ARCTAN2':
        out_val = 'atan({0}, {1})'.format(val1, val2)

    if node.use_clamp:
        return 'clamp({0}, 0.0, 1.0)'.format(out_val)
    else:
        return out_val


def parse_rgbtobw(node: bpy.types.ShaderNodeRGBToBW, out_socket: bpy.types.NodeSocket, state: ParserState) -> floatstr:
    col = c.parse_vector_input(node.inputs[0])
    return '((({0}.r * 0.3 + {0}.g * 0.59 + {0}.b * 0.11) / 3.0) * 2.5)'.format(col)


def parse_sephsv(node: bpy.types.ShaderNodeSeparateHSV, out_socket: bpy.types.NodeSocket) -> floatstr:
    # TODO
    return '0.0'


def parse_seprgb(node: bpy.types.ShaderNodeSeparateRGB, out_socket: bpy.types.NodeSocket, state: ParserState) -> floatstr:
    col = c.parse_vector_input(node.inputs[0])
    if out_socket == node.outputs[0]:
        return '{0}.r'.format(col)
    elif out_socket == node.outputs[1]:
        return '{0}.g'.format(col)
    elif out_socket == node.outputs[2]:
        return '{0}.b'.format(col)


def parse_sepxyz(node: bpy.types.ShaderNodeSeparateXYZ, out_socket: bpy.types.NodeSocket, state: ParserState) -> floatstr:
    vec = c.parse_vector_input(node.inputs[0])
    if out_socket == node.outputs[0]:
        return '{0}.x'.format(vec)
    elif out_socket == node.outputs[1]:
        return '{0}.y'.format(vec)
    elif out_socket == node.outputs[2]:
        return '{0}.z'.format(vec)
