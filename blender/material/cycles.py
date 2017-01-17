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
import assets
import make_state
import material.mat_state as mat_state
import material.texture as texture
import material.functions as functions
import log

def parse(nodes, vert, frag, geom, tesc, tese, parse_surface=True, parse_opacity=True, parse_displacement=True):
    output_node = node_by_type(nodes, 'OUTPUT_MATERIAL')
    if output_node != None:
        parse_output(output_node, vert, frag, geom, tesc, tese, parse_surface, parse_opacity, parse_displacement)

def parse_output(node, _vert, _frag, _geom, _tesc, _tese, _parse_surface, _parse_opacity, parse_displacement):
    global parsed # Compute nodes only once
    global parents
    global normal_written # Normal socket is linked on shader node - overwrite fs normal
    global curshader # Active shader - frag for surface / tese for displacement
    global vert
    global frag
    global geom
    global tesc
    global tese
    global parse_surface
    global parse_opacity
    global parsing_basecol
    global parse_teximage_vector
    vert = _vert
    frag = _frag
    geom = _geom
    tesc = _tesc
    tese = _tese
    parse_surface = _parse_surface
    parse_opacity = _parse_opacity
    parsing_basecol = False
    parse_teximage_vector = True

    # Surface
    if parse_surface or parse_opacity:
        parsed = []
        parents = []
        normal_written = False
        curshader = frag
        
        out_basecol, out_roughness, out_metallic, out_occlusion, out_opacity = parse_shader_input(node.inputs[0])
        if parse_surface:
            frag.write('basecol = {0};'.format(out_basecol))
            frag.write('roughness = {0};'.format(out_roughness))
            frag.write('metallic = {0};'.format(out_metallic))
            frag.write('occlusion = {0};'.format(out_occlusion))
        if parse_opacity:
            frag.write('opacity = {0};'.format(out_opacity))

    # Volume
    # parse_volume_input(node.inputs[1])

    # Displacement
    if parse_displacement and armutils.tess_enabled(make_state.target) and node.inputs[2].is_linked and tese != None:
        parsed = []
        parents = []
        normal_written = False
        curshader = tese

        out_disp = parse_displacement_input(node.inputs[2])
        tese.write('float disp = {0};'.format(out_disp))

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

def parse_group_input(node, socket):
    index = socket_index(node, socket)
    parent = parents.pop() # Leaving group
    inp = parent.inputs[index]
    res = parse_input(inp)
    parents.append(parent) # Return to group
    return res

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

        if l.from_node.type == 'REROUTE':
            return parse_shader_input(l.from_node.inputs[0])

        return parse_shader(l.from_node, l.from_socket)
    else:
        out_basecol = 'vec3(0.8)'
        out_roughness = '0.0'
        out_metallic = '0.0'
        out_occlusion = '1.0'
        out_opacity = '1.0'
        return out_basecol, out_roughness, out_metallic, out_occlusion, out_opacity

def write_normal(inp):
    if inp.is_linked:
        normal_res = parse_vector_input(inp)
        if normal_res != None:
            curshader.write('n = {0};'.format(normal_res))
            normal_written = True

