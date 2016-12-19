import bpy
import make_state as state
import material.mat_state as mat_state
import material.mat_utils as mat_utils
import material.cycles as cycles
import material.make_shadows as make_shadows
import material.make_skin as make_skin
import armutils
import assets

def make(context_id, rid):
    if rid == 'forward':
        return make_forward(context_id)
    elif rid == 'deferred':
        return make_deferred(context_id)

def make_deferred(context_id):
    con_mesh = mat_state.data.add_context({ 'name': context_id, 'depth_write': True, 'compare_mode': 'less', 'cull_mode': 'clockwise' })

    vert = con_mesh.make_vert()
    frag = con_mesh.make_frag(mrt=2)
    geom = None
    tesc = None
    tese = None

    vert.add_out('vec3 wposition')
    vert.add_uniform('mat4 W', '_worldMatrix')
    vert.add_uniform('mat4 N', '_normalMatrix')
    vert.write_pre = True
    vert.write('vec4 spos = vec4(pos, 1.0);')
    if mat_state.data.is_elem('off'):
        vert.write('spos.xyz += off;')
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
        tesc.write_tesc_levels()

        tese.add_out('vec3 wposition')
        tese.add_out('vec3 wnormal')
        tese.add_out('vec3 eyeDir')
        tese.write('vec3 p0 = gl_TessCoord.x * tc_wposition[0];')
        tese.write('vec3 p1 = gl_TessCoord.y * tc_wposition[1];')
        tese.write('vec3 p2 = gl_TessCoord.z * tc_wposition[2];')
        tese.write('wposition = p0 + p1 + p2;')
        tese.write('vec3 n0 = gl_TessCoord.x * tc_wnormal[0];')
        tese.write('vec3 n1 = gl_TessCoord.y * tc_wnormal[1];')
        tese.write('vec3 n2 = gl_TessCoord.z * tc_wnormal[2];')
        tese.write('wnormal = normalize(n0 + n1 + n2);')
    # No displacement
    else:
        frag.ins = vert.outs
        vert.add_out('vec3 eyeDir')
        vert.add_uniform('mat4 WVP', '_worldViewProjectionMatrix')
        vert.add_uniform('vec3 eye', '_cameraPosition')
        vert.write('eyeDir = eye - wposition;')
        vert.write('gl_Position = WVP * spos;')

    frag.add_include('../../Shaders/compiled.glsl')
    frag.add_include('../../Shaders/std/gbuffer.glsl')
    frag.write('vec3 v = normalize(eyeDir);')
    frag.write('float dotNV = max(dot(n, v), 0.0);') # frag.write('float dotNV = dot(n, v);')

    frag.write('vec3 basecol;')
    frag.write('float roughness;')
    frag.write('float metallic;')
    frag.write('float occlusion;')

    cycles.parse(mat_state.nodes, vert, frag, geom, tesc, tese)

    if mat_state.data.is_elem('tex'):
        vert.add_out('vec2 texCoord')
        vert.write('texCoord = tex;')
        if tese != None:
            # TODO: also includes texCoord1
            tese.write_pre = True
            if frag.contains('texCoord'):
                tese.add_out('vec2 texCoord')
                tese.write('vec2 tc0 = gl_TessCoord.x * tc_texCoord[0];')
                tese.write('vec2 tc1 = gl_TessCoord.y * tc_texCoord[1];')
                tese.write('vec2 tc2 = gl_TessCoord.z * tc_texCoord[2];')
                tese.write('texCoord = tc0 + tc1 + tc2;')
            elif tese.contains('texCoord'):
                tese.write('vec2 tc0 = gl_TessCoord.x * tc_texCoord[0];')
                tese.write('vec2 tc1 = gl_TessCoord.y * tc_texCoord[1];')
                tese.write('vec2 tc2 = gl_TessCoord.z * tc_texCoord[2];')
                tese.write('vec2 texCoord = tc0 + tc1 + tc2;')
            tese.write_pre = False

    if mat_state.data.is_elem('tex1'):
        vert.add_out('vec2 texCoord1')
        vert.write('texCoord1 = tex1;')
        if tese != None:
            tese.write_pre = True
            if frag.contains('texCoord1'):
                tese.add_out('vec2 texCoord1')
                tese.write('vec2 tc01 = gl_TessCoord.x * tc_texCoord1[0];')
                tese.write('vec2 tc11 = gl_TessCoord.y * tc_texCoord1[1];')
                tese.write('vec2 tc21 = gl_TessCoord.z * tc_texCoord1[2];')
                tese.write('texCoord1 = tc01 + tc11 + tc21;')
            elif tese.contains('texCoord1'):
                tese.write('vec2 tc01 = gl_TessCoord.x * tc_texCoord1[0];')
                tese.write('vec2 tc11 = gl_TessCoord.y * tc_texCoord1[1];')
                tese.write('vec2 tc21 = gl_TessCoord.z * tc_texCoord1[2];')
                tese.write('vec2 texCoord1 = tc01 + tc11 + tc21;')
            tese.write_pre = False

    if mat_state.data.is_elem('col'):
        vert.add_out('vec3 vcolor')
        vert.write('vcolor = col;')
        if tese != None:
            tese.write_pre = True
            tese.add_out('vec3 vcolor')
            tese.write('vec3 vcol0 = gl_TessCoord.x * tc_vcolor[0];')
            tese.write('vec3 vcol1 = gl_TessCoord.y * tc_vcolor[1];')
            tese.write('vec3 vcol2 = gl_TessCoord.z * tc_vcolor[2];')
            tese.write('vcolor = vcol0 + vcol1 + vcol2;')
            tese.write_pre = False

    if mat_state.data.is_elem('tan'):
        if tese != None:
            vert.add_out('vec3 wnormal')
            vert.add_out('vec3 wtangent')
            write_norpos(vert)
            vert.write('wtangent = normalize(mat3(N) * tan);')
            tese.add_out('mat3 TBN')
            tese.write('vec3 tan0 = gl_TessCoord.x * tc_wtangent[0];')
            tese.write('vec3 tan1 = gl_TessCoord.y * tc_wtangent[1];')
            tese.write('vec3 tan2 = gl_TessCoord.z * tc_wtangent[2];')
            tese.write('vec3 wtangent = normalize(tan0 + tan1 + tan2);')
            tese.write('vec3 wbitangent = normalize(cross(wnormal, wtangent));')
            tese.write('TBN = mat3(wtangent, wbitangent, wnormal);')
        else:
            vert.add_out('mat3 TBN')
            write_norpos(vert, declare=True)
            vert.write('vec3 tangent = normalize(mat3(N) * tan);')
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

    # Pack gbuffer
    frag.write('n /= (abs(n.x) + abs(n.y) + abs(n.z));')
    frag.write('n.xy = n.z >= 0.0 ? n.xy : octahedronWrap(n.xy);')
    frag.write('fragColor[0] = vec4(n.xy, packFloat(metallic, roughness), 1.0 - gl_FragCoord.z);')
    frag.write('fragColor[1] = vec4(basecol.rgb, occlusion);')

    return con_mesh

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
    vert.write('wposition = vec4(W * spos).xyz;')
    vert.write_pre = False

