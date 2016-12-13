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
import armutils

def node_by_type(nodes, ntype):
    for n in nodes:
        if n.type == ntype:
            return n

def socket_index(node, socket):
    for i in range(0, len(node.outputs)):
        if node.outputs[i] == socket:
            return i

def parse(nodes, vert, frag):
    # global parsed
    # parsed = [] # Compute node only once
    output_node = node_by_type(nodes, 'OUTPUT_MATERIAL')
    if output_node != None:
        parse_output(output_node, vert, frag)

def parse_output(node, _vert, _frag):
    global parents
    global vert
    global frag
    parents = []
    vert = _vert
    frag = _frag
    out_basecol, out_roughness, out_metallic, out_occlusion = parse_shader_input(node.inputs[0])
    frag.write('basecol = {0};'.format(out_basecol))
    frag.write('roughness = {0};'.format(out_roughness))
    frag.write('metallic = {0};'.format(out_metallic))
    frag.write('occlusion = {0};'.format(out_occlusion))

def parse_group(node, socket): # Entering group
    index = socket_index(node, socket)
    output_node = node_by_type(node.node_tree.nodes, 'GROUP_OUTPUT')
    if output_node == None:
        return
    inp = output_node.inputs[index]
    parents.append(node)
    out_group = parse_input(inp)
    parents.pop()
    return out_group

def parse_input_group(node, socket): # Leaving group
    index = socket_index(node, socket)
    parent = parents[-1]
    inp = parent.inputs[index]
    return parse_input(inp)

def parse_input(inp):
    if inp.type == 'SHADER':
        return parse_shader_input(inp)
    elif inp.type == 'RGB':
        return parse_vector_input(inp)
    elif inp.type == 'RGBA':
        return parse_vector_input(inp)
    elif inp.type == 'VECTOR':
        return parse_vector_input(inp)
    elif inp.type == 'VALUE':
        return parse_value_input(inp)

def parse_shader_input(inp):
    if inp.is_linked:
        l = inp.links[0]
        return parse_shader(l.from_node, l.from_socket)
    else:
        out_basecol = 'vec3(0.8)'
        out_roughness = '0.0'
        out_metallic = '0.0'
        out_occlusion = '1.0'
        return out_basecol, out_roughness, out_metallic, out_occlusion

