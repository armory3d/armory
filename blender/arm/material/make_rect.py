import bpy
import arm.make_state as state
import arm.material.mat_state as mat_state
import arm.material.mat_utils as mat_utils
import arm.material.cycles as cycles
import arm.material.make_skin as make_skin
import arm.material.make_tess as make_tess
import arm.utils

is_displacement = False

def make(context_id):
    con_rect = mat_state.data.add_context({ 'name': context_id, 'depth_write': False, 'compare_mode': 'equal', 'cull_mode': 'none' })

    make_rect(con_rect)

    return con_rect

def make_rect(con_rect):
    wrd = bpy.data.worlds['Arm']
    vert = con_rect.make_vert()
    frag = con_rect.make_frag()

    vert.vstruct_as_vsin = False # Rect structure is used instead

    vert.add_in('vec2 pos')
    vert.add_out('vec2 texCoordRect')
    vert.add_out('vec3 viewRay')
    vert.add_uniform('float materialID', link='_objectInfoMaterialIndex')
    vert.add_uniform('mat4 invVP', link='_inverseViewProjectionMatrix')
    vert.add_uniform('vec3 eye', link='_cameraPosition')
    vert.write('const vec2 madd = vec2(0.5, 0.5);') 
    vert.write('texCoordRect = pos.xy * madd + madd;')
    vert.write('const float fstep = 1.0 / 16777216.0; // 24bit')
    # vert.write('const float fstep = 1.0 / 65536.0; // 16bit')
    vert.write('gl_Position = vec4(pos.xy, (materialID * fstep) * 2.0 - 1.0, 1.0);')
    vert.write('vec4 v = vec4(pos.xy, 1.0, 1.0);')
    vert.write('v = vec4(invVP * v);')
    vert.write('v.xyz /= v.w;')
    vert.write('viewRay = v.xyz - eye;')

    frag.ins = vert.outs
    frag.add_out('vec4 fragColor')
    frag.add_include('compiled.inc')
    frag.add_include('std/brdf.glsl')
    frag.add_include('std/math.glsl')
    frag.add_include('std/gbuffer.glsl')
    frag.add_include('std/shirr.glsl')
    frag.add_include('std/shadows.glsl')

    frag.add_uniform('sampler2D gbuffer0')
    frag.add_uniform('sampler2D gbuffer1')
    frag.add_uniform('sampler2D gbuffer2')
    frag.add_uniform('sampler2D gbufferD')
    frag.add_uniform('sampler2D ssaotex')
    frag.add_uniform('sampler2D shadowMap')
    frag.add_uniform('sampler2D shadowMapCube')
    frag.add_uniform('mat4 LWVP', link='_biasLightWorldViewProjectionMatrix')
    frag.add_uniform('vec3 eye', link='_cameraPosition')
    frag.add_uniform('vec3 eyeLook', link='_cameraLook')
    frag.add_uniform('vec3 lightPos', link='_lightPosition')
    frag.add_uniform('vec3 lightColor', link='_lightColor')
    frag.add_uniform('int lightShadow', link='_lightCastShadow')
    frag.add_uniform('vec2 lightProj', link='_lightPlaneProj')
    frag.add_uniform('float shadowsBias', link='_lightShadowsBias')
    # TODO: ifdef
    frag.add_uniform('float envmapStrength', link='_envmapStrength')
    frag.add_uniform('vec4 shirr[7]', link='_envmapIrradiance', included=True)
    frag.add_uniform('sampler2D senvmapRadiance', link='_envmapRadiance')
    frag.add_uniform('sampler2D senvmapBrdf', link='_envmapBrdf')
    frag.add_uniform('int envmapNumMipmaps', link='_envmapNumMipmaps')

    frag.write_pre = True
    frag.write('vec4 g0 = texture(gbuffer0, texCoordRect);')
    frag.write('vec4 g1 = texture(gbuffer1, texCoordRect);')
    frag.write('vec4 g2 = texture(gbuffer2, texCoordRect);')
    frag.write('float depth = texture(gbufferD, texCoordRect).r * 2.0 - 1.0;')

    frag.write('vec3 n;')
    frag.write('n.z = 1.0 - abs(g0.x) - abs(g0.y);')
    frag.write('n.xy = n.z >= 0.0 ? g0.xy : octahedronWrap(g0.xy);')
    frag.write('n = normalize(n);')
    frag.write('vec2 texCoord = g0.zw;');
    frag.add_uniform('vec2 cameraProj', link='_cameraPlaneProj')
    frag.write('vec3 wposition = getPos(eye, eyeLook, viewRay, depth, cameraProj);')
    frag.write('vec3 vVec = normalize(eye - wposition);')
    frag.write_pre = False

    frag.write('float dotNV = dot(n, vVec);')
    frag.write('vec3 lp = lightPos - wposition;')
    frag.write('vec3 l = normalize(lp);')
    frag.write('float dotNL = max(dot(n, l), 0.0);')
    frag.write('vec3 h = normalize(vVec + l);')
    frag.write('float dotNH = dot(n, h);')
    frag.write('float dotVH = dot(vVec, h);')
    frag.write('float visibility = 1.0;')
    
    frag.write('vec3 basecol;')
    frag.write('float roughness;')
    frag.write('float metallic;')
    frag.write('float occlusion;')
    frag.write('float specular;')

    mat_state.texture_grad = True
    cycles.parse(mat_state.nodes, con_rect, vert, frag, None, None, None, parse_opacity=False, parse_displacement=False)
    mat_state.texture_grad = False

    frag.write('vec3 albedo = surfaceAlbedo(basecol, metallic);')
    frag.write('vec3 f0 = surfaceF0(basecol, metallic);')

    # Shadows
    frag.write('if (lightShadow == 1) {')
    frag.write('    vec4 lPos = LWVP * vec4(wposition, 1.0);')
    frag.write('    lPos.xyz /= lPos.w;')
    frag.write('    if (lPos.x > 0.0 && lPos.y > 0.0 && lPos.x < 1.0 && lPos.y < 1.0) visibility = PCF(lPos.xy, lPos.z - shadowsBias);;')
    frag.write('}')
    frag.write('else if (lightShadow == 2) {')
    frag.write('    visibility = PCFCube(shadowMapCube, lp, -l, shadowsBias, lightProj, n);')
    frag.write('}')

    frag.write('visibility *= attenuate(distance(wposition, lightPos));')

    frag.write('fragColor.rgb = lambertDiffuseBRDF(albedo, dotNL) + specularBRDF(f0, roughness, dotNL, dotNH, dotNV, dotVH) * specular;')
    frag.write('fragColor.rgb *= lightColor;')
    frag.write('fragColor.rgb *= visibility;')

    # Env
    frag.write('vec2 envBRDF = texture(senvmapBrdf, vec2(roughness, 1.0 - dotNV)).xy;')
    frag.write('vec3 envl = shIrradiance(n) / PI;')

    frag.write('vec3 reflectionWorld = reflect(-vVec, n);')
    frag.write('float lod = getMipFromRoughness(roughness, envmapNumMipmaps);')
    frag.write('vec3 prefilteredColor = textureLod(senvmapRadiance, envMapEquirect(reflectionWorld), lod).rgb;')

    frag.write('envl.rgb *= albedo;')
    frag.write('envl.rgb += prefilteredColor * (f0 * envBRDF.x + envBRDF.y);')
    frag.write('envl.rgb *= texture(ssaotex, texCoordRect).r;')
    frag.write('envl.rgb *= envmapStrength * occlusion;')

    frag.write('fragColor.rgb += envl;')
