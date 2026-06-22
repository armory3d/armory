import arm
import arm.material.make_finalize as make_finalize
import arm.material.make_mesh as make_mesh
import arm.material.mat_state as mat_state
import arm.material.mat_utils as mat_utils

if arm.is_reload(__name__):
    make_finalize = arm.reload_module(make_finalize)
    make_mesh = arm.reload_module(make_mesh)
    mat_state = arm.reload_module(mat_state)
    mat_utils = arm.reload_module(mat_utils)
else:
    arm.enable_reload(__name__)


def make(context_id):
    con = { 'name': context_id, 'depth_write': True, 'compare_mode': 'less', 'cull_mode': 'clockwise' }
    mat = mat_state.material
    blend = mat.arm_blending
    if blend:
        con['blend_source'] = mat.arm_blending_source
        con['blend_destination'] = mat.arm_blending_destination
        con['blend_operation'] = mat.arm_blending_operation
        con['alpha_blend_source'] = mat.arm_blending_source_alpha
        con['alpha_blend_destination'] = mat.arm_blending_destination_alpha
        con['alpha_blend_operation'] = mat.arm_blending_operation_alpha

    con_overlay = mat_state.data.add_context(con)

    arm_discard = mat.arm_discard
    is_transluc = mat_utils.is_transluc(mat)
    parse_opacity = (blend and is_transluc) or arm_discard
    make_mesh.make_base(con_overlay, parse_opacity=parse_opacity)

    frag = con_overlay.frag

    if arm_discard:
        opac = mat.arm_discard_opacity
        frag.write('if (opacity < {0}) discard;'.format(opac))

    frag.add_out('vec4 fragColor')
    if blend and parse_opacity:
        frag.write('fragColor = vec4(basecol + emissionCol, opacity);')
    else:
        frag.write('fragColor = vec4(basecol + emissionCol, 1.0);')

    frag.write('fragColor.rgb = pow(fragColor.rgb, vec3(1.0 / 2.2));')

    make_finalize.make(con_overlay)

    return con_overlay
