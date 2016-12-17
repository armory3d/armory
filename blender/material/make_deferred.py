import make_state as state
import material.mat_state as mat_state
import material.make_cycles as make_cycles
import armutils

def mesh(context_id):
    con_mesh = mat_state.data.add_context({ 'name': context_id, 'depth_write': True, 'compare_mode': 'less', 'cull_mode': 'clockwise' })

    vert = con_mesh.make_vert()
    frag = con_mesh.make_frag(mrt=2)
    geom = None
    tesc = None
    tese = None

    # Displacement linked
    tess_enabled = armutils.tess_enabled(state.target)
    output_node = make_cycles.node_by_type(mat_state.nodes, 'OUTPUT_MATERIAL')
    if output_node == None:
        return None

    if output_node.inputs[2].is_linked:
        l = output_node.inputs[2].links[0]
        if l.from_node.type == 'GROUP' and l.from_node.node_tree.name.startswith('Armory PBR') and l.from_node.inputs[10].is_linked == False:
            tess_enabled = False

    if tess_enabled and output_node.inputs[2].is_linked:
        tesc = con_mesh.make_tesc()
        tese = con_mesh.make_tese()
        tesc.ins = vert.outs
        tese.ins = tesc.outs
        frag.ins = tese.outs

        vert.add_out('vec3 wposition')
        vert.add_uniform('mat4 W', '_worldMatrix')
        vert.write('vec4 spos = vec4(pos, 1.0);')
        vert.write('wposition = vec4(W * spos).xyz;')

        const = {}
        const['name'] = 'innerLevel'
        const['float'] = mat_state.material.height_tess_inner
        mat_state.mat_context['bind_constants'].append(const)
        const = {}
        const['name'] = 'outerLevel'
        const['float'] = mat_state.material.height_tess_outer
        mat_state.mat_context['bind_constants'].append(const)
        tesc.add_uniform('float innerLevel')
        tesc.add_uniform('float outerLevel')
        tesc.write_tesc_levels()

        tese.add_out('vec3 wposition')
        tese.add_out('vec3 wnormal')
        tese.add_out('vec3 eyeDir')
        tese.write('vec3 p0 = gl_TessCoord.x * tc_wposition[0];')
        tese.write('vec3 p1 = gl_TessCoord.y * tc_wposition[1];')
        tese.write('vec3 p2 = gl_TessCoord.z * tc_wposition[2];')
        tese.write('wposition = p0 + p1 + p2;')
        tese.write('vec3 n0 = gl_TessCoord.x * tc_wnormal[0];')
        tese.write('vec3 n1 = gl_TessCoord.y * tc_wnormal[1];')
        tese.write('vec3 n2 = gl_TessCoord.z * tc_wnormal[2];')
        tese.write('wnormal = normalize(n0 + n1 + n2);')

    # No displacement
    else:
        frag.ins = vert.outs
        vert.add_out('vec3 wposition')
        vert.add_out('vec3 eyeDir')
        vert.add_uniform('mat4 W', '_worldMatrix')
        vert.add_uniform('mat4 N', '_normalMatrix')
        vert.add_uniform('mat4 WVP', '_worldViewProjectionMatrix')
        vert.add_uniform('vec3 eye', '_cameraPosition')
        vert.write('vec4 spos = vec4(pos, 1.0);')
        vert.write('wposition = vec4(W * spos).xyz;')
        vert.write('eyeDir = eye - wposition;')
        vert.write('gl_Position = WVP * spos;')

    frag.add_include('../../Shaders/compiled.glsl')
    frag.add_include('../../Shaders/std/gbuffer.glsl')
    frag.write('vec3 v = normalize(eyeDir);')
    # frag.write('float dotNV = dot(n, v);')
    frag.write('float dotNV = max(dot(n, v), 0.0);')

    frag.write('vec3 basecol;')
    frag.write('float roughness;')
    frag.write('float metallic;')
    frag.write('float occlusion;')

    make_cycles.parse(mat_state.nodes, vert, frag, geom, tesc, tese)

    if mat_state.data.is_elem('tex'):
        vert.add_out('vec2 texCoord')
        vert.write('texCoord = tex;')

        if tese != None:
            if 'texCoord' in frag.main or 'texCoord' in frag.main_pre:
                tese.add_out('vec2 texCoord')
                tese.write_pre = True
                tese.write('vec2 tc0 = gl_TessCoord.x * tc_texCoord[0];')
                tese.write('vec2 tc1 = gl_TessCoord.y * tc_texCoord[1];')
                tese.write('vec2 tc2 = gl_TessCoord.z * tc_texCoord[2];')
                tese.write('texCoord = tc0 + tc1 + tc2;')
                tese.write_pre = False
            elif 'texCoord' in tese.main or 'texCoord' in tese.main_pre:
                tese.write_pre = True
                tese.write('vec2 tc0 = gl_TessCoord.x * tc_texCoord[0];')
                tese.write('vec2 tc1 = gl_TessCoord.y * tc_texCoord[1];')
                tese.write('vec2 tc2 = gl_TessCoord.z * tc_texCoord[2];')
                tese.write('vec2 texCoord = tc0 + tc1 + tc2;')
                tese.write_pre = False

    if mat_state.data.is_elem('col'):
        vert.add_out('vec3 color')
        vert.write('color = col;')

        if tese != None:
            tese.add_out('vec3 color')
            tese.write('vec3 col0 = gl_TessCoord.x * tc_color[0];')
            tese.write('vec3 col1 = gl_TessCoord.y * tc_color[1];')
            tese.write('vec3 col2 = gl_TessCoord.z * tc_color[2];')
            tese.write('color = col0 + col1 + col2;')

    if mat_state.data.is_elem('tan'):

        if tese != None:
            vert.add_out('vec3 wnormal')
            vert.add_out('vec3 wtangent')
            vert.add_uniform('mat4 N', '_normalMatrix')
            vert.write('wnormal = normalize(mat3(N) * nor);')
            vert.write('wtangent = normalize(mat3(N) * tan);')
            tese.add_out('mat3 TBN')
            tese.write('vec3 tan0 = gl_TessCoord.x * tc_wtangent[0];')
            tese.write('vec3 tan1 = gl_TessCoord.y * tc_wtangent[1];')
            tese.write('vec3 tan2 = gl_TessCoord.z * tc_wtangent[2];')
            tese.write('vec3 wtangent = normalize(tan0 + tan1 + tan2);')
            tese.write('vec3 wbitangent = normalize(cross(wnormal, wtangent));')
            tese.write('TBN = mat3(wtangent, wbitangent, wnormal);')
        else:
            vert.add_out('mat3 TBN')
            vert.add_uniform('mat4 N', '_normalMatrix')
            vert.write('vec3 wnormal = normalize(mat3(N) * nor);')
            vert.write('vec3 tangent = normalize(mat3(N) * tan);')
            vert.write('vec3 bitangent = normalize(cross(wnormal, tangent));')
            vert.write('TBN = mat3(tangent, bitangent, wnormal);')
    else:
        vert.add_uniform('mat4 N', '_normalMatrix')
        vert.add_out('vec3 wnormal')
        vert.write('wnormal = normalize(mat3(N) * nor);')
        frag.write_pre = True
        frag.write('vec3 n = normalize(wnormal);')
        frag.write_pre = False

    if tese != None:
        tese.add_uniform('mat4 VP', '_viewProjectionMatrix')
        # Sample disp at neightbour points to calc normal
        tese.write('wposition += wnormal * disp * 0.2;')
        tese.add_uniform('vec3 eye', '_cameraPosition')
        tese.write('eyeDir = eye - wposition;')
        tese.write('gl_Position = VP * vec4(wposition, 1.0);')

    # Pack normal
    frag.write('n /= (abs(n.x) + abs(n.y) + abs(n.z));')
    frag.write('n.xy = n.z >= 0.0 ? n.xy : octahedronWrap(n.xy);')
    frag.write('fragColor[0] = vec4(n.xy, packFloat(metallic, roughness), 1.0 - gl_FragCoord.z);')
    frag.write('fragColor[1] = vec4(basecol.rgb, occlusion);')

    return con_mesh

