from typing import Union

import bpy

import arm
import arm.log as log
import arm.material.cycles as c
import arm.material.cycles_functions as c_functions
from arm.material.parser_state import ParserPass, ParserState
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


def parse_maprange(node: bpy.types.ShaderNodeMapRange, out_socket: bpy.types.NodeSocket, state: ParserState) -> floatstr:

    interp = node.interpolation_type

    value: str = c.parse_value_input(node.inputs[0]) if node.inputs[0].is_linked else c.to_vec1(node.inputs[0].default_value)
    fromMin = c.parse_value_input(node.inputs[1])
    fromMax = c.parse_value_input(node.inputs[2])
    toMin = c.parse_value_input(node.inputs[3])
    toMax = c.parse_value_input(node.inputs[4])

    if interp == "LINEAR":
        state.curshader.add_function(c_functions.str_map_range_linear)
        out = f'map_range_linear({value}, {fromMin}, {fromMax}, {toMin}, {toMax})'

    elif interp == "STEPPED":
        steps = float(c.parse_value_input(node.inputs[5]))
        state.curshader.add_function(c_functions.str_map_range_stepped)
        out = f'map_range_stepped({value}, {fromMin}, {fromMax}, {toMin}, {toMax}, {steps})'

    elif interp == "SMOOTHSTEP":
        state.curshader.add_function(c_functions.str_map_range_smoothstep)
        out = f'map_range_smoothstep({value}, {fromMin}, {fromMax}, {toMin}, {toMax})'

    elif interp == "SMOOTHERSTEP":
        state.curshader.add_function(c_functions.str_map_range_smootherstep)
        out = f'map_range_smootherstep({value}, {fromMin}, {fromMax}, {toMin}, {toMax})'

    else:
        log.warn(f'Interpolation mode {interp} not supported for Map Range node')
        return '0.0'

    if node.clamp:
        out = f'clamp({out}, {toMin}, {toMax})'

    return out

def parse_blackbody(node: bpy.types.ShaderNodeBlackbody, out_socket: bpy.types.NodeSocket, state: ParserState) -> vec3str:

    t = c.parse_value_input(node.inputs[0])

    state.curshader.add_function(c_functions.str_blackbody)
    return f'blackbody({t})'

def parse_clamp(node: bpy.types.ShaderNodeClamp, out_socket: bpy.types.NodeSocket, state: ParserState) -> floatstr:
    value = c.parse_value_input(node.inputs['Value'])
    minVal = c.parse_value_input(node.inputs['Min'])
    maxVal = c.parse_value_input(node.inputs['Max'])

    if node.clamp_type == 'MINMAX':
        # Condition is minVal < maxVal, otherwise use 'RANGE' type
        return f'clamp({value}, {minVal}, {maxVal})'

    elif node.clamp_type == 'RANGE':
        return f'{minVal} < {maxVal} ? clamp({value}, {minVal}, {maxVal}) : clamp({value}, {maxVal}, {minVal})'

    else:
        log.warn(f'Clamp node: unsupported clamp type {node.clamp_type}.')
        return value


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

    if state.current_pass == ParserPass.REGULAR:
        cols_entries = ', '.join(f'vec3({elem.color[0]}, {elem.color[1]}, {elem.color[2]})' for elem in elems)
        cols_entries += f', vec3({elems[len(elems) - 1].color[0]}, {elems[len(elems) - 1].color[1]}, {elems[len(elems) - 1].color[2]})'
        state.curshader.add_const("vec3", cols_var, cols_entries, array_size=len(elems) + 1)

    fac_var = c.node_name(node.name) + '_fac' + state.get_parser_pass_suffix()
    state.curshader.write(f'float {fac_var} = {fac};')

    # Get index of the nearest left element relative to the factor
    index = '0 + '
    index += ' + '.join([f'(({fac_var} > {elems[i].position}) ? 1 : 0)' for i in range(1, len(elems))])

    # Write index
    index_var = c.node_name(node.name) + '_i' + state.get_parser_pass_suffix()
    state.curshader.write(f'int {index_var} = {index};')

    if interp == 'CONSTANT':
        return f'{cols_var}[{index_var}]'

    # Linear interpolation
    else:
        # Write factor array
        facs_var = c.node_name(node.name).upper() + '_FACS'
        if state.current_pass == ParserPass.REGULAR:
            facs_entries = ', '.join(str(elem.position) for elem in elems)
            # Add one more entry at the rightmost position so that the
            # interpolation between indices works (no out of bounds error)
            facs_entries += ', 1.0'
            state.curshader.add_const("float", facs_var, facs_entries, array_size=len(elems) + 1)

        # Mix color
        prev_stop_fac = f'{facs_var}[{index_var}]'
        next_stop_fac = f'{facs_var}[{index_var} + 1]'
        prev_stop_col = f'{cols_var}[{index_var}]'
        next_stop_col = f'{cols_var}[{index_var} + 1]'
        rel_pos = f'({fac_var} - {prev_stop_fac}) * (1.0 / ({next_stop_fac} - {prev_stop_fac}))'
        return f'mix({prev_stop_col}, {next_stop_col}, max({rel_pos}, 0.0))'

