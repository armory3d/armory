import bpy
import make_state as state
import material.mat_state as mat_state
import material.mat_utils as mat_utils
import material.cycles as cycles
import material.make_skin as make_skin
import material.make_tess as make_tess
import armutils
import assets

def make(context_id, rid):

    con_mesh = mat_state.data.add_context({ 'name': context_id, 'depth_write': True, 'compare_mode': 'less', 'cull_mode': 'clockwise' })

    if rid == 'forward':
        make_forward(con_mesh)
    elif rid == 'deferred':
        make_deferred(con_mesh)

    return con_mesh

def make_base(con_mesh, parse_opacity):
    vert = con_mesh.make_vert()
    frag = con_mesh.make_frag()
    geom = None
    tesc = None
    tese = None

    vert.add_out('vec3 wposition')
    vert.add_uniform('mat4 W', '_worldMatrix')
    vert.add_uniform('mat4 N', '_normalMatrix')
    vert.write_pre = True
    vert.write('vec4 spos = vec4(pos, 1.0);')
    vert.write_pre = False

    if mat_utils.disp_linked(mat_state.output_node):
        tesc = con_mesh.make_tesc()
        tese = con_mesh.make_tese()
        tesc.ins = vert.outs
        tese.ins = tesc.outs
        frag.ins = tese.outs

        const = {}
        const['name'] = 'innerLevel'
        const['float'] = mat_state.material.height_tess_inner
        mat_state.mat_context['bind_constants'].append(const)
        const = {}
        const['name'] = 'outerLevel'
        const['float'] = mat_state.material.height_tess_outer
        mat_state.mat_context['bind_constants'].append(const)
        tesc.add_uniform('float innerLevel')
        tesc.add_uniform('float outerLevel')
        make_tess.tesc_levels(tesc)
        tese.add_out('vec3 eyeDir')
        make_tess.interpolate(tese, 'wposition', 3, declare_out=True)
        make_tess.interpolate(tese, 'wnormal', 3, declare_out=True, normalize=True)
    # No displacement
    else:
        frag.ins = vert.outs
        vert.add_out('vec3 eyeDir')
        vert.add_uniform('mat4 WVP', '_worldViewProjectionMatrix')
        vert.add_uniform('vec3 eye', '_cameraPosition')
        vert.write('eyeDir = eye - wposition;')
        vert.write('gl_Position = WVP * spos;')

    frag.add_include('../../Shaders/compiled.glsl')
    frag.write('vec3 v = normalize(eyeDir);')
    frag.write('float dotNV = max(dot(n, v), 0.0);') # frag.write('float dotNV = dot(n, v);')

    frag.write('vec3 basecol;')
    frag.write('float roughness;')
    frag.write('float metallic;')
    frag.write('float occlusion;')
    if parse_opacity:
        frag.write('float opacity;')

    cycles.parse(mat_state.nodes, vert, frag, geom, tesc, tese, parse_opacity=parse_opacity)

    if mat_state.data.is_elem('tex'):
        vert.add_out('vec2 texCoord')
        vert.write('texCoord = tex;')
        if tese != None:
            # TODO: also includes texCoord1
            tese.write_pre = True
            make_tess.interpolate(tese, 'texCoord', 2, declare_out=frag.contains('texCoord'))
            tese.write_pre = False

    if mat_state.data.is_elem('tex1'):
        vert.add_out('vec2 texCoord1')
        vert.write('texCoord1 = tex1;')
        if tese != None:
            tese.write_pre = True
            make_tess.interpolate(tese, 'texCoord1', 2, declare_out=frag.contains('texCoord1'))
            tese.write_pre = False

    if mat_state.data.is_elem('col'):
        vert.add_out('vec3 vcolor')
        vert.write('vcolor = col;')
        if tese != None:
            tese.write_pre = True
            make_tess.interpolate(tese, 'vcolor', 3, declare_out=frag.contains('vcolor'))
            tese.write_pre = False

    if mat_state.data.is_elem('tang'):
        if tese != None:
            vert.add_out('vec3 wnormal')
            vert.add_out('vec3 wtangent')
            write_norpos(vert)
            vert.write('wtangent = normalize(mat3(N) * tang);')
            tese.add_out('mat3 TBN')
            make_tess.interpolate(tese, 'wtangent', 3, normalize=True)
            tese.write('vec3 wbitangent = normalize(cross(wnormal, wtangent));')
            tese.write('TBN = mat3(wtangent, wbitangent, wnormal);')
        else:
            vert.add_out('mat3 TBN')
            write_norpos(vert, declare=True)
            vert.write('vec3 tangent = normalize(mat3(N) * tang);')
            vert.write('vec3 bitangent = normalize(cross(wnormal, tangent));')
            vert.write('TBN = mat3(tangent, bitangent, wnormal);')
    else:
        vert.add_out('vec3 wnormal')
        write_norpos(vert)
        frag.write_pre = True
        frag.write('vec3 n = normalize(wnormal);')
        frag.write_pre = False

    if tese != None:
        tese.add_uniform('mat4 VP', '_viewProjectionMatrix')
        # TODO: Sample disp at neightbour points to calc normal
        tese.write('wposition += wnormal * disp * 0.2;')
        tese.add_uniform('vec3 eye', '_cameraPosition')
        tese.write('eyeDir = eye - wposition;')
        tese.write('gl_Position = VP * vec4(wposition, 1.0);')

