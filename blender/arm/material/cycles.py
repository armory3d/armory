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
import math
import bpy
import os
import arm.assets
import arm.utils
import arm.make_state
import arm.log
import arm.material.mat_state as mat_state
import arm.material.cycles_functions as c_functions
import shutil

emission_found = False
particle_info = None # Particle info export

def parse(nodes, con, vert, frag, geom, tesc, tese, parse_surface=True, parse_opacity=True, parse_displacement=True, basecol_only=False):
    output_node = node_by_type(nodes, 'OUTPUT_MATERIAL')
    if output_node != None:
        parse_output(output_node, con, vert, frag, geom, tesc, tese, parse_surface, parse_opacity, parse_displacement, basecol_only)

def parse_output(node, _con, _vert, _frag, _geom, _tesc, _tese, _parse_surface, _parse_opacity, _parse_displacement, _basecol_only):
    global parsed # Compute nodes only once
    global parents
    global normal_parsed
    global curshader # Active shader - frag for surface / tese for displacement
    global con
    global vert
    global frag
    global geom
    global tesc
    global tese
    global parse_surface
    global parse_opacity
    global basecol_only
    global emission_found
    global particle_info
    global sample_bump
    global sample_bump_res
    con = _con
    vert = _vert
    frag = _frag
    geom = _geom
    tesc = _tesc
    tese = _tese
    parse_surface = _parse_surface
    parse_opacity = _parse_opacity
    basecol_only = _basecol_only
    emission_found = False
    particle_info = {}
    particle_info['index'] = False
    particle_info['age'] = False
    particle_info['lifetime'] = False
    particle_info['location'] = False
    particle_info['size'] = False
    particle_info['velocity'] = False
    particle_info['angular_velocity'] = False
    sample_bump = False
    sample_bump_res = ''
    wrd = bpy.data.worlds['Arm']

    # Surface
    if parse_surface or parse_opacity:
        parsed = {}
        parents = []
        normal_parsed = False
        curshader = frag
        
        out_basecol, out_roughness, out_metallic, out_occlusion, out_specular, out_opacity, out_emission = parse_shader_input(node.inputs[0])
        if parse_surface:
            frag.write('basecol = {0};'.format(out_basecol))
            frag.write('roughness = {0};'.format(out_roughness))
            frag.write('metallic = {0};'.format(out_metallic))
            frag.write('occlusion = {0};'.format(out_occlusion))
            frag.write('specular = {0};'.format(out_specular))
            if '_Emission' in wrd.world_defs:
                frag.write('emission = {0};'.format(out_emission))
        if parse_opacity:
            frag.write('opacity = {0};'.format(out_opacity))

    # Volume
    # parse_volume_input(node.inputs[1])

    # Displacement
    if _parse_displacement and disp_enabled() and node.inputs[2].is_linked:
        parsed = {}
        parents = []
        normal_parsed = False
        rpdat = arm.utils.get_rp()
        if rpdat.arm_rp_displacement == 'Tessellation' and tese != None:
            curshader = tese
        else:
            curshader = vert
        out_disp = parse_displacement_input(node.inputs[2])
        curshader.write('vec3 disp = {0};'.format(out_disp))

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
        out_specular = '1.0'
        out_opacity = '1.0'
        out_emission = '0.0'
        return out_basecol, out_roughness, out_metallic, out_occlusion, out_specular, out_opacity, out_emission

