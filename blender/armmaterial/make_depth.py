import bpy
import make_state as state
import armmaterial.mat_state as mat_state
import armmaterial.mat_utils as mat_utils
import armutils
import assets

def make(context_id):

    con_depth = mat_state.data.add_context({ 'name': context_id, 'depth_write': True, 'compare_mode': 'less', 'cull_mode': 'clockwise', 'color_write_red': False, 'color_write_green': False, 'color_write_blue': False, 'color_write_alpha': False })

    vert = con_depth.make_vert()
    frag = con_depth.make_frag()

    vert.add_uniform('mat4 WVP', '_worldViewProjectionMatrix')
    vert.write('gl_Position = WVP * vec4(pos, 1.0);')

    # frag.add_out('vec4 fragColor')
    # frag.write('fragColor = vec4(0.0);')

    return con_depth
