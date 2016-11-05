import bpy
import math
import assets
import armutils
import os
import nodes
import log

def is_pow(num):
    return ((num & (num - 1)) == 0) and num != 0

# Material output is used as starting point
def parse(self, material, c, defs):
    tree = material.node_tree
    output_node = nodes.get_node_by_type(tree, 'OUTPUT_MATERIAL')

    # Traverse material tree
    if output_node != None:
        # Surface socket is linked
        if output_node.inputs[0].is_linked:
            surface_node = nodes.find_node_by_link(tree, output_node, output_node.inputs[0])
            parse_from(self, material, c, defs, surface_node)
        
        # Displace socket is linked
        if output_node.inputs[2].is_linked:
            displace_node = nodes.find_node_by_link(tree, output_node, output_node.inputs[2])
            parse_material_displacement(self, material, c, defs, tree, displace_node, 1.0)
            
        # No albedo color parsed, append white
        if parse.const_color == None:
            make_albedo_const([1.0, 1.0, 1.0, 1.0], c)
        if parse.const_occlusion == None and '_OccTex' not in defs:
            make_occlusion_const(1.0, c)
        if parse.const_roughness == None and '_RoughTex' not in defs:
            make_roughness_const(0.0, c)
        if parse.const_metalness == None and '_MetTex' not in defs:
            make_metalness_const(0.0, c)
        # Enable texcoords
        if '_Tex' not in defs:
            for d in defs:
                if d == '_BaseTex' or d == '_NorTex' or d == '_OccTex' or d == '_RoughTex' or d == '_MetTex' or d == '_HeightTex':
                    defs.append('_Tex')
                    break 

def parse_lamp(tree, o):
    # Emission only for now
    for n in tree.nodes:
        if n.type == 'EMISSION':
            col = n.inputs[0].default_value
            o['color'] = [col[0], col[1], col[2]]
            o['strength'] = n.inputs[1].default_value
            # Normalize point/spot strength
            if o['type'] != 'sun':
                o['strength'] /= 1000.0
            
            # Texture test..
            if n.inputs[0].is_linked:
                color_node = nodes.find_node_by_link(tree, n, n.inputs[0])
                if color_node.type == 'TEX_IMAGE':
                    o['color_texture'] = color_node.image.name
                    make_texture(None, '', color_node, None)
                    # bpy.data.worlds['Arm'].world_defs += '_LampTex'
            
            break

def make_albedo_const(col, c):
    const = {}
    parse.const_color = const
    c['bind_constants'].append(const)
    const['name'] = 'baseCol'
    const['vec4'] = [col[0], col[1], col[2], col[3]]

def make_roughness_const(f, c):
    const = {}
    parse.const_roughness = const
    c['bind_constants'].append(const)
    const['name'] = 'roughness'
    const['float'] = f

def make_occlusion_const(f, c):
    const = {}
    parse.const_occlusion = const
    c['bind_constants'].append(const)
    const['name'] = 'occlusion'
    const['float'] = f

def make_metalness_const(f, c):
    const = {}
    parse.const_metalness = const
    c['bind_constants'].append(const)
    const['name'] = 'metalness'
    const['float'] = f

# Manualy set starting material point
def parse_from(self, material, c, defs, surface_node):
    parse.const_color = None
    parse.const_occlusion = None
    parse.const_roughness = None
    parse.const_metalness = None
    
    tree = material.node_tree
    parse_material_surface(self, material, c, defs, tree, surface_node, 1.0)

