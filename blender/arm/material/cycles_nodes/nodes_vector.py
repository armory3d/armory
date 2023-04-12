from typing import Union

import bpy
from mathutils import Euler, Vector

import arm.log
import arm.material.cycles as c
import arm.material.cycles_functions as c_functions
from arm.material.parser_state import ParserState, ParserPass
from arm.material.shader import floatstr, vec3str
import arm.utils as utils

if arm.is_reload(__name__):
    arm.log = arm.reload_module(arm.log)
    c = arm.reload_module(c)
    c_functions = arm.reload_module(c_functions)
    arm.material.parser_state = arm.reload_module(arm.material.parser_state)
    from arm.material.parser_state import ParserState, ParserPass
    arm.material.shader = arm.reload_module(arm.material.shader)
    from arm.material.shader import floatstr, vec3str
    utils = arm.reload_module(utils)
else:
    arm.enable_reload(__name__)


def parse_curvevec(node: bpy.types.ShaderNodeVectorCurve, out_socket: bpy.types.NodeSocket, state: ParserState) -> vec3str:
    fac = c.parse_value_input(node.inputs[0])
    vec = c.parse_vector_input(node.inputs[1])
    curves = node.mapping.curves
    name = c.node_name(node.name)
    # mapping.curves[0].points[0].handle_type # bezier curve
    return '(vec3({0}, {1}, {2}) * {3})'.format(
        c.vector_curve(name + '0', vec + '.x', curves[0].points),
        c.vector_curve(name + '1', vec + '.y', curves[1].points),
        c.vector_curve(name + '2', vec + '.z', curves[2].points), fac)


def parse_bump(node: bpy.types.ShaderNodeBump, out_socket: bpy.types.NodeSocket, state: ParserState) -> vec3str:
    if state.curshader.shader_type != 'frag':
        arm.log.warn("Bump node not supported outside of fragment shaders")
        return 'vec3(0.0)'

    # Interpolation strength
    strength = c.parse_value_input(node.inputs[0])
    # Height multiplier
    # distance = c.parse_value_input(node.inputs[1])
    height = c.parse_value_input(node.inputs[2])

    state.current_pass = ParserPass.DX_SCREEN_SPACE
    height_dx = c.parse_value_input(node.inputs[2])
    state.current_pass = ParserPass.DY_SCREEN_SPACE
    height_dy = c.parse_value_input(node.inputs[2])
    state.current_pass = ParserPass.REGULAR

    # nor = c.parse_vector_input(node.inputs[3])

    if height_dx != height or height_dy != height:
        tangent = f'{c.dfdx_fine("wposition")} + n * ({height_dx} - {height})'
        bitangent = f'{c.dfdy_fine("wposition")} + n * ({height_dy} - {height})'

        # Cross-product operand order, dFdy is flipped on d3d11
        bitangent_first = utils.get_gapi() == 'direct3d11'

        if node.invert:
            bitangent_first = not bitangent_first

        if bitangent_first:
            # We need to normalize twice, once for the correct "weight" of the strength,
            # once for having a normalized output vector (lerping vectors does not preserve magnitude)
            res = f'normalize(mix(n, normalize(cross({bitangent}, {tangent})), {strength}))'
        else:
            res = f'normalize(mix(n, normalize(cross({tangent}, {bitangent})), {strength}))'

    else:
        res = 'n'

    return res


def parse_mapping(node: bpy.types.ShaderNodeMapping, out_socket: bpy.types.NodeSocket, state: ParserState) -> vec3str:
    # Only "Point", "Texture" and "Vector" types supported for now..
    # More information about the order of operations for this node:
    # https://docs.blender.org/manual/en/latest/render/shader_nodes/vector/mapping.html#properties

    input_vector: bpy.types.NodeSocket = node.inputs[0]
    input_location: bpy.types.NodeSocket = node.inputs['Location']
    input_rotation: bpy.types.NodeSocket = node.inputs['Rotation']
    input_scale: bpy.types.NodeSocket = node.inputs['Scale']
    out = c.parse_vector_input(input_vector) if input_vector.is_linked else c.to_vec3(input_vector.default_value)
    location = c.parse_vector_input(input_location) if input_location.is_linked else c.to_vec3(input_location.default_value)
    rotation = c.parse_vector_input(input_rotation) if input_rotation.is_linked else c.to_vec3(input_rotation.default_value)
    scale = c.parse_vector_input(input_scale) if input_scale.is_linked else c.to_vec3(input_scale.default_value)

    # Use inner functions because the order of operations varies between
    # mapping node vector types. This adds a slight overhead but makes
    # the code much more readable.
    # - "Point" and "Vector" use Scale -> Rotate -> Translate
    # - "Texture" uses Translate -> Rotate -> Scale
    def calc_location(output: str) -> str:
        # Vectors and Eulers support the "!=" operator
        if input_scale.is_linked or input_scale.default_value != Vector((1, 1, 1)):
            if node.vector_type == 'TEXTURE':
                output = f'({output} / {scale})'
            else:
                output = f'({output} * {scale})'

        return output

    def calc_scale(output: str) -> str:
        if input_location.is_linked or input_location.default_value != Vector((0, 0, 0)):
            # z location is a little off sometimes?...
            if node.vector_type == 'TEXTURE':
                output = f'({output} - {location})'
            else:
                output = f'({output} + {location})'
        return output

    out = calc_location(out) if node.vector_type == 'TEXTURE' else calc_scale(out)

    if input_rotation.is_linked or input_rotation.default_value != Euler((0, 0, 0)):
        var_name = c.node_name(node.name) + "_rotation" + state.get_parser_pass_suffix()
        if node.vector_type == 'TEXTURE':
            state.curshader.write(f'mat3 {var_name}X = mat3(1.0, 0.0, 0.0, 0.0, cos({rotation}.x), sin({rotation}.x), 0.0, -sin({rotation}.x), cos({rotation}.x));')
            state.curshader.write(f'mat3 {var_name}Y = mat3(cos({rotation}.y), 0.0, -sin({rotation}.y), 0.0, 1.0, 0.0, sin({rotation}.y), 0.0, cos({rotation}.y));')
            state.curshader.write(f'mat3 {var_name}Z = mat3(cos({rotation}.z), sin({rotation}.z), 0.0, -sin({rotation}.z), cos({rotation}.z), 0.0, 0.0, 0.0, 1.0);')
        else:
            # A little bit redundant, but faster than 12 more multiplications to make it work dynamically
            state.curshader.write(f'mat3 {var_name}X = mat3(1.0, 0.0, 0.0, 0.0, cos(-{rotation}.x), sin(-{rotation}.x), 0.0, -sin(-{rotation}.x), cos(-{rotation}.x));')
            state.curshader.write(f'mat3 {var_name}Y = mat3(cos(-{rotation}.y), 0.0, -sin(-{rotation}.y), 0.0, 1.0, 0.0, sin(-{rotation}.y), 0.0, cos(-{rotation}.y));')
            state.curshader.write(f'mat3 {var_name}Z = mat3(cos(-{rotation}.z), sin(-{rotation}.z), 0.0, -sin(-{rotation}.z), cos(-{rotation}.z), 0.0, 0.0, 0.0, 1.0);')

        # XYZ-order euler rotation
        out = f'{out} * {var_name}X * {var_name}Y * {var_name}Z'

    out = calc_scale(out) if node.vector_type == 'TEXTURE' else calc_location(out)

    return out


