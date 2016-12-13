import material.state as state

def node_by_type(ntype):
    for n in state.nodes:
        if n.type == ntype:
            return n

def mesh(context_id):
    # global parsed
    global frag
    global vert
    # global first_basecol # Do not multiply vals first time
    # global first_roughness
    # global first_metallic
    # parsed = [] # Compute node only onces
    # first_basecol = True
    # first_roughness = True
    # first_metallic = True

    con_mesh = state.data.add_context({ 'name': context_id, 'depth_write': True, 'compare_mode': 'less', 'cull_mode': 'clockwise' })

    vert = con_mesh.vert()
    frag = con_mesh.frag()

    vert.add_out('vec3 wnormal')
    vert.add_out('vec3 wposition')
    vert.add_out('vec3 eyeDir')
    vert.add_uniform('mat4 W', '_worldMatrix')
    vert.add_uniform('mat4 N', '_normalMatrix')
    vert.add_uniform('mat4 WVP', '_worldViewProjectionMatrix')
    vert.add_uniform('vec3 eye', '_cameraPosition')
    vert.write('vec4 spos = vec4(pos, 1.0);')
    vert.write('wnormal = normalize(mat3(N) * nor);')
    vert.write('wposition = vec4(W * spos).xyz;')
    vert.write('eyeDir = eye - wposition;')
    vert.write('gl_Position = WVP * spos;')

    frag.add_include('../../Shaders/compiled.glsl')
    frag.add_include('../../Shaders/std/brdf.glsl')
    frag.add_include('../../Shaders/std/math.glsl')
    frag.add_include('../../Shaders/std/shirr.glsl')
    frag.add_uniform('vec3 lightColor', '_lampColor')
    frag.add_uniform('vec3 lightDir', '_lampDirection')
    frag.add_uniform('vec3 lightPos', '_lampPosition')
    frag.add_uniform('int lightType', '_lampType')
    frag.add_uniform('float shirr[27]', link='_envmapIrradiance', included=True)
    frag.add_uniform('float envmapStrength', link='_envmapStrength')
    frag.add_uniform('sampler2D senvmapRadiance', link='_envmapRadiance')
    frag.add_uniform('sampler2D senvmapBrdf', link='_envmapBrdf')
    frag.add_uniform('int envmapNumMipmaps', link='_envmapNumMipmaps')
    frag.write('vec3 n = normalize(wnormal);')
    frag.write('vec3 l = lightType == 0 ? lightDir : normalize(lightPos - wposition);')
    frag.write('vec3 v = normalize(eyeDir);')
    frag.write('vec3 h = normalize(v + l);')
    frag.write('float dotNL = dot(n, l);')
    frag.write('float dotNV = dot(n, v);')
    frag.write('float dotNH = dot(n, h);')
    frag.write('float dotVH = dot(v, h);')

    vert.add_out('vec4 lampPos')
    vert.add_uniform('mat4 LWVP', '_lampWorldViewProjectionMatrix')
    vert.write('lampPos = LWVP * spos;')
    frag.add_include('../../Shaders/std/shadows.glsl')
    frag.add_uniform('sampler2D shadowMap', included=True)
    frag.add_uniform('bool receiveShadow')
    frag.add_uniform('float shadowsBias', '_lampShadowsBias')
    frag.write('float visibility = 1.0;')
    frag.write('if (receiveShadow && lampPos.w > 0.0) {')
    frag.tab += 1
    frag.write('vec3 lpos = lampPos.xyz / lampPos.w;')
    frag.write('lpos.xy = lpos.xy * 0.5 + 0.5;')
    frag.write('visibility = PCF(lpos.xy, lpos.z - shadowsBias);')
    frag.tab -= 1
    frag.write('}')

    frag.add_uniform('float spotlightCutoff', '_spotlampCutoff')
    frag.add_uniform('float spotlightExponent', '_spotlampExponent')
    frag.write('if (lightType == 2) {')
    frag.tab += 1
    frag.write('float spotEffect = dot(lightDir, l);')
    frag.write('if (spotEffect < spotlightCutoff) {')
    frag.tab += 1
    frag.write('spotEffect = smoothstep(spotlightCutoff - spotlightExponent, spotlightCutoff, spotEffect);')
    frag.write('visibility *= spotEffect;')
    frag.tab -= 1
    frag.write('}')
    frag.tab -= 1
    frag.write('}')

    frag.write('vec3 basecol;')
    frag.write('float roughness;')
    frag.write('float metallic;')
    # frag.write('float occlussion;')

    output_node = node_by_type('OUTPUT_MATERIAL')
    if output_node != None:
        parse_output(output_node)

    frag.write('vec3 albedo = surfaceAlbedo(basecol, metallic);')
    frag.write('vec3 f0 = surfaceF0(basecol, metallic);')
    frag.write('vec3 direct = lambertDiffuseBRDF(albedo, dotNL);')
    frag.write('direct += specularBRDF(f0, roughness, dotNL, dotNH, dotNV, dotVH);')

    frag.write('vec3 indirect = (shIrradiance(n, 2.2) / PI) * albedo;')
    frag.write('vec3 reflectionWorld = reflect(-v, n);')
    frag.write('float lod = getMipFromRoughness(roughness, envmapNumMipmaps);')
    frag.write('vec3 prefilteredColor = textureLod(senvmapRadiance, envMapEquirect(reflectionWorld), lod).rgb;')
    frag.write('vec2 envBRDF = texture(senvmapBrdf, vec2(roughness, 1.0 - dotNV)).xy;')
    frag.write('indirect += prefilteredColor * (f0 * envBRDF.x + envBRDF.y);')

    frag.write('fragColor = vec4(direct * lightColor * visibility + indirect * envmapStrength, 1.0);')

    return con_mesh