def parse_shader(node, socket):   
    global parsing_basecol
    out_basecol = 'vec3(0.8)'
    out_roughness = '0.0'
    out_metallic = '0.0'
    out_occlusion = '1.0'
    out_opacity = '1.0'

    if node.type == 'GROUP':
        if node.node_tree.name.startswith('Armory PBR'):
            
            if parse_surface:
                # Base color
                parsing_basecol = True
                out_basecol = parse_vector_input(node.inputs[0])
                parsing_basecol = False
                # Occlusion TODO: deprecated, occlussion is value instead of vector now
                if node.inputs[1].type == 'RGBA':
                    out_occlusion = '{0}.r'.format(parse_vector_input(node.inputs[1]))
                else:
                    out_occlusion = parse_value_input(node.inputs[1])
                if node.inputs[2].is_linked or node.inputs[2].default_value != 1.0:
                    out_occlusion = '({0} * {1})'.format(out_occlusion, parse_value_input(node.inputs[2]))
                # Roughness
                out_roughness = parse_value_input(node.inputs[3])
                if node.inputs[4].is_linked or node.inputs[4].default_value != 1.0:
                    out_roughness = '({0} * {1})'.format(out_roughness, parse_value_input(node.inputs[4]))
                # Metallic
                out_metallic = parse_value_input(node.inputs[5])
                # Normal
                if node.inputs[6].is_linked and node.inputs[6].links[0].from_node.type == 'NORMAL_MAP':
                    log.warn(mat_state.material.name + ' - Do not use Normal Map node with Armory PBR, connect Image Texture directly')
                parse_normal_map_color_input(node.inputs[6], node.inputs[7])
                # Emission
                if node.inputs[8].is_linked:
                    parsing_basecol = True
                    out_emission = parse_vector_input(node.inputs[8])
                    parsing_basecol = False
                    if node.inputs[9].is_linked or node.inputs[9].default_value != 1.0:
                        out_emission = '({0} * {1})'.format(out_emission, parse_value_input(node.inputs[9]))
                    out_basecol = '({0} + {1})'.format(out_basecol, out_emission)
            
            if parse_opacity:
                out_opacity = parse_value_input(node.inputs[12])
                if node.inputs[13].is_linked or node.inputs[13].default_value != 1.0:
                    out_opacity = '({0} * {1})'.format(out_opacity, parse_value_input(node.inputs[13]))
        else:
            return parse_group(node, socket)

    elif node.type == 'GROUP_INPUT':
        return parse_group_input(node, socket)

    elif node.type == 'MIX_SHADER':
        fac = parse_value_input(node.inputs[0])
        fac_var = node_name(node.name) + '_fac'
        fac_inv_var = node_name(node.name) + '_fac_inv'
        curshader.write('float {0} = {1};'.format(fac_var, fac))
        curshader.write('float {0} = 1.0 - {1};'.format(fac_inv_var, fac_var))
        bc1, rough1, met1, occ1, opac1 = parse_shader_input(node.inputs[1])
        bc2, rough2, met2, occ2, opac2 = parse_shader_input(node.inputs[2])
        if parse_surface:
            parsing_basecol = True
            out_basecol = '({0} * {3} + {1} * {2})'.format(bc1, bc2, fac_var, fac_inv_var)
            parsing_basecol = False
            out_roughness = '({0} * {3} + {1} * {2})'.format(rough1, rough2, fac_var, fac_inv_var)
            out_metallic = '({0} * {3} + {1} * {2})'.format(met1, met2, fac_var, fac_inv_var)
            out_occlusion = '({0} * {3} + {1} * {2})'.format(occ1, occ2, fac_var, fac_inv_var)
        if parse_opacity:
            out_opacity = '({0} * {3} + {1} * {2})'.format(opac1, opac2, fac_var, fac_inv_var)

    elif node.type == 'ADD_SHADER':
        bc1, rough1, met1, occ1, opac1 = parse_shader_input(node.inputs[0])
        bc2, rough2, met2, occ2, opac2 = parse_shader_input(node.inputs[1])
        if parse_surface:
            parsing_basecol = True
            out_basecol = '({0} + {1})'.format(bc1, bc2)
            parsing_basecol = False
            out_roughness = '({0} * 0.5 + {1} * 0.5)'.format(rough1, rough2)
            out_metallic = '({0} * 0.5 + {1} * 0.5)'.format(met1, met2)
            out_occlusion = '({0} * 0.5 + {1} * 0.5)'.format(occ1, occ2)
        if parse_opacity:
            out_opacity = '({0} * 0.5 + {1} * 0.5)'.format(opac1, opac2)

    elif node.type == 'BSDF_DIFFUSE':
        if parse_surface:
            write_normal(node.inputs[2])
            parsing_basecol = True
            out_basecol = parse_vector_input(node.inputs[0])
            parsing_basecol = False
            out_roughness = parse_value_input(node.inputs[1])

    elif node.type == 'BSDF_GLOSSY':
        if parse_surface:
            write_normal(node.inputs[2])
            parsing_basecol = True
            out_basecol = parse_vector_input(node.inputs[0])
            parsing_basecol = False
            out_roughness = parse_value_input(node.inputs[1])
            out_metallic = '1.0'

    elif node.type == 'AMBIENT_OCCLUSION':
        if parse_surface:    
            # Single channel
            out_occlusion = parse_vector_input(node.inputs[0]) + '.r'

    elif node.type == 'BSDF_ANISOTROPIC':
        if parse_surface:
            write_normal(node.inputs[4])
            # Revert to glossy
            parsing_basecol = True
            out_basecol = parse_vector_input(node.inputs[0])
            parsing_basecol = False
            out_roughness = parse_value_input(node.inputs[1])
            out_metallic = '1.0'

    elif node.type == 'EMISSION':
        if parse_surface:
            # Multiply basecol
            parsing_basecol = True
            out_basecol = parse_vector_input(node.inputs[0])
            parsing_basecol = False
            strength = parse_value_input(node.inputs[1])
            out_basecol = '({0} * {1} * 50.0)'.format(out_basecol, strength)

    elif node.type == 'BSDF_GLASS':
        if parse_surface:
            write_normal(node.inputs[3])
            out_roughness = parse_value_input(node.inputs[1])
        if parse_opacity:
            out_opacity = '(1.0 - {0}.r)'.format(parse_vector_input(node.inputs[0]))

    elif node.type == 'BSDF_HAIR':
        pass

    elif node.type == 'HOLDOUT':
        if parse_surface:
            # Occlude
            out_occlusion = '0.0'

    elif node.type == 'BSDF_REFRACTION':
        # write_normal(node.inputs[3])
        pass

    elif node.type == 'SUBSURFACE_SCATTERING':
        # write_normal(node.inputs[4])
        pass

    elif node.type == 'BSDF_TOON':
        # write_normal(node.inputs[3])
        pass

    elif node.type == 'BSDF_TRANSLUCENT':
        if parse_surface:
            write_normal(node.inputs[1])
        if parse_opacity:
            out_opacity = '(1.0 - {0}.r)'.format(parse_vector_input(node.inputs[0]))

    elif node.type == 'BSDF_TRANSPARENT':
        if parse_opacity:
            out_opacity = '(1.0 - {0}.r)'.format(parse_vector_input(node.inputs[0]))

    elif node.type == 'BSDF_VELVET':
        if parse_surface:
            write_normal(node.inputs[2])
            parsing_basecol = True
            out_basecol = parse_vector_input(node.inputs[0])
            parsing_basecol = False
            out_roughness = '1.0'
            out_metallic = '1.0'

    elif node.type == 'VOLUME_ABSORPTION':
        pass

    elif node.type == 'VOLUME_SCATTER':
        pass

    return out_basecol, out_roughness, out_metallic, out_occlusion, out_opacity