def parse_normal(node: bpy.types.ShaderNodeNormal, out_socket: bpy.types.NodeSocket, state: ParserState) -> Union[floatstr, vec3str]:
    nor1 = c.to_vec3(node.outputs['Normal'].default_value)

    if out_socket == node.outputs['Normal']:
        return nor1

    elif out_socket == node.outputs['Dot']:
        nor2 = c.parse_vector_input(node.inputs["Normal"])
        return f'dot({nor1}, {nor2})'


def parse_normalmap(node: bpy.types.ShaderNodeNormalMap, out_socket: bpy.types.NodeSocket, state: ParserState) -> vec3str:
    if state.curshader == state.tese:
        return c.parse_vector_input(node.inputs[1])
    else:
        # space = node.space
        # map = node.uv_map
        # Color
        c.parse_normal_map_color_input(node.inputs[1], node.inputs[0])
        return 'n'


def parse_vectortransform(node: bpy.types.ShaderNodeVectorTransform, out_socket: bpy.types.NodeSocket, state: ParserState) -> vec3str:
    # type = node.vector_type
    # conv_from = node.convert_from
    # conv_to = node.convert_to
    # Pass through
    return c.parse_vector_input(node.inputs[0])


def parse_displacement(node: bpy.types.ShaderNodeDisplacement, out_socket: bpy.types.NodeSocket, state: ParserState) -> vec3str:
    height = c.parse_value_input(node.inputs[0])
    midlevel = c.parse_value_input(node.inputs[1])
    scale = c.parse_value_input(node.inputs[2])
    nor = c.parse_vector_input(node.inputs[3])
    return f'(vec3({height}) * {scale})'

def parse_vectorrotate(node: bpy.types.ShaderNodeVectorRotate, out_socket: bpy.types.NodeSocket, state: ParserState) -> vec3str:

    type = node.rotation_type
    input_vector: bpy.types.NodeSocket = c.parse_vector_input(node.inputs[0])
    input_center: bpy.types.NodeSocket = c.parse_vector_input(node.inputs[1])
    input_axis: bpy.types.NodeSocket = c.parse_vector_input(node.inputs[2])
    input_angle: bpy.types.NodeSocket = c.parse_value_input(node.inputs[3])
    input_rotation: bpy.types.NodeSocket = c.parse_vector_input(node.inputs[4])

    if node.invert:
        input_invert = "0"
    else:
        input_invert = "1"

    state.curshader.add_function(c_functions.str_rotate_around_axis)

    if type == 'AXIS_ANGLE':
        return f'vec3( (length({input_axis}) != 0.0) ? rotate_around_axis({input_vector} - {input_center}, normalize({input_axis}), {input_angle} * {input_invert}) + {input_center} : {input_vector} )'
    elif type == 'X_AXIS':
        return f'vec3( rotate_around_axis({input_vector} - {input_center}, vec3(1.0, 0.0, 0.0), {input_angle} * {input_invert}) + {input_center} )'
    elif type == 'Y_AXIS':
        return f'vec3( rotate_around_axis({input_vector} - {input_center}, vec3(0.0, 1.0, 0.0), {input_angle} * {input_invert}) + {input_center} )'
    elif type == 'Z_AXIS':
        return f'vec3( rotate_around_axis({input_vector} - {input_center}, vec3(0.0, 0.0, 1.0), {input_angle} * {input_invert}) + {input_center} )'
    elif type == 'EULER_XYZ':
        state.curshader.add_function(c_functions.str_euler_to_mat3)
        return f'vec3( mat3(({input_invert} < 0.0) ? transpose(euler_to_mat3({input_rotation})) : euler_to_mat3({input_rotation})) * ({input_vector} - {input_center}) + {input_center})'

    return f'(vec3(1.0, 0.0, 0.0))'
