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

    con_voxel.add_elem('tex', 'short2norm')

    vert = con_voxel.make_vert()
    frag = con_voxel.make_frag()

    frag.ins = vert.outs

    frag.add_include('compiled.inc')
    frag.add_include('std/conetrace.glsl')
    frag.add_include('std/gbuffer.glsl')

    frag.write_header('#extension GL_ARB_shader_image_load_store : enable')

    frag.add_uniform('mat4 W', '_worldMatrix')
    frag.add_uniform('sampler3D voxels')
    frag.add_uniform('layout(binding = 0, rgba8) image3D voxelsBounce')
    frag.add_uniform('sampler2D gbufferD')
    frag.add_uniform('sampler2D gbuffer0')
    frag.add_uniform('sampler2D gbuffer1')
    frag.add_uniform('vec3 eye', '_cameraPosition')
    frag.add_uniform('vec3 eyeLook', '_cameraLook')
    frag.add_uniform('vec2 cameraProj', '_cameraPlaneProj')
    frag.add_uniform('vec3 viewerPos', '_viewerPos')
    vert.add_out('vec3 viewRay')

    frag.write('float depth = textureLod(gbufferD, texCoord, 0.0).r * 2.0 - 1.0;')
    frag.write('vec4 g0 = textureLod(gbuffer0, texCoord, 0.0);')
    frag.write('vec3 n;')
    frag.write('n.z = 1.0 - abs(g0.x) - abs(g0.y);')
    frag.write('n.xy = n.z >= 0.0 ? g0.xy : octahedronWrap(g0.xy);')
    frag.write('n = normalize(n);')

    frag.write('vec4 g1 = textureLod(gbuffer1, texCoord, 0.0);')
    frag.write('float spec = unpackFloat2(g1.a).y;')
    frag.write('float roughness = g0.b;')

    frag.write('vec3 p = getPos(eye, eyeLook, viewRay, depth, cameraProj);')
    frag.write('float dist = max(abs(viewerPos.x - p.x), max(abs(viewerPos.y - p.y), abs(viewerPos.z - p.z)));')
    frag.write('float clipmapLevel = max(log2(dist / voxelgiResolution.x * 2.0), 0);')
    frag.write('float voxelSize = pow(2.0, int(clipmapLevel)) / 2.0;')
    frag.write('vec3 eyeSnap = floor((viewerPos + eyeLook * voxelSize * voxelgiHalfExtents.x) / voxelSize) * voxelSize;')
    frag.write('vec3 voxpos = (p - eyeSnap) / voxelSize * 1.0 / voxelgiResolution.x;')

    vert.add_uniform('mat3 N', '_normalMatrix')
    vert.add_out('vec2 texCoord')
    vert.add_out('vec3 wnormal')
    vert.write('wnormal = normalize(N * vec3(nor.xy, pos.w));')

    frag.write('vec4 col = traceDiffuse(voxpos, wnormal, voxels, roughness, clipmapLevel);')
    frag.write('imageStore(voxelsBounce, ivec3(voxpos), col);')

    assets.fs_equal(con_voxel, assets.shader_cons['voxelbounce_frag'])

    return con_voxel