def parse_shader(node, socket):   
    out_basecol = 'vec3(0.8)'
    out_roughness = '0.0'
    out_metallic = '0.0'
    out_occlusion = '1.0'

    if node.type == 'REROUTE':
        l = node.inputs[0].links[0]
        return parse_shader(l.from_node, l.from_socket)

    elif node.type == 'GROUP':
        if node.node_tree.name.startswith('Armory PBR'):
            pass
        else:
            return parse_group(node, socket)

    elif node.type == 'GROUP_INPUT':
        return parse_input_group(node, socket)

    elif node.type == 'MIX_SHADER':
        fac = parse_value_input(node.inputs[0])
        bc1, rough1, met1, occ1 = parse_shader_input(node.inputs[1])
        bc2, rough2, met2, occ2 = parse_shader_input(node.inputs[2])
        out_basecol = '({0} * (1.0 - {2}) + {1} * {2})'.format(bc1, bc2, fac)
        out_roughness = '({0} * (1.0 - {2}) + {1} * {2})'.format(rough1, rough2, fac)
        out_metallic = '({0} * (1.0 - {2}) + {1} * {2})'.format(met1, met2, fac)
        out_occlusion = '({0} * (1.0 - {2}) + {1} * {2})'.format(occ1, occ2, fac)

    elif node.type == 'ADD_SHADER':
        bc1, rough1, met1, occ1 = parse_shader_input(node.inputs[0])
        bc2, rough2, met2, occ2 = parse_shader_input(node.inputs[1])
        out_basecol = '({0} + {1})'.format(bc1, bc2)
        out_roughness = '({0} + {1})'.format(rough1, rough2)
        out_metallic = '({0} + {1})'.format(met1, met2)
        out_occlusion = '({0} + {1})'.format(occ1, occ2)

    elif node.type == 'BSDF_DIFFUSE':
        out_basecol = parse_vector_input(node.inputs[0])
        out_roughness = parse_value_input(node.inputs[1])

    elif node.type == 'BSDF_GLOSSY':
        out_basecol = parse_vector_input(node.inputs[0])
        out_roughness = parse_value_input(node.inputs[1])
        out_metallic = '1.0'

    elif node.type == 'AMBIENT_OCCLUSION':
        # Single channel
        out_occlusion = parse_vector_input(node.inputs[0]) + '.r'

    elif node.type == 'BSDF_ANISOTROPIC':
        # Revert to glossy
        out_basecol = parse_vector_input(node.inputs[0])
        out_roughness = parse_value_input(node.inputs[1])
        out_metallic = '1.0'

    elif node.type == 'EMISSION':
        # Multiply basecol
        out_basecol = parse_vector_input(node.inputs[0])
        strength = parse_value_input(node.inputs[1])
        out_basecol = '({0} * {1} * 50.0)'.format(out_basecol, strength)

    elif node.type == 'BSDF_GLASS':
        # Switch to translucent
        pass

    elif node.type == 'BSDF_HAIR':
        pass

    elif node.type == 'HOLDOUT':
        # Occlude
        out_occlusion = '0.0'

    elif node.type == 'BSDF_REFRACTION':
        pass

    elif node.type == 'SUBSURFACE_SCATTERING':
        pass

    elif node.type == 'BSDF_TOON':
        pass

    elif node.type == 'BSDF_TRANSLUCENT':
        pass

    elif node.type == 'BSDF_TRANSPARENT':
        pass

    elif node.type == 'BSDF_VELVET':
        out_basecol = parse_vector_input(node.inputs[0])
        out_roughness = '1.0'
        out_metallic = '1.0'

    elif node.type == 'VOLUME_ABSORPTION':
        pass

    elif node.type == 'VOLUME_SCATTER':
        pass

    return out_basecol, out_roughness, out_metallic, out_occlusion

def parse_vector_input(inp):
    if inp.is_linked:
        l = inp.links[0]
        if l.from_socket.type == 'RGB' or l.from_socket.type == 'RGBA':
            return parse_rgb(l.from_node, l.from_socket)
        elif l.from_socket.type == 'VECTOR':
            return parse_vector(l.from_node, l.from_socket)
        elif l.from_socket.type == 'VALUE':
            return 'vec3({0})'.format(parse_value(l.from_node, l.from_socket))
    else:
        return vec3(inp.default_value)

