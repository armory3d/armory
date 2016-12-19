import material.cycles as cycles
import material.mat_state as mat_state
import material.mat_utils as mat_utils
import material.make_skin as make_skin

def make(context_id):
    con_shadowmap = mat_state.data.add_context({ 'name': context_id, 'depth_write': True, 'compare_mode': 'less', 'cull_mode': 'clockwise' })

    vert = con_shadowmap.make_vert()
    frag = con_shadowmap.make_frag()
    geom = None
    tesc = None
    tese = None

    vert.write('vec4 spos = vec4(pos, 1.0);')

    if mat_state.data.is_elem('bone'):
        make_skin.skin_pos(vert)

    if mat_utils.disp_linked(mat_state.output_node) and mat_state.material.height_tess_shadows:
        tesc = con_shadowmap.make_tesc()
        tese = con_shadowmap.make_tese()
        tesc.ins = vert.outs
        tese.ins = tesc.outs
        frag.ins = tese.outs

        vert.add_out('vec3 wposition')
        vert.add_out('vec3 wnormal')
        vert.add_uniform('mat4 W', '_worldMatrix')
        vert.add_uniform('mat4 N', '_normalMatrix')
        vert.write('wnormal = normalize(mat3(N) * nor);')
        vert.write('wposition = vec4(W * spos).xyz;')
        
        const = {}
        const['name'] = 'innerLevel'
        const['float'] = mat_state.material.height_tess_shadows_inner
        mat_state.mat_context['bind_constants'].append(const)
        const = {}
        const['name'] = 'outerLevel'
        const['float'] = mat_state.material.height_tess_shadows_outer
        mat_state.mat_context['bind_constants'].append(const)
        tesc.add_uniform('float innerLevel')
        tesc.add_uniform('float outerLevel')
        tesc.write_tesc_levels()

        tese.write('vec3 p0 = gl_TessCoord.x * tc_wposition[0];')
        tese.write('vec3 p1 = gl_TessCoord.y * tc_wposition[1];')
        tese.write('vec3 p2 = gl_TessCoord.z * tc_wposition[2];')
        tese.write('vec3 wposition = p0 + p1 + p2;')
        tese.write('vec3 n0 = gl_TessCoord.x * tc_wnormal[0];')
        tese.write('vec3 n1 = gl_TessCoord.y * tc_wnormal[1];')
        tese.write('vec3 n2 = gl_TessCoord.z * tc_wnormal[2];')
        tese.write('vec3 wnormal = normalize(n0 + n1 + n2);')

        cycles.parse(mat_state.nodes, vert, frag, geom, tesc, tese, parse_surface=False)

        if mat_state.data.is_elem('tex') and tese.contains('texCoord'):
            vert.add_out('vec2 texCoord')
            vert.write('texCoord = tex;')
            tese.write_pre = True
            tese.write('vec2 tc0 = gl_TessCoord.x * tc_texCoord[0];')
            tese.write('vec2 tc1 = gl_TessCoord.y * tc_texCoord[1];')
            tese.write('vec2 tc2 = gl_TessCoord.z * tc_texCoord[2];')
            tese.write('vec2 texCoord = tc0 + tc1 + tc2;')
            tese.write_pre = False

        if mat_state.data.is_elem('tex1') and tese.contains('texCoord1'):
            vert.add_out('vec2 texCoord1')
            vert.write('texCoord1 = tex1;')
            tese.write_pre = True
            tese.write('vec2 tc01 = gl_TessCoord.x * tc_texCoord1[0];')
            tese.write('vec2 tc11 = gl_TessCoord.y * tc_texCoord1[1];')
            tese.write('vec2 tc21 = gl_TessCoord.z * tc_texCoord1[2];')
            tese.write('vec2 texCoord1 = tc01 + tc11 + tc21;')
            tese.write_pre = False

        if mat_state.data.is_elem('col') and tese.contains('vcolor'):
            vert.add_out('vec3 vcolor')
            vert.write('vcolor = col;')
            tese.write_pre = True
            tese.write('vec3 vcol0 = gl_TessCoord.x * tc_vcolor[0];')
            tese.write('vec3 vcol1 = gl_TessCoord.y * tc_vcolor[1];')
            tese.write('vec3 vcol2 = gl_TessCoord.z * tc_vcolor[2];')
            tese.write('vec3 vcolor = vcol0 + vcol1 + vcol2;')
            tese.write_pre = False

        tese.add_uniform('mat4 LVP', '_lampViewProjectionMatrix')
        tese.write('wposition += wnormal * disp * 0.2;')
        tese.write('gl_Position = LVP * vec4(wposition, 1.0);')
    # No displacement
    else:
        frag.ins = vert.outs
        vert.add_uniform('mat4 LWVP', '_lampWorldViewProjectionMatrix')
        vert.write('gl_Position = LWVP * spos;')
    
    frag.write('fragColor = vec4(0.0);')

    return con_shadowmap