def parse_displacement_input(inp):
    if inp.is_linked:
        l = inp.links[0]

        if l.from_node.type == 'REROUTE':
            return parse_displacement_input(l.from_node.inputs[0])

        return parse_value_input(inp)
    else:
        return None

def res_var_name(node, socket):
    return node_name(node.name) + '_' + socket_name(socket.name) + '_res'

def write_result(l):
    res_var = res_var_name(l.from_node, l.from_socket)
    st = l.from_socket.type
    if res_var not in parsed:
        parsed.append(res_var)
        if st == 'RGB' or st == 'RGBA':
            res = parse_rgb(l.from_node, l.from_socket)
            if res == None:
                return None
            curshader.write('vec3 {0} = {1};'.format(res_var, res))
        elif st == 'VECTOR':
            res = parse_vector(l.from_node, l.from_socket)
            if res == None:
                return None
            size = 3
            if isinstance(res, tuple):
                size = res[1]
                res = res[0]
            curshader.write('vec{2} {0} = {1};'.format(res_var, res, size))
        elif st == 'VALUE':
            res = parse_value(l.from_node, l.from_socket)
            if res == None:
                return None
            curshader.write('float {0} = {1};'.format(res_var, res))
    # Normal map already parsed, return
    elif l.from_node.type == 'NORMAL_MAP':
        return None
    return res_var

