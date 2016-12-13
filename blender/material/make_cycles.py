
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

def parse_output(node, vert, frag):
    global parents
    parents = []
    out_basecol, out_roughness, out_metallic = parse_shader_input(node.inputs[0])
    frag.write('basecol = {0};'.format(out_basecol))
    frag.write('roughness = {0};'.format(out_roughness))
    frag.write('metallic = {0};'.format(out_metallic))

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
        return parse_rgb_input(inp)
    elif inp.type == 'RGBA':
        return parse_rgb_input(inp)
    elif inp.type == 'VECTOR':
        return parse_vector_input(inp)
    elif inp.type == 'VALUE':
        return parse_value_input(inp)

def parse_shader_input(inp):
    if inp.is_linked:
        l = inp.links[0]
        return parse_shader(l.from_node, l.from_socket)
    else:
        out_basecol = 'vec3(0.0)'
        out_roughness = '0.0'
        out_metallic = '0.0'
        return out_basecol, out_roughness, out_metallic

def parse_shader(node, socket):   

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
        bc1, rough1, met1 = parse_shader_input(node.inputs[1])
        bc2, rough2, met2 = parse_shader_input(node.inputs[2])
        out_basecol = '({0} * (1.0 - {2}) + {1} * {2})'.format(bc1, bc2, fac)
        out_roughness = '({0} * (1.0 - {2}) + {1} * {2})'.format(rough1, rough2, fac)
        out_metallic = '({0} * (1.0 - {2}) + {1} * {2})'.format(met1, met2, fac)

    elif node.type == 'ADD_SHADER':
        pass

    elif node.type == 'BSDF_DIFFUSE':
        out_basecol = parse_rgb_input(node.inputs[0])
        out_roughness = parse_value_input(node.inputs[1])
        out_metallic = '0.0'

    elif node.type == 'BSDF_GLOSSY':
        out_basecol = parse_rgb_input(node.inputs[0])
        out_roughness = parse_value_input(node.inputs[1])
        out_metallic = '1.0'

    elif node.type == 'AMBIENT_OCCLUSION':
        pass

    elif node.type == 'BSDF_ANISOTROPIC':
        pass

    elif node.type == 'EMISSION':
        pass

    elif node.type == 'BSDF_GLASS':
        pass

    elif node.type == 'BSDF_HAIR':
        pass

    elif node.type == 'HOLDOUT':
        pass

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
        pass

    elif node.type == 'VOLUME_ABSORPTION':
        pass

    elif node.type == 'VOLUME_SCATTER':
        pass

    else:
        out_basecol = 'vec3(0.0)'
        out_roughness = '0.0'
        out_metallic = '0.0'

    return out_basecol, out_roughness, out_metallic

def parse_rgb_input(inp):
    if inp.is_linked:
        l = inp.links[0]
        return parse_rgb(l.from_node, l.from_socket)
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
        pass

    elif node.type == 'RGB':
        pass

    elif node.type == 'TEX_BRICK':
        pass

    elif node.type == 'TEX_CHECKER':
        pass

    elif node.type == 'TEX_ENVIRONMENT':
        pass

    elif node.type == 'TEX_GRADIENT':
        pass

    elif node.type == 'TEX_IMAGE':
        pass

    elif node.type == 'TEX_MAGIC':
        pass

    elif node.type == 'TEX_MUSGRAVE':
        pass

    elif node.type == 'TEX_NOISE':
        pass

    elif node.type == 'TEX_POINTDENSITY':
        pass

    elif node.type == 'TEX_SKY':
        pass

    elif node.type == 'TEX_VORONOI':
        pass

    elif node.type == 'TEX_WAVE':
        pass

    elif node.type == 'BRIGHTCONTRAST':
        pass

    elif node.type == 'GAMMA':
        pass

    elif node.type == 'HUE_SAT':
        pass

    elif node.type == 'INVERT':
        pass

    elif node.type == 'MIX_RGB':
        pass

    elif node.type == 'CURVE_RGB':
        pass

    elif node.type == 'BLACKBODY':
        pass

    elif node.type == 'VALTORGB':
        pass

    elif node.type == 'COMBHSV':
        pass

    elif node.type == 'COMBRGB':
        pass

    elif node.type == 'WAVELENGTH':
        pass