def write_norpos(vert, declare=False):
    prep = ''
    if declare:
        prep = 'vec3 '
    vert.write_pre = True
    if mat_state.data.is_elem('bone'):
        make_skin.skin_pos(vert)
        vert.write(prep + 'wnormal = normalize(mat3(N) * (nor + 2.0 * cross(skinA.xyz, cross(skinA.xyz, nor) + skinA.w * nor)));')
    else:
        vert.write(prep + 'wnormal = normalize(mat3(N) * nor);')
    if mat_state.data.is_elem('off'):
        vert.write('spos.xyz += off;')
    vert.write('wposition = vec4(W * spos).xyz;')
    vert.write_pre = False

def make_deferred(con_mesh):
    wrd = bpy.data.worlds['Arm']
    make_base(con_mesh, parse_opacity=False)

    frag = con_mesh.frag
    vert = con_mesh.vert
    tese = con_mesh.tese

    if '_Veloc' in wrd.rp_defs:
        frag.add_out('vec4[3] fragColor')
        if tese == None:
            vert.add_uniform('mat4 prevWVP', link='_prevWorldViewProjectionMatrix')
            vert.add_out('vec4 wvpposition')
            vert.add_out('vec4 prevwvpposition')
            vert.write('wvpposition = gl_Position;')
            vert.write('prevwvpposition = prevWVP * spos;')
        else:
            vert.add_uniform('mat4 prevW', link='_prevWorldMatrix')
            vert.add_out('vec3 prevwposition')
            vert.write('prevwposition = vec4(prevW * spos).xyz;')
            tese.add_out('vec4 wvpposition')
            tese.add_out('vec4 prevwvpposition')
            tese.add_uniform('mat4 prevVP', '_prevViewProjectionMatrix')
            tese.write('wvpposition = gl_Position;')
            make_tess.interpolate(tese, 'prevwposition', 3)
            tese.write('prevwvpposition = prevVP * vec4(prevwposition, 1.0);')
    else:
        frag.add_out('vec4[2] fragColor')

    # Pack gbuffer
    frag.add_include('../../Shaders/std/gbuffer.glsl')
    frag.write('n /= (abs(n.x) + abs(n.y) + abs(n.z));')
    frag.write('n.xy = n.z >= 0.0 ? n.xy : octahedronWrap(n.xy);')
    frag.write('fragColor[0] = vec4(n.xy, packFloat(metallic, roughness), 1.0 - gl_FragCoord.z);')
    frag.write('fragColor[1] = vec4(basecol.rgb, occlusion);')

    if '_Veloc' in wrd.rp_defs:
        frag.write('vec2 posa = (wvpposition.xy / wvpposition.w) * 0.5 + 0.5;')
        frag.write('vec2 posb = (prevwvpposition.xy / prevwvpposition.w) * 0.5 + 0.5;')
        frag.write('fragColor[2].rg = vec2(posa - posb);')

    return con_mesh

def make_forward(con_mesh):
    make_forward_base(con_mesh)

    frag = con_mesh.frag
    frag.add_out('vec4 fragColor')

    frag.write('fragColor = vec4(direct * lightColor * visibility + indirect * occlusion * envmapStrength, 1.0);')
    
    if '_LDR' in bpy.data.worlds['Arm'].rp_defs:
        frag.write('fragColor.rgb = pow(fragColor.rgb, vec3(1.0 / 2.2));')

