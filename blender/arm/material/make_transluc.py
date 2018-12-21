import arm.material.cycles as cycles
import arm.material.mat_state as mat_state
import arm.material.make_mesh as make_mesh
import arm.material.make_finalize as make_finalize
import arm.assets as assets

def make(context_id):
	con_transluc = mat_state.data.add_context({ 'name': context_id, 'depth_write': False, 'compare_mode': 'less', 'cull_mode': 'clockwise', \
		'blend_source': 'blend_one', 'blend_destination': 'blend_one', 'blend_operation': 'add', \
		'alpha_blend_source': 'blend_zero', 'alpha_blend_destination': 'inverse_source_alpha', 'alpha_blend_operation': 'add' })

	make_mesh.make_forward_base(con_transluc, parse_opacity=True)

	vert = con_transluc.vert
	frag = con_transluc.frag
	tese = con_transluc.tese

	frag.add_out('vec4[2] fragColor')

	sh = tese if tese != None else vert
	sh.add_out('vec4 wvpposition')
	sh.write('wvpposition = gl_Position;')

	# Remove fragColor = ...;
	frag.main = frag.main[:frag.main.rfind('fragColor')]

	frag.write('\n')
	frag.add_uniform('vec3 lightColor', link='_lightColor')
	frag.write('float visibility = 1.0;')
	frag.write('vec4 premultipliedReflect = vec4(vec3(direct * lightColor * visibility + indirect * occlusion) * opacity, opacity);')
	
	frag.write('float fragZ = wvpposition.z / wvpposition.w;')
	frag.write('float w = clamp(pow(min(1.0, premultipliedReflect.a * 10.0) + 0.01, 3.0) * 1e8 * pow(1.0 - fragZ * 0.9, 3.0), 1e-2, 3e3);')
	frag.write('fragColor[0] = vec4(premultipliedReflect.rgb * w, premultipliedReflect.a);')
	frag.write('fragColor[1] = vec4(premultipliedReflect.a * w, 0.0, 0.0, 1.0);')

	make_finalize.make(con_transluc)

	# assets.vs_equal(con_transluc, assets.shader_cons['transluc_vert']) # shader_cons has no transluc yet
    # assets.fs_equal(con_transluc, assets.shader_cons['transluc_frag'])

	return con_transluc
