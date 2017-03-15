import bpy
import arm.make_state as state
import arm.material.mat_state as mat_state
import arm.material.mat_utils as mat_utils
import arm.utils

def make(context_id):

    con_depth = mat_state.data.add_context({ 'name': context_id, 'depth_write': True, 'compare_mode': 'less', 'cull_mode': 'clockwise', 'color_write_red': False, 'color_write_green': False, 'color_write_blue': False, 'color_write_alpha': False })

    vert = con_depth.make_vert()
    frag = con_depth.make_frag()

    vert.add_uniform('mat4 WVP', '_worldViewProjectionMatrix')
    vert.write('gl_Position = WVP * vec4(pos, 1.0);')

    # frag.add_out('vec4 fragColor')
    # frag.write('fragColor = vec4(0.0);')

    return con_depth