def make_texture(self, id, image_node, material, image_format='RGBA32'):
    tex = {}
    tex['name'] = id
    image = image_node.image
    if image != None:
        if image.packed_file != None:
            # Extract packed data
            unpack_path = armutils.get_fp() + '/build/compiled/Assets/unpacked'
            if not os.path.exists(unpack_path):
                os.makedirs(unpack_path)
            unpack_filepath = unpack_path + '/' + image.name
            # Write bytes if size is different or file does not exist yet
            if os.path.isfile(unpack_filepath) == False or os.path.getsize(unpack_filepath) != image.packed_file.size:
                with open(unpack_filepath, 'wb') as f:
                    f.write(image.packed_file.data)
            # Add asset
            assets.add(unpack_filepath)
        else:
            # Link image path to assets
            assets.add(armutils.safe_assetpath(image.filepath))
        # Reference image name
        powimage = is_pow(image.size[0]) and is_pow(image.size[1])
        tex['file'] = armutils.extract_filename(image.filepath)
        ext = tex['file'][-3:].lower()
        if ext != 'jpg' and ext != 'png' and ext != 'hdr':
            log.warn(material.name + '/' + image.name + ' - image format is not supported yet. Use jpg, png, hdr.')
        tex['file'] = armutils.safe_filename(tex['file'])
        if image_format != 'RGBA32':
            tex['format'] = image_format
        interpolation = image_node.interpolation
        if bpy.data.worlds['Arm'].force_anisotropic_filtering:
            interpolation = 'Smart'
        if interpolation == 'Cubic': # Mipmap linear
            tex['mipmap_filter'] = 'linear'
            tex['generate_mipmaps'] = True
        elif interpolation == 'Smart': # Mipmap anisotropic
            tex['min_filter'] = 'anisotropic'
            tex['mipmap_filter'] = 'linear'
            tex['generate_mipmaps'] = True
        if image_node.extension != 'REPEAT': # Extend or clip
            tex['u_addressing'] = 'clamp'
            tex['v_addressing'] = 'clamp'
        else:
            if bpy.data.worlds['Arm'].npot_texture_repeat == False and powimage == False:
                print('Armory Warning: ' + material.name + '/' + image.name + ' - non power of 2 texture can not use repeat mode')
                tex['u_addressing'] = 'clamp'
                tex['v_addressing'] = 'clamp'
        
        if image.source == 'MOVIE': # Just append movie texture trait for now
            movie_trait = {}
            movie_trait['type'] = 'Script'
            movie_trait['class_name'] = 'armory.trait.internal.MovieTexture'
            movie_trait['parameters'] = [tex['file']]
            for o in self.materialToGameObjectDict[material]:
                o['traits'].append(movie_trait)
            tex['source'] = 'movie'
            tex['file'] = '' # MovieTexture will load the video
    else:
        tex['file'] = ''
    return tex

def parse_value_node(node):
    return node.outputs[0].default_value

def parse_float_input(tree, node, inp):
    if inp.is_linked:
        float_node = nodes.find_node_by_link(tree, node, inp)
        if float_node.type == 'VALUE':
            return parse_value_node(float_node)
    else:
        return inp.default_value

def parse_material_displacement(self, material, c, defs, tree, node, factor):
    # Normal
    if node.type == 'NORMAL_MAP':
        normal_map_input = node.inputs[1]
        parse_normal_map_socket(self, normal_map_input, material, c, defs, tree, node, factor)

def parse_material_surface(self, material, c, defs, tree, node, factor):
    if node.type == 'GROUP' and node.node_tree.name.split('.', 1)[0] == 'Armory PBR':
        parse_pbr_group(self, material, c, defs, tree, node, factor)
    
    elif node.type == 'BSDF_TRANSPARENT':
        parse_bsdf_transparent(self, material, c, defs, tree, node, factor)
    
    elif node.type == 'BSDF_DIFFUSE':
        parse_bsdf_diffuse(self, material, c, defs, tree, node, factor)
        
    elif node.type == 'EMISSION':
        parse_emission(self, material, c, defs, tree, node, factor)
    
    elif node.type == 'BSDF_GLOSSY':
        parse_bsdf_glossy(self, material, c, defs, tree, node, factor)
        
    # elif node.type == 'BSDF_TRANSLUCENT':
        # parse_bsdf_translucent(self, material, c, defs, tree, node, factor)
        
    elif node.type == 'BSDF_GLASS':
        parse_bsdf_glass(self, material, c, defs, tree, node, factor)
    
    elif node.type == 'SUBSURFACE_SCATTERING':
        parse_sss(self, material, c, defs, tree, node, factor)
    
    elif node.type == 'BSDF_TOON':
        parse_bsdf_toon(self, material, c, defs, tree, node, factor)

    elif node.type == 'MIX_SHADER':
        parse_mix_shader(self, material, c, defs, tree, node, factor)

    else:
        print('Armory Warning: Material node ' + node.type + ' in ' + material.name + ' is not yet supported! Please use "Armory PBR" node group for now.')

def parse_mix_shader(self, material, c, defs, tree, node, factor):
    mixfactor = node.inputs[0].default_value * factor
    if node.inputs[1].is_linked:
        mixfactor0 = 1.0 - mixfactor
        surface1_node = nodes.find_node_by_link(tree, node, node.inputs[1])
        parse_material_surface(self, material, c, defs, tree, surface1_node, mixfactor0)
    if node.inputs[2].is_linked:
        surface2_node = nodes.find_node_by_link(tree, node, node.inputs[2])
        parse_material_surface(self, material, c, defs, tree, surface2_node, mixfactor)

def parse_bsdf_transparent(self, material, c, defs, tree, node, factor):
    defs.append('_AlphaTest')
    
