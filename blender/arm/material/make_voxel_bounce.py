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

    frag = con_voxel.make_frag()

    frag.add_include('compiled.inc')
    frag.add_include('std/conetrace.glsl')
    frag.write_header('#extension GL_ARB_shader_image_load_store : enable')

    frag.add_uniform('sampler3D voxels')
    frag.add_uniform('sampler3D voxelsBounce')
    frag.add_uniform('sampler2D gbuffer_voxpos')
    frag.add_uniform('mat3 N', '_normalMatrix')

    frag.write('vec3 voxpos = textureLod(gbuffer_voxpos, texCoord, 0.0).rgb;')
    frag.write('vec3 wnormal = normalize(N * vec3(nor.xy, pos.w));')
    frag.write('vec4 col = traceDiffure(voxpos, wnormal, voxels);')
    frag.write('imageStore(voxelsBounce, voxpos, col);')

    assets.fs_equal(con_voxel, assets.shader_cons['voxel_bounce_frag'])

    return con_voxel