def parse_shader(node, socket):
    global emission_found
    out_basecol = 'vec3(0.8)'
    out_roughness = '0.0'
    out_metallic = '0.0'
    out_occlusion = '1.0'
    out_specular = '1.0'
    out_opacity = '1.0'
    out_emission = '0.0'

    if node.type == 'GROUP':
        if node.node_tree.name.startswith('Armory PBR'):     
            if parse_surface:
                # Base color
                out_basecol = parse_vector_input(node.inputs[0])
                # Occlusion
                out_occlusion = parse_value_input(node.inputs[2])
                # Roughness
                out_roughness = parse_value_input(node.inputs[3])
                # Metallic
                out_metallic = parse_value_input(node.inputs[4])
                # Normal
                if node.inputs[5].is_linked and node.inputs[5].links[0].from_node.type == 'NORMAL_MAP':
                    warn(mat_name() + ' - Do not use Normal Map node with Armory PBR, connect Image Texture directly')
                parse_normal_map_color_input(node.inputs[5])
                # Emission
                if node.inputs[6].is_linked or node.inputs[6].default_value != 0.0:
                    out_emission = parse_value_input(node.inputs[6])
                    emission_found = True
            if parse_opacity:
                out_opacity = parse_value_input(node.inputs[1])
        else:
            return parse_group(node, socket)

    elif node.type == 'GROUP_INPUT':
        return parse_group_input(node, socket)

    elif node.type == 'MIX_SHADER':
        prefix = '' if node.inputs[0].is_linked else 'const '
        fac = parse_value_input(node.inputs[0])
        fac_var = node_name(node.name) + '_fac'
        fac_inv_var = node_name(node.name) + '_fac_inv'
        curshader.write('{0}float {1} = {2};'.format(prefix, fac_var, fac))
        curshader.write('{0}float {1} = 1.0 - {2};'.format(prefix, fac_inv_var, fac_var))
        bc1, rough1, met1, occ1, spec1, opac1, emi1 = parse_shader_input(node.inputs[1])
        bc2, rough2, met2, occ2, spec2, opac2, emi2 = parse_shader_input(node.inputs[2])
        if parse_surface:
            out_basecol = '({0} * {3} + {1} * {2})'.format(bc1, bc2, fac_var, fac_inv_var)
            out_roughness = '({0} * {3} + {1} * {2})'.format(rough1, rough2, fac_var, fac_inv_var)
            out_metallic = '({0} * {3} + {1} * {2})'.format(met1, met2, fac_var, fac_inv_var)
            out_occlusion = '({0} * {3} + {1} * {2})'.format(occ1, occ2, fac_var, fac_inv_var)
            out_specular = '({0} * {3} + {1} * {2})'.format(spec1, spec2, fac_var, fac_inv_var)
            out_emission = '({0} * {3} + {1} * {2})'.format(emi1, emi2, fac_var, fac_inv_var)
        if parse_opacity:
            out_opacity = '({0} * {3} + {1} * {2})'.format(opac1, opac2, fac_var, fac_inv_var)

    elif node.type == 'ADD_SHADER':
        bc1, rough1, met1, occ1, spec1, opac1, emi1 = parse_shader_input(node.inputs[0])
        bc2, rough2, met2, occ2, spec2, opac2, emi2 = parse_shader_input(node.inputs[1])
        if parse_surface:
            out_basecol = '({0} + {1})'.format(bc1, bc2)
            out_roughness = '({0} * 0.5 + {1} * 0.5)'.format(rough1, rough2)
            out_metallic = '({0} * 0.5 + {1} * 0.5)'.format(met1, met2)
            out_occlusion = '({0} * 0.5 + {1} * 0.5)'.format(occ1, occ2)
            out_specular = '({0} * 0.5 + {1} * 0.5)'.format(spec1, spec2)
            out_emission = '({0} * 0.5 + {1} * 0.5)'.format(emi1, emi2)
        if parse_opacity:
            out_opacity = '({0} * 0.5 + {1} * 0.5)'.format(opac1, opac2)

    elif node.type == 'BSDF_PRINCIPLED':
        if parse_surface:
            write_normal(node.inputs[19])
            out_basecol = parse_vector_input(node.inputs[0])
            # subsurface = parse_vector_input(node.inputs[1])
            # subsurface_radius = parse_vector_input(node.inputs[2])
            # subsurface_color = parse_vector_input(node.inputs[3])
            out_metallic = parse_value_input(node.inputs[4])
            out_specular = parse_value_input(node.inputs[5])
            # specular_tint = parse_vector_input(node.inputs[6])
            out_roughness = parse_value_input(node.inputs[7])
            # aniso = parse_vector_input(node.inputs[8])
            # aniso_rot = parse_vector_input(node.inputs[9])
            # sheen = parse_vector_input(node.inputs[10])
            # sheen_tint = parse_vector_input(node.inputs[11])
            # clearcoat = parse_vector_input(node.inputs[12])
            # clearcoat_rough = parse_vector_input(node.inputs[13])
            # ior = parse_vector_input(node.inputs[14])
            # transmission = parse_vector_input(node.inputs[15])
            # transmission_roughness = parse_vector_input(node.inputs[16])
            if node.inputs[17].is_linked or node.inputs[17].default_value[0] != 0.0:
                out_emission = '({0}.x)'.format(parse_vector_input(node.inputs[17]))
                emission_found = True
            # clearcoar_normal = parse_vector_input(node.inputs[20])
            # tangent = parse_vector_input(node.inputs[21])
        if parse_opacity:
            if len(node.inputs) > 20:
                out_opacity = parse_value_input(node.inputs[18])

    elif node.type == 'BSDF_DIFFUSE':
        if parse_surface:
            write_normal(node.inputs[2])
            out_basecol = parse_vector_input(node.inputs[0])
            out_roughness = parse_value_input(node.inputs[1])
            out_specular = '0.0'

    elif node.type == 'BSDF_GLOSSY':
        if parse_surface:
            write_normal(node.inputs[2])
            out_basecol = parse_vector_input(node.inputs[0])
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
            out_basecol = parse_vector_input(node.inputs[0])
            out_roughness = parse_value_input(node.inputs[1])
            out_metallic = '1.0'

    elif node.type == 'EMISSION':
        if parse_surface:
            # Multiply basecol
            out_basecol = parse_vector_input(node.inputs[0])
            out_emission = '1.0'
            emission_found = True
            emission_strength = parse_value_input(node.inputs[1])
            out_basecol = '({0} * {1})'.format(out_basecol, emission_strength)

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
        if parse_surface:
            write_normal(node.inputs[4])
            out_basecol = parse_vector_input(node.inputs[0])

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
            out_basecol = parse_vector_input(node.inputs[0])
            out_roughness = '1.0'
            out_metallic = '1.0'

    elif node.type == 'VOLUME_ABSORPTION':
        pass

    elif node.type == 'VOLUME_SCATTER':
        pass

    return out_basecol, out_roughness, out_metallic, out_occlusion, out_specular, out_opacity, out_emission

def parse_displacement_input(inp):
    if inp.is_linked:
        l = inp.links[0]
        if l.from_node.type == 'REROUTE':
            return parse_displacement_input(l.from_node.inputs[0])
        return parse_vector_input(inp)
    else:
        return None

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
            return to_vec3([0.0, 0.0, 0.0])
        else:
            if mat_batch() and inp.is_uniform:
                return to_uniform(inp)
            else:
                return to_vec3(inp.default_value)