def parse_sss(self, material, c, defs, tree, node, factor):
    # Set stencil mask
    # append '_SSS' to deferred_light
    pass
    
def parse_bsdf_toon(self, material, c, defs, tree, node, factor):
    # set pipe pass
    defs.append('_Toon')
    pass
    
def parse_bsdf_diffuse(self, material, c, defs, tree, node, factor):
    # Color
    base_color_input = node.inputs[0]
    parse_base_color_socket(self, base_color_input, material, c, defs, tree, node, factor)
    # Parse roughness but force 0.4 as minimum, set 0.0 metalness
    add_metalness_const(0.0, c, factor)
    roughness_input = node.inputs[1]
    parse_roughness_socket(self, roughness_input, material, c, defs, tree, node, factor, minimum_val=0.4)
    # Normal
    normal_input = node.inputs[2]
    if normal_input.is_linked:
        normal_map_node = nodes.find_node_by_link(tree, node, normal_input)
        if normal_map_node.type == 'NORMAL_MAP':
            normal_map_input = normal_map_node.inputs[1]
            parse_normal_map_socket(self, normal_map_input, material, c, defs, tree, node, factor)

def parse_emission(self, material, c, defs, tree, node, factor):
    # Color
    base_color_input = node.inputs[0]
    parse_base_color_socket(self, base_color_input, material, c, defs, tree, node, factor)
    # Multiply color by strength
    strength_input = node.inputs[1]
    strength = strength_input.default_value * 50.0 + 1.0
    col = parse.const_color['vec4']
    col[0] *= strength
    col[1] *= strength
    col[2] *= strength
    parse.const_color['vec4'] = [col[0], col[1], col[2], col[3]]

def parse_bsdf_glossy(self, material, c, defs, tree, node, factor):
    # Mix with current color
    base_color_input = node.inputs[0]
    parse_base_color_socket(self, base_color_input, material, c, defs, tree, node, factor)
    # Parse sqrt roughness and set 1.0 metalness
    add_metalness_const(1.0, c, factor)
    roughness_input = node.inputs[1]
    parse_roughness_socket(self, roughness_input, material, c, defs, tree, node, factor, sqrt_val=True)

def parse_bsdf_glass(self, material, c, defs, tree, node, factor):
    # Mix with current color
    base_color_input = node.inputs[0]
    parse_base_color_socket(self, base_color_input, material, c, defs, tree, node, factor)
    # Calculate alpha, TODO: take only glass color into account, separate getSocketColor method
    col = parse.const_color['vec4']
    sum = (col[0] + col[1] + col[2]) / 3
    # Roughly guess color to match cycles
    mincol = min(col[:3])
    parse.const_color['vec4'] = [col[0] - mincol, col[1] - mincol, col[2] - mincol, 1.0 - (sum * 0.7)]
    # Parse sqrt roughness and set 0.0 metalness
    add_metalness_const(0.0, c, factor)
    roughness_input = node.inputs[1]
    parse_roughness_socket(self, roughness_input, material, c, defs, tree, node, factor, sqrt_val=True)
    # Append translucent
    defs.append('_Translucent')

def mix_float(f1, f2, factor=0.5):
    return (f1 + f2) * factor

def mix_color_vec4(col1, col2, factor=0.5):
    return [mix_float(col1[0], col2[0], factor), mix_float(col1[1], col2[1], factor), mix_float(col1[2], col2[2], factor), mix_float(col1[3], col2[3], factor)]

def parse_val_to_rgb(node, c, defs):
    factor = node.inputs[0].default_value
    if not node.inputs[0].is_linked: # Take ramp color
        return node.color_ramp.evaluate(factor)
    else: # Assume 2 colors interpolated by id for now
        defs.append('_RampID')
        # Link baseCol2 as color 2
        const = {}
        c['bind_constants'].append(const)
        const['name'] = 'baseCol2'
        res = node.color_ramp.elements[1].color
        const['vec4'] = [res[0], res[1], res[2], res[3]]
        # Return color 1
        return node.color_ramp.elements[0].color

def add_base_color(c, col):
    if parse.const_color == None:
        make_albedo_const(col, c)
    else:
        const = parse.const_color
        res = mix_color_vec4(col, const['vec4'])
        const['vec4'] = [res[0], res[1], res[2], res[3]]

def parse_mix_rgb(self, material, c, defs, tree, node, factor):
    # blend_type = MULTIPLY
    # use_clamp = False
    # Factor, col1, col2
    parse_base_color_socket(self, node.inputs[1], material, c, defs, tree, node, factor)
    # Assume color 2 as occlusion
    parse_occlusion_socket(self, node.inputs[2], material, c, defs, tree, node, factor)