def parse_rgb(node, socket):

    if node.type == 'REROUTE':
        l = node.inputs[0].links[0]
        return parse_rgb(l.from_node, l.from_socket)

    elif node.type == 'GROUP':
        return parse_group(node, socket)

    elif node.type == 'GROUP_INPUT':
        return parse_input_group(node, socket)

    elif node.type == 'ATTRIBUTE':
        # Vcols
        pass

    elif node.type == 'RGB':
        return vec3(socket.default_value)

    elif node.type == 'TEX_BRICK':
        # Pass through
        return vec3([0.0, 0.0, 0.0])

    elif node.type == 'TEX_CHECKER':
        frag.add_function(\
"""vec3 tex_checker(const vec3 co, const vec3 col1, const vec3 col2, const float scale) {
    vec3 p = co * scale;
    // Prevent precision issues on unit coordinates
    //p.x = (p.x + 0.000001) * 0.999999;
    //p.y = (p.y + 0.000001) * 0.999999;
    //p.z = (p.z + 0.000001) * 0.999999;
    float xi = abs(floor(p.x));
    float yi = abs(floor(p.y));
    float zi = abs(floor(p.z));
    bool check = ((mod(xi, 2.0) == mod(yi, 2.0)) == bool(mod(zi, 2.0)));
    return check ? col1 : col2;
}
""")
        # co = parse_vector_input(node.inputs[0])
        col1 = parse_vector_input(node.inputs[1])
        col2 = parse_vector_input(node.inputs[2])
        scale = parse_value_input(node.inputs[3])
        return 'tex_checker(wposition, {0}, {1}, {2})'.format(col1, col2, scale)

    elif node.type == 'TEX_ENVIRONMENT':
        # Pass through
        return vec3([0.0, 0.0, 0.0])

    elif node.type == 'TEX_GRADIENT':
        grad = node.gradient_type
        if grad == 'LINEAR':
            f = 'wposition.x'
        elif grad == 'QUADRATIC':
            f = '0.0'
        elif grad == 'EASING':
            f = '0.0'
        elif grad == 'DIAGONAL':
            f = '(wposition.x + wposition.y) * 0.5'
        elif grad == 'RADIAL':
            f = 'atan(wposition.y, wposition.x) / PI2 + 0.5'
        elif grad == 'QUADRATIC_SPHERE':
            f = '0.0'
        elif grad == 'SPHERICAL':
            f = 'max(1.0 - sqrt(wposition.x * wposition.x + wposition.y * wposition.y + wposition.z * wposition.z), 0.0)'
        return 'vec3(clamp({0}, 0.0, 1.0))'.format(f)

    elif node.type == 'TEX_IMAGE':
        # Pass through
        return vec3([0.0, 0.0, 0.0])

    elif node.type == 'TEX_MAGIC':
        # Pass through
        return vec3([0.0, 0.0, 0.0])

    elif node.type == 'TEX_MUSGRAVE':
        # Pass through
        return vec3([0.0, 0.0, 0.0])

    elif node.type == 'TEX_NOISE':
        # co = parse_vector_input(node.inputs[0])
        # scale = parse_value_input(node.inputs[1])
        # detail = parse_value_input(node.inputs[2])
        # distortion = parse_value_input(node.inputs[3])
        # No proper noise yet
        return 'vec3(fract(sin(dot(wposition.xy, vec2(12.9898,78.233))) * 43758.5453))'

    elif node.type == 'TEX_POINTDENSITY':
        # Pass through
        return vec3([0.0, 0.0, 0.0])

    elif node.type == 'TEX_SKY':
        # Pass through
        return vec3([0.0, 0.0, 0.0])

    elif node.type == 'TEX_VORONOI':
        # Pass through
        return vec3([0.0, 0.0, 0.0])

    elif node.type == 'TEX_WAVE':
        # Pass through
        return vec3([0.0, 0.0, 0.0])

    elif node.type == 'BRIGHTCONTRAST':
        out_col = parse_vector_input(node.inputs[0])
        bright = parse_value_input(node.inputs[1])
        contr = parse_value_input(node.inputs[2])
        frag.add_function(\
"""vec3 brightcontrast(const vec3 col, const float bright, const float contr) {
    float a = 1.0 + contr;
    float b = bright - contr * 0.5;
    return max(a * col + b, 0.0);
}
""")
        return 'brightcontrast({0}, {1}, {2})'.format(out_col, bright, contr)

    elif node.type == 'GAMMA':
        out_col = parse_vector_input(node.inputs[0])
        gamma = parse_value_input(node.inputs[1])
        return 'pow({0}, vec3({1}))'.format(out_col, gamma)

    elif node.type == 'HUE_SAT':
#         hue = parse_value_input(node.inputs[0])
#         sat = parse_value_input(node.inputs[1])
#         val = parse_value_input(node.inputs[2])
#         fac = parse_value_input(node.inputs[3])
        out_col = parse_vector_input(node.inputs[4])
