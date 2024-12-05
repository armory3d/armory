import bpy

import arm
import arm.material.cycles as cycles
import arm.material.mat_state as mat_state
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
    con_refract = mat_state.data.add_context({ 'name': context_id, 'depth_write': False, 'compare_mode': 'less', 'cull_mode': 'clockwise' })
    con_refract.data["vertex_elements"].append({'name' : 'pos', 'data' : 'short4norm'})

    make_mesh.make_forward_base(con_refract, parse_opacity=True, transluc_pass=True)

    vert = con_refract.vert
    frag = con_refract.frag
    tese = con_refract.tese

    frag.add_include('std/gbuffer.glsl')
    frag.add_out('vec4 fragColor[3]')

    # Remove fragColor = ...;
    frag.main = frag.main[:frag.main.rfind('fragColor')]
    frag.write('\n')

    wrd = bpy.data.worlds['Arm']

    frag.write('n /= (abs(n.x) + abs(n.y) + abs(n.z));')
    frag.write('n.xy = n.z >= 0.0 ? n.xy : octahedronWrap(n.xy);')
    frag.write('fragColor[0] = vec4(n.xy, roughness, metallic);')
    frag.write('fragColor[1] = vec4(direct + indirect, packFloat2(occlusion, specular));')
    frag.write('fragColor[2] = vec4(ior, opacity, 0.0, 0.0);')
    make_finalize.make(con_refract)

    # assets.vs_equal(con_refract, assets.shader_cons['transluc_vert']) # shader_cons has no transluc yet
    # assets.fs_equal(con_refract, assets.shader_cons['transluc_frag'])

    return con_refract
