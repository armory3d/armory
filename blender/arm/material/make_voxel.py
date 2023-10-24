import bpy

import arm.utils
import arm.assets as assets
import arm.material.cycles as cycles
import arm.material.mat_state as mat_state
import arm.material.mat_utils as mat_utils
import arm.material.make_particle as make_particle
import arm.make_state as state

import arm.utils
import arm.assets as assets
import arm.material.mat_state as mat_state

if arm.is_reload(__name__):
    arm.utils = arm.reload_module(arm.utils)
    assets = arm.reload_module(assets)
    mat_state = arm.reload_module(mat_state)
else:
    arm.enable_reload(__name__)

def make(context_id):
    rpdat = arm.utils.get_rp()
    if rpdat.rp_voxels == 'Voxel GI':
        con = make_gi(context_id)
    else:
        con = make_ao(context_id)

    assets.vs_equal(con, assets.shader_cons['voxel_vert'])
    assets.fs_equal(con, assets.shader_cons['voxel_frag'])
    assets.gs_equal(con, assets.shader_cons['voxel_geom'])

    return con

def make_gi(context_id):
    con_voxel = mat_state.data.add_context({ 'name': context_id, 'depth_write': False, 'compare_mode': 'always', 'cull_mode': 'none', 'color_write_red': False, 'color_write_green': False, 'color_write_blue': False, 'color_write_alpha': False, 'conservative_raster': True })
    wrd = bpy.data.worlds['Arm']

    vert = con_voxel.make_vert()
    frag = con_voxel.make_frag()
    geom = con_voxel.make_geom()
    tesc = None
    tese = None
    geom.ins = vert.outs
    frag.ins = geom.outs

    vert.add_include('compiled.inc')
    geom.add_include('compiled.inc')
    frag.add_include('compiled.inc')
    frag.add_include('std/math.glsl')
    frag.add_include('std/imageatomic.glsl')
    frag.add_include('std/gbuffer.glsl')
    frag.add_include('std/brdf.glsl')
    frag.write_header('#extension GL_ARB_shader_image_load_store : enable')

    rpdat = arm.utils.get_rp()
    frag.add_uniform('layout(rgba8) image3D voxels')

    frag.write('vec3 basecol;')
    frag.write('float roughness;') #
    frag.write('float metallic;') #
    frag.write('float occlusion;') #
    frag.write('float specular;') #
    frag.write('vec3 emissionCol = vec3(0.0);')
    parse_opacity = rpdat.arm_voxelgi_refraction
    if parse_opacity:
        frag.write('float opacity;')
        frag.write('float ior;')

    frag.write('float dotNV = 0.0;')
    cycles.parse(mat_state.nodes, con_voxel, vert, frag, geom, tesc, tese, parse_opacity=False, parse_displacement=False, basecol_only=True)

    # Voxelized particles
    particle = mat_state.material.arm_particle_flag
    if particle and rpdat.arm_particles == 'On':
        # make_particle.write(vert, particle_info=cycles.particle_info)
        frag.write_pre = True
        frag.write('const float p_index = 0;')
        frag.write('const float p_age = 0;')
        frag.write('const float p_lifetime = 0;')
        frag.write('const vec3 p_location = vec3(0);')
        frag.write('const float p_size = 0;')
        frag.write('const vec3 p_velocity = vec3(0);')
        frag.write('const vec3 p_angular_velocity = vec3(0);')
        frag.write_pre = False

    if not frag.contains('vec3 n ='):
        frag.write_pre = True
        frag.write('vec3 n;')
        frag.write_pre = False

    export_mpos = frag.contains('mposition') and not frag.contains('vec3 mposition')
    if export_mpos:
        vert.add_out('vec3 mpositionGeom')
        vert.write_pre = True
        vert.write('mpositionGeom = pos;')
        vert.write_pre = False

    export_bpos = frag.contains('bposition') and not frag.contains('vec3 bposition')
    if export_bpos:
        vert.add_out('vec3 bpositionGeom')
        vert.add_uniform('vec3 dim', link='_dim')
        vert.add_uniform('vec3 hdim', link='_halfDim')
        vert.write_pre = True
        vert.write('bpositionGeom = (pos.xyz + hdim) / dim;')
        vert.write_pre = False

    vert.add_uniform('mat4 W', '_worldMatrix')
    vert.add_uniform('mat3 N', '_normalMatrix')
    vert.add_out('vec3 voxpositionGeom')

    if con_voxel.is_elem('col'):
        vert.add_out('vec3 vcolorGeom')
        vert.write('vcolorGeom = col.rgb;')

    if con_voxel.is_elem('tex'):
        vert.add_out('vec2 texCoordGeom')
        vert.write('texCoordGeom = tex;')

    vert.add_uniform('vec3 viewerPos', '_viewerPos')
    vert.add_uniform('vec3 eyeLook', '_cameraLook')

    vert.write('vec3 P = vec3(W * vec4(pos.xyz, 1.0));')
    vert.write('float dist = max(abs(P.x - viewerPos.x), max(abs(P.y - viewerPos.y), abs(P.z - viewerPos.z)));')
    vert.write('int clipmapLevel = int(max(log2(dist / voxelgiHalfExtents.x * 0.125), 0));')
    vert.write('float voxelSize = pow(2.0, clipmapLevel) * 4.0;')
    vert.write('vec3 eyeSnap = floor((viewerPos + eyeLook) / voxelSize) * voxelSize;')
    vert.write('voxpositionGeom = (P - eyeSnap) / voxelSize * 0.25 / voxelgiHalfExtents.x;')

    geom.add_out('vec3 voxposition')
    geom.add_out('vec3 voxnormal')

    if con_voxel.is_elem('col'):
        geom.add_out('vec3 vcolor')
    if con_voxel.is_elem('tex'):
        geom.add_out('vec2 texCoord')
    if export_mpos:
        geom.add_out('vec3 mposition')
    if export_bpos:
        geom.add_out('vec3 bposition')

    geom.write('vec3 p1 = voxpositionGeom[1] - voxpositionGeom[0];')
    geom.write('vec3 p2 = voxpositionGeom[2] - voxpositionGeom[0];')

    geom.write('vec3 p = abs(cross(p1, p2));')
    geom.write('for (uint i = 0; i < 3; ++i) {')
    geom.write('    voxposition = voxpositionGeom[i];')
    if '_Sun' in wrd.world_defs:
        geom.write('lightPosition = lightPositionGeom[i];')
    if '_SinglePoint' in wrd.world_defs and '_Spot' in wrd.world_defs:
        geom.write('spotPosition = spotPositionGeom[i];')
    if con_voxel.is_elem('col'):
        geom.write('    vcolor = vcolorGeom[i];')
    if con_voxel.is_elem('tex'):
        geom.write('    texCoord = texCoordGeom[i];')
    if export_mpos:
        geom.write('    mposition = mpositionGeom[i];')
    if export_bpos:
        geom.write('    bposition = bpositionGeom[i];')
    geom.write('    if (p.z > p.x && p.z > p.y) {')
    geom.write('        gl_Position = vec4(voxposition.x, voxposition.y, 0.0, 1.0);')
    geom.write('    }')
    geom.write('    else if (p.x > p.y && p.x > p.z) {')
    geom.write('        gl_Position = vec4(voxposition.y, voxposition.z, 0.0, 1.0);')
    geom.write('    }')
    geom.write('    else {')
    geom.write('        gl_Position = vec4(voxposition.x, voxposition.z, 0.0, 1.0);')
    geom.write('    }')
    geom.write('    EmitVertex();')
    geom.write('}')
    geom.write('EndPrimitive();')

    is_shadows = '_ShadowMap' in wrd.world_defs
    is_shadows_atlas = '_ShadowMapAtlas' in wrd.world_defs
    shadowmap_sun = 'shadowMap'
    if is_shadows_atlas:
        is_single_atlas = '_SingleAtlas' in wrd.world_defs
        shadowmap_sun = 'shadowMapAtlasSun' if not is_single_atlas else 'shadowMapAtlas'
        frag.add_uniform('vec2 smSizeUniform', '_shadowMapSize', included=True)
    frag.write('vec3 direct = vec3(0.0);')

    if '_Sun' in wrd.world_defs:
        frag.add_uniform('vec3 sunCol', '_sunColor')
        frag.add_uniform('vec3 sunDir', '_sunDirection')
        frag.write('float svisibility = 1.0;')
        vert.add_out('vec4 lightPositionGeom')
        geom.add_out('vec4 lightPosition')
        if is_shadows:
            vert.add_uniform('mat4 LWVP', '_biasLightWorldViewProjectionMatrixSun')
            vert.write('lightPositionGeom = LWVP * pos;')
            frag.add_uniform('bool receiveShadow')
            frag.add_uniform(f'sampler2DShadow {shadowmap_sun}')
            frag.add_uniform('float shadowsBias', '_sunShadowsBias')

            frag.write('if (receiveShadow) {')
            frag.write('    if (lightPosition.w > 0.0) {')
            frag.write('    vec3 lPos = lightPosition.xyz / lightPosition.w;')
            if '_Legacy' in wrd.world_defs:
                frag.write(f'       svisibility = float(texture({shadowmap_sun}, vec2(lPos.xy)).r > lPos.z - shadowsBias);')
            else:
                frag.write(f'        svisibility = texture({shadowmap_sun}, vec3(lPos.xy, lPos.z - shadowsBias)).r;')
            frag.write('    }')
            frag.write('}') # receiveShadow
            frag.write('basecol *= sunCol * svisibility;')

    if '_SinglePoint' in wrd.world_defs:
        frag.add_uniform('vec3 pointPos', '_pointPosition')
        frag.add_uniform('vec3 pointCol', '_pointColor')
        if '_Spot' in wrd.world_defs:
            frag.add_uniform('vec3 spotDir', link='_spotDirection')
            frag.add_uniform('vec3 spotRight', link='_spotRight')
            frag.add_uniform('vec4 spotData', link='_spotData')
        frag.write('float visibility = 1.0;')
        frag.write('vec3 ld = pointPos - voxposition;')
        frag.write('vec3 l = normalize(ld);')
        frag.write('float dotNL = max(dot(n, l), 0.0);')
        if is_shadows:
            frag.add_uniform('bool receiveShadow')
            frag.add_uniform('float pointBias', link='_pointShadowsBias')
            frag.add_include('std/shadows.glsl')

            frag.write('if (receiveShadow) {')
            if '_Spot' in wrd.world_defs:
                vert.add_out('vec4 spotPositionGeom')
                geom.add_out('vec4 spotPosition')
                vert.add_uniform('mat4 LWVPSpotArray[1]', link='_biasLightWorldViewProjectionMatrixSpotArray')
                vert.write('spotPositionGeom = LWVPSpotArray[0] * pos;')
                frag.add_uniform('sampler2DShadow shadowMapSpot[1]')
                frag.write('if (spotPosition.w > 0.0) {')
                frag.write('    vec3 lPos = spotPosition.xyz / spotPosition.w;')
                if '_Legacy' in wrd.world_defs:
                    frag.write('    visibility = float(texture(shadowMapSpot[0], vec2(lPos.xy)).r > lPos.z - pointBias);')
                else:
                    frag.write('    visibility = texture(shadowMapSpot[0], vec3(lPos.xy, lPos.z - pointBias)).r;')
                frag.write('}')
            else:
                frag.add_uniform('vec2 lightProj', link='_lightPlaneProj')
                frag.add_uniform('samplerCubeShadow shadowMapPoint[1]')
                frag.write('const float s = shadowmapCubePcfSize;') # TODO: incorrect...
                frag.write('float compare = lpToDepth(ld, lightProj) - pointBias * 1.5;')
                frag.write('#ifdef _InvY')
                frag.write('l.y = -l.y;')
                frag.write('#endif')
                if '_Legacy' in wrd.world_defs:
                    frag.write('visibility *= float(texture(shadowMapPoint[0], vec3(-l + n * pointBias * 20)).r > compare);')
                else:
                    frag.write('visibility *= texture(shadowMapPoint[0], vec4(-l + n * pointBias * 20, compare)).r;')
            frag.write('}')
            frag.write('basecol *= pointCol * attenuate(distance(voxposition, pointPos)) * visibility;')

    if '_Clusters' in wrd.world_defs:
        is_shadows = '_ShadowMap' in wrd.world_defs
        is_shadows_atlas = '_ShadowMapAtlas' in wrd.world_defs
        is_single_atlas = '_SingleAtlas' in wrd.world_defs
        frag.add_include_front('std/clusters.glsl')
        frag.add_uniform('vec2 cameraProj', link='_cameraPlaneProj')
        frag.add_uniform('vec2 cameraPlane', link='_cameraPlane')
        frag.add_uniform('vec4 lightsArray[maxLights * 3]', link='_lightsArray')
        frag.add_uniform('sampler2D clustersData', link='_clustersData')
        if is_shadows:
            frag.add_uniform('bool receiveShadow')
            frag.add_uniform('vec2 lightProj', link='_lightPlaneProj')
            frag.add_include('std/shadows.glsl')
            if is_shadows_atlas:
                if not is_single_atlas:
                    frag.add_uniform('sampler2DShadow shadowMapAtlasPoint')
                    frag.add_uniform('sampler2DShadow shadowMapAtlasSpot')
                else:
                    frag.add_uniform('sampler2DShadow shadowMapAtlas', top=True)
                    frag.add_uniform('sampler2DShadow shadowMapAtlas', top=True)
                frag.add_uniform('vec4 pointLightDataArray[maxLightsCluster]', link='_pointLightsAtlasArray')
            else:
                frag.add_uniform('samplerCubeShadow shadowMapPoint[4]')
                frag.add_uniform('sampler2DShadow shadowMapSpot[4]')
            frag.add_uniform('vec4 LWVPSpotArray[maxLightsCluster]', link='_biasLightWorldViewProjectionMatrixSpotArray')

        frag.write('float viewz = linearize(voxposition.z, cameraProj);')
        frag.write('int clusterI = getClusterI((voxposition.xy) * 0.5 + 0.5, viewz, cameraPlane);')
        frag.write('int numLights = int(texelFetch(clustersData, ivec2(clusterI, 0), 0).r * 255);')

        frag.add_uniform('vec4 lightsArraySpot[maxLights * 2]', link='_lightsArraySpot')
        frag.write('int numSpots = int(texelFetch(clustersData, ivec2(clusterI, 1 + maxLightsCluster), 0).r * 255);')
        frag.write('int numPoints = numLights - numSpots;')

        frag.write('#ifdef HLSL')
        frag.write('viewz += texture(clustersData, vec2(0.0)).r * 1e-9;') # TODO: krafix bug, needs to generate sampler
        frag.write('#endif')

        frag.write('for (int i = 0; i < min(numLights, maxLightsCluster); i++) {')
        frag.write('float visibility = 1.0;')
        frag.write('    int li = int(texelFetch(clustersData, ivec2(clusterI, i + 1), 0).r * 255);')
        frag.write('    if(lightsArray[li * 3 + 2].y == 0.0) {') #point light
        frag.write('    visibility = attenuate(distance(lightsArray[li * 3].xyz, voxposition));')
        if is_shadows_atlas:
            if not is_single_atlas:
                frag.write('    visibility *= texture(shadowMapAtlasPoint, vec4(-normalize(lightsArray[li * 3].xyz - voxposition), lpToDepth(lightsArray[li * 3].xyz, lightProj) - lightsArray[li * 3 + 2].x)).r;')
            else:
                frag.write('    visibility *= texture(shadowMapAtlas, vec4(-normalize(lightsArray[li * 3].xyz - voxposition), lpToDepth(lightsArray[li * 3].xyz, lightProj) - lightsArray[li * 3 + 2].x)).r;')
        else:
            frag.write('if (li == 0) visibility *= texture(shadowMapPoint[0], vec4(-normalize(lightsArray[li * 3].xyz - voxposition), lpToDepth(lightsArray[li * 3].xyz, lightProj) - lightsArray[li * 3 + 2].x)).r;')
            frag.write('if (li == 1) visibility *= texture(shadowMapPoint[1], vec4(-normalize(lightsArray[li * 3].xyz - voxposition), lpToDepth(lightsArray[li * 3].xyz, lightProj) - lightsArray[li * 3 + 2].x)).r;')
            frag.write('if (li == 2) visibility *= texture(shadowMapPoint[2], vec4(-normalize(lightsArray[li * 3].xyz - voxposition), lpToDepth(lightsArray[li * 3].xyz, lightProj) - lightsArray[li * 3 + 2].x)).r;')
            frag.write('if (li == 3) visibility *= texture(shadowMapPoint[3], vec4(-normalize(lightsArray[li * 3].xyz - voxposition), lpToDepth(lightsArray[li * 3].xyz, lightProj) - lightsArray[li * 3 + 2].x)).r;')

        frag.write('}')
        frag.write('    else {')#spot light
        frag.write('        vec4 lightPosition = LWVPSpotArray[li * 3] * vec4(voxposition, 1.0);')
        frag.write('        vec3 lPos = lightPosition.xyz / lightPosition.w;')
        if is_shadows_atlas:
            if not is_single_atlas:
                frag.write('        visibility *= texture(shadowMapAtlaSpot, vec3(lPos.xy, lPos.z - lightsArray[li * 3 + 2].x)).r;')
            else:
                frag.write('        visibility *= texture(shadowMapAtla, vec3(lPos.xy, lPos.z - lightsArray[li * 3 + 2].x)).r;')
        else:
            frag.write('    if (li == 0) visibility *= texture(shadowMapSpot[0], vec3(lPos.xy, lPos.z - lightsArray[li * 3 + 2].x)).r;')
            frag.write('    if (li == 1) visibility *= texture(shadowMapSpot[1], vec3(lPos.xy, lPos.z - lightsArray[li * 3 + 2].x)).r;')
            frag.write('    if (li == 2) visibility *= texture(shadowMapSpot[2], vec3(lPos.xy, lPos.z - lightsArray[li * 3 + 2].x)).r;')
            frag.write('    if (li == 3) visibility *= texture(shadowMapSpot[3], vec3(lPos.xy, lPos.z - lightsArray[li * 3 + 2].x)).r;')

        frag.write('    }')
        frag.write('basecol *= visibility * lightsArray[li * 3 + 1].xyz;')
        frag.write('}')

    frag.write('vec3 uvw = (voxposition * 0.5 + 0.5) * voxelgiResolution;')
    frag.write('imageStore(voxels, ivec3(uvw), vec4(min(surfaceAlbedo(basecol + emissionCol, metallic), vec3(1.0)), 1.0));')

    return con_voxel


