import bpy

import arm
import arm.material.cycles as cycles
import arm.material.mat_state as mat_state
import arm.material.make_mesh as make_mesh
import arm.material.make_finalize as make_finalize
import arm.material.ray_marching_glsl as ray_marching_glsl
import arm.assets as assets

if arm.is_reload(__name__):
    cycles = arm.reload_module(cycles)
    mat_state = arm.reload_module(mat_state)
    make_mesh = arm.reload_module(make_mesh)
    make_finalize = arm.reload_module(make_finalize)
    assets = arm.reload_module(assets)
else:
    arm.enable_reload(__name__)


def make(context_id, rpasses):
    wrd = bpy.data.worlds['Arm']
    
    con_refract = mat_state.data.add_context({ 'name': context_id, 'depth_write': False, 'compare_mode': 'less', 'cull_mode': 'clockwise', \
        'blend_source': 'blend_one', 'blend_destination': 'blend_one', 'blend_operation': 'add', \
		'alpha_blend_source': 'blend_zero', 'alpha_blend_destination': 'inverse_source_alpha', 'alpha_blend_operation': 'add'})

    make_mesh.make_deferred(con_refract, rpasses)

    vert = con_refract.vert
    frag = con_refract.frag
    tese = con_refract.tese

    frag.add_include('compiled.inc')
    frag.add_include('std/math.glsl')
    frag.add_include('std/gbuffer.glsl')

    frag.add_uniform('sampler2D tex')
    frag.add_uniform('sampler2D gbufferD')
    
    frag.write('fragColor[2] = vec4(opacity, rior, 0.0, 0.0);')

	# assets.vs_equal(con_transluc, assets.shader_cons['transluc_vert']) # shader_cons has no transluc yet
    # assets.fs_equal(con_transluc, assets.shader_cons['transluc_frag'])

    return con_refract
