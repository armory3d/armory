import material.state as state
import material.make_cycles as make_cycles

def mesh(context_id):
    con_mesh = state.data.add_context({ 'name': context_id, 'depth_write': True, 'compare_mode': 'less', 'cull_mode': 'clockwise' })

    vert = con_mesh.make_vert()
    frag = con_mesh.make_frag()

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

    make_cycles.parse(state.nodes, vert, frag)

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

def shadows(context_id):
    con_shadowmap = state.data.add_context({ 'name': context_id, 'depth_write': True, 'compare_mode': 'less', 'cull_mode': 'clockwise' })

    vert = con_shadowmap.make_vert()
    vert.add_uniform('mat4 LWVP', '_lampWorldViewProjectionMatrix')
    vert.write('gl_Position = LWVP * vec4(pos, 1.0);')

    frag = con_shadowmap.make_frag()
    frag.write('fragColor = vec4(0.0);')

    return con_shadowmap
    