#         frag.add_function(\
# """vec3 hue_sat(const float hue, const float sat, const float val, const float fac, const vec3 col) {
# }
# """)
        return out_col

    elif node.type == 'INVERT':
        fac = parse_value_input(node.inputs[0])
        out_col = parse_vector_input(node.inputs[1])
        return 'mix({0}, vec3(1.0) - ({0}), {1})'.format(out_col, fac)

    elif node.type == 'MIX_RGB':
        fac = parse_value_input(node.inputs[0])
        col1 = parse_vector_input(node.inputs[1])
        col2 = parse_vector_input(node.inputs[2])
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
            out_col = '((1.0 - {2}) * {0} + {2} * ((vec3(1.0) - {0}) * {1} * {0} + {0} * (vec3(1.0) - (vec3(1.0) - {1}) * (vec3(1.0) - {0}))));'.format(col1, col2, fac)
        elif blend == 'LINEAR_LIGHT':
            out_col = 'mix({0}, {1}, {2})'.format(col1, col2, fac) # Revert to mix
            # out_col = '({0} + {2} * (2.0 * ({1} - vec3(0.5))))'.format(col1, col2, fac)
        if node.use_clamp:
            return 'clamp({0}, vec3(0.0), vec3(1.0))'.format(out_col)
        else:
            return out_col

    elif node.type == 'CURVE_RGB':
        # Pass throuh
        return parse_vector_input(node.inputs[1])

    elif node.type == 'BLACKBODY':
        # Pass constant
        return vec3([0.84, 0.38, 0.0])

    elif node.type == 'VALTORGB': # ColorRamp
        # Max 2 elements, no position
        fac = parse_value_input(node.inputs[0])
        elems = node.color_ramp.elements
        # elem[0].position - 0 to 1
        if len(elems) == 1:
            return vec3(elems[0].color)
        else:
            return 'mix({0}, {1}, {2})'.format(vec3(elems[0].color), vec3(elems[1].color), fac)

    elif node.type == 'COMBHSV':
# vec3 hsv2rgb(vec3 c) {
#     vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
#     vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
#     return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
# }
# vec3 rgb2hsv(vec3 c) {
#     vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
#     vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
#     vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));

#     float d = q.x - min(q.w, q.y);
#     float e = 1.0e-10;
#     return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
# }
        # Pass constant
        return vec3([0.0, 0.0, 0.0])

    elif node.type == 'COMBRGB':
        r = parse_value_input(node.inputs[0])
        g = parse_value_input(node.inputs[1])
        b = parse_value_input(node.inputs[2])
        return 'vec3({0}, {1}, {2})'.format(r, g, b)

    elif node.type == 'WAVELENGTH':
        # Pass constant
        return vec3([0.0, 0.27, 0.19])