def parse_vector_input(inp):
    if inp.is_linked:
        l = inp.links[0]
        return parse_vector(l.from_node, l.from_socket)
    else:
        return vec3(inp.default_value)

def parse_vector(node, socket):
    if node.type == 'REROUTE':
        l = node.inputs[0].links[0]
        return parse_vector(l.from_node, l.from_socket)

    elif node.type == 'GROUP':
        return parse_group(node, socket)

    elif node.type == 'GROUP_INPUT':
        return parse_input_group(node, socket)

    elif node.type == 'ATTRIBUTE':
        pass

    elif node.type == 'CAMERA':
        pass

    elif node.type == 'NEW_GEOMETRY':
        pass

    elif node.type == 'HAIR_INFO':
        pass

    elif node.type == 'OBJECT_INFO':
        pass

    elif node.type == 'PARTICLE_INFO':
        pass

    elif node.type == 'TANGENT':
        pass

    elif node.type == 'TEX_COORD':
        pass

    elif node.type == 'UVMAP':
        pass

    elif node.type == 'BUMP':
        pass

    elif node.type == 'MAPPING':
        pass

    elif node.type == 'NORMAL':
        pass

    elif node.type == 'NORMAL_MAP':
        pass

    elif node.type == 'CURVE_VEC':
        pass

    elif node.type == 'VECT_TRANSFORM':
        pass

    elif node.type == 'COMBXYZ':
        pass

    elif node.type == 'VECT_MATH':
        pass

def parse_value_input(inp):
    if inp.is_linked:
        l = inp.links[0]
        return parse_value(l.from_node, l.from_socket)
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
        pass

    elif node.type == 'CAMERA':
        pass

    elif node.type == 'FRESNEL':
        pass

    elif node.type == 'NEW_GEOMETRY':
        pass

    elif node.type == 'HAIR_INFO':
        pass

    elif node.type == 'LAYER_WEIGHT':
        pass

    elif node.type == 'LIGHT_PATH':
        pass

    elif node.type == 'OBJECT_INFO':
        pass

    elif node.type == 'PARTICLE_INFO':
        pass

    elif node.type == 'VALUE':
        return vec1(node.outputs[0].default_value)

    elif node.type == 'WIREFRAME':
        pass

    elif node.type == 'TEX_BRICK':
        pass

    elif node.type == 'TEX_CHECKER':
        pass

    elif node.type == 'TEX_GRADIENT':
        pass

    elif node.type == 'TEX_IMAGE':
        pass

    elif node.type == 'TEX_MAGIC':
        pass

    elif node.type == 'TEX_MUSGRAVE':
        pass

    elif node.type == 'TEX_NOISE':
        pass

    elif node.type == 'TEX_POINTDENSITY':
        pass

    elif node.type == 'TEX_VORONOI':
        pass

    elif node.type == 'TEX_WAVE':
        pass

    elif node.type == 'LIGHT_FALLOFF':
        pass

    elif node.type == 'NORMAL':
        pass

    elif node.type == 'VALTORGB':
        pass

    elif node.type == 'MATH':
        pass

    elif node.type == 'RGBTOBW':
        pass

    elif node.type == 'SEPHSV':
        pass

    elif node.type == 'SEPRGB':
        pass

    elif node.type == 'SEPXYZ':
        pass

    elif node.type == 'VECT_MATH':
        pass

def vec1(v):
    return str(v)

def vec2(v):
    return 'vec2({0}, {1})'.format(v[0], v[1])

def vec3(v):
    return 'vec3({0}, {1}, {2})'.format(v[0], v[1], v[2])

def vec4(v):
    return 'vec4({0}, {1}, {2}, {3})'.format(v[0], v[1], v[2], v[3])
