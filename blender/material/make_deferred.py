import material.state as state
import material.make_cycles as make_cycles

def mesh(context_id):
    con_mesh = state.data.add_context({ 'name': context_id, 'depth_write': True, 'compare_mode': 'less', 'cull_mode': 'clockwise' })

    vert = con_mesh.make_vert()
    frag = con_mesh.make_frag()

    # make_cycles.parse(state.nodes, vert, frag)

    return con_mesh

def shadows(context_id):
    con_shadowmap = state.data.add_context({ 'name': context_id, 'depth_write': True, 'compare_mode': 'less', 'cull_mode': 'clockwise' })

    vert = con_shadowmap.make_vert()
    vert.add_uniform('mat4 LWVP', '_lampWorldViewProjectionMatrix')
    vert.write('gl_Position = LWVP * vec4(pos, 1.0);')

    frag = con_shadowmap.make_frag()
    frag.write('fragColor = vec4(0.0);')

    return con_shadowmap