def parse_vector(node, socket):
    if node.type == 'REROUTE':
        l = node.inputs[0].links[0]
        return parse_vector(l.from_node, l.from_socket)

    elif node.type == 'GROUP':
        return parse_group(node, socket)

    elif node.type == 'GROUP_INPUT':
        return parse_input_group(node, socket)

    elif node.type == 'ATTRIBUTE':
        # Vector
        pass

    elif node.type == 'CAMERA':
        # View Vector
        return 'v'

    elif node.type == 'NEW_GEOMETRY':
        if socket == node.outputs[0]: # Position
            return 'wposition'
        elif socket == node.outputs[1]: # Normal
            return 'n'
        elif socket == node.outputs[2]: # Tangent
            return 'vec3(0.0)'
        elif socket == node.outputs[3]: # True Normal
            return 'n'
        elif socket == node.outputs[4]: # Incoming
            trace('asdasdasd')
            return 'v'
        elif socket == node.outputs[5]: # Parametric
            return 'wposition'

    elif node.type == 'HAIR_INFO':
        return 'vec3(0.0)' # Tangent Normal

    elif node.type == 'OBJECT_INFO':
        return 'wposition'

    elif node.type == 'PARTICLE_INFO':
        if socket == node.outputs[3]: # Location
            return 'vec3(0.0)'
        elif socket == node.outputs[5]: # Velocity
            return 'vec3(0.0)'
        elif socket == node.outputs[6]: # Angular Velocity
            return 'vec3(0.0)'

    elif node.type == 'TANGENT':
        return 'vec3(0.0)'

    elif node.type == 'TEX_COORD':
        #obj = node.object
        #dupli = node.from_dupli
        if socket == node.outputs[0]: # Generated
            return 'vec2(0.0)'
        elif socket == node.outputs[1]: # Normal
            return 'vec2(0.0)'
        elif socket == node.outputs[2]: # UV
            return 'vec2(0.0)'
        elif socket == node.outputs[3]: # Object
            return 'vec2(0.0)'
        elif socket == node.outputs[4]: # Camera
            return 'vec2(0.0)'
        elif socket == node.outputs[5]: # Window
            return 'vec2(0.0)'
        elif socket == node.outputs[6]: # Reflection
            return 'vec2(0.0)'

    elif node.type == 'UVMAP':
        #map = node.uv_map
        #dupli = node.from_dupli
        return 'vec2(0.0)'

    elif node.type == 'BUMP':
        #invert = node.invert
        # strength = parse_value_input(node.inputs[0])
        # distance = parse_value_input(node.inputs[1])
        # height = parse_value_input(node.inputs[2])
        # nor = parse_vector_input(node.inputs[3])
        return 'vec3(0.0)'

    elif node.type == 'MAPPING':
        # vector = parse_vector_input(node.inputs[0])
        return 'vec3(0.0)'

    elif node.type == 'NORMAL':
        if socket == node.outputs[0]:
            return vec3(node.outputs[0].default_value)
        elif socket == node.outputs[1]: # TODO: is parse_value path preferred?
            nor = parse_vector_input(node.inputs[0])
            return 'vec3(dot({0}, {1}))'.format(vec3(node.outputs[0].default_value), nor)

    elif node.type == 'NORMAL_MAP':
        #space = node.space
        #map = node.uv_map
        # strength = parse_value_input(node.inputs[0])
        # color = parse_vector_input(node.inputs[1])
        return 'vec3(0.0)'

    elif node.type == 'CURVE_VEC':
        # fac = parse_value_input(node.inputs[0])
        # Pass throuh
        return parse_vector_input(node.inputs[1])

    elif node.type == 'VECT_TRANSFORM':
        #type = node.vector_type
        #conv_from = node.convert_from
        #conv_to = node.convert_to
        # Pass throuh
        return parse_vector_input(node.inputs[0])

    elif node.type == 'COMBXYZ':
        x = parse_value_input(node.inputs[0])
        y = parse_value_input(node.inputs[1])
        z = parse_value_input(node.inputs[2])
        return 'vec3({0}, {1}, {2})'.format(x, y, z)

    elif node.type == 'VECT_MATH':
        vec1 = parse_vector_input(node.inputs[0])
        vec2 = parse_vector_input(node.inputs[1])
        op = node.operation
        if op == 'ADD':
            return '({0} + {1})'.format(vec1, vec2)
        elif op == 'SUBTRACT':
            return '({0} - {1})'.format(vec1, vec2)
        elif op == 'AVERAGE':
            return '(({0} + {1}) / 2.0)'.format(vec1, vec2)
        elif op == 'DOT_PRODUCT':
            return 'vec3(dot({0}, {1}))'.format(vec1, vec2)
        elif op == 'CROSS_PRODUCT':
            return 'cross({0}, {1})'.format(vec1, vec2)
        elif op == 'NORMALIZE':
            return 'normalize({0})'.format(vec1)

def parse_value_input(inp):
    if inp.is_linked:
        l = inp.links[0]
        if l.from_socket.type == 'VALUE':
            return parse_value(l.from_node, l.from_socket)
        else:
            return '0.0'
    else:
        return vec1(inp.default_value)

