import material.state as state
import material.make_cycles as make_cycles

def mesh(context_id):
    con_mesh = state.data.add_context({ 'name': context_id, 'depth_write': True, 'compare_mode': 'less', 'cull_mode': 'clockwise' })

    vert = con_mesh.make_vert()
    frag = con_mesh.make_frag(mrt=2)

    vert.add_out('vec3 wnormal')
    vert.add_out('vec3 wposition')
    vert.add_out('vec3 eyeDir')
    vert.add_uniform('mat4 W', '_worldMatrix')
    vert.add_uniform('mat4 N', '_normalMatrix')
    vert.add_uniform('mat4 WVP', '_worldViewProjectionMatrix')
    vert.add_uniform('vec3 eye', '_cameraPosition')
    vert.write('vec4 spos = vec4(pos, 1.0);')
    vert.write('wnormal = normalize(mat3(N) * nor);')
    vert.write('wposition = vec4(W * spos).xyz;')
    vert.write('eyeDir = eye - wposition;')
    vert.write('gl_Position = WVP * spos;')

    frag.add_include('../../Shaders/compiled.glsl')
    frag.add_include('../../Shaders/std/gbuffer.glsl')
    frag.add_uniform('sampler2D snoise', link='_noise64')
    frag.add_uniform('int lightType', '_lampType')
    frag.write('vec3 n = normalize(wnormal);')
    frag.write('vec3 v = normalize(eyeDir);')
    # frag.write('float dotNV = dot(n, v);')
    frag.write('float dotNV = max(dot(n, v), 0.0);')

    frag.write('vec3 basecol;')
    frag.write('float roughness;')
    frag.write('float metallic;')
    frag.write('float occlusion;')

    make_cycles.parse(state.nodes, vert, frag)

    # Pack normal
    frag.write('n /= (abs(n.x) + abs(n.y) + abs(n.z));')
    frag.write('n.xy = n.z >= 0.0 ? n.xy : octahedronWrap(n.xy);')
    frag.write('fragColor[0] = vec4(n.xy, packFloat(metallic, roughness), 1.0 - gl_FragCoord.z);')
    frag.write('fragColor[1] = vec4(basecol.rgb, occlusion);')

    return con_mesh

def shadows(context_id):
    con_shadowmap = state.data.add_context({ 'name': context_id, 'depth_write': True, 'compare_mode': 'less', 'cull_mode': 'clockwise' })

    vert = con_shadowmap.make_vert()
    vert.add_uniform('mat4 LWVP', '_lampWorldViewProjectionMatrix')
    vert.write('gl_Position = LWVP * vec4(pos, 1.0);')

    frag = con_shadowmap.make_frag()
    frag.write('fragColor = vec4(0.0);')

    return con_shadowmap