def parse_vector(node, socket):
    global particle_info
    global sample_bump
    global sample_bump_res

    # RGB
    if node.type == 'GROUP':
        return parse_group(node, socket)

    elif node.type == 'GROUP_INPUT':
        return parse_group_input(node, socket)

    elif node.type == 'ATTRIBUTE':
        if socket == node.outputs[0]: # Color
            con.add_elem('col', 'short4norm') # Vcols only for now
            return 'vcolor'
        else: # Vector
            con.add_elem('tex', 'short2norm') # UVMaps only for now
            mat = mat_get_material()
            mat_users = mat_get_material_users()
            if mat_users != None and mat in mat_users:
                mat_user = mat_users[mat][0]
                if hasattr(mat_user.data, 'uv_layers'): # No uvlayers for Curve
                    lays = mat_user.data.uv_layers
                    # Second uvmap referenced
                    if len(lays) > 1 and node.attribute_name == lays[1].name:
                        con.add_elem('tex1', 'short2norm')
                        return 'vec3(texCoord1.x, 1.0 - texCoord1.y, 0.0)'
            return 'vec3(texCoord.x, 1.0 - texCoord.y, 0.0)'

    elif node.type == 'RGB':
        if node.arm_material_param:
            nn = 'param_' + node_name(node.name)
            curshader.add_uniform('vec3 {0}'.format(nn), link='{0}'.format(node.name))
            return nn
        else:
            return to_vec3(socket.default_value)

    elif node.type == 'TEX_BRICK':
        curshader.add_function(c_functions.str_tex_brick)
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'bposition'
        col1 = parse_vector_input(node.inputs[1])
        col2 = parse_vector_input(node.inputs[2])
        col3 = parse_vector_input(node.inputs[3])
        scale = parse_value_input(node.inputs[4])
        res = 'tex_brick({0} * {4}, {1}, {2}, {3})'.format(co, col1, col2, col3, scale)
        if sample_bump:
            write_bump(node, res)
        return res

    elif node.type == 'TEX_CHECKER':
        curshader.add_function(c_functions.str_tex_checker)
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'bposition'
        col1 = parse_vector_input(node.inputs[1])
        col2 = parse_vector_input(node.inputs[2])
        scale = parse_value_input(node.inputs[3])
        res = 'tex_checker({0}, {1}, {2}, {3})'.format(co, col1, col2, scale)
        if sample_bump:
            write_bump(node, res)
        return res

    elif node.type == 'TEX_ENVIRONMENT':
        # Pass through
        return to_vec3([0.0, 0.0, 0.0])

    elif node.type == 'TEX_GRADIENT':
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'bposition'
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
        res = 'vec3(clamp({0}, 0.0, 1.0))'.format(f)
        if sample_bump:
            write_bump(node, res)
        return res

    elif node.type == 'TEX_IMAGE':
        # Already fetched
        if is_parsed(store_var_name(node)):
            return '{0}.rgb'.format(store_var_name(node))
        tex_name = node_name(node.name)
        tex = make_texture(node, tex_name)
        tex_link = node.name if node.arm_material_param else None
        if tex != None:
            curshader.write_textures += 1
            to_linear = node.image != None and node.image.colorspace_settings.name == 'sRGB'
            res = '{0}.rgb'.format(texture_store(node, tex, tex_name, to_linear, tex_link=tex_link))
            curshader.write_textures -= 1
            return res
        elif node.image == None: # Empty texture
            tex = {}
            tex['name'] = tex_name
            tex['file'] = ''
            return '{0}.rgb'.format(texture_store(node, tex, tex_name, to_linear=False, tex_link=tex_link))
        else:
            global parsed
            tex_store = store_var_name(node) # Pink color for missing texture
            parsed[tex_store] = True
            curshader.write_textures += 1
            curshader.write('vec4 {0} = vec4(1.0, 0.0, 1.0, 1.0);'.format(tex_store))
            curshader.write_textures -= 1
            return '{0}.rgb'.format(tex_store)

    elif node.type == 'TEX_MAGIC':
        curshader.add_function(c_functions.str_tex_magic)
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'bposition'
        scale = parse_value_input(node.inputs[1])
        res = 'tex_magic({0} * {1} * 4.0)'.format(co, scale)
        if sample_bump:
            write_bump(node, res, 0.1)
        return res

    elif node.type == 'TEX_MUSGRAVE':
        curshader.add_function(c_functions.str_tex_musgrave)
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'bposition'
        scale = parse_value_input(node.inputs[1])
        # detail = parse_value_input(node.inputs[2])
        # distortion = parse_value_input(node.inputs[3])
        res = 'vec3(tex_musgrave_f({0} * {1} * 0.5))'.format(co, scale)
        if sample_bump:
            write_bump(node, res)
        return res

    elif node.type == 'TEX_NOISE':
        curshader.add_function(c_functions.str_tex_noise)
        assets_add(get_sdk_path() + '/armory/Assets/' + 'noise256.png')
        assets_add_embedded_data('noise256.png')
        curshader.add_uniform('sampler2D snoise256', link='$noise256.png')
        curshader.add_function(c_functions.str_tex_noise)
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'bposition'
        scale = parse_value_input(node.inputs[1])
        # detail = parse_value_input(node.inputs[2])
        # distortion = parse_value_input(node.inputs[3])
        # Slow..
        res = 'vec3(tex_noise({0} * {1}), tex_noise({0} * {1} + 0.33), tex_noise({0} * {1} + 0.66))'.format(co, scale)
        if sample_bump:
            write_bump(node, res, 0.1)
        return res

    elif node.type == 'TEX_POINTDENSITY':
        # Pass through
        return to_vec3([0.0, 0.0, 0.0])

    elif node.type == 'TEX_SKY':
        # Pass through
        return to_vec3([0.0, 0.0, 0.0])

    elif node.type == 'TEX_VORONOI':
        curshader.add_function(c_functions.str_tex_voronoi)
        assets_add(get_sdk_path() + '/armory/Assets/' + 'noise256.png')
        assets_add_embedded_data('noise256.png')
        curshader.add_uniform('sampler2D snoise256', link='$noise256.png')
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'bposition'
        scale = parse_value_input(node.inputs[1])
        if node.coloring == 'INTENSITY':
            res = 'vec3(tex_voronoi({0} * {1}).a)'.format(co, scale)
        else: # CELLS
            res = 'tex_voronoi({0} * {1}).rgb'.format(co, scale)
        if sample_bump:
            write_bump(node, res)
        return res

    elif node.type == 'TEX_WAVE':
        curshader.add_function(c_functions.str_tex_wave)
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'bposition'
        scale = parse_value_input(node.inputs[1])
        res = 'vec3(tex_wave_f({0} * {1}))'.format(co, scale)
        if sample_bump:
            write_bump(node, res)
        return res

    elif node.type == 'BRIGHTCONTRAST':
        out_col = parse_vector_input(node.inputs[0])
        bright = parse_value_input(node.inputs[1])
        contr = parse_value_input(node.inputs[2])
        curshader.add_function(c_functions.str_brightcontrast)
        return 'brightcontrast({0}, {1}, {2})'.format(out_col, bright, contr)

    elif node.type == 'GAMMA':
        out_col = parse_vector_input(node.inputs[0])
        gamma = parse_value_input(node.inputs[1])
        return 'pow({0}, vec3({1}))'.format(out_col, gamma)

    elif node.type == 'HUE_SAT':
        curshader.add_function(c_functions.str_hue_sat)
        hue = parse_value_input(node.inputs[0])
        sat = parse_value_input(node.inputs[1])
        val = parse_value_input(node.inputs[2])
        fac = parse_value_input(node.inputs[3])
        col = parse_vector_input(node.inputs[4])
        return 'hue_sat({0}, vec4({1}-0.5, {2}, {3}, 1.0-{4}))'.format(col, hue, sat, val, fac)

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

    elif node.type == 'BLACKBODY':
        # Pass constant
        return to_vec3([0.84, 0.38, 0.0])

    elif node.type == 'VALTORGB': # ColorRamp
        fac = parse_value_input(node.inputs[0])
        interp = node.color_ramp.interpolation
        elems = node.color_ramp.elements
        if len(elems) == 1:
            return to_vec3(elems[0].color)
        # Write cols array
        cols_var = node_name(node.name) + '_cols'
        curshader.write('vec3 {0}[{1}];'.format(cols_var, len(elems))) # TODO: Make const
        for i in range(0, len(elems)):
            curshader.write('{0}[{1}] = vec3({2}, {3}, {4});'.format(cols_var, i, elems[i].color[0], elems[i].color[1], elems[i].color[2]))
        # Get index
        fac_var = node_name(node.name) + '_fac'
        curshader.write('float {0} = {1};'.format(fac_var, fac))
        index = '0'
        for i in range(1, len(elems)):
            index += ' + ({0} > {1} ? 1 : 0)'.format(fac_var, elems[i].position)
        # Write index
        index_var = node_name(node.name) + '_i'
        curshader.write('int {0} = {1};'.format(index_var, index))
        if interp == 'CONSTANT':
            return '{0}[{1}]'.format(cols_var, index_var)
        else: # Linear
            # Write facs array
            facs_var = node_name(node.name) + '_facs'
            curshader.write('float {0}[{1}];'.format(facs_var, len(elems))) # TODO: Make const
            for i in range(0, len(elems)):
                curshader.write('{0}[{1}] = {2};'.format(facs_var, i, elems[i].position))
            # Mix color
            # float f = (pos - start) * (1.0 / (finish - start))
            return 'mix({0}[{1}], {0}[{1} + 1], ({2} - {3}[{1}]) * (1.0 / ({3}[{1} + 1] - {3}[{1}]) ))'.format(cols_var, index_var, fac_var, facs_var)

    elif node.type == 'CURVE_VEC': # Vector Curves
        fac = parse_value_input(node.inputs[0])
        vec = parse_vector_input(node.inputs[1])
        curves = node.mapping.curves
        name = node_name(node.name)
        # mapping.curves[0].points[0].handle_type # bezier curve
        return '(vec3({0}, {1}, {2}) * {3})'.format(\
            vector_curve(name + '0', vec + '.x', curves[0].points), vector_curve(name + '1', vec + '.y', curves[1].points), vector_curve(name + '2', vec + '.z', curves[2].points), fac)

    elif node.type == 'CURVE_RGB': # RGB Curves
        fac = parse_value_input(node.inputs[0])
        vec = parse_vector_input(node.inputs[1])
        curves = node.mapping.curves
        name = node_name(node.name)
        # mapping.curves[0].points[0].handle_type
        return '(sqrt(vec3({0}, {1}, {2}) * vec3({4}, {5}, {6})) * {3})'.format(\
            vector_curve(name + '0', vec + '.x', curves[0].points), vector_curve(name + '1', vec + '.y', curves[1].points), vector_curve(name + '2', vec + '.z', curves[2].points), fac,\
            vector_curve(name + '3a', vec + '.x', curves[3].points), vector_curve(name + '3b', vec + '.y', curves[3].points), vector_curve(name + '3c', vec + '.z', curves[3].points))

    elif node.type == 'COMBHSV':
        curshader.add_function(c_functions.str_hue_sat)
        h = parse_value_input(node.inputs[0])
        s = parse_value_input(node.inputs[1])
        v = parse_value_input(node.inputs[2])
        return 'hsv_to_rgb(vec3({0}, {1}, {2}))'.format(h,s,v)

    elif node.type == 'COMBRGB':
        r = parse_value_input(node.inputs[0])
        g = parse_value_input(node.inputs[1])
        b = parse_value_input(node.inputs[2])
        return 'vec3({0}, {1}, {2})'.format(r, g, b)

    elif node.type == 'WAVELENGTH':
        curshader.add_function(c_functions.str_wavelength_to_rgb)
        wl = parse_value_input(node.inputs[0])
        # Roughly map to cycles - 450 to 600 nanometers
        return 'wavelength_to_rgb(({0} - 450.0) / 150.0)'.format(wl)

    # Vector

    elif node.type == 'CAMERA':
        # View Vector in camera space
        return 'vVecCam'

    elif node.type == 'NEW_GEOMETRY':
        if socket == node.outputs[0]: # Position
            return 'wposition'
        elif socket == node.outputs[1]: # Normal
            return 'n' if curshader.shader_type == 'frag' else 'wnormal'
        elif socket == node.outputs[2]: # Tangent
            return 'wtangent'
        elif socket == node.outputs[3]: # True Normal
            return 'n' if curshader.shader_type == 'frag' else 'wnormal'
        elif socket == node.outputs[4]: # Incoming
            return 'vVec'
        elif socket == node.outputs[5]: # Parametric
            return 'mposition'

    elif node.type == 'HAIR_INFO':
        return 'vec3(0.0)' # Tangent Normal

    elif node.type == 'OBJECT_INFO':
        return 'wposition'

    elif node.type == 'PARTICLE_INFO':
        if socket == node.outputs[3]: # Location
            particle_info['location'] = True
            return 'p_location' if arm.utils.get_rp().arm_particles == 'On' else 'vec3(0.0)'
        elif socket == node.outputs[5]: # Velocity
            particle_info['velocity'] = True
            return 'p_velocity' if arm.utils.get_rp().arm_particles == 'On' else 'vec3(0.0)'
        elif socket == node.outputs[6]: # Angular Velocity
            particle_info['angular_velocity'] = True
            return 'vec3(0.0)'

    elif node.type == 'TANGENT':
        return 'wtangent'

    elif node.type == 'TEX_COORD':
        #obj = node.object
        #instance = node.from_instance
        if socket == node.outputs[0]: # Generated - bounds
            return 'bposition'
        elif socket == node.outputs[1]: # Normal
            return 'n'
        elif socket == node.outputs[2]: # UV
            con.add_elem('tex', 'short2norm')
            return 'vec3(texCoord.x, 1.0 - texCoord.y, 0.0)'
        elif socket == node.outputs[3]: # Object
            return 'mposition'
        elif socket == node.outputs[4]: # Camera
            return 'vec3(0.0)' # 'vposition'
        elif socket == node.outputs[5]: # Window
            return 'vec3(0.0)' # 'wvpposition'
        elif socket == node.outputs[6]: # Reflection
            return 'vec3(0.0)'

    elif node.type == 'UVMAP':
        #instance = node.from_instance
        con.add_elem('tex', 'short2norm')
        mat = mat_get_material()
        mat_users = mat_get_material_users()
        if mat_users != None and mat in mat_users:
            mat_user = mat_users[mat][0]
            if hasattr(mat_user.data, 'uv_layers'):
                lays = mat_user.data.uv_layers
                # Second uvmap referenced
                if len(lays) > 1 and node.uv_map == lays[1].name:
                    con.add_elem('tex1', 'short2norm')
                    return 'vec3(texCoord1.x, 1.0 - texCoord1.y, 0.0)'
        return 'vec3(texCoord.x, 1.0 - texCoord.y, 0.0)'

    elif node.type == 'BUMP':
        # Interpolation strength
        strength = parse_value_input(node.inputs[0])
        # Height multiplier
        # distance = parse_value_input(node.inputs[1])
        sample_bump = True
        height = parse_value_input(node.inputs[2])
        sample_bump = False
        nor = parse_vector_input(node.inputs[3])
        if sample_bump_res != '':
            if node.invert:
                ext = ['1', '2', '3', '4']
            else:
                ext = ['2', '1', '4', '3']
            curshader.write('float {0}_fh1 = {0}_{1} - {0}_{2}; float {0}_fh2 = {0}_{3} - {0}_{4};'.format(sample_bump_res, ext[0], ext[1], ext[2], ext[3]))
            curshader.write('{0}_fh1 *= ({1}) * 3.0; {0}_fh2 *= ({1}) * 3.0;'.format(sample_bump_res, strength))
            curshader.write('vec3 {0}_a = normalize(vec3(2.0, 0.0, {0}_fh1));'.format(sample_bump_res))
            curshader.write('vec3 {0}_b = normalize(vec3(0.0, 2.0, {0}_fh2));'.format(sample_bump_res))
            res = 'normalize(mat3({0}_a, {0}_b, normalize(vec3({0}_fh1, {0}_fh2, 2.0))) * n)'.format(sample_bump_res)
            sample_bump_res = ''
        else:
            res = 'n'
        return res

    elif node.type == 'MAPPING':
        out = parse_vector_input(node.inputs[0])
        if node.scale[0] != 1.0 or node.scale[1] != 1.0 or node.scale[2] != 1.0:
            out = '({0} * vec3({1}, {2}, {3}))'.format(out, node.scale[0], node.scale[1], node.scale[2])
        if node.rotation[2] != 0.0:
            # ZYX rotation, Z axis for now..
            a = node.rotation[2]
            # x * cos(theta) - y * sin(theta)
            # x * sin(theta) + y * cos(theta)
            out = 'vec3({0}.x * {1} - ({0}.y) * {2}, {0}.x * {2} + ({0}.y) * {1}, 0.0)'.format(out, math.cos(a), math.sin(a))
        # if node.rotation[1] != 0.0:
        #     a = node.rotation[1]
        #     out = 'vec3({0}.x * {1} - {0}.z * {2}, {0}.x * {2} + {0}.z * {1}, 0.0)'.format(out, math.cos(a), math.sin(a))
        # if node.rotation[0] != 0.0:
        #     a = node.rotation[0]
        #     out = 'vec3({0}.y * {1} - {0}.z * {2}, {0}.y * {2} + {0}.z * {1}, 0.0)'.format(out, math.cos(a), math.sin(a))
        
        if node.translation[0] != 0.0 or node.translation[1] != 0.0 or node.translation[2] != 0.0:
            out = '({0} + vec3({1}, {2}, {3}))'.format(out, node.translation[0], node.translation[1], node.translation[2])
        if node.use_min:
            out = 'max({0}, vec3({1}, {2}, {3}))'.format(out, node.min[0], node.min[1])
        if node.use_max:
             out = 'min({0}, vec3({1}, {2}, {3}))'.format(out, node.max[0], node.max[1])
        return out

    elif node.type == 'NORMAL':
        if socket == node.outputs[0]:
            return to_vec3(node.outputs[0].default_value)
        elif socket == node.outputs[1]: # TODO: is parse_value path preferred?
            nor = parse_vector_input(node.inputs[0])
            return 'vec3(dot({0}, {1}))'.format(to_vec3(node.outputs[0].default_value), nor)

    elif node.type == 'NORMAL_MAP':
        if curshader == tese:
            return parse_vector_input(node.inputs[1])
        else:
            #space = node.space
            #map = node.uv_map
            # Color
            parse_normal_map_color_input(node.inputs[1], node.inputs[0])
            return None

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

    elif node.type == 'DISPLACEMENT':
        height = parse_value_input(node.inputs[0])
        midlevel = parse_value_input(node.inputs[1])
        scale = parse_value_input(node.inputs[2])
        nor = parse_vector_input(node.inputs[3])
        return '(vec3({0}) * {1})'.format(height, scale)

