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

    rpdat = arm.utils.get_rp()
    frag.add_uniform('layout(r32ui) uimage3D voxels')
    frag.add_uniform('layout(r32ui) uimage3D voxelsEmission')
    frag.add_uniform('layout(r32ui) uimage3D voxelsNor')

    frag.write('vec3 wposition;')
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
    vert.add_out('vec3 voxnormalGeom')

    if con_voxel.is_elem('col'):
        vert.add_out('vec3 vcolorGeom')
        vert.write('vcolorGeom = col.rgb;')

    if con_voxel.is_elem('tex'):
        vert.add_out('vec2 texCoordGeom')
        vert.write('texCoordGeom = tex;')

    vert.write('vec3 P = vec3(W * vec4(pos.xyz, 1.0));')
    vert.write('voxpositionGeom = P;')
    vert.write('voxnormalGeom = normalize(N * vec3(nor.xy, pos.w));')

    geom.add_out('vec3 voxposition')
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

    geom.write('vec3 p1 = voxpositionGeom[1] - voxpositionGeom[0];')
    geom.write('vec3 p2 = voxpositionGeom[2] - voxpositionGeom[0];')

    geom.write('vec3 p = abs(cross(p1, p2));')
    geom.write('for (uint i = 0; i < 3; ++i) {')
    geom.write('    voxposition = (voxpositionGeom[i] - vec3(clipmaps[int(clipmapLevel * 10 + 4)], clipmaps[int(clipmapLevel * 10 + 5)], clipmaps[int(clipmapLevel * 10 + 6)])) / (float(clipmaps[int(clipmapLevel * 10)]) * voxelgiResolution.x);')
    geom.write('    voxnormal = voxnormalGeom[i];')
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

    frag.add_uniform('float clipmaps[voxelgiClipmapCount * 10]', '_clipmaps')
    frag.add_uniform('int clipmapLevel', '_clipmapLevel')

    frag.write('vec3 uvw = (voxposition - vec3(clipmaps[int(clipmapLevel * 10 + 4)], clipmaps[int(clipmapLevel * 10 + 5)], clipmaps[int(clipmapLevel * 10 + 6)])) / (float(clipmaps[int(clipmapLevel * 10)]) * voxelgiResolution.x);')
    frag.write('uvw = (voxposition * 0.5 + 0.5);')
    frag.write('if(any(notEqual(uvw, clamp(uvw, 0.0, 1.0)))) return;')
    frag.write('uvw = floor(uvw * voxelgiResolution.x);')
    frag.write('uvec3 face_offsets = uvec3(')
    frag.write('	voxnormal.x > 0 ? 0 : 1,')
    frag.write('	voxnormal.y > 0 ? 2 : 3,')
    frag.write('	voxnormal.z > 0 ? 4 : 5')
    frag.write('	) * voxelgiResolution.x;')
    frag.write('vec3 direction_weights = abs(voxnormal);')

    frag.write('if (direction_weights.x > 0.0) {')
    frag.write('    uint basecol_direction = convVec4ToRGBA8(vec4(min(basecol * direction_weights.x, vec3(1.0)), 1.0));')
    frag.write('    uint emission_direction = convVec4ToRGBA8(vec4(min(emissionCol * direction_weights.x, vec3(1.0)), 1.0));')
    frag.write('    uint normal_direction = encNor(voxnormal * direction_weights.x);')
    frag.write('    imageAtomicMax(voxels, ivec3(uvw.x + face_offsets.x, uvw.y, uvw.z), basecol_direction);')
    frag.write('    imageAtomicMax(voxelsEmission, ivec3(uvw.x + face_offsets.x, uvw.y, uvw.z), emission_direction);')
    frag.write('    imageAtomicMax(voxelsNor, ivec3(uvw.x + face_offsets.x, uvw.y, uvw.z), normal_direction);')
    frag.write('}')

    frag.write('if (direction_weights.y > 0.0) {')
    frag.write('    uint basecol_direction = convVec4ToRGBA8(vec4(min(basecol * direction_weights.y, vec3(1.0)), 1.0));')
    frag.write('    uint emission_direction = convVec4ToRGBA8(vec4(min(emissionCol * direction_weights.y, vec3(1.0)), 1.0));')
    frag.write('    uint normal_direction = encNor(voxnormal * direction_weights.y);')
    frag.write('    imageAtomicMax(voxels, ivec3(uvw.x + face_offsets.y, uvw.y, uvw.z), basecol_direction);')
    frag.write('    imageAtomicMax(voxelsEmission, ivec3(uvw.x + face_offsets.y, uvw.y, uvw.z), emission_direction);')
    frag.write('    imageAtomicMax(voxelsNor, ivec3(uvw.x + face_offsets.y, uvw.y, uvw.z), normal_direction);')
    frag.write('}')

    frag.write('if (direction_weights.z > 0.0) {')
    frag.write('    uint basecol_direction = convVec4ToRGBA8(vec4(min(basecol * direction_weights.z, vec3(1.0)), 1.0));')
    frag.write('    uint emission_direction = convVec4ToRGBA8(vec4(min(emissionCol * direction_weights.z, vec3(1.0)), 1.0));')
    frag.write('    uint normal_direction = encNor(voxnormal * direction_weights.z);')
    frag.write('    imageAtomicMax(voxels, ivec3(uvw.x + face_offsets.z, uvw.y, uvw.z), basecol_direction);')
    frag.write('    imageAtomicMax(voxelsEmission, ivec3(uvw.x + face_offsets.z, uvw.y, uvw.z), emission_direction);')
    frag.write('    imageAtomicMax(voxelsNor, ivec3(uvw.x + face_offsets.z, uvw.y, uvw.z), normal_direction);')
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
    frag.add_uniform('layout(r8) image3D voxels')
    frag.add_uniform('layout(r8) image3D voxelsB')

    vert.add_include('compiled.inc')
    vert.add_uniform('mat4 W', '_worldMatrix')
    vert.add_uniform('mat3 N', '_normalMatrix')
    vert.add_out('vec3 voxpositionGeom')
    vert.add_out('vec3 voxnormalGeom')

    vert.write('vec3 P = vec3(W * vec4(pos.xyz, 1.0));')
    vert.write('voxpositionGeom = P;')
    vert.write('voxnormalGeom = normalize(N * vec3(nor.xy, pos.w));')

    geom.add_uniform('float clipmaps[voxelgiClipmapCount * 10]', '_clipmaps')
    geom.add_uniform('int clipmapLevel', '_clipmapLevel')

    geom.add_out('vec3 voxposition')
    geom.add_out('vec3 voxnormal')

    geom.write('vec3 p1 = voxpositionGeom[1] - voxpositionGeom[0];')
    geom.write('vec3 p2 = voxpositionGeom[2] - voxpositionGeom[0];')
    geom.write('vec3 p = abs(cross(p1, p2));')
    geom.write('for (uint i = 0; i < 3; ++i) {')
    geom.write('    voxposition = (voxpositionGeom[i] - vec3(clipmaps[int(clipmapLevel * 10 + 4)], clipmaps[int(clipmapLevel * 10 + 5)], clipmaps[int(clipmapLevel * 10 + 6)])) / (float(clipmaps[int(clipmapLevel * 10)]) * voxelgiResolution.x);')
    geom.write('    voxnormal = voxnormalGeom[i];')
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

    frag.add_uniform('float clipmaps[voxelgiClipmapCount * 10]', '_clipmaps')
    frag.add_uniform('int clipmapLevel', '_clipmapLevel')

    frag.write('vec3 uvw = (voxposition - vec3(clipmaps[int(clipmapLevel * 10 + 4)], clipmaps[int(clipmapLevel * 10 + 5)], clipmaps[int(clipmapLevel * 10 + 6)])) / (float(clipmaps[int(clipmapLevel * 10)]) * voxelgiResolution.x);')
    frag.write('uvw = (voxposition * 0.5 + 0.5);')
    frag.write('if(any(notEqual(uvw, clamp(uvw, 0.0, 1.0)))) return;')
    frag.write('uvw = floor(uvw * voxelgiResolution.x);')
    frag.write('uvec3 face_offsets = uvec3(')
    frag.write('	voxnormal.x > 0 ? 0 : 1,')
    frag.write('	voxnormal.y > 0 ? 2 : 3,')
    frag.write('	voxnormal.z > 0 ? 4 : 5')
    frag.write('	) * voxelgiResolution.x;')
    frag.write('vec3 direction_weights = abs(voxnormal);')

    frag.write('if (direction_weights.x > 0.0) {')
    frag.write('    float opac_direction = direction_weights.x;')
    frag.write('    imageStore(voxels, ivec3(uvw + ivec3(face_offsets.x, 0, 0)), vec4(opac_direction));')
    frag.write('    imageStore(voxelsB, ivec3(uvw + ivec3(face_offsets.x, 0, 0)), vec4(opac_direction));')
    frag.write('}')

    frag.write('if (direction_weights.y > 0.0) {')
    frag.write('    float opac_direction = direction_weights.y;')
    frag.write('    imageStore(voxels, ivec3(uvw + ivec3(face_offsets.y, 0, 0)), vec4(opac_direction));')
    frag.write('    imageStore(voxelsB, ivec3(uvw + ivec3(face_offsets.y, 0, 0)), vec4(opac_direction));')
    frag.write('}')

    frag.write('if (direction_weights.z > 0.0) {')
    frag.write('    float opac_direction = direction_weights.z;')
    frag.write('    imageStore(voxels, ivec3(uvw + ivec3(face_offsets.z, 0, 0)), vec4(opac_direction));')
    frag.write('    imageStore(voxelsB, ivec3(uvw + ivec3(face_offsets.z, 0, 0)), vec4(opac_direction));')
    frag.write('}')

    return con_voxel