def make_forward(context_id):
    con_mesh = mat_state.data.add_context({ 'name': context_id, 'depth_write': True, 'compare_mode': 'less', 'cull_mode': 'clockwise' })
    forward(con_mesh)
    return con_mesh

def forward(con_mesh, mrt=1):
    wrd = bpy.data.worlds['Arm']
    if '_PCSS' in wrd.world_defs:
        is_pcss = True
    else:
        is_pcss = False

    vert = con_mesh.make_vert()
    frag = con_mesh.make_frag(mrt=mrt)
    geom = None
    tesc = None
    tese = None

    frag.ins = vert.outs

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
    # frag.write('float dotNV = dot(n, v);')
    frag.write('float dotNV = max(dot(n, v), 0.0);')
    frag.write('float dotNH = dot(n, h);')
    frag.write('float dotVH = dot(v, h);')

    vert.add_out('vec4 lampPos')
    vert.add_uniform('mat4 LWVP', '_lampWorldViewProjectionMatrix')
    vert.write('lampPos = LWVP * spos;')
    if is_pcss:
        frag.add_include('../../Shaders/std/shadows_pcss.glsl')
        frag.add_uniform('sampler2D snoise', link='_noise64', included=True)
    else:
        frag.add_include('../../Shaders/std/shadows.glsl')
    frag.add_uniform('sampler2D shadowMap', included=True)
    frag.add_uniform('float lampSizeUV', link='_lampSizeUV', included=True)
    frag.add_uniform('bool receiveShadow')
    frag.add_uniform('float shadowsBias', '_lampShadowsBias')
    frag.write('float visibility = 1.0;')
    frag.write('if (receiveShadow && lampPos.w > 0.0) {')
    frag.tab += 1
    frag.write('vec3 lpos = lampPos.xyz / lampPos.w;')
    frag.write('lpos.xy = lpos.xy * 0.5 + 0.5;')
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

    frag.write('vec3 basecol;')
    frag.write('float roughness;')
    frag.write('float metallic;')
    frag.write('float occlusion;')

    cycles.parse(mat_state.nodes, vert, frag, geom, tesc, tese)

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

    frag.write('fragColor = vec4(direct * lightColor * visibility + indirect * occlusion * envmapStrength, 1.0);')