def parse_normal_map_color_input(inp, strength_input=None):
    global normal_parsed
    global frag
    if basecol_only:
        return
    if inp.is_linked == False:
        return
    if normal_parsed:
        return
    normal_parsed = True
    frag.write_normal += 1
    if not get_arm_export_tangents() or mat_get_material().arm_decal: # Compute TBN matrix
        frag.write('vec3 texn = ({0}) * 2.0 - 1.0;'.format(parse_vector_input(inp)))
        frag.write('texn.y = -texn.y;')
        frag.add_include('std/normals.glsl')
        frag.write('mat3 TBN = cotangentFrame(n, -vVec, texCoord);')
        frag.write('n = TBN * normalize(texn);')
    else:
        frag.write('vec3 n = ({0}) * 2.0 - 1.0;'.format(parse_vector_input(inp)))
        if strength_input != None:
            strength = parse_value_input(strength_input)
            if strength != '1.0':
                frag.write('n.xy *= {0};'.format(strength))
        frag.write('n = normalize(TBN * n);')
        con.add_elem('tang', 'short4norm')
    frag.write_normal -= 1

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
        if mat_batch() and inp.is_uniform:
            return to_uniform(inp)
        else:
            return to_vec1(inp.default_value)

def parse_value(node, socket):
    global particle_info
    global sample_bump

    if node.type == 'GROUP':
        if node.node_tree.name.startswith('Armory PBR'):
            # Displacement
            if socket == node.outputs[1]:
                return parse_value_input(node.inputs[7])
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
            curshader.add_include('std/math.glsl')
            curshader.add_uniform('vec2 cameraProj', link='_cameraPlaneProj')
            return 'linearize(gl_FragCoord.z, cameraProj)'
        # View Distance
        else:
            curshader.add_uniform('vec3 eye', link='_cameraPosition')
            return 'distance(eye, wposition)'

    elif node.type == 'FRESNEL':
        curshader.add_function(c_functions.str_fresnel)
        ior = parse_value_input(node.inputs[0])
        if node.inputs[1].is_linked:
            dotnv = 'dot({0}, vVec)'.format(parse_vector_input(node.inputs[1]))
        else:
            dotnv = 'dotNV'
        return 'fresnel({0}, {1})'.format(ior, dotnv)

    elif node.type == 'NEW_GEOMETRY':
        if socket == node.outputs[6]: # Backfacing
            return '(1.0 - float(gl_FrontFacing))'
        elif socket == node.outputs[7]: # Pointiness
            return '0.0'

    elif node.type == 'HAIR_INFO':
        # Is Strand
        # Intercept
        # Thickness
        return '0.5'

    elif node.type == 'LAYER_WEIGHT':
        blend = parse_value_input(node.inputs[0])
        if node.inputs[1].is_linked:
            dotnv = 'dot({0}, vVec)'.format(parse_vector_input(node.inputs[1]))
        else:
            dotnv = 'dotNV'
        if socket == node.outputs[0]: # Fresnel
            curshader.add_function(c_functions.str_fresnel)
            return 'fresnel(1.0 / (1.0 - {0}), {1})'.format(blend, dotnv)
        elif socket == node.outputs[1]: # Facing
            return '(1.0 - pow({0}, ({1} < 0.5) ? 2.0 * {1} : 0.5 / (1.0 - {1})))'.format(dotnv, blend)

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
        if socket == node.outputs[1]: # Object Index
            curshader.add_uniform('float objectInfoIndex', link='_objectInfoIndex')
            return 'objectInfoIndex'
        elif socket == node.outputs[2]: # Material Index
            curshader.add_uniform('float objectInfoMaterialIndex', link='_objectInfoMaterialIndex')
            return 'objectInfoMaterialIndex'
        elif socket == node.outputs[3]: # Random
            curshader.add_uniform('float objectInfoRandom', link='_objectInfoRandom')
            return 'objectInfoRandom'

    elif node.type == 'PARTICLE_INFO':
        if socket == node.outputs[0]: # Index
            particle_info['index'] = True
            return 'p_index' if arm.utils.get_rp().arm_particles == 'On' else '0.0'
        elif socket == node.outputs[1]: # Age
            particle_info['age'] = True
            return 'p_age' if arm.utils.get_rp().arm_particles == 'On' else '0.0'
        elif socket == node.outputs[2]: # Lifetime
            particle_info['lifetime'] = True
            return 'p_lifetime' if arm.utils.get_rp().arm_particles == 'On' else '0.0'
        elif socket == node.outputs[4]: # Size
            particle_info['size'] = True
            return '1.0'

    elif node.type == 'VALUE':
        if node.arm_material_param:
            nn = 'param_' + node_name(node.name)
            curshader.add_uniform('float {0}'.format(nn), link='{0}'.format(node.name))
            return nn
        else:
            return to_vec1(node.outputs[0].default_value)

    elif node.type == 'WIREFRAME':
        #node.use_pixel_size
        # size = parse_value_input(node.inputs[0])
        return '0.0'

    elif node.type == 'TEX_BRICK':
        curshader.add_function(c_functions.str_tex_brick)
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'bposition'
        scale = parse_value_input(node.inputs[4])
        res = 'tex_brick_f({0} * {1})'.format(co, scale)
        if sample_bump:
            write_bump(node, res)
        return res

    elif node.type == 'TEX_CHECKER':
        curshader.add_function(c_functions.str_tex_checker)
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'bposition'
        scale = parse_value_input(node.inputs[3])
        res = 'tex_checker_f({0}, {1})'.format(co, scale)
        if sample_bump:
            write_bump(node, res)
        return res

    elif node.type == 'TEX_GRADIENT':
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'bposition'
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
        res = '(clamp({0}, 0.0, 1.0))'.format(f)
        if sample_bump:
            write_bump(node, res)
        return res

    elif node.type == 'TEX_IMAGE':
        # Already fetched
        if is_parsed(store_var_name(node)):
            return '{0}.a'.format(store_var_name(node))
        tex_name = safesrc(node.name)
        tex = make_texture(node, tex_name)
        tex_link = node.name if node.arm_material_param else None
        if tex != None:
            curshader.write_textures += 1
            res = '{0}.a'.format(texture_store(node, tex, tex_name, tex_link=tex_link))
            curshader.write_textures -= 1
            return res
        elif node.image == None: # Empty texture
            tex = {}
            tex['name'] = tex_name
            tex['file'] = ''
            return '{0}.a'.format(texture_store(node, tex, tex_name, True, tex_link=tex_link))
        else:
            tex_store = store_var_name(node) # Pink color for missing texture
            curshader.write('vec4 {0} = vec4(1.0, 0.0, 1.0, 1.0);'.format(tex_store))
            return '{0}.a'.format(tex_store)

    elif node.type == 'TEX_MAGIC':
        curshader.add_function(c_functions.str_tex_magic)
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'bposition'
        scale = parse_value_input(node.inputs[1])
        res = 'tex_magic_f({0} * {1} * 4.0)'.format(co, scale)
        if sample_bump:
            write_bump(node, res, 0.1)
        return res

    elif node.type == 'TEX_MUSGRAVE':
        # Fall back to noise
        curshader.add_function(c_functions.str_tex_musgrave)
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'bposition'
        scale = parse_value_input(node.inputs[1])
        # detail = parse_value_input(node.inputs[2])
        # distortion = parse_value_input(node.inputs[3])
        res = 'tex_musgrave_f({0} * {1} * 0.5)'.format(co, scale)
        if sample_bump:
            write_bump(node, res)
        return res

    elif node.type == 'TEX_NOISE':
        curshader.add_function(c_functions.str_tex_noise)
        assets_add(get_sdk_path() + '/armory/Assets/' + 'noise256.png')
        assets_add_embedded_data('noise256.png')
        curshader.add_uniform('sampler2D snoise256', link='$noise256.png')
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'bposition'
        scale = parse_value_input(node.inputs[1])
        # detail = parse_value_input(node.inputs[2])
        # distortion = parse_value_input(node.inputs[3])
        res = 'tex_noise({0} * {1})'.format(co, scale)
        if sample_bump:
            write_bump(node, res, 0.1)
        return res

    elif node.type == 'TEX_POINTDENSITY':
        return '0.0'

    elif node.type == 'TEX_VORONOI':
        curshader.add_function(c_functions.str_tex_voronoi)
        assets_add(get_sdk_path() + '/armory/Assets/' + 'noise256.png')
        assets_add_embedded_data('noise256.png')
        curshader.add_uniform('sampler2D snoise256', link='$noise256.png')
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'bposition'
        scale = parse_value_input(node.inputs[1])
        if node.coloring == 'INTENSITY':
            res = 'tex_voronoi({0} * {1}).a'.format(co, scale)
        else: # CELLS
            res = 'tex_voronoi({0} * {1}).r'.format(co, scale)
        if sample_bump:
            write_bump(node, res)
        return res

    elif node.type == 'TEX_WAVE':
        curshader.add_function(c_functions.str_tex_wave)
        if node.inputs[0].is_linked:
            co = parse_vector_input(node.inputs[0])
        else:
            co = 'bposition'
        scale = parse_value_input(node.inputs[1])
        res = 'tex_wave_f({0} * {1})'.format(co, scale)
        if sample_bump:
            write_bump(node, res)
        return res

    elif node.type == 'LIGHT_FALLOFF':
        # Constant, linear, quadratic
        # Shaders default to quadratic for now
        return '1.0'

    elif node.type == 'NORMAL':
        nor = parse_vector_input(node.inputs[0])
        return 'dot({0}, {1})'.format(to_vec3(node.outputs[0].default_value), nor)

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

