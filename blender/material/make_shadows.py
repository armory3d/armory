import material.cycles as cycles
import material.mat_state as mat_state
import material.mat_utils as mat_utils
import material.make_skin as make_skin
import material.make_tess as make_tess

def make(context_id, rpasses):
    con_shadowmap = mat_state.data.add_context({ 'name': context_id, 'depth_write': True, 'compare_mode': 'less', 'cull_mode': 'clockwise' })

    vert = con_shadowmap.make_vert()
    frag = con_shadowmap.make_frag()
    geom = None
    tesc = None
    tese = None

    vert.write('vec4 spos = vec4(pos, 1.0);')

    parse_opacity = 'translucent' in rpasses
    if parse_opacity:
        frag.write('float opacity;')

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
        make_tess.tesc_levels(tesc)

        make_tess.interpolate(tese, 'wposition', 3)
        make_tess.interpolate(tese, 'wnormal', 3, normalize=True)

        cycles.parse(mat_state.nodes, vert, frag, geom, tesc, tese, parse_surface=False, parse_opacity=parse_opacity)

        if mat_state.data.is_elem('tex'):
            vert.add_out('vec2 texCoord')
            vert.write('texCoord = tex;')
            tese.write_pre = True
            make_tess.interpolate(tese, 'texCoord', 2, declare_out=frag.contains('texCoord'))
            tese.write_pre = False

        if mat_state.data.is_elem('tex1'):
            vert.add_out('vec2 texCoord1')
            vert.write('texCoord1 = tex1;')
            tese.write_pre = True
            make_tess.interpolate(tese, 'texCoord1', 2, declare_out=frag.contains('texCoord1'))
            tese.write_pre = False

        if mat_state.data.is_elem('col'):
            vert.add_out('vec3 vcolor')
            vert.write('vcolor = col;')
            tese.write_pre = True
            make_tess.interpolate(tese, 'vcolor', 2, declare_out=frag.contains('vcolor'))
            tese.write_pre = False

        tese.add_uniform('mat4 LVP', '_lampViewProjectionMatrix')
        tese.write('wposition += wnormal * disp * 0.2;')
        tese.write('gl_Position = LVP * vec4(wposition, 1.0);')
    # No displacement
    else:
        frag.ins = vert.outs
        vert.add_uniform('mat4 LWVP', '_lampWorldViewProjectionMatrix')
        vert.write('gl_Position = LWVP * spos;')

        if parse_opacity:
            cycles.parse(mat_state.nodes, vert, frag, geom, tesc, tese, parse_surface=False, parse_opacity=True)

            if mat_state.data.is_elem('tex'):
                vert.add_out('vec2 texCoord')
                vert.write('texCoord = tex;')

            if mat_state.data.is_elem('tex1'):
                vert.add_out('vec2 texCoord1')
                vert.write('texCoord1 = tex1;')

            if mat_state.data.is_elem('col'):
                vert.add_out('vec3 vcolor')
                vert.write('vcolor = col;')
    
    if parse_opacity:
        frag.write('if (opacity < 0.5) discard;')

    frag.write('fragColor = vec4(0.0);')

    return con_shadowmap
