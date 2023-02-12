import bpy
import arm.utils
import arm.assets as assets
import arm.material.cycles as cycles
import arm.material.mat_state as mat_state
import arm.material.mat_utils as mat_utils
import arm.material.make_particle as make_particle
import arm.make_state as state

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
    con_voxel = mat_state.data.add_context({ 'name': context_id, 'depth_write': False, 'compare_mode': 'always', 'cull_mode': 'none', 'color_write_reds': [False], 'color_writes_green': [False], 'color_writes_blue': [False], 'color_write_alpha': [False], 'conservative_raster': True })
    wrd = bpy.data.worlds['Arm']

    vert = con_voxel.make_vert()
    frag = con_voxel.make_frag()
    geom = con_voxel.make_geom()
    tesc = None
    tese = None
    geom.ins = vert.outs
    frag.ins = geom.outs

    frag.add_include('compiled.inc')
    frag.add_include('std/math.glsl')
    frag.add_include('std/imageatomic.glsl')
    frag.add_include('std/gbuffer.glsl')
    frag.write_header('#extension GL_ARB_shader_image_load_store : enable')

    rpdat = arm.utils.get_rp()
    if arm.utils.get_gapi() == True:#'direct3d11':
        for e in con_voxel.data['vertex_elements']:
            if e['name'] == 'nor':
                con_voxel.data['vertex_elements'].remove(e)
                break
    frag.add_uniform('layout(rgba16) writeonly image3D voxels')

    frag.write('if (abs(voxposition.z) > ' + rpdat.rp_voxelgi_resolution_z + ' || abs(voxposition.x) > 1 || abs(voxposition.y) > 1) return;')
    frag.write('vec3 wposition = voxposition * voxelgiHalfExtents;')
    if rpdat.arm_voxelgi_revoxelize and rpdat.arm_voxelgi_camera:
        frag.add_uniform('vec3 eyeSnap', '_cameraPositionSnap')
        frag.write('wposition += eyeSnap;')

    frag.write('vec3 basecol;')
    frag.write('float roughness;') #
    frag.write('float metallic;') #
    frag.write('float occlusion;') #
    frag.write('float specular;') #
    frag.write('vec3 emissionCol = vec3(0.0);') #
    frag.write('float opacity = 1.0;');
    frag.write('float dotNV = 0.0;')
    cycles.parse(mat_state.nodes, con_voxel, vert, frag, geom, tesc, tese, parse_opacity=False, parse_displacement=False, basecol_only=True)

    # Voxelized particles
    particle = mat_state.material.arm_particle_flag
    if particle and rpdat.arm_particles == 'GPU':
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
    vert.add_out('vec3 voxpositionGeom')
    vert.add_include('compiled.inc')

    if con_voxel.is_elem('col'):
        vert.add_out('vec3 vcolorGeom')
        vert.write('vcolorGeom = col.rgb;')

    if con_voxel.is_elem('tex'):
        vert.add_out('vec2 texCoordGeom')
        vert.write('texCoordGeom = tex;')

    if rpdat.arm_voxelgi_revoxelize and rpdat.arm_voxelgi_camera:
        vert.add_uniform('vec3 eyeSnap', '_cameraPositionSnap')
        vert.write('voxpositionGeom = (vec3(W * vec4(pos.xyz, 1.0)) - eyeSnap) / voxelgiHalfExtents;')
    else:
        vert.write('voxpositionGeom = vec3(W * vec4(pos.xyz, 1.0)) / voxelgiHalfExtents;')
    vert.write('gl_Position = vec4(0.0, 0.0, 0.0, 1.0);')

    geom.add_out('vec3 voxposition')
    geom.add_out('vec4 lightPosition')
    if con_voxel.is_elem('col'):
        geom.add_out('vec3 vcolor')
    if con_voxel.is_elem('tex'):
        geom.add_out('vec2 texCoord')
    if export_mpos:
        geom.add_out('vec3 mposition')
    if export_bpos:
        geom.add_out('vec3 bposition')

    if arm.utils.get_gapi() == 'direct3d11':
        voxHalfExt = str(round(rpdat.arm_voxelgi_dimensions / 2.0 + 2.0))
        if rpdat.arm_voxelgi_revoxelize and rpdat.arm_voxelgi_camera:
            vert.write('  stage_output.svpos.xyz = (mul(float4(stage_input.pos.xyz, 1.0), W).xyz - eyeSnap) / float3(' + voxHalfExt + ', ' + voxHalfExt + ', ' + voxHalfExt + ');')
        else:
            vert.write('  stage_output.svpos.xyz = mul(float4(stage_input.pos.xyz, 1.0), W).xyz / float3(' + voxHalfExt + ', ' + voxHalfExt + ', ' + voxHalfExt + ');')
        # No geom shader compiler for hlsl yet
        geom.noprocessing = True
        struct_input = 'struct SPIRV_Cross_Input {'
        struct_output= 'struct SPIRV_Cross_Output {'
        pos = 0
        if export_bpos:
            struct_input += ' float3 bpositionGeom : TEXCOORD' + str(pos) + ';'
            struct_output += ' float3 bposition : TEXCOORD' + str(pos) + ';'
            pos += 1
        struct_input += ' float3 lightPositionGeom : TEXCOORD' + str(pos) + ';'
        struct_output += ' float3 lightPosition : TEXCOORD' + str(pos) + ';'
        pos +=1
        if export_mpos:
            struct_input += ' float3 mpositionGeom : TEXCOORD' + str(pos) + ';'
            struct_output += ' float3 mposition : TEXCOORD' + str(pos) + ';'
            pos += 1
        if con_voxel.is_elem('tex'):
            struct_input += ' float2 texCoordGeom : TEXCOORD' + str(pos) + ';'
            struct_output += ' float2 texCoord : TEXCOORD' + str(pos) + ';'
            pos += 1
        if con_voxel.is_elem('col'):
            struct_input += ' float3 vcolorGeom : TEXCOORD' + str(pos) + ';'
            struct_output += ' float3 vcolor : TEXCOORD' + str(pos) + ';'
            pos += 1
        struct_input += ' float3 voxpositionGeom : TEXCOORD' + str(pos) + ';'
        struct_output += ' float3 voxposition : TEXCOORD' + str(pos) + ';'
        pos +=1
        struct_input += ' float4 gl_Position : SV_POSITION; };'
        struct_output += ' float4 gl_Position : SV_POSITION; };'
        geom.write(struct_input)
        geom.write(struct_output)
        geom.write('[maxvertexcount(3)]')
        geom.write('void main(triangle SPIRV_Cross_Input stage_input[3], inout TriangleStream<SPIRV_Cross_Output> output) {')
        geom.write('  float3 p1 = stage_input[1].voxpositionGeom.xyz - stage_input[0].voxpositionGeom.xyz;')
        geom.write('  float3 p2 = stage_input[2].voxpositionGeom.xyz - stage_input[0].voxpositionGeom.xyz;')
        geom.write('  float3 p = abs(cross(p1, p2));')
        geom.write('  for (int i = 0; i < 3; ++i) {')
        geom.write('    SPIRV_Cross_Output stage_output;')
        geom.write('    stage_output.voxposition = stage_input[i].voxpositionGeom;')
        geom.write('    stage_output.lightPosition = stage_input[i].lightPositionGeom;')
        if con_voxel.is_elem('col'):
            geom.write('    stage_output.vcolor = stage_input[i].vcolorGeom;')
        if con_voxel.is_elem('tex'):
            geom.write('    stage_output.texCoord = stage_input[i].texCoordGeom;')
        if export_mpos:
            geom.write('    stage_output.mposition = stage_input[i].mpositionGeom;')
        if export_bpos:
            geom.write('    stage_output.bposition = stage_input[i].bpositionGeom;')
        geom.write('    if (p.z > p.x && p.z > p.y) {')
        geom.write('      stage_output.gl_Position = float4(stage_input[i].voxpositionGeom.x, stage_input[i].voxpositionGeom.y, 0.0, 1.0);')
        geom.write('    }')
        geom.write('    else if (p.x > p.y && p.x > p.z) {')
        geom.write('      stage_output.gl_Position = float4(stage_input[i].voxpositionGeom.y, stage_input[i].voxpositionGeom.z, 0.0, 1.0);')
        geom.write('    }')
        geom.write('    else {')
        geom.write('      stage_output.gl_Position = float4(stage_input[i].voxpositionGeom.x, stage_input[i].voxpositionGeom.z, 0.0, 1.0);')

        geom.write('    }')
        geom.write('    output.Append(stage_output);')
        geom.write('  }')
        geom.write('}')
    else:
        if rpdat.arm_voxelgi_revoxelize and rpdat.arm_voxelgi_camera:
            vert.add_uniform('vec3 eyeSnap', '_cameraPositionSnap')
            vert.write('voxpositionGeom = (vec3(W * vec4(pos.xyz, 1.0)) - eyeSnap) / voxelgiHalfExtents;')
        else:
            vert.write('voxpositionGeom = vec3(W * vec4(pos.xyz, 1.0)) / voxelgiHalfExtents;')
    
        geom.write('vec3 p1 = voxpositionGeom[1] - voxpositionGeom[0];')
        geom.write('vec3 p2 = voxpositionGeom[2] - voxpositionGeom[0];')
        geom.write('vec3 p = abs(cross(p1, p2));')
        geom.write('for (uint i = 0; i < 3; ++i) {')
        geom.write('    voxposition = voxpositionGeom[i];')
        geom.write('    lightPosition = lightPositionGeom[i];')
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

    frag.add_include('std/light.glsl')
    is_shadows = '_ShadowMap' in wrd.world_defs
    is_shadows_atlas = '_ShadowMapAtlas' in wrd.world_defs
    is_single_atlas = is_shadows_atlas and '_SingleAtlas' in wrd.world_defs
    shadowmap_sun = 'shadowMap'
    if is_shadows_atlas:
        shadowmap_sun = 'shadowMapAtlasSun' if not is_single_atlas else 'shadowMapAtlas'
        frag.add_uniform('vec2 smSizeUniform', '_shadowMapSize', included=True)

    frag.add_uniform('vec3 eye', '_cameraPosition')
    frag.write('vec3 eyeDir;')
    frag.write('eyeDir = normalize(eye - wposition);')
    
    frag.write('vec3 vVec = normalize(eyeDir);')
    frag.write('dotNV = max(dot(n, vVec), 0.0);')
    frag.write('float svisibility = 1.0;')

    vert.add_out('vec4 lightPositionGeom')

    if '_Sun' in wrd.world_defs:
        vert.add_uniform('mat4 LWVP', link='_biasLightWorldViewProjectionMatrix')
        vert.write('lightPositionGeom = LWVP * vec4(pos.xyz, 1.0);')
        frag.add_uniform('vec3 sunCol', '_sunColor')
        frag.add_uniform('vec3 sunDir', '_sunDirection')
        frag.write('vec3 sh = normalize(vVec + sunDir);')
        frag.write('float sdotNL = dot(n, sunDir);')
        frag.write('float sdotNH = dot(n, sh);')
        frag.write('float sdotVH = dot(vVec, sh);')
        if is_shadows:
            frag.add_uniform('bool receiveShadow')
            frag.add_uniform(f'sampler2DShadow {shadowmap_sun}', top=True)
            frag.add_uniform('float shadowsBias', '_sunShadowsBias')
            frag.write('if (receiveShadow) {')
            if '_CSM' in wrd.world_defs:
                frag.add_include('std/shadows.glsl')
                frag.add_uniform('vec4 casData[shadowmapCascades * 4 + 4]', '_cascadeData', included=True)
                frag.add_uniform('vec3 eye', '_cameraPosition')
                frag.write(f'svisibility = shadowTestCascade({shadowmap_sun}, eye, wposition, shadowsBias);')
            else:
                vert.add_uniform('mat4 LVP', '_biasLightViewProjectionMatrix')
                vert.write('lightPos = LVP * vec4(wposition + n * shadowsBias * 100.0, 1.0);')
                frag.write('if(lightPosition.w > 0.0) svisibility = shadowTest({shadowmap_sun}, wposition, shadowsBias);')
            frag.write('}')
        frag.write('basecol *= svisibility * sunCol;')

    frag.write('vec3 albedo = surfaceAlbedo(basecol, metallic);')
    frag.write('vec3 f0 = surfaceF0(basecol, metallic);')

    if '_SinglePoint' in wrd.world_defs:
        frag.add_uniform('vec3 pointPos', link='_pointPosition')
        frag.add_uniform('vec3 pointCol', link='_pointColor')
        if '_Spot' in wrd.world_defs:
            frag.add_uniform('vec3 spotDir', link='_spotDirection')
            frag.add_uniform('vec3 spotRight', link='_spotRight')
            frag.add_uniform('vec4 spotData', link='_spotData')
        if is_shadows:
            frag.add_uniform('bool receiveShadow')
            frag.add_uniform('float pointBias', link='_pointShadowsBias')
            if '_Spot' in wrd.world_defs:
                # Skip world matrix, already in world-space
                frag.add_uniform('mat4 LWVPSpot[1]', link='_biasLightViewProjectionMatrixSpotArray', included=True)
                frag.add_uniform('sampler2DShadow shadowMapSpot[1]', included=True)
            else:
                frag.add_uniform('vec2 lightProj', link='_lightPlaneProj', included=True)
                frag.add_uniform('samplerCubeShadow shadowMapPoint[1]', included=True)
        frag.write('basecol += sampleLight(')
        frag.write('  wposition, n, vVec, dotNV, pointPos, pointCol, albedo, roughness, specular, f0, true')
        if is_shadows:
            frag.write('  , 0, pointBias, receiveShadow')
        if '_Spot' in wrd.world_defs:
            frag.write('  , true, spotData.x, spotData.y, spotDir, spotData.zw, spotRight')
        #Just pass garbage data here
        if '_VoxelShadow' in wrd.world_defs and ('_VoxelGI' in wrd.world_defs or '_VoxelAO' in wrd.world_defs):
            frag.add_uniform('sampler3D vox');
            frag.write_attrib('vec3 posvox;');
            frag.write(', vox, posvox')
        if '_MicroShadowing' in wrd.world_defs:
            frag.write(', 0.0')
        if '_SSRS' in wrd.world_defs:
            frag.add_uniform('sampler2D d');
            frag.write_attrib('mat4 m;');
            frag.write_attrib('vec3 e;');
            frag.write(', d, m, e')
        frag.write(');')

    if '_Clusters' in wrd.world_defs:
        frag.add_uniform('vec4 lightsArray[maxLights * 3]', link='_lightsArray')
        frag.add_uniform('sampler2D clustersData', link='_clustersData')

        frag.add_include_front('std/clusters.glsl')
        frag.add_uniform('vec2 cameraProj', link='_cameraPlaneProj')
        frag.add_uniform('vec2 cameraPlane', link='_cameraPlane')

        geom.add_out('vec4 wvpposition')
        geom.write('wvpposition = gl_Position;')

        if is_shadows:
            frag.add_uniform('bool receiveShadow')
            frag.add_uniform('vec2 lightProj', link='_lightPlaneProj', included=True)
            if is_shadows_atlas:
                if not is_single_atlas:
                    frag.add_uniform('sampler2DShadow shadowMapAtlasPoint', included=True)
                else:
                    frag.add_uniform('sampler2DShadow shadowMapAtlas', top=True)
                frag.add_uniform('vec4 pointLightDataArray[maxLightsCluster]', link='_pointLightsAtlasArray', included=True)
            else:
                frag.add_uniform('samplerCubeShadow shadowMapPoint[4]', included=True)

        frag.write('float viewz = linearize(gl_FragCoord.z, cameraProj);')
        frag.write('int clusterI = getClusterI((wvpposition.xy / wvpposition.w) * 0.5 + 0.5, viewz, cameraPlane);')
        frag.write('int numLights = int(texelFetch(clustersData, ivec2(clusterI, 0), 0).r * 255);')

        frag.write('#ifdef HLSL')
        frag.write('viewz += texture(clustersData, vec2(0.0)).r * 1e-9;') # TODO: krafix bug, needs to generate sampler
        frag.write('#endif')

        if '_Spot' in wrd.world_defs:
            frag.add_uniform('vec4 lightsArraySpot[maxLights * 2]', link='_lightsArraySpot')
            frag.write('int numSpots = int(texelFetch(clustersData, ivec2(clusterI, 1 + maxLightsCluster), 0).r * 255);')
            frag.write('int numPoints = numLights - numSpots;')
            if is_shadows:
                if is_shadows_atlas:
                    if not is_single_atlas:
                        frag.add_uniform('sampler2DShadow shadowMapAtlasSpot', included=True)
                    else:
                        frag.add_uniform('sampler2DShadow shadowMapAtlas', top=True)
                else:
                    frag.add_uniform('sampler2DShadow shadowMapSpot[4]', included=True)
                # FIXME: type is actually mat4, but otherwise it will not be set as floats when writing the shaders' json files
                frag.add_uniform('vec4 LWVPSpotArray[maxLightsCluster]', link='_biasLightWorldViewProjectionMatrixSpotArray', included=True)

    
        frag.write('for (int i = 0; i < min(numLights, maxLightsCluster); i++) {')
        frag.write('	int li = int(texelFetch(clustersData, ivec2(clusterI, i + 1), 0).r * 255);')
        frag.write('	basecol += sampleLight(')
        frag.write('    wposition,')
        frag.write('    n,')
        frag.write('    vVec,')
        frag.write('    dotNV,')
        frag.write('    lightsArray[li * 3].xyz,') # lp
        frag.write('    lightsArray[li * 3 + 1].xyz,') # lightCol
        frag.write('    albedo,')#not used
        frag.write('    roughness,')
        frag.write('    specular,')
        frag.write('    f0,')
        frag.write('    true')
        if is_shadows:
            frag.write('\t, li, lightsArray[li * 3 + 2].x, lightsArray[li * 3 + 2].z != 0.0') # bias
        if '_Spot' in wrd.world_defs:
            frag.write('\t, lightsArray[li * 3 + 2].y != 0.0')
            frag.write('\t, lightsArray[li * 3 + 2].y') # spot size (cutoff)
            frag.write('\t, lightsArraySpot[li].w') # spot blend (exponent)
            frag.write('\t, lightsArraySpot[li].xyz') # spotDir
            frag.write('\t, vec2(lightsArray[li * 3].w, lightsArray[li * 3 + 1].w)') # scale
            frag.write('\t, lightsArraySpot[li * 2 + 1].xyz') # right
    
        #Just pass garbage data here
        if '_VoxelShadow' in wrd.world_defs and ('_VoxelGI' in wrd.world_defs or '_VoxelAO' in wrd.world_defs):
            frag.add_uniform('sampler3D vox');
            frag.write_attrib('vec3 posvox;');
            frag.write(', vox, posvox')
        if '_MicroShadowing' in wrd.world_defs:
            frag.write(', 0.0')
        if '_SSRS' in wrd.world_defs:
            frag.add_uniform('sampler2D d');
            frag.write_attrib('mat4 m;');
            frag.write_attrib('vec3 e;');
            frag.write(', d, mat4 m, e')

        frag.write('	);')
        frag.write('};')
    
    frag.write('basecol += emissionCol;')
    frag.write('vec3 voxel = voxposition * 0.5 + 0.5;')
    frag.write('imageStore(voxels, ivec3((voxelgiResolution + 2.0) * voxel), vec4(min(basecol, vec3(1.0)), opacity));')

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

    if arm.utils.get_gapi() == 'direct3d11':
        for e in con_voxel.data['vertex_elements']:
            if e['name'] == 'nor':
                con_voxel.data['vertex_elements'].remove(e)
                break

        # No geom shader compiler for hlsl yet
        vert.noprocessing = True
        frag.noprocessing = True
        geom.noprocessing = True

        vert.add_uniform('mat4 W', '_worldMatrix')
        vert.write('uniform float4x4 W;')
        if rpdat.arm_voxelgi_revoxelize and rpdat.arm_voxelgi_camera:
            vert.add_uniform('vec3 eyeSnap', '_cameraPositionSnap')
            vert.write('uniform float3 eyeSnap;')
        vert.write('struct SPIRV_Cross_Input { float4 pos : TEXCOORD0; };')
        vert.write('struct SPIRV_Cross_Output { float4 svpos : SV_POSITION; };')
        vert.write('SPIRV_Cross_Output main(SPIRV_Cross_Input stage_input) {')
        vert.write('  SPIRV_Cross_Output stage_output;')
        voxHalfExt = str(round(rpdat.arm_voxelgi_dimensions / 2.0 + 2.0))
        if rpdat.arm_voxelgi_revoxelize and rpdat.arm_voxelgi_camera:
            vert.write('  stage_output.svpos.xyz = (mul(float4(stage_input.pos.xyz, 1.0), W).xyz - eyeSnap) / float3(' + voxHalfExt + ', ' + voxHalfExt + ', ' + voxHalfExt + ');')
        else:
            vert.write('  stage_output.svpos.xyz = mul(float4(stage_input.pos.xyz, 1.0), W).xyz / float3(' + voxHalfExt + ', ' + voxHalfExt + ', ' + voxHalfExt + ');')
        vert.write('  stage_output.svpos.w = 1.0;')
        vert.write('  return stage_output;')
        vert.write('}')

        geom.write('struct SPIRV_Cross_Input { float4 svpos : SV_POSITION; };')
        geom.write('struct SPIRV_Cross_Output { float3 wpos : TEXCOORD0; float4 svpos : SV_POSITION; };')
        geom.write('[maxvertexcount(3)]')
        geom.write('void main(triangle SPIRV_Cross_Input stage_input[3], inout TriangleStream<SPIRV_Cross_Output> output) {')
        geom.write('  float3 p1 = stage_input[1].svpos.xyz - stage_input[0].svpos.xyz;')
        geom.write('  float3 p2 = stage_input[2].svpos.xyz - stage_input[0].svpos.xyz;')
        geom.write('  float3 p = abs(cross(p1, p2));')
        geom.write('  for (int i = 0; i < 3; ++i) {')
        geom.write('    SPIRV_Cross_Output stage_output;')
        geom.write('    stage_output.wpos = stage_input[i].svpos.xyz;')
        geom.write('    if (p.z > p.x && p.z > p.y) {')
        geom.write('      stage_output.svpos = float4(stage_input[i].svpos.x, stage_input[i].svpos.y, 0.0, 1.0);')
        geom.write('    }')
        geom.write('    else if (p.x > p.y && p.x > p.z) {')
        geom.write('      stage_output.svpos = float4(stage_input[i].svpos.y, stage_input[i].svpos.z, 0.0, 1.0);')
        geom.write('    }')
        geom.write('    else {')
        geom.write('      stage_output.svpos = float4(stage_input[i].svpos.x, stage_input[i].svpos.z, 0.0, 1.0);')
        geom.write('    }')
        geom.write('    output.Append(stage_output);')
        geom.write('  }')
        geom.write('}')

        frag.add_uniform('layout(r8) writeonly image3D voxels')
        frag.write('RWTexture3D<float> voxels;')
        frag.write('struct SPIRV_Cross_Input { float3 wpos : TEXCOORD0; };')
        frag.write('struct SPIRV_Cross_Output { float4 FragColor : SV_TARGET0; };')
        frag.write('void main(SPIRV_Cross_Input stage_input) {')
        frag.write('  if (abs(stage_input.wpos.z) > ' + (rpdat.rp_voxelgi_resolution_z + 2.0) + ' || abs(stage_input.wpos.x) > 1 || abs(stage_input.wpos.y) > 1) return;')
        voxRes = str(rpdat.rp_voxelgi_resolution + 2.0)
        voxResZ = str(int(int(rpdat.rp_voxelgi_resolution + 2.0) * float(rpdat.rp_voxelgi_resolution_z + 2.0)))
        frag.write('  voxels[int3(' + voxRes + ', ' + voxRes + ', ' + voxResZ + ') * (stage_input.wpos * 0.5 + 0.5)] = 1.0;')
        frag.write('')
        frag.write('}')
    else:
        geom.ins = vert.outs
        frag.ins = geom.outs

        frag.add_include('compiled.inc')
        frag.add_include('std/math.glsl')
        frag.add_include('std/imageatomic.glsl')
        frag.write_header('#extension GL_ARB_shader_image_load_store : enable')

        frag.add_uniform('layout(r8) writeonly image3D voxels')

        vert.add_include('compiled.inc')
        vert.add_uniform('mat4 W', '_worldMatrix')
        vert.add_out('vec3 voxpositionGeom')

        if rpdat.arm_voxelgi_revoxelize and rpdat.arm_voxelgi_camera:
            vert.add_uniform('vec3 eyeSnap', '_cameraPositionSnap')
            vert.write('voxpositionGeom = (vec3(W * vec4(pos.xyz, 1.0)) - eyeSnap) / voxelgiHalfExtents;')
        else:
            vert.write('voxpositionGeom = vec3(W * vec4(pos.xyz, 1.0)) / voxelgiHalfExtents;')

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

        frag.write('imageStore(voxels, ivec3((voxelgiResolution + 1.0) * (voxposition * 0.5 + 0.5)), vec4(1.0));')

    return con_voxel