def parse_value(node, socket):
    if node.type == 'REROUTE':
        l = node.inputs[0].links[0]
        return parse_value(l.from_node, l.from_socket)

    elif node.type == 'GROUP':
        return parse_group(node, socket)

    elif node.type == 'GROUP_INPUT':
        return parse_input_group(node, socket)

    elif node.type == 'ATTRIBUTE':
        # Fac
        return '1.0'

    elif node.type == 'CAMERA':
        # View Z Depth
        if socket == node.outputs[1]:
            return 'gl_FragCoord.z'
        # View Distance
        else:
            return 'length(eyeDir)'

    elif node.type == 'FRESNEL':
        ior = parse_value_input(node.inputs[0])
        #nor = parse_vectorZ_input(node.inputs[1])
        return 'pow(1.0 - dotNV, 7.25 / {0})'.format(ior) # max(dotNV, 0.0)

    elif node.type == 'NEW_GEOMETRY':
        if socket == node.outputs[6]: # Backfacing
            return '0.0'
        elif socket == node.outputs[7]: # Pointiness
            return '0.0'

    elif node.type == 'HAIR_INFO':
        # Is Strand
        # Intercept
        # Thickness
        pass

    elif node.type == 'LAYER_WEIGHT':
        blend = parse_value_input(node.inputs[0])
        # nor = parse_vector_input(node.inputs[1])
        if socket == node.outputs[0]: # Fresnel
            return 'pow(1.0 - dotNV, (1.0 - {0}) * 10.0)'.format(blend)
        elif socket == node.outputs[1]: # Facing
            return '((1.0 - dotNV) * {0})'.format(blend)

    elif node.type == 'LIGHT_PATH':
        if socket == node.outputs[0]: # Is Camera Ray
            return '1.0'
        elif socket == node.outputs[0]: # Is Shadow Ray
            return '0.0'
        elif socket == node.outputs[0]: # Is Diffuse Ray
            return '1.0'
        elif socket == node.outputs[0]: # Is Glossy Ray
            return '1.0'
        elif socket == node.outputs[0]: # Is Singular Ray
            return '0.0'
        elif socket == node.outputs[0]: # Is Reflection Ray
            return '0.0'
        elif socket == node.outputs[0]: # Is Transmission Ray
            return '0.0'
        elif socket == node.outputs[0]: # Ray Length
            return '0.0'
        elif socket == node.outputs[0]: # Ray Depth
            return '0.0'
        elif socket == node.outputs[0]: # Transparent Depth
            return '0.0'
        elif socket == node.outputs[0]: # Transmission Depth
            return '0.0'

    elif node.type == 'OBJECT_INFO':
        if socket == node.outputs[0]: # Object Index
            return '0.0'
        elif socket == node.outputs[0]: # Material Index
            return '0.0'
        elif socket == node.outputs[0]: # Random
            return '0.0'

    elif node.type == 'PARTICLE_INFO':
        if socket == node.outputs[0]: # Index
            return '0.0'
        elif socket == node.outputs[1]: # Age
            return '0.0'
        elif socket == node.outputs[2]: # Lifetime
            return '0.0'
        elif socket == node.outputs[4]: # Size
            return '0.0'

    elif node.type == 'VALUE':
        return vec1(node.outputs[0].default_value)

    elif node.type == 'WIREFRAME':
        #node.use_pixel_size
        # size = parse_value_input(node.inputs[0])
        return '0.0'

    elif node.type == 'TEX_BRICK':
        return '0.0'

    elif node.type == 'TEX_CHECKER':
        return '0.0'

    elif node.type == 'TEX_GRADIENT':
        return '0.0'

    elif node.type == 'TEX_IMAGE':
        return '0.0'

    elif node.type == 'TEX_MAGIC':
        return '0.0'

    elif node.type == 'TEX_MUSGRAVE':
        return '0.0'

    elif node.type == 'TEX_NOISE':
        return '0.0'

    elif node.type == 'TEX_POINTDENSITY':
        return '0.0'

    elif node.type == 'TEX_VORONOI':
        return '0.0'

    elif node.type == 'TEX_WAVE':
        return '0.0'

    elif node.type == 'LIGHT_FALLOFF':
        return '0.0'

    elif node.type == 'NORMAL':
        nor = parse_vector_input(node.inputs[0])
        return 'dot({0}, {1})'.format(vec3(node.outputs[0].default_value), nor)

    elif node.type == 'VALTORGB': # ColorRamp
        return '1.0'

    elif node.type == 'MATH':
        val1 = parse_value_input(node.inputs[0])
        val2 = parse_value_input(node.inputs[1])
        op = node.operation
        if op == 'ADD':
            out_val = '({0} + {1})'.format(val1, val2)
        elif op == 'SUBTRACT':
            out_val = '({0} - {1})'.format(val1, val2)
        elif op == 'MULTIPLY':
            out_val = '({0} * {1})'.format(val1, val2)
        elif op == 'DIVIDE':
            out_val = '({0} / {1})'.format(val1, val2)
        elif op == 'SINE':
            out_val = 'sin({0}, {1})'.format(val1, val2)
        elif op == 'COSINE':
            out_val = 'cos({0}, {1})'.format(val1, val2)
        elif op == 'TANGENT':
            out_val = 'tan({0}, {1})'.format(val1, val2)
        elif op == 'ARCSINE':
            out_val = 'asin({0}, {1})'.format(val1, val2)
        elif op == 'ARCCOSINE':
            out_val = 'acos({0}, {1})'.format(val1, val2)
        elif op == 'ARCTANGENT':
            out_val = 'atan({0}, {1})'.format(val1, val2)
        elif op == 'POWER':
            out_val = 'pow({0}, {1})'.format(val1, val2)
        elif op == 'LOGARITHM':
            out_val = 'log({0})'.format(val1)
        elif op == 'MINIMUM':
            out_val = 'min({0}, {1})'.format(val1, val2)
        elif op == 'MAXIMUM':
            out_val = 'max({0}, {1})'.format(val1, val2)
        elif op == 'ROUND':
            out_val = 'round({0})'.format(val1)
        elif op == 'LESS_THAN':
            out_val = 'float({0} < {1})'.format(val1, val2)
        elif op == 'GREATER_THAN':
            out_val = 'float({0} > {1})'.format(val1, val2)
        elif op == 'MODULO':
            out_val = 'float({0} % {1})'.format(val1, val2)
        elif op == 'ABSOLUTE':
            out_val = 'abs({0})'.format(val1)
        if node.use_clamp:
            return 'clamp({0}, 0.0, 1.0)'.format(out_val)
        else:
            return out_val

    elif node.type == 'RGBTOBW':
        col = parse_vector_input(node.inputs[0])
        return '((({0}.r * 0.3 + {0}.g * 0.59 + {0}.b * 0.11) / 3.0) * 2.5)'.format(col)

    elif node.type == 'SEPHSV':
        return '0.0'

    elif node.type == 'SEPRGB':
        col = parse_vector_input(node.inputs[0])
        if socket == node.outputs[0]:
            return '{0}.r'.format(col)
        elif socket == node.outputs[1]:
            return '{0}.g'.format(col)
        elif socket == node.outputs[2]:
            return '{0}.b'.format(col)

    elif node.type == 'SEPXYZ':
        vec = parse_vector_input(node.inputs[0])
        if socket == node.outputs[0]:
            return '{0}.x'.format(vec)
        elif socket == node.outputs[1]:
            return '{0}.y'.format(vec)
        elif socket == node.outputs[2]:
            return '{0}.z'.format(vec)

    elif node.type == 'VECT_MATH':
        vec1 = parse_vector_input(node.inputs[0])
        vec2 = parse_vector_input(node.inputs[1])
        op = node.operation
        if op == 'DOT_PRODUCT':
            return 'dot({0}, {1})'.format(vec1, vec2)
        else:
            return '0.0'

def vec1(v):
    return str(v)

def vec2(v):
    return 'vec2({0}, {1})'.format(v[0], v[1])

def vec3(v):
    return 'vec3({0}, {1}, {2})'.format(v[0], v[1], v[2])

def vec4(v):
    return 'vec4({0}, {1}, {2}, {3})'.format(v[0], v[1], v[2], v[3])