if bpy.app.version > (3, 2, 0):
    def parse_combine_color(node: bpy.types.ShaderNodeCombineColor, out_socket: bpy.types.NodeSocket, state: ParserState) -> floatstr:
        if node.mode == 'RGB':
            return parse_combrgb(node, out_socket, state)
        elif node.mode == 'HSV':
            return parse_combhsv(node, out_socket, state)
        elif node.mode == 'HSL':
            log.warn('Combine Color node: HSL mode is not supported, using default value')
            return c.to_vec3((0.0, 0.0, 0.0))


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
            return f'safe_divide({vec1}, {vec2})'

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
    elif op == 'MULTIPLY_ADD':
        val3 = c.parse_value_input(node.inputs[2])
        out_val = '({0} * {1} + {2})'.format(val1, val2, val3)
    elif op == 'POWER':
        out_val = 'pow({0}, {1})'.format(val1, val2)
    elif op == 'LOGARITHM':
        out_val = 'log({0})'.format(val1)
    elif op == 'SQRT':
        out_val = 'sqrt({0})'.format(val1)
    elif op == 'INVERSE_SQRT':
        out_val = 'inversesqrt({0})'.format(val1)
    elif op == 'ABSOLUTE':
        out_val = 'abs({0})'.format(val1)
    elif op == 'EXPONENT':
        out_val = 'exp({0})'.format(val1)
    elif op == 'MINIMUM':
        out_val = 'min({0}, {1})'.format(val1, val2)
    elif op == 'MAXIMUM':
        out_val = 'max({0}, {1})'.format(val1, val2)
    elif op == 'LESS_THAN':
        out_val = 'float({0} < {1})'.format(val1, val2)
    elif op == 'GREATER_THAN':
        out_val = 'float({0} > {1})'.format(val1, val2)
    elif op == 'SIGN':
        out_val = 'sign({0})'.format(val1)
    elif op == 'COMPARE':
        val3 = c.parse_value_input(node.inputs[2])
        out_val = 'float((abs({0} - {1}) <= max({2}, 1e-5)) ? 1.0 : 0.0)'.format(val1, val2, val3)
    elif op == 'SMOOTH_MIN':
        val3 = c.parse_value_input(node.inputs[2])
        out_val = 'float(float({2} != 0.0 ? min({0},{1}) - (max({2} - abs({0} - {1}), 0.0) / {2}) * (max({2} - abs({0} - {1}), 0.0) / {2}) * (max({2} - abs({0} - {1}), 0.0) / {2}) * {2} * (1.0 / 6.0) : min({0}, {1})))'.format(val1, val2, val3)
    elif op == 'SMOOTH_MAX':
        val3 = c.parse_value_input(node.inputs[2])
        out_val = 'float(0-(float({2} != 0.0 ? min(-{0},-{1}) - (max({2} - abs(-{0} - (-{1})), 0.0) / {2}) * (max({2} - abs(-{0} - (-{1})), 0.0) / {2}) * (max({2} - abs(-{0} - (-{1})), 0.0) / {2}) * {2} * (1.0 / 6.0) : min(-{0}, (-{1})))))'.format(val1, val2, val3)
    elif op == 'ROUND':
        # out_val = 'round({0})'.format(val1)
        out_val = 'floor({0} + 0.5)'.format(val1)
    elif op == 'FLOOR':
        out_val = 'floor({0})'.format(val1)
    elif op == 'CEIL':
        out_val = 'ceil({0})'.format(val1)
    elif op == 'TRUNC':
        out_val = 'trunc({0})'.format(val1)
    elif op == 'FRACT':
        out_val = 'fract({0})'.format(val1)
    elif op == 'MODULO':
        # out_val = 'float({0} % {1})'.format(val1, val2)
        out_val = 'mod({0}, {1})'.format(val1, val2)
    elif op == 'WRAP':
        val3 = c.parse_value_input(node.inputs[2])
        out_val = 'float((({1}-{2}) != 0.0) ? {0} - (({1}-{2}) * floor(({0} - {2}) / ({1}-{2}))) : {2})'.format(val1, val2, val3)
    elif op == 'SNAP':
        out_val = 'floor(({1} != 0.0) ? {0} / {1} : 0.0) * {1}'.format(val1, val2)
    elif op == 'PINGPONG':
        out_val = 'float(({1} != 0.0) ? abs(fract(({0} - {1}) / ({1} * 2.0)) * {1} * 2.0 - {1}) : 0.0)'.format(val1, val2)
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
    elif op == 'SINH':
        out_val = 'sinh({0})'.format(val1)
    elif op == 'COSH':
        out_val = 'cosh({0})'.format(val1)
    elif op == 'TANH':
        out_val = 'tanh({0})'.format(val1)
    elif op == 'RADIANS':
        out_val = 'radians({0})'.format(val1)
    elif op == 'DEGREES':
        out_val = 'degrees({0})'.format(val1)

    if node.use_clamp:
        return 'clamp({0}, 0.0, 1.0)'.format(out_val)
    else:
        return out_val


