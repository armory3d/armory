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
    frag.write('    vec4 basecol_direction = vec4(min(basecol * direction_weights.x, vec3(1.0)), opacity);')
    frag.write('    vec3 emission_direction = emissionCol * direction_weights.x;')
    frag.write('    vec2 normal_direction = encode_oct(N * direction_weights.x) * 0.5 + 0.5;')
    frag.write('    vec3 envl_direction = envl * direction_weights.x;')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.x, 0, 0)), uint(basecol_direction.r * 255));')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.x, 0, voxelgiResolution.x)), uint(basecol_direction.g * 255));')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.x, 0, voxelgiResolution.x * 2)), uint(basecol_direction.b * 255));')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.x, 0, voxelgiResolution.x * 3)), uint(basecol_direction.a * 255));')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.x, 0, voxelgiResolution.x * 4)), uint(emission_direction.r * 255));')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.x, 0, voxelgiResolution.x * 5)), uint(emission_direction.g * 255));')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.x, 0, voxelgiResolution.x * 6)), uint(emission_direction.b * 255));')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.x, 0, voxelgiResolution.x * 7)), uint(normal_direction.r * 255));')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.x, 0, voxelgiResolution.x * 8)), uint(normal_direction.g * 255));')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.x, 0, voxelgiResolution.x * 9)), uint(envl_direction.r * 255));')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.x, 0, voxelgiResolution.x * 10)), uint(envl_direction.g * 255));')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.x, 0, voxelgiResolution.x * 11)), uint(envl_direction.b * 255));')
    frag.write('}')

    frag.write('if (direction_weights.y > 0) {')
    frag.write('    vec4 basecol_direction = vec4(min(basecol * direction_weights.y, vec3(1.0)), opacity);')
    frag.write('    vec3 emission_direction = emissionCol * direction_weights.y;')
    frag.write('    vec2 normal_direction = encode_oct(N * direction_weights.y) * 0.5 + 0.5;')
    frag.write('    vec3 envl_direction = envl * direction_weights.y;')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.y, 0, 0)), uint(basecol_direction.r * 255));')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.y, 0, voxelgiResolution.x)), uint(basecol_direction.g * 255));')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.y, 0, voxelgiResolution.x * 2)), uint(basecol_direction.b * 255));')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.y, 0, voxelgiResolution.x * 3)), uint(basecol_direction.a * 255));')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.y, 0, voxelgiResolution.x * 4)), uint(emission_direction.r * 255));')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.y, 0, voxelgiResolution.x * 5)), uint(emission_direction.g * 255));')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.y, 0, voxelgiResolution.x * 6)), uint(emission_direction.b * 255));')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.y, 0, voxelgiResolution.x * 7)), uint(normal_direction.r * 255));')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.y, 0, voxelgiResolution.x * 8)), uint(normal_direction.g * 255));')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.y, 0, voxelgiResolution.x * 9)), uint(envl_direction.r * 255));')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.y, 0, voxelgiResolution.x * 10)), uint(envl_direction.g * 255));')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.y, 0, voxelgiResolution.x * 11)), uint(envl_direction.b * 255));')
    frag.write('}')

    frag.write('if (direction_weights.z > 0) {')
    frag.write('    vec4 basecol_direction = vec4(min(basecol * direction_weights.z, vec3(1.0)), opacity);')
    frag.write('    vec3 emission_direction = emissionCol * direction_weights.z;')
    frag.write('    vec2 normal_direction = encode_oct(n * direction_weights.z) * 0.5 + 0.5;')
    frag.write('    vec3 envl_direction = envl * direction_weights.z;')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.z, 0, 0)), uint(basecol_direction.r * 255));')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.z, 0, voxelgiResolution.x)), uint(basecol_direction.g * 255));')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.z, 0, voxelgiResolution.x * 2)), uint(basecol_direction.b * 255));')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.z, 0, voxelgiResolution.x * 3)), uint(basecol_direction.a * 255));')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.z, 0, voxelgiResolution.x * 4)), uint(emission_direction.r * 255));')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.z, 0, voxelgiResolution.x * 5)), uint(emission_direction.g * 255));')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.z, 0, voxelgiResolution.x * 6)), uint(emission_direction.b * 255));')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.z, 0, voxelgiResolution.x * 7)), uint(normal_direction.r * 255));')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.z, 0, voxelgiResolution.x * 8)), uint(normal_direction.g * 255));')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.z, 0, voxelgiResolution.x * 9)), uint(envl_direction.r * 255));')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.z, 0, voxelgiResolution.x * 10)), uint(envl_direction.g * 255));')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.z, 0, voxelgiResolution.x * 11)), uint(envl_direction.b * 255));')
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
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.x, 0, 0)), uint(direction_weights.x * 255));')
    frag.write('}')

    frag.write('if (direction_weights.y > 0) {')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.y, 0, 0)), uint(direction_weights.y * 255));')
    frag.write('}')

    frag.write('if (direction_weights.z > 0) {')
    frag.write('    imageAtomicAdd(voxels, ivec3(writecoords + ivec3(face_offsets.z, 0, 0)), uint(direction_weights.z * 255));')
    frag.write('}')

    return con_voxel
