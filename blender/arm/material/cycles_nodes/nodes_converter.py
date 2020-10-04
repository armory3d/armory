import bpy

import arm.material.cycles as cycles
import arm.material.cycles_functions as c_functions
from arm.material.shader import vec3str


def parse_blackbody(node: bpy.types.ShaderNodeBlackbody, out_socket: bpy.types.NodeSocket) -> vec3str:
    t = float(cycles.parse_value_input(node.inputs[0]))

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
    return cycles.to_vec3([rgb[0], rgb[1], rgb[2]])


def parse_valtorgb(node: bpy.types.ShaderNodeValToRGB, out_socket: bpy.types.NodeSocket) -> vec3str:
    input_fac: bpy.types.NodeSocket = node.inputs[0]

    fac: str = cycles.parse_value_input(input_fac) if input_fac.is_linked else cycles.to_vec1(input_fac.default_value)
    interp = node.color_ramp.interpolation
    elems = node.color_ramp.elements

    if len(elems) == 1:
        return cycles.to_vec3(elems[0].color)

    # Write color array
    # The last entry is included twice so that the interpolation
    # between indices works (no out of bounds error)
    cols_var = cycles.node_name(node.name).upper() + '_COLS'
    cols_entries = ', '.join(f'vec3({elem.color[0]}, {elem.color[1]}, {elem.color[2]})' for elem in elems)
    cols_entries += f', vec3({elems[len(elems) - 1].color[0]}, {elems[len(elems) - 1].color[1]}, {elems[len(elems) - 1].color[2]})'
    cycles.curshader.add_const("vec3", cols_var, cols_entries, array_size=len(elems) + 1)

    fac_var = cycles.node_name(node.name) + '_fac'
    cycles.curshader.write(f'float {fac_var} = {fac};')

    # Get index of the nearest left element relative to the factor
    index = '0 + '
    index += ' + '.join([f'(({fac_var} > {elems[i].position}) ? 1 : 0)' for i in range(1, len(elems))])

    # Write index
    index_var = cycles.node_name(node.name) + '_i'
    cycles.curshader.write(f'int {index_var} = {index};')

    if interp == 'CONSTANT':
        return f'{cols_var}[{index_var}]'

    # Linear interpolation
    else:
        # Write factor array
        facs_var = cycles.node_name(node.name).upper() + '_FACS'
        facs_entries = ', '.join(str(elem.position) for elem in elems)
        # Add one more entry at the rightmost position so that the
        # interpolation between indices works (no out of bounds error)
        facs_entries += ', 1.0'
        cycles.curshader.add_const("float", facs_var, facs_entries, array_size=len(elems) + 1)

        # Mix color
        # float f = (pos - start) * (1.0 / (finish - start))
        return 'mix({0}[{1}], {0}[{1} + 1], ({2} - {3}[{1}]) * (1.0 / ({3}[{1} + 1] - {3}[{1}]) ))'.format(cols_var, index_var, fac_var, facs_var)


def parse_combhsv(node: bpy.types.ShaderNodeCombineHSV, out_socket: bpy.types.NodeSocket) -> vec3str:
    cycles.curshader.add_function(c_functions.str_hue_sat)
    h = cycles.parse_value_input(node.inputs[0])
    s = cycles.parse_value_input(node.inputs[1])
    v = cycles.parse_value_input(node.inputs[2])
    return f'hsv_to_rgb(vec3({h}, {s}, {v}))'


def parse_combrgb(node: bpy.types.ShaderNodeCombineRGB, out_socket: bpy.types.NodeSocket) -> vec3str:
    r = cycles.parse_value_input(node.inputs[0])
    g = cycles.parse_value_input(node.inputs[1])
    b = cycles.parse_value_input(node.inputs[2])
    return f'vec3({r}, {g}, {b})'


def parse_combxyz(node: bpy.types.ShaderNodeCombineXYZ, out_socket: bpy.types.NodeSocket) -> vec3str:
    x = cycles.parse_value_input(node.inputs[0])
    y = cycles.parse_value_input(node.inputs[1])
    z = cycles.parse_value_input(node.inputs[2])
    return f'vec3({x}, {y}, {z})'


def parse_wavelength(node: bpy.types.ShaderNodeWavelength, out_socket: bpy.types.NodeSocket) -> vec3str:
    cycles.curshader.add_function(c_functions.str_wavelength_to_rgb)
    wl = cycles.parse_value_input(node.inputs[0])
    # Roughly map to cycles - 450 to 600 nanometers
    return f'wavelength_to_rgb(({wl} - 450.0) / 150.0)'


def parse_vectormath(node: bpy.types.ShaderNodeVectorMath, out_socket: bpy.types.NodeSocket) -> vec3str:
    vec1 = cycles.parse_vector_input(node.inputs[0])
    vec2 = cycles.parse_vector_input(node.inputs[1])
    op = node.operation
    if op == 'ADD':
        return f'({vec1} + {vec2})'
    elif op == 'SUBTRACT':
        return f'({vec1} - {vec2})'
    elif op == 'AVERAGE':
        return f'(({vec1} + {vec2}) / 2.0)'
    elif op == 'DOT_PRODUCT':
        return f'vec3(dot({vec1}, {vec2}))'
    elif op == 'CROSS_PRODUCT':
        return f'cross({vec1}, {vec2})'
    elif op == 'NORMALIZE':
        return f'normalize({vec1})'