def parse_vector_input(inp):
    if inp.is_linked:
        l = inp.links[0]

        if l.from_node.type == 'REROUTE':
            return parse_vector_input(l.from_node.inputs[0])

        res_var = write_result(l)
        st = l.from_socket.type        
        if st == 'RGB' or st == 'RGBA' or st == 'VECTOR':
            return res_var
        else: # VALUE
            return 'vec3({0})'.format(res_var)
    else:
        if inp.type == 'VALUE': # Unlinked reroute
            return tovec3([0.0, 0.0, 0.0])
        else:
            return tovec3(inp.default_value)

def parse_rgb(node, socket):

    if node.type == 'GROUP':
        return parse_group(node, socket)

    elif node.type == 'GROUP_INPUT':
        return parse_group_input(node, socket)

    elif node.type == 'ATTRIBUTE':
        # Vcols only for now
        # node.attribute_name
        mat_state.data.add_elem('col', 3)
        return 'vcolor'

    elif node.type == 'RGB':
        return tovec3(socket.default_value)

    elif node.type == 'TEX_BRICK':
        # Pass through
        return tovec3([0.0, 0.0, 0.0])

    elif node.type == 'TEX_CHECKER':
        curshader.add_function(functions.str_tex_checker)
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'wposition'
        col1 = parse_vector_input(node.inputs[1])
        col2 = parse_vector_input(node.inputs[2])
        scale = parse_value_input(node.inputs[3])
        return 'tex_checker({0}, {1}, {2}, {3})'.format(co, col1, col2, scale)

    elif node.type == 'TEX_ENVIRONMENT':
        # Pass through
        return tovec3([0.0, 0.0, 0.0])

    elif node.type == 'TEX_GRADIENT':
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'wposition'
        grad = node.gradient_type
        if grad == 'LINEAR':
            f = '{0}.x'.format(co)
        elif grad == 'QUADRATIC':
            f = '0.0'
        elif grad == 'EASING':
            f = '0.0'
        elif grad == 'DIAGONAL':
            f = '({0}.x + {0}.y) * 0.5'.format(co)
        elif grad == 'RADIAL':
            f = 'atan({0}.y, {0}.x) / PI2 + 0.5'.format(co)
        elif grad == 'QUADRATIC_SPHERE':
            f = '0.0'
        elif grad == 'SPHERICAL':
            f = 'max(1.0 - sqrt({0}.x * {0}.x + {0}.y * {0}.y + {0}.z * {0}.z), 0.0)'.format(co)
        return 'vec3(clamp({0}, 0.0, 1.0))'.format(f)

    elif node.type == 'TEX_IMAGE':
        # Already fetched
        if res_var_name(node, node.outputs[1]) in parsed:
            return '{0}.rgb'.format(store_var_name(node))
        tex_name = armutils.safe_source_name(node.name)
        tex = texture.make_texture(node, tex_name)
        if tex != None:
            to_linear = parsing_basecol and not tex['file'].endswith('.hdr')
            return '{0}.rgb'.format(texture_store(node, tex, tex_name, to_linear))
        else:
            tex_store = store_var_name(node) # Pink color for missing texture
            curshader.write('vec4 {0} = vec4(1.0, 0.0, 1.0, 1.0);'.format(tex_store))
            return '{0}.rgb'.format(tex_store)

    elif node.type == 'TEX_MAGIC':
        # Pass through
        return tovec3([0.0, 0.0, 0.0])

    elif node.type == 'TEX_MUSGRAVE':
        # Fall back to noise
        curshader.add_function(functions.str_tex_noise)
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'wposition'
        scale = parse_value_input(node.inputs[1])
        # detail = parse_value_input(node.inputs[2])
        # distortion = parse_value_input(node.inputs[3])
        return 'vec3(tex_noise_f({0} * {1}))'.format(co, scale)

    elif node.type == 'TEX_NOISE':
        curshader.add_function(functions.str_tex_noise)
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'wposition'
        scale = parse_value_input(node.inputs[1])
        # detail = parse_value_input(node.inputs[2])
        # distortion = parse_value_input(node.inputs[3])
        # Slow..
        return 'vec3(tex_noise({0} * {1}), tex_noise({0} * {1} + 0.33), tex_noise({0} * {1} + 0.66))'.format(co, scale)

    elif node.type == 'TEX_POINTDENSITY':
        # Pass through
        return tovec3([0.0, 0.0, 0.0])

    elif node.type == 'TEX_SKY':
        # Pass through
        return tovec3([0.0, 0.0, 0.0])

    elif node.type == 'TEX_VORONOI':
        curshader.add_function(functions.str_tex_voronoi)
        assets.add(armutils.get_sdk_path() + '/armory/Assets/' + 'noise64.png')
        assets.add_embedded_data('noise64.png')
        curshader.add_uniform('sampler2D snoise', link='_noise64')
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'wposition'
        scale = parse_value_input(node.inputs[1])
        if node.coloring == 'INTENSITY':
            return 'vec3(tex_voronoi({0} / {1}).a)'.format(co, scale)
        else: # CELLS
            return 'tex_voronoi({0} / {1}).rgb'.format(co, scale)

    elif node.type == 'TEX_WAVE':
        # Pass through
        return tovec3([0.0, 0.0, 0.0])

    elif node.type == 'BRIGHTCONTRAST':
        out_col = parse_vector_input(node.inputs[0])
        bright = parse_value_input(node.inputs[1])
        contr = parse_value_input(node.inputs[2])
        curshader.add_function(\
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
#         curshader.add_function(\
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
        fac_var = node_name(node.name) + '_fac'
        curshader.write('float {0} = {1};'.format(fac_var, fac))
        col1 = parse_vector_input(node.inputs[1])
        col2 = parse_vector_input(node.inputs[2])
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
        else:
            return out_col

    elif node.type == 'CURVE_RGB':
        # Pass throuh
        return parse_vector_input(node.inputs[1])

    elif node.type == 'BLACKBODY':
        # Pass constant
        return tovec3([0.84, 0.38, 0.0])

    elif node.type == 'VALTORGB': # ColorRamp
        fac = parse_value_input(node.inputs[0])
        interp = node.color_ramp.interpolation
        elems = node.color_ramp.elements
        if len(elems) == 1:
            return tovec3(elems[0].color)
        if interp == 'CONSTANT':
            fac_var = node_name(node.name) + '_fac'
            curshader.write('float {0} = {1};'.format(fac_var, fac))
            # Get index
            out_i = '0'
            for i in  range(1, len(elems)):
                out_i += ' + ({0} > {1} ? 1 : 0)'.format(fac_var, elems[i].position)
            # Write cols array
            cols_var = node_name(node.name) + '_cols'
            curshader.write('vec3 {0}[{1}];'.format(cols_var, len(elems)))
            for i in range(0, len(elems)):
                curshader.write('{0}[{1}] = vec3({2}, {3}, {4});'.format(cols_var, i, elems[i].color[0], elems[i].color[1], elems[i].color[2]))
            return '{0}[{1}]'.format(cols_var, out_i)
        else: # Linear, .. - 2 elems only, end pos assumed to be 1
            # float f = clamp((pos - start) * (1.0 / (1.0 - start)), 0.0, 1.0);
            return 'mix({0}, {1}, clamp(({2} - {3}) * (1.0 / (1.0 - {3})), 0.0, 1.0))'.format(tovec3(elems[0].color), tovec3(elems[1].color), fac, elems[0].position)

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
        return tovec3([0.0, 0.0, 0.0])

    elif node.type == 'COMBRGB':
        r = parse_value_input(node.inputs[0])
        g = parse_value_input(node.inputs[1])
        b = parse_value_input(node.inputs[2])
        return 'vec3({0}, {1}, {2})'.format(r, g, b)

    elif node.type == 'WAVELENGTH':
        # Pass constant
        return tovec3([0.0, 0.27, 0.19])

def store_var_name(node):
    return node_name(node.name) + '_store'

def texture_store(node, tex, tex_name, to_linear=False):
    global parse_teximage_vector
    mat_state.mat_context['bind_textures'].append(tex)
    mat_state.data.add_elem('tex', 2)
    curshader.add_uniform('sampler2D {0}'.format(tex_name))
    if node.inputs[0].is_linked and parse_teximage_vector:
        uv_name = parse_vector_input(node.inputs[0])
    else:
        uv_name = 'texCoord'
    tex_store = store_var_name(node)
    curshader.write('vec4 {0} = texture({1}, {2}.xy);'.format(tex_store, tex_name, uv_name))
    if to_linear:
        curshader.write('{0}.rgb = pow({0}.rgb, vec3(2.2));'.format(tex_store))
    return tex_store

def parse_vector(node, socket):

    if node.type == 'GROUP':
        return parse_group(node, socket)

    elif node.type == 'GROUP_INPUT':
        return parse_group_input(node, socket)

    elif node.type == 'ATTRIBUTE':
        # UVMaps only for now
        mat_state.data.add_elem('tex', 2)
        mat = mat_state.material
        mat_users = mat_state.mat_users
        if mat_users != None and mat in mat_users:
            mat_user = mat_users[mat][0]
            if hasattr(mat_user.data, 'uv_layers'): # No uvlayers for Curve
                lays = mat_user.data.uv_layers
                # Second uvmap referenced
                if len(lays) > 1 and node.attribute_name == lays[1].name:
                    mat_state.data.add_elem('tex1', 2)
                    return 'texCoord1', 2
        return 'texCoord', 2

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
            return 'vec2(0.0)', 2
        elif socket == node.outputs[1]: # Normal
            return 'vec2(0.0)', 2
        elif socket == node.outputs[2]: # UV
            mat_state.data.add_elem('tex', 2)
            return 'texCoord', 2
        elif socket == node.outputs[3]: # Object
            return 'vec2(0.0)', 2
        elif socket == node.outputs[4]: # Camera
            return 'vec2(0.0)', 2
        elif socket == node.outputs[5]: # Window
            return 'vec2(0.0)', 2
        elif socket == node.outputs[6]: # Reflection
            return 'vec2(0.0)', 2

    elif node.type == 'UVMAP':
        #map = node.uv_map
        #dupli = node.from_dupli
        return 'vec2(0.0)', 2

    elif node.type == 'BUMP':
        #invert = node.invert
        # strength = parse_value_input(node.inputs[0])
        # distance = parse_value_input(node.inputs[1])
        # height = parse_value_input(node.inputs[2])
        # nor = parse_vector_input(node.inputs[3])
        # Sample height around the normal and compute normal
        return 'n'

    elif node.type == 'MAPPING':
        return parse_vector_input(node.inputs[0]), 2

    elif node.type == 'NORMAL':
        if socket == node.outputs[0]:
            return tovec3(node.outputs[0].default_value)
        elif socket == node.outputs[1]: # TODO: is parse_value path preferred?
            nor = parse_vector_input(node.inputs[0])
            return 'vec3(dot({0}, {1}))'.format(tovec3(node.outputs[0].default_value), nor)

    elif node.type == 'NORMAL_MAP':
        if curshader == tese:
            return parse_vector_input(node.inputs[1])
        else:
            #space = node.space
            #map = node.uv_map
            # strength = parse_value_input(node.inputs[0])
            parse_normal_map_color_input(node.inputs[1]) # Color
            return None

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

def parse_normal_map_color_input(inp, str_inp=None):
    global parse_teximage_vector
    if inp.is_linked == False:
        return
    frag.write_pre = True
    parse_teximage_vector = False # Force texCoord for normal map image vector
    frag.write('vec3 n = ({0}) * 2.0 - 1.0;'.format(parse_vector_input(inp)))
    parse_teximage_vector = True
    frag.write('n = normalize(TBN * normalize(n));')
    mat_state.data.add_elem('tan', 3)
    frag.write_pre = False

def parse_value_input(inp):
    if inp.is_linked:
        l = inp.links[0]

        if l.from_node.type == 'REROUTE':
            return parse_value_input(l.from_node.inputs[0])

        res_var = write_result(l)
        st = l.from_socket.type        
        if st == 'RGB' or st == 'RGBA' or st == 'VECTOR':
            return '{0}.x'.format(res_var)
        else: # VALUE
            return res_var
    else:
        return tovec1(inp.default_value)

def parse_value(node, socket):

    if node.type == 'GROUP':
        if node.node_tree.name.startswith('Armory PBR'):
            # Displacement
            if socket == node.outputs[1]:
                res = parse_value_input(node.inputs[10])
                if node.inputs[11].is_linked or node.inputs[11].default_value != 1.0:
                    res = "({0} * {1})".format(res, parse_value_input(node.inputs[11]))
                return res
            else:
                return None
        else:
            return parse_group(node, socket)

    elif node.type == 'GROUP_INPUT':
        return parse_group_input(node, socket)

    elif node.type == 'ATTRIBUTE':
        # Pass time till drivers are implemented
        if node.attribute_name == 'time':
            curshader.add_uniform('float time', link='_time')
            return 'time'
        else:
            return '0.0'

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
        return '0.5'

    elif node.type == 'LAYER_WEIGHT':
        blend = parse_value_input(node.inputs[0])
        # nor = parse_vector_input(node.inputs[1])
        if socket == node.outputs[0]: # Fresnel
            return 'clamp(pow(1.0 - dotNV, (1.0 - {0}) * 10.0), 0.0, 1.0)'.format(blend)
        elif socket == node.outputs[1]: # Facing
            return '((1.0 - dotNV) * {0})'.format(blend)

    elif node.type == 'LIGHT_PATH':
        if socket == node.outputs[0]: # Is Camera Ray
            return '1.0'
        elif socket == node.outputs[1]: # Is Shadow Ray
            return '0.0'
        elif socket == node.outputs[2]: # Is Diffuse Ray
            return '1.0'
        elif socket == node.outputs[3]: # Is Glossy Ray
            return '1.0'
        elif socket == node.outputs[4]: # Is Singular Ray
            return '0.0'
        elif socket == node.outputs[5]: # Is Reflection Ray
            return '0.0'
        elif socket == node.outputs[6]: # Is Transmission Ray
            return '0.0'
        elif socket == node.outputs[7]: # Ray Length
            return '0.0'
        elif socket == node.outputs[8]: # Ray Depth
            return '0.0'
        elif socket == node.outputs[9]: # Transparent Depth
            return '0.0'
        elif socket == node.outputs[10]: # Transmission Depth
            return '0.0'

    elif node.type == 'OBJECT_INFO':
        if socket == node.outputs[0]: # Object Index
            return '0.0'
        elif socket == node.outputs[1]: # Material Index
            return '0.0'
        elif socket == node.outputs[2]: # Random
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
        return tovec1(node.outputs[0].default_value)

    elif node.type == 'WIREFRAME':
        #node.use_pixel_size
        # size = parse_value_input(node.inputs[0])
        return '0.0'

    elif node.type == 'TEX_BRICK':
        return '0.0'

    elif node.type == 'TEX_CHECKER':
        # TODO: do not recompute when color socket is also connected
        curshader.add_function(functions.str_tex_checker)
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'wposition'
        col1 = parse_vector_input(node.inputs[1])
        col2 = parse_vector_input(node.inputs[2])
        scale = parse_value_input(node.inputs[3])
        return 'tex_checker({0}, {1}, {2}, {3}).r'.format(co, col1, col2, scale)

    elif node.type == 'TEX_GRADIENT':
        return '0.0'

    elif node.type == 'TEX_IMAGE':
        # Already fetched
        if res_var_name(node, node.outputs[0]) in parsed:
            return '{0}.a'.format(store_var_name(node))
        tex_name = armutils.safe_source_name(node.name)
        tex = texture.make_texture(node, tex_name)
        if tex != None:
            return '{0}.a'.format(texture_store(node, tex, tex_name))
        else:
            tex_store = store_var_name(node) # Pink color for missing texture
            curshader.write('vec4 {0} = vec4(1.0, 0.0, 1.0, 1.0);'.format(tex_store))
            return '{0}.a'.format(tex_store)

    elif node.type == 'TEX_MAGIC':
        return '0.0'

    elif node.type == 'TEX_MUSGRAVE':
        # Fall back to noise
        curshader.add_function(functions.str_tex_noise)
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'wposition'
        scale = parse_value_input(node.inputs[1])
        # detail = parse_value_input(node.inputs[2])
        # distortion = parse_value_input(node.inputs[3])
        return 'tex_noise_f({0} * {1})'.format(co, scale)

    elif node.type == 'TEX_NOISE':
        curshader.add_function(functions.str_tex_noise)
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'wposition'
        scale = parse_value_input(node.inputs[1])
        # detail = parse_value_input(node.inputs[2])
        # distortion = parse_value_input(node.inputs[3])
        return 'tex_noise({0} * {1})'.format(co, scale)

    elif node.type == 'TEX_POINTDENSITY':
        return '0.0'

    elif node.type == 'TEX_VORONOI':
        curshader.add_function(functions.str_tex_voronoi)
        assets.add(armutils.get_sdk_path() + '/armory/Assets/' + 'noise64.png')
        assets.add_embedded_data('noise64.png')
        curshader.add_uniform('sampler2D snoise', link='_noise64')
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'wposition'
        scale = parse_value_input(node.inputs[1])
        if node.coloring == 'INTENSITY':
            return 'tex_voronoi({0} * {1}).a'.format(co, scale)
        else: # CELLS
            return 'tex_voronoi({0} * {1}).r'.format(co, scale)

    elif node.type == 'TEX_WAVE':
        return '0.0'

    elif node.type == 'LIGHT_FALLOFF':
        return '0.0'

    elif node.type == 'NORMAL':
        nor = parse_vector_input(node.inputs[0])
        return 'dot({0}, {1})'.format(tovec3(node.outputs[0].default_value), nor)

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
        elif op == 'POWER':
            out_val = 'pow({0}, {1})'.format(val1, val2)
        elif op == 'LOGARITHM':
            out_val = 'log({0})'.format(val1)
        elif op == 'MINIMUM':
            out_val = 'min({0}, {1})'.format(val1, val2)
        elif op == 'MAXIMUM':
            out_val = 'max({0}, {1})'.format(val1, val2)
        elif op == 'ROUND':
            # out_val = 'round({0})'.format(val1)
            out_val = 'floor({0} + 0.5)'.format(val1)
        elif op == 'LESS_THAN':
            out_val = 'float({0} < {1})'.format(val1, val2)
        elif op == 'GREATER_THAN':
            out_val = 'float({0} > {1})'.format(val1, val2)
        elif op == 'MODULO':
            # out_val = 'float({0} % {1})'.format(val1, val2)
            out_val = 'mod({0}, {1})'.format(val1, val2)
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

def tovec1(v):
    return str(v)

def tovec2(v):
    return 'vec2({0}, {1})'.format(v[0], v[1])

def tovec3(v):
    return 'vec3({0}, {1}, {2})'.format(v[0], v[1], v[2])

def tovec4(v):
    return 'vec4({0}, {1}, {2}, {3})'.format(v[0], v[1], v[2], v[3])

def node_by_type(nodes, ntype):
    for n in nodes:
        if n.type == ntype:
            return n

def socket_index(node, socket):
    for i in range(0, len(node.outputs)):
        if node.outputs[i] == socket:
            return i

def node_name(s):
    s = armutils.safe_source_name(s)
    if len(parents) > 0:
        s = armutils.safe_source_name(parents[-1].name) + '_' + s
    return s

def socket_name(s):
    return armutils.safe_source_name(s)