##

def vector_curve(name, fac, points):
    # Write Ys array
    ys_var = name + '_ys'
    curshader.write('float {0}[{1}];'.format(ys_var, len(points))) # TODO: Make const
    for i in range(0, len(points)):
        curshader.write('{0}[{1}] = {2};'.format(ys_var, i, points[i].location[1]))
    # Get index
    fac_var = name + '_fac'
    curshader.write('float {0} = {1};'.format(fac_var, fac))
    index = '0'
    for i in range(1, len(points)):
        index += ' + ({0} > {1} ? 1 : 0)'.format(fac_var, points[i].location[0])
    # Write index
    index_var = name + '_i'
    curshader.write('int {0} = {1};'.format(index_var, index))
    # Linear
    # Write Xs array
    facs_var = name + '_xs'
    curshader.write('float {0}[{1}];'.format(facs_var, len(points))) # TODO: Make const
    for i in range(0, len(points)):
        curshader.write('{0}[{1}] = {2};'.format(facs_var, i, points[i].location[0]))
    # Map vector
    return 'mix({0}[{1}], {0}[{1} + 1], ({2} - {3}[{1}]) * (1.0 / ({3}[{1} + 1] - {3}[{1}]) ))'.format(ys_var, index_var, fac_var, facs_var)

def write_normal(inp):
    if inp.is_linked and inp.links[0].from_node.type != 'GROUP_INPUT':
        normal_res = parse_vector_input(inp)
        if normal_res != None:
            curshader.write('n = {0};'.format(normal_res))

