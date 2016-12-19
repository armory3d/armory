import material.cycles as cycles
import material.mat_state as mat_state
import material.make_mesh as make_mesh

def make(context_id):
	con_overlay = mat_state.data.add_context({ 'name': context_id, 'depth_write': True, 'compare_mode': 'less', 'cull_mode': 'clockwise' })

	make_mesh.forward(con_overlay)

	return con_overlay