def add_albedo_tex(self, node, material, c, defs):
    if '_BaseTex' not in defs:
        defs.append('_BaseTex')
        tex = make_texture(self, 'sbase', node, material)
        c['bind_textures'].append(tex)

def add_metalness_tex(self, node, material, c, defs):
    if '_MetTex' not in defs:
        defs.append('_MetTex')
        tex = make_texture(self, 'smetal', node, material, image_format='R8')
        c['bind_textures'].append(tex)
        if parse.const_metalness != None: # If texture is used, remove constant
            c['bind_constants'].remove(parse.const_metalness)

def add_roughness_tex(self, node, material, c, defs):
    if '_RoughTex' not in defs:
        defs.append('_RoughTex')
        tex = make_texture(self, 'srough', node, material, image_format='R8')
        c['bind_textures'].append(tex)
        if parse.const_roughness != None:
            c['bind_constants'].remove(parse.const_roughness)

def add_roughness_strength(self, c, defs, f):
    if '_RoughStr' not in defs:
        defs.append('_RoughStr')
        const = {}
        c['bind_constants'].append(const)
        const['name'] = 'roughnessStrength'
        const['float'] = f

def add_occlusion_tex(self, node, material, c, defs):
    if '_OccTex' not in defs:
        defs.append('_OccTex')
        tex = make_texture(self, 'socclusion', node, material, image_format='R8')
        c['bind_textures'].append(tex)

def add_height_tex(self, node, material, c, defs):
    if '_HeightTex' not in defs:
        defs.append('_HeightTex')
        tex = make_texture(self, 'sheight', node, material, image_format='R8')
        c['bind_textures'].append(tex)

def add_height_strength(self, c, f):
    const = {}
    c['bind_constants'].append(const)
    const['name'] = 'heightStrength'
    const['float'] = f

def add_normal_tex(self, node, material, c, defs):
    if '_NorTex' not in defs:
        defs.append('_NorTex')
        tex = make_texture(self, 'snormal', node, material)
        c['bind_textures'].append(tex)

def add_normal_strength(self, c, defs, f):
    if '_NorStr' not in defs:
        defs.append('_NorStr')
        const = {}
        c['bind_constants'].append(const)
        const['name'] = 'normalStrength'
        const['float'] = f

def parse_base_color_socket(self, base_color_input, material, c, defs, tree, node, factor):
    if base_color_input.is_linked:
        color_node = nodes.find_node_by_link(tree, node, base_color_input)
        if color_node.type == 'TEX_IMAGE':
            add_albedo_tex(self, color_node, material, c, defs)
        elif color_node.type == 'TEX_CHECKER':
            pass
        elif color_node.type == 'ATTRIBUTE': # Assume vcols for now
            defs.append('_VCols')
        elif color_node.type == 'VALTORGB':
            col = parse_val_to_rgb(color_node, c, defs)
            add_base_color(c, col)
        elif color_node.type == 'MIX_RGB':
            parse_mix_rgb(self, material, c, defs, tree, color_node, factor)
    else: # Take node color
        add_base_color(c, base_color_input.default_value)

def add_metalness_const(res, c, factor, minimum_val=0.0, sqrt_val=False):
    if res < minimum_val:
        res = minimum_val
    if sqrt_val:
        res = math.sqrt(res)
    if parse.const_metalness == None:
        make_metalness_const(res * factor, c)
    else:
        const = parse.const_metalness       
        const['float'] = mix_float(res, const['float'], factor=factor) 

def parse_metalness_socket(self, metalness_input, material, c, defs, tree, node, factor, minimum_val=0.0, sqrt_val=False):
    if metalness_input.is_linked:
        metalness_node = nodes.find_node_by_link(tree, node, metalness_input)
        add_metalness_tex(self, metalness_node, material, c, defs)
    elif '_MetTex' not in defs:
        res = metalness_input.default_value
        add_metalness_const(res, c, factor, minimum_val, sqrt_val)

def add_roughness_const(res, c, factor, minimum_val=0.0, sqrt_val=False):
    if res < minimum_val:
        res = minimum_val
    if sqrt_val:
        res = math.sqrt(res)
    if parse.const_roughness == None:
        make_roughness_const(res * factor, c)
    else:
        const = parse.const_roughness
        const['float'] = mix_float(res, const['float'], factor=factor)
        
