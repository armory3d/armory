import bpy

import arm
import arm.material.cycles as cycles
import arm.material.mat_state as mat_state
import arm.material.mat_utils as mat_utils
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
<<<<<<< HEAD
    con_refraction_buffer = mat_state.data.add_context({ 'name': context_id, 'depth_write': False, 'compare_mode': 'less', 'cull_mode': 'clockwise' })

    arm_discard = mat_state.material.arm_discard
    blend = mat_state.material.arm_blending
    parse_opacity = blend or mat_utils.is_transluc(mat_state.material) or arm_discard
=======
    con_refraction_buffer = mat_state.data.add_context({ 'name': context_id, 'depth_write': True, 'compare_mode': 'less', 'cull_mode': 'clockwise' })

    arm_discard = mat_state.material.arm_discard
    blend = mat_state.material.arm_blending
    is_transluc = mat_utils.is_transluc(mat_state.material)
    parse_opacity = (blend and is_transluc) or arm_discard
>>>>>>> 0dd8663f88c28f904e010a031ff81f35364d2486

    make_mesh.make_base(con_refraction_buffer, parse_opacity)

    vert = con_refraction_buffer.vert
    frag = con_refraction_buffer.frag
<<<<<<< HEAD

=======
    tese = con_refraction_buffer.tese

    frag.add_include('std/gbuffer.glsl')
>>>>>>> 0dd8663f88c28f904e010a031ff81f35364d2486
    frag.add_out('vec4 fragColor')

    # Remove fragColor = ...;
    frag.main = frag.main[:frag.main.rfind('fragColor')]
    frag.write('\n')

<<<<<<< HEAD
    if parse_opacity:
        frag.write('fragColor = vec4(ior, opacity, 0.0, 1.0);')
    else:
        frag.write('fragColor = vec4(1.0, 1.0, 0.0, 1.0);')
=======
    wrd = bpy.data.worlds['Arm']

    if parse_opacity:
        frag.write('fragColor = vec4(ior, opacity, 0.0, 0.0);')
    else:
        frag.write('fragColor = vec4(1.0, 1.0, 0.0, 0.0);')
>>>>>>> 0dd8663f88c28f904e010a031ff81f35364d2486

    make_finalize.make(con_refraction_buffer)

    # assets.vs_equal(con_refract, assets.shader_cons['transluc_vert']) # shader_cons has no transluc yet
    # assets.fs_equal(con_refract, assets.shader_cons['transluc_frag'])

    return con_refraction_buffer
