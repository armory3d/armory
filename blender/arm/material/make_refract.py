import bpy

import arm
import arm.material.cycles as cycles
import arm.material.mat_state as mat_state
import arm.material.mat_utils as mat_utils
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
    is_displacement = mat_utils.disp_linked(mat_state.output_node)
    wrd = bpy.data.worlds['Arm']
    con_refract = mat_state.data.add_context({ 'name': context_id, 'depth_write': True, 'compare_mode': 'less', 'cull_mode': 'clockwise' })
    make_mesh.make_forward_base(con_refract, parse_opacity=True, transluc_pass=True)

    vert = con_refract.vert
    frag = con_refract.frag
    tese = con_refract.tese

    frag.add_include('std/gbuffer.glsl')
    frag.add_out('vec4 fragColor[GBUF_SIZE]')

    if '_gbuffer2' in wrd.world_defs:
        if '_Veloc' in wrd.world_defs:
            if tese is None:
                vert.add_uniform('mat4 prevWVP', link='_prevWorldViewProjectionMatrix')
                vert.add_out('vec4 wvpposition')
                vert.add_out('vec4 prevwvpposition')
                vert.write('wvpposition = gl_Position;')
                if is_displacement:
                    vert.add_uniform('mat4 invW', link='_inverseWorldMatrix')
                    vert.write('prevwvpposition = prevWVP * (invW * vec4(wposition, 1.0));')
                else:
                    vert.write('prevwvpposition = prevWVP * spos;')
            else:
                tese.add_out('vec4 wvpposition')
                tese.add_out('vec4 prevwvpposition')
                tese.write('wvpposition = gl_Position;')
                if is_displacement:
                    tese.add_uniform('mat4 invW', link='_inverseWorldMatrix')
                    tese.add_uniform('mat4 prevWVP', '_prevWorldViewProjectionMatrix')
                    tese.write('prevwvpposition = prevWVP * (invW * vec4(wposition, 1.0));')
                else:
                    vert.add_uniform('mat4 prevW', link='_prevWorldMatrix')
                    vert.add_out('vec3 prevwposition')
                    vert.write('prevwposition = vec4(prevW * spos).xyz;')
                    tese.add_uniform('mat4 prevVP', '_prevViewProjectionMatrix')
                    make_tess.interpolate(tese, 'prevwposition', 3)
                    tese.write('prevwvpposition = prevVP * vec4(prevwposition, 1.0);')

    # Remove fragColor = ...;
    frag.main = frag.main[:frag.main.rfind('fragColor')]
    frag.write('\n')


    frag.write('n /= (abs(n.x) + abs(n.y) + abs(n.z));')
    frag.write('n.xy = n.z >= 0.0 ? n.xy : octahedronWrap(n.xy);')

    is_shadeless = mat_state.emission_type == mat_state.EmissionType.SHADELESS
    if is_shadeless or '_SSS' in wrd.world_defs or '_Hair' in wrd.world_defs:
        if is_shadeless:
            frag.write('basecol = emissionCol;')
        if '_SSS' in wrd.world_defs or '_Hair' in wrd.world_defs:
            frag.write('fragColor[GBUF_IDX_SUBSURFACE_1] = vec4(subsurfaceCol, 1.0);')
            frag.write('fragColor[GBUF_IDX_SUBSURFACE_2] = vec4(subsurfaceWeights, packFloat2(subsurfaceIor, subsurfaceScale));')
    else:
        frag.write('const uint matid = 0;')

    frag.write('fragColor[GBUF_IDX_0] = vec4(n.xy, roughness, packFloatInt16(metallic, matid));')
    frag.write('fragColor[GBUF_IDX_1] = vec4(direct + indirect, packFloat2(occlusion, specular));')

    if '_gbuffer2' in wrd.world_defs:
        if '_Veloc' in wrd.world_defs:
            frag.write('vec2 posa = (wvpposition.xy / wvpposition.w) * 0.5 + 0.5;')
            frag.write('vec2 posb = (prevwvpposition.xy / prevwvpposition.w) * 0.5 + 0.5;')
            frag.write('fragColor[GBUF_IDX_2].rg = vec2(posa - posb);')
            frag.write('fragColor[GBUF_IDX_2].b = 0.0;')

        if mat_state.material.arm_ignore_irradiance:
            frag.write('fragColor[GBUF_IDX_2].b = 1.0;')

    # Even if the material doesn't use emission we need to write to the
    # emission buffer (if used) to prevent undefined behaviour
    frag.write('#ifdef _EmissionShaded')
    frag.write('fragColor[GBUF_IDX_EMISSION] = vec4(emissionCol, 0.0);')  #Alpha channel is unused at the moment
    frag.write('#endif')

    frag.write('fragColor[GBUF_IDX_REFRACTION] = vec4(ior, opacity, 0.0, 0.0);')

    make_finalize.make(con_refract)

    # assets.vs_equal(con_refract, assets.shader_cons['transluc_vert']) # shader_cons has no transluc yet
    # assets.fs_equal(con_refract, assets.shader_cons['transluc_frag'])

    return con_refract