def make_ao(context_id):
    con_voxel = mat_state.data.add_context({ 'name': context_id, 'depth_write': False, 'compare_mode': 'always', 'cull_mode': 'none', 'color_writes_red': [False], 'color_writes_green': [False], 'color_writes_blue': [False], 'color_writes_alpha': [False], 'conservative_raster': False })
    wrd = bpy.data.worlds['Arm']
    rpdat = arm.utils.get_rp()

    vert = con_voxel.make_vert()
    frag = con_voxel.make_frag()
    geom = con_voxel.make_geom()
    tesc = None
    tese = None

    geom.ins = vert.outs
    frag.ins = geom.outs

    frag.add_include('compiled.inc')
    geom.add_include('compiled.inc')
    frag.add_include('std/math.glsl')
    frag.add_include('std/imageatomic.glsl')
    frag.write_header('#extension GL_ARB_shader_image_load_store : enable')
    frag.add_uniform('layout(r8) writeonly image3D voxels')

    vert.add_include('compiled.inc')
    vert.add_uniform('mat4 W', '_worldMatrix')
    vert.add_out('vec3 voxpositionGeom')

    vert.add_uniform('vec3 viewerPos', '_viewerPos')
    vert.add_uniform('vec3 eyeLook', '_cameraLook')

    vert.write('vec3 P = vec3(W * vec4(pos.xyz, 1.0));')
    vert.write('float dist = max(abs(P.x - viewerPos.x), max(abs(P.y - viewerPos.y), abs(P.z - viewerPos.z)));')
    vert.write('int clipmapLevel = int(max(log2(dist / voxelgiHalfExtents.x * 0.125), 0));')
    vert.write('float voxelSize = pow(2.0, clipmapLevel) * 0.5;')
    vert.write('vec3 eyeSnap = floor((viewerPos + eyeLook) / voxelSize) * voxelSize;')
    vert.write('voxpositionGeom = (P - eyeSnap) / voxelSize * 0.25 / voxelgiHalfExtents.x;')

    geom.add_out('vec3 voxposition')

    geom.write('vec3 p1 = voxpositionGeom[1] - voxpositionGeom[0];')
    geom.write('vec3 p2 = voxpositionGeom[2] - voxpositionGeom[0];')
    geom.write('vec3 p = abs(cross(p1, p2));')
    geom.write('for (uint i = 0; i < 3; ++i) {')
    geom.write('    voxposition = voxpositionGeom[i];')
    geom.write('    if (p.z > p.x && p.z > p.y) {')
    geom.write('        gl_Position = vec4(voxposition.x, voxposition.y, 0.0, 1.0);')
    geom.write('    }')
    geom.write('    else if (p.x > p.y && p.x > p.z) {')
    geom.write('        gl_Position = vec4(voxposition.y, voxposition.z, 0.0, 1.0);')
    geom.write('    }')
    geom.write('    else {')
    geom.write('        gl_Position = vec4(voxposition.x, voxposition.z, 0.0, 1.0);')
    geom.write('    }')
    geom.write('    EmitVertex();')
    geom.write('}')
    geom.write('EndPrimitive();')

    frag.write('vec3 uvw = (voxposition * 0.5 + 0.5) * voxelgiResolution;')
    frag.write('imageStore(voxels, ivec3(uvw), vec4(1.0));')

    return con_voxel