def is_parsed(s):
    global parsed
    return s in parsed

def res_var_name(node, socket):
    return node_name(node.name) + '_' + safesrc(socket.name) + '_res'

def write_result(l):
    global parsed
    res_var = res_var_name(l.from_node, l.from_socket)
    # Unparsed node
    if not is_parsed(res_var):
        parsed[res_var] = True
        st = l.from_socket.type
        if st == 'RGB' or st == 'RGBA' or st == 'VECTOR':
            res = parse_vector(l.from_node, l.from_socket)
            if res == None:
                return None
            curshader.write('vec3 {0} = {1};'.format(res_var, res))
        elif st == 'VALUE':
            res = parse_value(l.from_node, l.from_socket)
            if res == None:
                return None
            curshader.write('float {0} = {1};'.format(res_var, res))
    # Normal map already parsed, return
    elif l.from_node.type == 'NORMAL_MAP':
        return None
    return res_var

def glsl_type(t):
    if t == 'RGB' or t == 'RGBA' or t == 'VECTOR':
        return 'vec3'
    else:
        return 'float'

def to_uniform(inp):
    uname = safesrc(inp.node.name) + safesrc(inp.name)
    curshader.add_uniform(glsl_type(inp.type) + ' ' + uname)
    return uname

def store_var_name(node):
    return node_name(node.name) + '_store'

