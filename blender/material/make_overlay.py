import material.cycles as cycles
import material.mat_state as mat_state
import material.make_mesh as make_mesh

def make(context_id):
	con_overlay = mat_state.data.add_context({ 'name': context_id, 'depth_write': True, 'compare_mode': 'less', 'cull_mode': 'clockwise' })

	make_mesh.make_base(con_overlay, parse_opacity=False)

	frag = con_overlay.frag
	frag.add_out('vec4 fragColor')
	frag.write('fragColor = vec4(basecol, 1.0);')
	frag.write('fragColor.rgb = pow(fragColor.rgb, vec3(1.0 / 2.2));')

	return con_overlay
