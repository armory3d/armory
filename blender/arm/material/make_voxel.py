"""
Copyright (c) 2024 Turánszki János

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
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
    frag.add_include('std/brdf.glsl')

    rpdat = arm.utils.get_rp()
    frag.add_uniform('layout(r32ui) uimage3D voxels')

    frag.write('vec3 n;')
    frag.write('vec3 wposition;')
    frag.write('vec3 basecol;')
    frag.write('float roughness;') #
    frag.write('float metallic;') #
    frag.write('float occlusion;') #
    frag.write('float specular;') #
    frag.write('vec3 emissionCol = vec3(0.0);')
    blend = mat_state.material.arm_blending
    parse_opacity = blend or mat_utils.is_transluc(mat_state.material)
    if parse_opacity:
        frag.write('float opacity;')
        frag.write('float ior;')
    else:
        frag.write('float opacity = 1.0;')

    frag.write('float dotNV = 0.0;')
    cycles.parse(mat_state.nodes, con_voxel, vert, frag, geom, tesc, tese, parse_opacity=parse_opacity, parse_displacement=False, basecol_only=True)

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

    export_mpos = frag.contains('mposition') and not frag.contains('vec3 mposition')
    if export_mpos:
        vert.add_out('vec3 mpositionGeom')
        vert.write_pre = True
        vert.write('mpositionGeom = pos.xyz;')
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

    vert.write('voxpositionGeom = vec3(W * vec4(pos.xyz, 1.0));')
    vert.write('voxnormalGeom = N * vec3(nor.xy, pos.w);')

    geom.add_out('vec4 voxposition[3]')
    geom.add_out('vec3 P')
    geom.add_out('vec3 voxnormal')
    geom.add_out('vec4 lightPosition')
    geom.add_out('vec4 spotPosition')
    geom.add_out('vec4 wvpposition')

    if con_voxel.is_elem('col'):
        geom.add_out('vec3 vcolor')
    if con_voxel.is_elem('tex'):
        geom.add_out('vec2 texCoord')
    if export_mpos:
        geom.add_out('vec3 mposition')
    if export_bpos:
        geom.add_out('vec3 bposition')

    geom.add_uniform('float clipmaps[voxelgiClipmapCount * 10]', '_clipmaps')
    geom.add_uniform('int clipmapLevel', '_clipmapLevel')

    geom.write('vec3 facenormal = abs(voxnormalGeom[0] + voxnormalGeom[1] + voxnormalGeom[2]);')
    geom.write('uint maxi = facenormal[1] > facenormal[0] ? 1 : 0;')
    geom.write('maxi = facenormal[2] > facenormal[maxi] ? 2 : maxi;')

    geom.write('for (uint i = 0; i < 3; ++i) {')
    geom.write('    voxposition[i].xyz = (voxpositionGeom[i] - vec3(clipmaps[int(clipmapLevel * 10 + 4)], clipmaps[int(clipmapLevel * 10 + 5)], clipmaps[int(clipmapLevel * 10 + 6)])) / (float(clipmaps[int(clipmapLevel * 10)]));')
    geom.write('    if (maxi == 0)')
    geom.write('    {')
    geom.write('        voxposition[i].xyz = voxposition[i].zyx;')
    geom.write('    }')
    geom.write('    else if (maxi == 1)')
    geom.write('    {')
    geom.write('        voxposition[i].xyz = voxposition[i].xzy;')
    geom.write('    }')
    geom.write('}')

    geom.write('for (uint i = 0; i < 3; ++i) {')
    geom.write('    voxposition[i].xy /= voxelgiResolution.xy;')
    geom.write('    voxposition[i].zw = vec2(1.0);')
    geom.write('    P = voxpositionGeom[i];')
    geom.write('    voxnormal = voxnormalGeom[i];')
    if con_voxel.is_elem('col'):
        geom.write('vcolor = vcolorGeom[i];')
    if con_voxel.is_elem('tex'):
        geom.write('texCoord = texCoordGeom[i];')
    if export_mpos:
        geom.write('mposition = mpositionGeom[i];')
    if export_bpos:
        geom.write('bposition = bpositionGeom[i];')
    geom.write('    gl_Position = voxposition[i];')
    geom.write('    EmitVertex();')
    geom.write('}')
    geom.write('EndPrimitive();')

    frag.add_uniform('float clipmaps[voxelgiClipmapCount * 10]', '_clipmaps')
    frag.add_uniform('int clipmapLevel', '_clipmapLevel')

    frag.write('vec3 uvw = (P - vec3(clipmaps[int(clipmapLevel * 10 + 4)], clipmaps[int(clipmapLevel * 10 + 5)], clipmaps[int(clipmapLevel * 10 + 6)])) / (float(clipmaps[int(clipmapLevel * 10)]) * voxelgiResolution);')
    frag.write('uvw = (uvw * 0.5 + 0.5);')
    frag.write('if(any(notEqual(uvw, clamp(uvw, 0.0, 1.0)))) return;')
    frag.write('vec3 writecoords = floor(uvw * voxelgiResolution);')
    frag.write_attrib('vec3 N = normalize(voxnormal);')
    frag.write('vec3 aniso_direction = N;')
    frag.write('uvec3 face_offsets = uvec3(')
    frag.write('    aniso_direction.x > 0 ? 0 : 1,')
    frag.write('    aniso_direction.y > 0 ? 2 : 3,')
    frag.write('    aniso_direction.z > 0 ? 4 : 5')
    frag.write('    ) * voxelgiResolution;')
    frag.write('vec3 direction_weights = abs(N);')

    frag.write('vec3 albedo = surfaceAlbedo(basecol, metallic);')
    frag.write('vec3 f0 = surfaceF0(basecol, metallic);')

    frag.add_uniform('vec3 eye', '_cameraPosition')
    frag.write('vec3 eyeDir = eye - wposition;')

    if '_Brdf' in wrd.world_defs:
        frag.add_uniform('sampler2D senvmapBrdf', link='$brdf.png')
        frag.write('vec2 envBRDF = texelFetch(senvmapBrdf, ivec2(vec2(dotNV, 1.0 - roughness) * 256.0), 0).xy;')

    if '_Irr' in wrd.world_defs:
        frag.add_include('std/shirr.glsl')
        frag.add_uniform('vec4 shirr[7]', link='_envmapIrradiance')
        frag.write('vec3 envl = shIrradiance(n, shirr);')
        if '_EnvTex' in wrd.world_defs:
            frag.write('envl /= PI;')
    else:
        frag.write('vec3 envl = vec3(0.0);')

    if '_Rad' in wrd.world_defs:
        frag.add_uniform('sampler2D senvmapRadiance', link='_envmapRadiance')
        frag.add_uniform('int envmapNumMipmaps', link='_envmapNumMipmaps')
        frag.write('vec3 reflectionWorld = reflect(-eyeDir, n);')
        frag.write('float lod = getMipFromRoughness(roughness, envmapNumMipmaps);')
        frag.write('vec3 prefilteredColor = textureLod(senvmapRadiance, envMapEquirect(reflectionWorld), lod).rgb;')

    if '_EnvLDR' in wrd.world_defs:
        frag.write('envl = pow(envl, vec3(2.2));')
        if '_Rad' in wrd.world_defs:
            frag.write('prefilteredColor = pow(prefilteredColor, vec3(2.2));')

    frag.write('envl *= albedo;')

    if '_Brdf' in wrd.world_defs:
        frag.write('envl.rgb *= 1.0 - (f0 * envBRDF.x + envBRDF.y);')
    if '_Rad' in wrd.world_defs:
        frag.write('envl += prefilteredColor * (f0 * envBRDF.x + envBRDF.y);')
    elif '_EnvCol' in wrd.world_defs:
        frag.add_uniform('vec3 backgroundCol', link='_backgroundCol')
        frag.write('envl += backgroundCol * (f0 * envBRDF.x + envBRDF.y);')

    frag.add_uniform('float envmapStrength', link='_envmapStrength')
    frag.write('envl *= envmapStrength * occlusion;')

    frag.write('if (direction_weights.x > 0) {')
    frag.write('    uint basecol_direction = convVec4ToRGBA8(vec4(min(basecol * direction_weights.x, vec3(1.0)), opacity));')
    frag.write('    uint emission_direction = convVec4ToRGBA8(vec4(emissionCol * direction_weights.x, 1.0));')
    frag.write('    uint normal_direction = encNor(N * direction_weights.x);')
    frag.write('    uint envl_direction = convVec4ToRGBA8(vec4(envl * direction_weights.x, 1.0));')
    frag.write('    imageAtomicMax(voxels, ivec3(writecoords + ivec3(face_offsets.x, 0, 0)), basecol_direction);')
    frag.write('    imageAtomicMax(voxels, ivec3(writecoords + ivec3(face_offsets.x, 0, voxelgiResolution.x)), emission_direction);')
    frag.write('    imageAtomicMax(voxels, ivec3(writecoords + ivec3(face_offsets.x, 0, voxelgiResolution.x * 2)), normal_direction);')
    frag.write('    imageAtomicMax(voxels, ivec3(writecoords + ivec3(face_offsets.x, 0, voxelgiResolution.x * 3)), envl_direction);')
    frag.write('}')

    frag.write('if (direction_weights.y > 0) {')
    frag.write('    uint basecol_direction = convVec4ToRGBA8(vec4(min(basecol * direction_weights.y, vec3(1.0)), opacity));')
    frag.write('    uint emission_direction = convVec4ToRGBA8(vec4(emissionCol * direction_weights.y, 1.0));')
    frag.write('    uint normal_direction = encNor(N * direction_weights.y);')
    frag.write('    uint envl_direction = convVec4ToRGBA8(vec4(envl * direction_weights.y, 1.0));')
    frag.write('    imageAtomicMax(voxels, ivec3(writecoords + ivec3(face_offsets.x, 0, 0)), basecol_direction);')
    frag.write('    imageAtomicMax(voxels, ivec3(writecoords + ivec3(face_offsets.x, 0, voxelgiResolution.x)), emission_direction);')
    frag.write('    imageAtomicMax(voxels, ivec3(writecoords + ivec3(face_offsets.x, 0, voxelgiResolution.x * 2)), normal_direction);')
    frag.write('    imageAtomicMax(voxels, ivec3(writecoords + ivec3(face_offsets.x, 0, voxelgiResolution.x * 3)), envl_direction);')
    frag.write('}')

    frag.write('if (direction_weights.z > 0) {')
    frag.write('    uint basecol_direction = convVec4ToRGBA8(vec4(min(basecol * direction_weights.z, vec3(1.0)), opacity));')
    frag.write('    uint emission_direction = convVec4ToRGBA8(vec4(emissionCol * direction_weights.z, 1.0));')
    frag.write('    uint normal_direction = encNor(N * direction_weights.z);')
    frag.write('    uint envl_direction = convVec4ToRGBA8(vec4(envl * direction_weights.z, 1.0));')
    frag.write('    imageAtomicMax(voxels, ivec3(writecoords + ivec3(face_offsets.x, 0, 0)), basecol_direction);')
    frag.write('    imageAtomicMax(voxels, ivec3(writecoords + ivec3(face_offsets.x, 0, voxelgiResolution.x)), emission_direction);')
    frag.write('    imageAtomicMax(voxels, ivec3(writecoords + ivec3(face_offsets.x, 0, voxelgiResolution.x * 2)), normal_direction);')
    frag.write('    imageAtomicMax(voxels, ivec3(writecoords + ivec3(face_offsets.x, 0, voxelgiResolution.x * 3)), envl_direction);')
    frag.write('}')

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

    vert.add_include('compiled.inc')
    vert.add_uniform('mat4 W', '_worldMatrix')
    vert.add_uniform('mat3 N', '_normalMatrix')

    geom.add_uniform('float clipmaps[voxelgiClipmapCount * 10]', '_clipmaps')
    geom.add_uniform('int clipmapLevel', '_clipmapLevel')

    frag.add_uniform('float clipmaps[voxelgiClipmapCount * 10]', '_clipmaps')
    frag.add_uniform('int clipmapLevel', '_clipmapLevel')

    """
    if arm.utils.get_gapi() == 'direct3d11':
        for e in con_voxel.data['vertex_elements']:
            if e['name'] == 'nor':
                con_voxel.data['vertex_elements'].remove(e)
                break

        vert.write('uniform float4x4 W;')
        vert.write('uniform float3x3 N;')
        vert.write('struct SPIRV_Cross_Input {')
        vert.write('    float4 pos : TEXCOORD0;')
        vert.write('    float3 nor : NORMAL;')
        vert.write('};')
        vert.write('struct SPIRV_Cross_Output {')
        vert.write('    float4 svpos : SV_POSITION;')
        vert.write('    float3 svnor : NORMAL;')
        vert.write('};')
        vert.write('SPIRV_Cross_Output main(SPIRV_Cross_Input stage_input) {')
        vert.write('  SPIRV_Cross_Output stage_output;')
        vert.write('  stage_output.svpos.xyz = mul(float4(stage_input.pos.xyz, 1.0), W).xyz;')
        vert.write('  stage_output.svpos.w = 1.0;')
        vert.write('  stage_output.svnor.xyz = normalize(mul(float3(nor.xy, pos.w), N).xyz);')
        vert.write('  return stage_output;')
        vert.write('}')

        geom.write('uniform float clipmaps[voxelgiClipmapCount * 10];')
        geom.write('uniform int clipmapLevel;')
        geom.write('struct SPIRV_Cross_Input {')
        geom.write('    float4 svpos : SV_POSITION;')
        geom.write('    float3 svnor : NORMAL;')
        geom.write('};')
        geom.write('struct SPIRV_Cross_Output {')
        geom.write('    float3 wpos : TEXCOORD0;')
        geom.write('    float3 wnor : NORMAL;')
        geom.write('};')
        geom.write('[maxvertexcount(3)]')
        geom.write('void main(triangle SPIRV_Cross_Input stage_input[3], inout TriangleStream<SPIRV_Cross_Output> output) {')
        geom.write('  float3 p1 = stage_input[1].svpos.xyz - stage_input[0].svpos.xyz;')
        geom.write('  float3 p2 = stage_input[2].svpos.xyz - stage_input[0].svpos.xyz;')
        geom.write('  float3 p = abs(cross(p1, p2));')
        geom.write('  for (int i = 0; i < 3; ++i) {')
        geom.write('    SPIRV_Cross_Output stage_output;')
        geom.write('    stage_output.wpos = (stage_input[i].svpos.xyz + float3(clipmaps[int(clipmapLevel * 10 + 4)], clipmaps[int(clipmapLevel * 10 + 5)], clipmaps[int(clipmapLevel * 10 + 6)])) / (float(clipmaps[clipmapLevel * 10]) * voxelgiResolution);')
        geom.write('    stage_output.wnor = stage_input[i].svnor.xyz;')
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
        frag.write('uniform float clipmaps[voxelgiClipmapCount * 10];')
        frag.write('uniform int clipmapLevel;')

        frag.write('struct SPIRV_Cross_Input {')
        frag.write('    float3 wpos : TEXCOORD0;')
        frag.write('    float3 wnor : NORMAL;')
        frag.write('};')
        frag.write('struct SPIRV_Cross_Output { float4 FragColor : SV_TARGET0; };')
        frag.write('void main(SPIRV_Cross_Input stage_input) {')
        frag.write('    float3 uvw = (stage_input.wpos.xyz - float3(clipmaps[int(clipmapLevel * 10 + 4)], clipmaps[int(clipmapLevel * 10 + 5)], clipmaps[int(clipmapLevel * 10 + 6)])) / (float(clipmaps[int(clipmapLevel * 10)]) * voxelgiResolution);')
        frag.write('    uvw = uvw * 0.5 + 0.5;')
        frag.write('    if(any(!saturate(uvw))) return;')
        frag.write('    uvw = floor(uvw * voxelgiResolution);')
        frag.write('    uint3 face_offsets = uint3(')
        frag.write('	   stage_input.wnor.x > 0 ? 0 : 1,')
        frag.write('	   stage_input.wnor.y > 0 ? 2 : 3,')
        frag.write('	   stage_input.wnor.z > 0 ? 4 : 5')
        frag.write('	   ) * voxelgiResolution;')
        frag.write('    float3 direction_weights = abs(stage_input.wnor);')

        frag.write('    if (direction_weights.x > 0.0) {')
        frag.write('        float opac_direction = direction_weights.x;')
        frag.write('        voxels[uvw + int3(face_offsets.x, 0, 0))] = float4(opac_direction);')
        frag.write('    }')

        frag.write('    if (direction_weights.y > 0.0) {')
        frag.write('        float opac_direction = direction_weights.y;')
        frag.write('        voxels[uvw + int3(face_offsets.y, 0, 0))] = float4(opac_direction);')
        frag.write('    }')

        frag.write('    if (direction_weights.z > 0.0) {')
        frag.write('        float opac_direction = direction_weights.z;')
        frag.write('        voxels[uvw + int3(face_offsets.z, 0, 0))] = float4(opac_direction);')
        frag.write('    }')
        frag.write('}')
    else:
    """
    frag.add_uniform('layout(r32ui) uimage3D voxels')

    vert.add_out('vec3 voxpositionGeom')
    vert.add_out('vec3 voxnormalGeom')

    vert.write('voxpositionGeom = vec3(W * vec4(pos.xyz, 1.0));')
    vert.write('voxnormalGeom = N * vec3(nor.xy, pos.w);')

    geom.add_out('vec4 voxposition[3]')
    geom.add_out('vec3 P')
    geom.add_out('vec3 voxnormal')

    geom.write('vec3 facenormal = abs(voxnormalGeom[0] + voxnormalGeom[1] + voxnormalGeom[2]);')
    geom.write('uint maxi = facenormal[1] > facenormal[0] ? 1 : 0;')
    geom.write('maxi = facenormal[2] > facenormal[maxi] ? 2 : maxi;')

    geom.write('for (uint i = 0; i < 3; ++i) {')
    geom.write('    voxposition[i].xyz = (voxpositionGeom[i] - vec3(clipmaps[int(clipmapLevel * 10 + 4)], clipmaps[int(clipmapLevel * 10 + 5)], clipmaps[int(clipmapLevel * 10 + 6)])) / (float(clipmaps[int(clipmapLevel * 10)]));')
    geom.write('    if (maxi == 0)')
    geom.write('    {')
    geom.write('        voxposition[i].xyz = voxposition[i].zyx;')
    geom.write('    }')
    geom.write('    else if (maxi == 1)')
    geom.write('    {')
    geom.write('        voxposition[i].xyz = voxposition[i].xzy;')
    geom.write('    }')
    geom.write('}')

    geom.write('for (uint i = 0; i < 3; ++i) {')
    geom.write('    voxposition[i].xy /= voxelgiResolution.x;')
    geom.write('    voxposition[i].zw = vec2(1.0);')
    geom.write('    P = voxpositionGeom[i];')
    geom.write('    voxnormal = voxnormalGeom[i];')
    geom.write('    gl_Position = voxposition[i];')
    geom.write('    EmitVertex();')
    geom.write('}')
    geom.write('EndPrimitive();')

    frag.write('vec3 uvw = (P - vec3(clipmaps[int(clipmapLevel * 10 + 4)], clipmaps[int(clipmapLevel * 10 + 5)], clipmaps[int(clipmapLevel * 10 + 6)])) / (float(clipmaps[int(clipmapLevel * 10)]) * voxelgiResolution);')
    frag.write('uvw = uvw * 0.5 + 0.5;')
    frag.write('if(any(notEqual(uvw, clamp(uvw, 0.0, 1.0)))) return;')
    frag.write('vec3 writecoords = floor(uvw * voxelgiResolution);')
    frag.write('vec3 N = normalize(voxnormal);')
    frag.write('vec3 aniso_direction = N;')
    frag.write('uvec3 face_offsets = uvec3(')
    frag.write('	aniso_direction.x > 0 ? 0 : 1,')
    frag.write('	aniso_direction.y > 0 ? 2 : 3,')
    frag.write('	aniso_direction.z > 0 ? 4 : 5')
    frag.write('	) * voxelgiResolution;')
    frag.write('vec3 direction_weights = abs(N);')

    frag.write('if (direction_weights.x > 0) {')
    frag.write('    imageAtomicMax(voxels, ivec3(writecoords + ivec3(face_offsets.x, 0, 0)), uint(direction_weights.x * 255));')
    frag.write('}')

    frag.write('if (direction_weights.y > 0) {')
    frag.write('    imageAtomicMax(voxels, ivec3(writecoords + ivec3(face_offsets.y, 0, 0)), uint(direction_weights.y * 255));')
    frag.write('}')

    frag.write('if (direction_weights.z > 0) {')
    frag.write('    imageAtomicMax(voxels, ivec3(writecoords + ivec3(face_offsets.z, 0, 0)), uint(direction_weights.z * 255));')
    frag.write('}')

    return con_voxel
