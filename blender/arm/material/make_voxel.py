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
    frag.write_header('#extension GL_ARB_shader_image_load_store : enable')

    rpdat = arm.utils.get_rp()
    frag.add_uniform('layout(binding = 0, rgba8) image3D voxels')
    frag.add_uniform('layout(binding = 1, rgba8) image3D voxelsNor')

    frag.write('vec3 basecol;')
    frag.write('float roughness;') #
    frag.write('float metallic;') #
    frag.write('float occlusion;') #
    frag.write('float specular;') #
    frag.write('vec3 emissionCol = vec3(0.0);')
    parse_opacity = rpdat.arm_voxelgi_refraction
    if parse_opacity:
        frag.write('float opacity;')
        frag.write('float rior;')

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
    vert.add_uniform('mat3 N', '_normalMatrix')
    vert.add_out('vec3 voxpositionGeom')
    vert.add_out('vec3 voxnormalGeom')

    if con_voxel.is_elem('col'):
        vert.add_out('vec3 vcolorGeom')
        vert.write('vcolorGeom = col.rgb;')

    if con_voxel.is_elem('tex'):
        vert.add_out('vec2 texCoordGeom')
        vert.write('texCoordGeom = tex;')

    vert.add_uniform('vec3 viewerPos', '_viewerPos')
    vert.add_uniform('mat4 viewMatrix', '_viewMatrix')
    vert.add_out('float clipmapLevelGeom')
    vert.write('vec3 P = vec3(W * vec4(pos.xyz, 1.0));')
    vert.write('float dist = distance(viewerPos, P);')
    vert.write('clipmapLevelGeom = max(log2(dist / voxelgiResolution.x), 0);')
    vert.write('float clipmapLevelSize = voxelgiHalfExtents.x * pow(2.0, clipmapLevelGeom);')
    vert.write('vec3 lookDirection = normalize(viewMatrix[2].xyz);')
    vert.write('float voxelSize = voxelgiHalfExtents.x * 2 * (1 + 2 + 3 + 4 + 5 + 6) / voxelgiResolution.x;')
    vert.write('vec3 eyeSnap = viewerPos - lookDirection;')
    vert.write('voxpositionGeom = (P - eyeSnap) / (clipmapLevelSize * voxelSize * dist);')
    vert.write('voxnormalGeom = N * vec3(nor.xy, pos.w);')

    geom.add_out('vec3 voxposition')
    geom.add_out('vec3 voxnormal')
    geom.add_out('flat float clipmapLevel')

    geom.write('clipmapLevel = clipmapLevelGeom[0];')

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
    geom.write('    voxnormal = voxnormalGeom[i];')
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

    frag.write('if (abs(voxposition.z) > 1 || abs(voxposition.x) > 1 || abs(voxposition.y) > 1) return;')

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
        frag.write('float sdotNL = max(dot(n, sunDir), 0.0);')
        if is_shadows:
            vert.add_out('vec4 lightPositionGeom')
            geom.add_out('vec4 lightPosition')
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
            frag.write('basecol *= sunCol * svisibility;// * sdotNL;')

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
                    frag.write('visibility = float(texture(shadowMapPoint[0], vec3(-l + n * pointBias * 20)).r > compare);')
                else:
                    frag.write('visibility = texture(shadowMapPoint[0], vec4(-l + n * pointBias * 20, compare)).r;')
            frag.write('}')
            frag.write('basecol *= visibility * pointCol;')

    frag.write('vec3 uvw = voxposition;')
    frag.write('if(abs(voxposition.x) < clipmapLevel / 6 || abs(voxposition.y) < clipmapLevel / 6 || abs(voxposition.z) < clipmapLevel / 6) return;')
    frag.write('uvw = uvw * 0.5 + 0.5;')
    frag.write('vec3 writecoord = uvw * voxelgiResolution;')
    frag.write('imageStore(voxels, ivec3(writecoord), vec4(min(basecol+emissionCol, vec3(1.0)), 1.0));')
    frag.write('imageStore(voxelsNor, ivec3(writecoord), vec4(min(voxnormal, vec3(1.0)), 1.0));')

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

    vert.add_uniform('vec3 eyeSnap', '_eyeSnap')
    vert.add_uniform('float voxelSize', '_voxelSize')

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

        vert.write('struct SPIRV_Cross_Input { float4 pos : TEXCOORD0; };')
        vert.write('struct SPIRV_Cross_Output { float4 svpos : SV_POSITION; };')
        vert.write('SPIRV_Cross_Output main(SPIRV_Cross_Input stage_input) {')
        vert.write('  SPIRV_Cross_Output stage_output;')
        vert.add_uniform('vec3 viewerPos', '_viewerPos')
        vert.add_uniform('mat4 viewMatrix', '_viewMatrix')
        vert.write('vec3 P = vec3(W * vec4(pos.xyz, 1.0));')
        vert.write('float dist = distance(viewerPos, P);')
        vert.write('float clipmapLevel = max(log2(dist / voxelgiResolution.x), 0);')
        vert.write('float clipmapLevelSize = voxelgiHalfExtents.x * pow(2.0, clipmapLevel);')
        vert.write('vec3 lookDirection = normalize(viewMatrix[2].xyz);')
        vert.write('float voxelSize = (voxelgiHalfExtents.x * 2 * (1 + 2 + 3 + 4 + 5 + 6)) / voxelgiResolution.x;')
        vert.write('vec3 eyeSnap = viewerPos - lookDirection;')

        vert.write('  stage_output.svpos.xyz = (mul(float4(stage_input.pos.xyz, 1.0), W).xyz - eyeSnap) / (clipmapLevelSize * voxelSize);')
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
        frag.write('  if (abs(stage_input.wpos.z) > ' + rpdat.rp_voxelgi_resolution_z + ' || abs(stage_input.wpos.x) > 1 || abs(stage_input.wpos.y * 6) > 1) return;')
        voxRes = str(rpdat.rp_voxelgi_resolution)
        voxResZ = str(int(int(rpdat.rp_voxelgi_resolution) * float(rpdat.rp_voxelgi_resolution_z)))

        frag.write('vec3 uvw = voxposition * 0.5 + 0.5;')
        frag.write('vec3 writecoord = uvw * int3(' + voxRes + ', ' + voxRes + ', ' + voxResZ + ');')

        frag.write('  voxels[uvw * (stage_input.wpos * 0.5 + 0.5)] = 1.0;')
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

        vert.add_uniform('vec3 viewerPos', '_viewerPos')
        vert.add_uniform('mat4 viewMatrix', '_viewMatrix')
        vert.write('vec3 P = vec3(W * vec4(pos.xyz, 1.0));')
        vert.write('float dist = distance(viewerPos, P);')
        vert.write('float clipmapLevel = max(log2(dist / voxelgiResolution.x), 0);')
        vert.write('float clipmapLevelSize = voxelgiHalfExtents.x * pow(2.0, clipmapLevel);')
        vert.write('vec3 lookDirection = normalize(viewMatrix[2].xyz);')
        vert.write('float voxelSize = (voxelgiHalfExtents.x * 2 * (1 + 2 + 3 + 4 + 5 + 6)) / voxelgiResolution.x;')
        vert.write('vec3 eyeSnap = viewerPos - lookDirection;')
        vert.write('voxpositionGeom = (P - eyeSnap) / (clipmapLevelSize * voxelSize);')

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

        frag.write('if (abs(voxposition.z) > ' + rpdat.rp_voxelgi_resolution_z + ' || abs(voxposition.x) > 1 || abs(voxposition.y * 6) > 1) return;')

        frag.add_uniform('int clipmap_to_update', '_clipmap_to_update')
        frag.write('vec3 uvw = voxposition * 0.5 + 0.5;')
        frag.write('vec3 writecoord = uvw * voxelgiResolution;')

        frag.write('imageStore(voxels, ivec3(writecoord), vec4(1.0));')

    return con_voxel