def shadows(context_id):
    con_shadowmap = mat_state.data.add_context({ 'name': context_id, 'depth_write': True, 'compare_mode': 'less', 'cull_mode': 'clockwise' })

    vert = con_shadowmap.make_vert()
    frag = con_shadowmap.make_frag()
    geom = None
    tesc = None
    tese = None

    # Displacement linked
    tess_enabled = armutils.tess_enabled(state.target)
    tess_enabled_shadow = mat_state.material.height_tess_shadows

    output_node = make_cycles.node_by_type(mat_state.nodes, 'OUTPUT_MATERIAL')
    if output_node == None:
        return None

    if output_node.inputs[2].is_linked:
        l = output_node.inputs[2].links[0]
        if l.from_node.type == 'GROUP' and l.from_node.node_tree.name.startswith('Armory PBR') and l.from_node.inputs[10].is_linked == False:
            tess_enabled = False

    if tess_enabled and tess_enabled_shadow and output_node != None and output_node.inputs[2].is_linked:
        tesc = con_shadowmap.make_tesc()
        tese = con_shadowmap.make_tese()
        tesc.ins = vert.outs
        tese.ins = tesc.outs
        frag.ins = tese.outs

        vert.add_out('vec3 wposition')
        vert.add_out('vec3 wnormal')
        vert.add_uniform('mat4 W', '_worldMatrix')
        vert.add_uniform('mat4 N', '_normalMatrix')
        vert.write('vec4 spos = vec4(pos, 1.0);')
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

        make_cycles.parse(mat_state.nodes, vert, frag, geom, tesc, tese, parse_surface=False)

        if mat_state.data.is_elem('tex'):
            if tese != None and 'texCoord' in tese.main:
                vert.add_out('vec2 texCoord')
                vert.write('texCoord = tex;')
                tese.write_pre = True
                tese.write('vec2 tc0 = gl_TessCoord.x * tc_texCoord[0];')
                tese.write('vec2 tc1 = gl_TessCoord.y * tc_texCoord[1];')
                tese.write('vec2 tc2 = gl_TessCoord.z * tc_texCoord[2];')
                tese.write('vec2 texCoord = tc0 + tc1 + tc2;')
                tese.write_pre = False

        tese.add_uniform('mat4 LVP', '_lampViewProjectionMatrix')
        # tese.add_uniform('mat4 LWVP', '_lampWorldViewProjectionMatrix')
        tese.write('wposition += wnormal * disp * 0.2;')
        tese.write('gl_Position = LVP * vec4(wposition, 1.0);')
        # tese.write('gl_Position = LWVP * vec4(wposition, 1.0);')

    else:
        frag.ins = vert.outs
        vert.add_uniform('mat4 LWVP', '_lampWorldViewProjectionMatrix')
        vert.write('gl_Position = LWVP * vec4(pos, 1.0);')
    
    frag.write('fragColor = vec4(0.0);')

    return con_shadowmap