def parse_roughness_socket(self, roughness_input, material, c, defs, tree, node, factor, minimum_val=0.0, sqrt_val=False):
    if roughness_input.is_linked:
        roughness_node = nodes.find_node_by_link(tree, node, roughness_input)
        add_roughness_tex(self, roughness_node, material, c, defs)
    elif '_RoughTex' not in defs:
        res = parse_float_input(tree, node, roughness_input)
        add_roughness_const(res, c, factor, minimum_val, sqrt_val)

def parse_normal_map_socket(self, normal_input, material, c, defs, tree, node, factor):
    if normal_input.is_linked:
        normal_node = nodes.find_node_by_link(tree, node, normal_input)
        add_normal_tex(self, normal_node, material, c, defs)

def add_occlusion_const(res, c, factor):
    if parse.const_occlusion == None:
        make_occlusion_const(res * factor, c)
    else:
        const = parse.const_occlusion       
        const['float'] = mix_float(res, const['float'], factor=factor) 

def parse_occlusion_socket(self, occlusion_input, material, c, defs, tree, node, factor):
    if occlusion_input.is_linked:
        occlusion_node = nodes.find_node_by_link(tree, node, occlusion_input)
        add_occlusion_tex(self, occlusion_node, material, c, defs)
    elif '_OccTex' not in defs:
        res = occlusion_input.default_value[0] # Take only one channel
        add_occlusion_const(res, c, factor)

def parse_height_socket(self, height_input, material, c, defs, tree, node, factor):
    if height_input.is_linked:
        height_node = nodes.find_node_by_link(tree, node, height_input)
        add_height_tex(self, height_node, material, c, defs)

def parse_pbr_group(self, material, c, defs, tree, node, factor):
    # Albedo Map
    base_color_input = node.inputs[0]
    parse_base_color_socket(self, base_color_input, material, c, defs, tree, node, factor)
    # Occlusion Map
    occlusion_input = node.inputs[1]
    # occlusion_strength_input = node.inputs[2]
    # occlusion_strength = occlusion_strength_input.default_value
    parse_occlusion_socket(self, occlusion_input, material, c, defs, tree, node, factor)
    # Roughness Map
    roughness_input = node.inputs[3]
    parse_roughness_socket(self, roughness_input, material, c, defs, tree, node, factor)
    roughness_strength_input = node.inputs[4]
    roughness_strength = roughness_strength_input.default_value
    if roughness_strength != 1.0:
        if roughness_input.is_linked:
            add_roughness_strength(self, c, defs, roughness_strength)
        else:
            # No texture, multiply roughness float instead
            const = parse.const_roughness
            const['float'] *= roughness_strength
    # Metalness Map
    metalness_input = node.inputs[5]
    parse_metalness_socket(self, metalness_input, material, c, defs, tree, node, factor)
    # Normal Map
    normal_map_input = node.inputs[6]
    parse_normal_map_socket(self, normal_map_input, material, c, defs, tree, node, factor)
    normal_strength_input = node.inputs[7]
    normal_strength = normal_strength_input.default_value
    if normal_strength != 1.0:
        add_normal_strength(self, c, defs, normal_strength)
    # Emission
    emission_input = node.inputs[8]
    emission_strength_input = node.inputs[9]
    emission_strength = emission_strength_input.default_value
    if emission_strength != 1.0: # Just multiply base color for now
        if parse.const_color == None:
            make_albedo_const([1.0, 1.0, 1.0, 1.0], c)
        col = parse.const_color['vec4']
        col[0] *= emission_strength
        col[1] *= emission_strength
        col[2] *= emission_strength
        parse.const_color['vec4'] = [col[0], col[1], col[2], col[3]]
    # Height Map
    height_input = node.inputs[10]
    parse_height_socket(self, height_input, material, c, defs, tree, node, factor)
    # Height Strength
    if height_input.is_linked:
        height_strength_input = node.inputs[11]
        add_height_strength(self, c, height_strength_input.default_value)
    # Opacity
    opacity_input = node.inputs[12]
    opacity = opacity_input.default_value
    opacity_strength_input = node.inputs[13]
    opacity_strength = opacity_strength_input.default_value
    opacity_val = opacity * opacity_strength
    if opacity_val != 1.0:
        if parse.const_color == None:
            make_albedo_const([1.0, 1.0, 1.0, 1.0], c)
        col = parse.const_color['vec4']
        # sum = (col[0] + col[1] + col[2]) / 3
        # mincol = min(col[:3])
        # parse.const_color['vec4'] = [col[0] - mincol, col[1] - mincol, col[2] - mincol, 1.0 - (sum * 0.7)]
        parse.const_color['vec4'] = [col[0], col[1], col[2], opacity_val]
        # Append translucent
        defs.append('_Translucent')