def parse_output(node):
    out_basecol, out_roughness, out_metallic = parse_shader_input(node.inputs[0])
    frag.write('basecol = {0};'.format(out_basecol))
    frag.write('roughness = {0};'.format(out_roughness))
    frag.write('metallic = {0};'.format(out_metallic))

def parse_shader_input(inp):
    if inp.is_linked:
        return parse_shader(inp.links[0].from_node)
    else:
        out_basecol = 'vec3(0.0)'
        out_roughness = '0.0'
        out_metallic = '0.0'
        return out_basecol, out_roughness, out_metallic

def parse_shader(node):   

    if node.type == 'REROUTE':
        return parse_shader(node.inputs[0].links[0].from_node)

    elif node.type == 'MIX_SHADER':
        fac = parse_float_input(node.inputs[0])
        bc1, rough1, met1 = parse_shader_input(node.inputs[1])
        bc2, rough2, met2 = parse_shader_input(node.inputs[2])
        out_basecol = '({0} * (1.0 - {2}) + {1} * {2})'.format(bc1, bc2, fac)
        out_roughness = '({0} * (1.0 - {2}) + {1} * {2})'.format(rough1, rough2, fac)
        out_metallic = '({0} * (1.0 - {2}) + {1} * {2})'.format(met1, met2, fac)

    elif node.type == 'ADD_SHADER':
        pass

    elif node.type == 'BSDF_DIFFUSE':
        out_basecol = parse_color_input(node.inputs[0])
        out_roughness = parse_float_input(node.inputs[1])
        out_metallic = '0.0'

    elif node.type == 'BSDF_GLOSSY':
        out_basecol = parse_color_input(node.inputs[0])
        out_roughness = parse_float_input(node.inputs[1])
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

    elif node.type == 'GROUP' and node.node_tree.name.startswith('Armory PBR'):
        pass

    else:
        out_basecol = 'vec3(0.0)'
        out_roughness = '0.0'
        out_metallic = '0.0'

    return out_basecol, out_roughness, out_metallic

def parse_color_input(inp):
    if inp.is_linked:
        parse_color(inp.links[0].from_node)
    else:
        return vec3(inp.default_value)

def parse_color(node):

    if node.type == 'REROUTE':
        return parse_color(node.inputs[0].links[0].from_node)

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
        return parse_vector(inp.links[0].from_node)
    else:
        return vec3(inp.default_value)

def parse_vector(node):
    if node.type == 'REROUTE':
        return parse_vector(node.inputs[0].links[0].from_node)

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

def parse_float_input(inp):
    if inp.is_linked:
        return parse_float(inp.links[0].from_node)
    else:
        return vec1(inp.default_value)

def parse_float(node):
    if node.type == 'REROUTE':
        return parse_float(node.inputs[0].links[0].from_node)

    if node.type == 'ATTRIBUTE':
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

def shadows(context_id):
    con_shadowmap = state.data.add_context({ 'name': context_id, 'depth_write': True, 'compare_mode': 'less', 'cull_mode': 'clockwise' })

    vert = con_shadowmap.vert()
    vert.add_uniform('mat4 LWVP', '_lampWorldViewProjectionMatrix')
    vert.write('gl_Position = LWVP * vec4(pos, 1.0);')

    frag = con_shadowmap.frag()
    frag.write('fragColor = vec4(0.0);')

    return con_shadowmap
    