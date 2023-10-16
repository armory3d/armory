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
    con_voxel = mat_state.data.add_context({ 'name': context_id, 'depth_write': False, 'compare_mode': 'always', 'cull_mode': 'none', 'color_write_red': False, 'color_write_green': False, 'color_write_blue': False, 'color_write_alpha': False, 'conservative_raster': True })

    vert = con_voxel.make_vert()
    frag = con_voxel.make_frag()
    tesc = None
    tese = None

    frag.ins = vert.outs

    vert.add_include('compiled.inc')
    frag.add_include('compiled.inc')
    frag.add_include('std/conetrace.glsl')
    frag.add_include('std/gbuffer.glsl')

    frag.write_header('#extension GL_ARB_shader_image_load_store : enable')

    frag.add_uniform('layout(binding = 0) sampler3D voxels')
    frag.add_uniform('layout(binding = 1, rgba8) image3D voxelsBounce')
    frag.add_uniform('sampler2D gbufferD')
    frag.add_uniform('sampler2D gbuffer0')
    frag.add_uniform('sampler2D gbuffer1')
    frag.add_uniform('sampler2D gbuffer_refraction')

    vert.add_uniform('vec3 eyeLook', '_cameraLook')
    vert.add_uniform('vec3 viewerPos', '_viewerPos')

    frag.write('vec4 g1 = textureLod(gbuffer1, texCoord, 0.0);')
    frag.write('vec4 g0 = textureLod(gbuffer0, texCoord, 0.0);')
    frag.write('float spec = unpackFloat2(g1.a).y;')
    frag.write('float roughness = g0.b;')

    vert.add_uniform('mat4 W', '_worldMatrix')
    vert.add_uniform('mat3 N', '_normalMatrix')
    vert.add_out('vec3 voxpos')
    vert.add_out('flat int clipmapLevel')
    vert.add_out('vec3 wnormal')

    vert.add_out('vec2 texCoord')
    vert.write('texCoord = pos.xy * 0.5 + 0.5;')

    vert.write('vec3 P = vec3(W * vec4(pos.xyz, 1.0));')
    vert.write('float dist = max(abs(P.x - viewerPos.x), max(abs(P.y - viewerPos.y), abs(P.z - viewerPos.z)));')
    vert.write('clipmapLevel = int(max(log2(dist / voxelgiResolution.x), 0));')
    vert.write('float voxelSize = pow(2.0, clipmapLevel) * 0.5;')
    vert.write('vec3 eyeSnap = floor((normalize(viewerPos + eyeLook)) / voxelSize) * voxelSize;')
    vert.write('voxpos = (P - eyeSnap) / voxelSize * 1.0 / voxelgiResolution.x;')

    vert.write('wnormal = normalize(N * vec3(nor.xy, pos.w));')

    frag.write('vec4 col = textureLod(voxels, voxpos * 0.5 + 0.5, clipmapLevel);')
    frag.write('col += traceDiffuse(voxpos, wnormal, voxels, clipmapLevel);')

    frag.add_uniform('vec3 eye', '_cameraPosition')
    frag.write('vec3 v = normalize(eye - voxpos);')

    frag.write('if(roughness < 1.0 && spec > 0.0)')
    frag.write('    col += traceSpecular(voxpos, wnormal, voxels, -v, roughness, clipmapLevel);')

    frag.write('#ifdef _VoxelRefract')
    frag.write('vec4 gr = textureLod(gbuffer_refraction, texCoord, 0.0);')
    frag.write('float ior = gr.x;')
    frag.write('float opacity = gr.y;')
    frag.write('if(opacity < 1.0)')
    frag.write('    col.rgb = mix(traceRefraction(voxpos, wnormal, voxels, -v, ior, roughness, clipmapLevel) + col.rgb, col.rgb, opacity);')
    frag.write('#endif')

    frag.write('imageStore(voxelsBounce, ivec3((voxpos * 0.5 + 0.5) * voxelgiResolution.x), vec4(1.0));')

    assets.vs_equal(con_voxel, assets.shader_cons['voxelbounce_vert'])
    assets.fs_equal(con_voxel, assets.shader_cons['voxelbounce_frag'])

    return con_voxel