def make_forward_base(con_mesh, parse_opacity=False):
    wrd = bpy.data.worlds['Arm']
    make_base(con_mesh, parse_opacity=parse_opacity)
    vert = con_mesh.vert
    frag = con_mesh.frag
    tese = con_mesh.tese

    frag.add_include('../../Shaders/std/brdf.glsl')
    frag.add_include('../../Shaders/std/math.glsl')
    frag.add_uniform('vec3 lightColor', '_lampColor')
    frag.add_uniform('vec3 lightDir', '_lampDirection')
    frag.add_uniform('vec3 lightPos', '_lampPosition')
    frag.add_uniform('int lightType', '_lampType')
    frag.add_uniform('float envmapStrength', link='_envmapStrength')

    if '_Irr' in wrd.world_defs:
        frag.add_include('../../Shaders/std/shirr.glsl')
        frag.add_uniform('vec4 shirr[7]', link='_envmapIrradiance', included=True)
        if '_Rad' in wrd.world_defs:
            frag.add_uniform('sampler2D senvmapRadiance', link='_envmapRadiance')
            frag.add_uniform('sampler2D senvmapBrdf', link='_envmapBrdf')
            frag.add_uniform('int envmapNumMipmaps', link='_envmapNumMipmaps')

    if '_NoShadows' in wrd.world_defs:
        is_shadows = False
    else:
        is_shadows = True
    if '_PCSS' in wrd.world_defs:
        is_pcss = True
    else:
        is_pcss = False

    frag.write('float visibility = 1.0;')

    frag.write('vec3 l;')
    frag.write('if (lightType == 0) l = lightDir;')
    frag.write('else { l = normalize(lightPos - wposition); visibility *= attenuate(distance(wposition, lightPos)); }')
    frag.write('vec3 h = normalize(v + l);')
    frag.write('float dotNL = dot(n, l);')
    frag.write('float dotNH = dot(n, h);')
    frag.write('float dotVH = dot(v, h);')

    if is_shadows:
        if tese != None:
            tese.add_out('vec4 lampPos')
            tese.add_uniform('mat4 LVP', '_biasLampViewProjectionMatrix')
            tese.write('lampPos = LVP * vec4(wposition, 1.0);')
        else:
            vert.add_out('vec4 lampPos')
            vert.add_uniform('mat4 LWVP', '_biasLampWorldViewProjectionMatrix')
            vert.write('lampPos = LWVP * spos;')
        
        if is_pcss:
            frag.add_include('../../Shaders/std/shadows_pcss.glsl')
            frag.add_uniform('sampler2D snoise', link='_noise64', included=True)
            frag.add_uniform('float lampSizeUV', link='_lampSizeUV', included=True)
        else:
            frag.add_include('../../Shaders/std/shadows.glsl')
        frag.add_uniform('sampler2D shadowMap', included=True)
        frag.add_uniform('bool receiveShadow')
        frag.add_uniform('float shadowsBias', '_lampShadowsBias')

        frag.write('if (receiveShadow && lampPos.w > 0.0) {')
        frag.tab += 1
        frag.write('vec3 lpos = lampPos.xyz / lampPos.w;')
        # frag.write('float bias = clamp(shadowsBias * 1.0 * tan(acos(clamp(dotNL, 0.0, 1.0))), 0.0, 0.01);')
        if is_pcss:
            frag.write('visibility = PCSS(lpos.xy, lpos.z - shadowsBias);')
        else:
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

    frag.write('vec3 albedo = surfaceAlbedo(basecol, metallic);')
    frag.write('vec3 f0 = surfaceF0(basecol, metallic);')
    frag.write('vec3 direct = lambertDiffuseBRDF(albedo, dotNL);')
    frag.write('direct += specularBRDF(f0, roughness, dotNL, dotNH, dotNV, dotVH);')

    if '_Irr' in wrd.world_defs:
        frag.write('vec3 indirect = (shIrradiance(n, 2.2) / PI) * albedo;')

        if '_Rad' in wrd.world_defs:
            frag.write('vec3 reflectionWorld = reflect(-v, n);')
            frag.write('float lod = getMipFromRoughness(roughness, envmapNumMipmaps);')
            frag.write('vec3 prefilteredColor = textureLod(senvmapRadiance, envMapEquirect(reflectionWorld), lod).rgb;')
            if '_EnvLDR' in wrd.world_defs:
                frag.write('prefilteredColor = pow(prefilteredColor, vec3(2.2));')
            frag.write('vec2 envBRDF = texture(senvmapBrdf, vec2(roughness, 1.0 - dotNV)).xy;')
            frag.write('indirect += prefilteredColor * (f0 * envBRDF.x + envBRDF.y);')
    else:
        frag.write('vec3 indirect = albedo;')
