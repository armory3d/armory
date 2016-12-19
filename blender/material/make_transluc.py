import material.cycles as cycles
import material.mat_state as mat_state
import material.make_mesh as make_mesh

def make(context_id):
	con_transluc = mat_state.data.add_context({ 'name': context_id, 'depth_write': False, 'compare_mode': 'less', 'cull_mode': 'clockwise', \
		'blend_source': 'blend_one', 'blend_destination': 'blend_one', 'blend_operation': 'add', \
		'alpha_blend_source': 'blend_zero', 'alpha_blend_destination': 'inverse_source_alpha', 'alpha_blend_operation': 'add' })

	make_mesh.forward(con_transluc, mrt=2)

	vert = con_transluc.vert
	frag = con_transluc.frag

	vert.add_out('vec4 wvpposition')
	vert.write('wvpposition = gl_Position;')

	# Remove fragColor = ...;
	frag.main = frag.main[:frag.main.rfind('fragColor')]



	frag.write('vec4 premultipliedReflect = vec4(vec3(direct * visibility + indirect * occlusion), 0.1);')

#ifdef _OpacTex
	# premultipliedReflect.a *= texture(sopacity, texCoord).r;
#else
	#ifdef _BaseTex
	# premultipliedReflect.a *= texel.a; // Base color alpha
	#endif
#endif
	
	frag.write('float fragZ = wvpposition.z / wvpposition.w;')
	frag.write('float a = min(1.0, premultipliedReflect.a) * 8.0 + 0.01;')
	frag.write('float b = -fragZ * 0.95 + 1.0;')
	frag.write('float w = clamp(a * a * a * 1e8 * b * b * b, 1e-2, 3e2);')
	frag.write('fragColor[0] = vec4(premultipliedReflect.rgb * w, premultipliedReflect.a);')
	frag.write('fragColor[1] = vec4(premultipliedReflect.a * w, 0.0, 0.0, 1.0);')

	return con_transluc