def texture_store(node, tex, tex_name, to_linear=False, tex_link=None):
    global sample_bump
    global sample_bump_res
    global parsed
    tex_store = store_var_name(node)
    if is_parsed(tex_store):
        return tex_store
    parsed[tex_store] = True
    mat_bind_texture(tex)
    con.add_elem('tex', 'short2norm')
    curshader.add_uniform('sampler2D {0}'.format(tex_name), link=tex_link)
    if node.inputs[0].is_linked:
        uv_name = parse_vector_input(node.inputs[0])
        uv_name = 'vec2({0}.x, 1.0 - {0}.y)'.format(uv_name)
    else:
        uv_name = 'texCoord'
    triplanar = node.projection == 'BOX'
    if triplanar:
        curshader.write(f'vec3 texCoordBlend = vec3(0.0); vec2 {uv_name}1 = vec2(0.0); vec2 {uv_name}2 = vec2(0.0);') # Temp
        curshader.write(f'vec4 {tex_store} = vec4(0.0, 0.0, 0.0, 0.0);')
        curshader.write(f'if (texCoordBlend.x > 0) {tex_store} += texture({tex_name}, {uv_name}.xy) * texCoordBlend.x;')
        curshader.write(f'if (texCoordBlend.y > 0) {tex_store} += texture({tex_name}, {uv_name}1.xy) * texCoordBlend.y;')
        curshader.write(f'if (texCoordBlend.z > 0) {tex_store} += texture({tex_name}, {uv_name}2.xy) * texCoordBlend.z;')
    else:
        if mat_texture_grad():
            curshader.write('vec4 {0} = textureGrad({1}, {2}.xy, g2.xy, g2.zw);'.format(tex_store, tex_name, uv_name))
        else:
            curshader.write('vec4 {0} = texture({1}, {2}.xy);'.format(tex_store, tex_name, uv_name))
    if sample_bump:
        sample_bump_res = tex_store
        curshader.write('float {0}_1 = textureOffset({1}, {2}.xy, ivec2(-2, 0)).r;'.format(tex_store, tex_name, uv_name))
        curshader.write('float {0}_2 = textureOffset({1}, {2}.xy, ivec2(2, 0)).r;'.format(tex_store, tex_name, uv_name))
        curshader.write('float {0}_3 = textureOffset({1}, {2}.xy, ivec2(0, -2)).r;'.format(tex_store, tex_name, uv_name))
        curshader.write('float {0}_4 = textureOffset({1}, {2}.xy, ivec2(0, 2)).r;'.format(tex_store, tex_name, uv_name))
        sample_bump = False
    if to_linear:
        curshader.write('{0}.rgb = pow({0}.rgb, vec3(2.2));'.format(tex_store))
    return tex_store

def write_bump(node, res, scl=0.001):
    global sample_bump
    global sample_bump_res
    sample_bump_res = store_var_name(node) + '_bump'
    # Testing.. get function parts..
    ar = res.split('(', 1)
    pre = ar[0] + '('
    if ',' in ar[1]:
        ar2 = ar[1].split(',', 1)
        co = ar2[0]
        post = ',' + ar2[1]
    else:
        co = ar[1][:-1]
        post = ')'
    curshader.write('float {0}_1 = {1}{2} + vec3(-{4}, 0.0, 0.0){3};'.format(sample_bump_res, pre, co, post, scl))
    curshader.write('float {0}_2 = {1}{2} + vec3({4},  0.0, {4}){3};'.format(sample_bump_res, pre, co, post, scl))
    curshader.write('float {0}_3 = {1}{2} + vec3(0.0, -{4}, 0.0){3};'.format(sample_bump_res, pre, co, post, scl))
    curshader.write('float {0}_4 = {1}{2} + vec3(0.0, {4}, -{4}){3};'.format(sample_bump_res, pre, co, post, scl))
    sample_bump = False

def to_vec1(v):
    return str(v)

def to_vec3(v):
    return 'vec3({0}, {1}, {2})'.format(v[0], v[1], v[2])

