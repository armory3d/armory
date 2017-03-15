import armmaterial.cycles as cycles
import armmaterial.mat_state as mat_state
import armmaterial.make_mesh as make_mesh

def make(context_id):
	con_transluc = mat_state.data.add_context({ 'name': context_id, 'depth_write': False, 'compare_mode': 'less', 'cull_mode': 'clockwise', \
		'blend_source': 'blend_one', 'blend_destination': 'blend_one', 'blend_operation': 'add', \
		'alpha_blend_source': 'blend_zero', 'alpha_blend_destination': 'inverse_source_alpha', 'alpha_blend_operation': 'add' })

	make_mesh.make_forward_base(con_transluc, parse_opacity=True)

	vert = con_transluc.vert
	frag = con_transluc.frag
	tese = con_transluc.tese

	frag.add_out('vec4[2] fragColor')

	if tese != None:
		tese.add_out('vec4 wvpposition')
		tese.write('wvpposition = gl_Position;')
	else:
		vert.add_out('vec4 wvpposition')
		vert.write('wvpposition = gl_Position;')

	# Remove fragColor = ...;
	frag.main = frag.main[:frag.main.rfind('fragColor')]

	frag.write('vec4 premultipliedReflect = vec4(vec3(direct * visibility + indirect * occlusion), opacity);')
	
	frag.write('float fragZ = wvpposition.z / wvpposition.w;')
	frag.write('float a = min(1.0, premultipliedReflect.a) * 8.0 + 0.01;')
	frag.write('float b = -fragZ * 0.95 + 1.0;')
	frag.write('float w = clamp(a * a * a * 1e8 * b * b * b, 1e-2, 3e2);')
	frag.write('fragColor[0] = vec4(premultipliedReflect.rgb * w, premultipliedReflect.a);')
	frag.write('fragColor[1] = vec4(premultipliedReflect.a * w, 0.0, 0.0, 1.0);')

	return con_transluc