def parse_rgbtobw(node: bpy.types.ShaderNodeRGBToBW, out_socket: bpy.types.NodeSocket, state: ParserState) -> floatstr:
    return c.rgb_to_bw(c.parse_vector_input(node.inputs[0]))

if bpy.app.version > (3, 2, 0):
    def parse_separate_color(node: bpy.types.ShaderNodeSeparateColor, out_socket: bpy.types.NodeSocket, state: ParserState) -> floatstr:
        if node.mode == 'RGB':
            return parse_seprgb(node, out_socket, state)
        elif node.mode == 'HSV':
            return parse_sephsv(node, out_socket, state)
        elif node.mode == 'HSL':
            log.warn('Separate Color node: HSL mode is not supported, using default value')
            return '0.0'


def parse_sephsv(node: bpy.types.ShaderNodeSeparateHSV, out_socket: bpy.types.NodeSocket, state: ParserState) -> floatstr:
    state.curshader.add_function(c_functions.str_hue_sat)

    hsv_var = c.node_name(node.name) + '_hsv' + state.get_parser_pass_suffix()
    if not state.curshader.contains(hsv_var):  # Already written if a second output is parsed
        state.curshader.write(f'const vec3 {hsv_var} = rgb_to_hsv({c.parse_vector_input(node.inputs["Color"])}.rgb);')

    if out_socket == node.outputs[0]:
        return f'{hsv_var}.x'
    elif out_socket == node.outputs[1]:
        return f'{hsv_var}.y'
    elif out_socket == node.outputs[2]:
        return f'{hsv_var}.z'


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