def node_by_type(nodes, ntype):
    for n in nodes:
        if n.type == ntype:
            return n

def socket_index(node, socket):
    for i in range(0, len(node.outputs)):
        if node.outputs[i] == socket:
            return i

def node_name(s):
    for p in parents:
        s = p.name + '_' + s
    if curshader.write_textures > 0:
        s += '_texread'
    s = safesrc(s)
    if '__' in s: # Consecutive _ are reserved
        s = s.replace('_', '_x')
    return s

##

def make_texture(image_node, tex_name, matname=None):
    tex = {}
    tex['name'] = tex_name
    image = image_node.image
    if matname == None:
        matname = mat_state.material.name

    if image == None:
        return None

    # Get filepath
    filepath = image.filepath
    if filepath == '':
        if image.packed_file != None:
            filepath = './' + image.name
            has_ext = filepath.endswith('.jpg') or filepath.endswith('.png') or filepath.endswith('.hdr')
            if not has_ext:
                # Raw bytes, write converted .jpg to /unpacked
                filepath += '.raw'
        else:
            arm.log.warn(matname + '/' + image.name + ' - invalid file path')
            return None

    # Reference image name
    texpath = arm.utils.asset_path(filepath)
    texfile = arm.utils.extract_filename(filepath)
    tex['file'] = arm.utils.safestr(texfile)
    s = tex['file'].rsplit('.', 1)
    
    if len(s) == 1:
        arm.log.warn(matname + '/' + image.name + ' - file extension required for image name')
        return None

    ext = s[1].lower()
    do_convert = ext != 'jpg' and ext != 'png' and ext != 'hdr' and ext != 'mp4' # Convert image
    if do_convert:
        new_ext = 'png' if (ext == 'tga' or ext == 'dds') else 'jpg'
        tex['file'] = tex['file'].rsplit('.', 1)[0] + '.' + new_ext

    if image.packed_file != None or not is_ascii(texfile):
        # Extract packed data / copy non-ascii texture
        unpack_path = arm.utils.get_fp_build() + '/compiled/Assets/unpacked'
        if not os.path.exists(unpack_path):
            os.makedirs(unpack_path)
        unpack_filepath = unpack_path + '/' + tex['file']
        
        if do_convert:
            if not os.path.isfile(unpack_filepath):
                fmt = 'PNG' if new_ext == 'png' else 'JPEG'
                arm.utils.convert_image(image, unpack_filepath, file_format=fmt)
        else:

            # Write bytes if size is different or file does not exist yet
            if image.packed_file != None:
                if not os.path.isfile(unpack_filepath) or os.path.getsize(unpack_filepath) != image.packed_file.size:
                    with open(unpack_filepath, 'wb') as f:
                        f.write(image.packed_file.data)
            # Copy non-ascii texture
            else:
                if not os.path.isfile(unpack_filepath) or os.path.getsize(unpack_filepath) != os.path.getsize(texpath):
                    shutil.copy(texpath, unpack_filepath)

        arm.assets.add(unpack_filepath)

    else:
        if not os.path.isfile(arm.utils.asset_path(filepath)):
            arm.log.warn('Material ' + matname + '/' + image.name + ' - file not found(' + filepath + ')')
            return None

        if do_convert:
            unpack_path = arm.utils.get_fp_build() + '/compiled/Assets/unpacked'
            if not os.path.exists(unpack_path):
                os.makedirs(unpack_path)
            converted_path = unpack_path + '/' + tex['file']
            # TODO: delete cache when file changes
            if not os.path.isfile(converted_path):
                fmt = 'PNG' if new_ext == 'png' else 'JPEG'
                arm.utils.convert_image(image, converted_path, file_format=fmt)
            arm.assets.add(converted_path)
        else:
            # Link image path to assets
            # TODO: Khamake converts .PNG to .jpg? Convert ext to lowercase on windows
            if arm.utils.get_os() == 'win':
                s = filepath.rsplit('.', 1)
                arm.assets.add(arm.utils.asset_path(s[0] + '.' + s[1].lower()))
            else:
                arm.assets.add(arm.utils.asset_path(filepath))


    # if image_format != 'RGBA32':
        # tex['format'] = image_format
    
    interpolation = image_node.interpolation
    rpdat = arm.utils.get_rp()
    texfilter = rpdat.arm_texture_filter
    if texfilter == 'Anisotropic':
        interpolation = 'Smart'
    elif texfilter == 'Linear':
        interpolation = 'Linear'
    elif texfilter == 'Point':
        interpolation = 'Closest'

    # TODO: Blender seems to load full images on size request, cache size instead
    powimage = is_pow(image.size[0]) and is_pow(image.size[1])

    if interpolation == 'Cubic': # Mipmap linear
        tex['mipmap_filter'] = 'linear'
        tex['generate_mipmaps'] = True
    elif interpolation == 'Smart': # Mipmap anisotropic
        tex['min_filter'] = 'anisotropic'
        tex['mipmap_filter'] = 'linear'
        tex['generate_mipmaps'] = True
    elif interpolation == 'Closest':
        tex['min_filter'] = 'point'
        tex['mag_filter'] = 'point'
    # else defaults to linear

    if image_node.extension != 'REPEAT': # Extend or clip
        tex['u_addressing'] = 'clamp'
        tex['v_addressing'] = 'clamp'
    
    if image.source == 'MOVIE':
        tex['source'] = 'movie'
        tex['min_filter'] = 'linear'
        tex['mag_filter'] = 'linear'
        tex['mipmap_filter'] = 'no'
        tex['generate_mipmaps'] = False

    return tex

def is_pow(num):
    return ((num & (num - 1)) == 0) and num != 0

def is_ascii(s):
    return len(s) == len(s.encode())

##

def get_rp_renderer():
    return arm.utils.get_rp().rp_renderer

def get_arm_export_tangents():
    return bpy.data.worlds['Arm'].arm_export_tangents

def safesrc(name):
    return arm.utils.safesrc(name)

def get_sdk_path():
    return arm.utils.get_sdk_path()

def disp_enabled():
    return arm.utils.disp_enabled(arm.make_state.target)

def warn(text):
    arm.log.warn(text)

def assets_add(path):
    arm.assets.add(path)

def assets_add_embedded_data(path):
    arm.assets.add_embedded_data(path)

def mat_name():
    return mat_state.material.name

def mat_batch():
    return mat_state.batch

def mat_bind_texture(tex):
    mat_state.bind_textures.append(tex)

def mat_texture_grad():
    return mat_state.texture_grad

def mat_get_material():
    return mat_state.material

def mat_get_material_users():
    return mat_state.mat_users
