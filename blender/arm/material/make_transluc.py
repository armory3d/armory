import bpy

import arm
import arm.material.cycles as cycles
import arm.material.mat_state as mat_state
import arm.material.make_mesh as make_mesh
import arm.material.make_finalize as make_finalize
import arm.assets as assets

if arm.is_reload(__name__):
	cycles = arm.reload_module(cycles)
	mat_state = arm.reload_module(mat_state)
	make_mesh = arm.reload_module(make_mesh)
	make_finalize = arm.reload_module(make_finalize)
	assets = arm.reload_module(assets)
else:
	arm.enable_reload(__name__)


def make(context_id):
    con_transluc = mat_state.data.add_context({ 'name': context_id, 'depth_write': True, 'compare_mode': 'less', 'cull_mode': 'clockwise', \
		'blend_source': 'blend_one', 'blend_destination': 'blend_one', 'blend_operation': 'add', \
		'alpha_blend_source': 'blend_zero', 'alpha_blend_destination': 'inverse_source_alpha', 'alpha_blend_operation': 'add' })

    make_mesh.make_forward_base(con_transluc, parse_opacity=True, transluc_pass=True)

    vert = con_transluc.vert
    frag = con_transluc.frag
    tese = con_transluc.tese

    frag.add_out('vec4 fragColor[2]')

    # Remove fragColor = ...;
    frag.main = frag.main[:frag.main.rfind('fragColor')]
    frag.write('\n')

    wrd = bpy.data.worlds['Arm']
    if '_VoxelAOvar' in wrd.world_defs:
        frag.write('indirect *= 0.25;')
    frag.write('vec4 premultipliedReflect = vec4(vec3(direct + indirect * 0.5) * opacity, opacity);');

    frag.write('float w = clamp(pow(min(1.0, premultipliedReflect.a * 10.0) + 0.01, 3.0) * 1e8 * pow(1.0 - (gl_FragCoord.z) * 0.9, 3.0), 1e-2, 3e3);')
    frag.write('fragColor[0] = vec4(premultipliedReflect.rgb * w, premultipliedReflect.a);')
    frag.write('fragColor[1] = vec4(premultipliedReflect.a * w, 0.0, 0.0, 1.0);')

    make_finalize.make(con_transluc)

    # assets.vs_equal(con_transluc, assets.shader_cons['transluc_vert']) # shader_cons has no transluc yet
    # assets.fs_equal(con_transluc, assets.shader_cons['transluc_frag'])

    return con_transluc
