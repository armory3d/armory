import armmaterial.cycles as cycles
import armmaterial.mat_state as mat_state
import armmaterial.mat_utils as mat_utils
import bpy

def make(context_id):
    con_voxel = mat_state.data.add_context({ 'name': context_id, 'depth_write': False, 'compare_mode': 'always', 'cull_mode': 'none', 'color_write_red': False, 'color_write_green': False, 'color_write_blue': False, 'color_write_alpha': False })
    wrd = bpy.data.worlds['Arm']

    if '_NoShadows' in wrd.world_defs:
        is_shadows = False
    else:
        is_shadows = True

    vert = con_voxel.make_vert()
    frag = con_voxel.make_frag()
    geom = con_voxel.make_geom()
    tesc = None
    tese = None

    geom.ins = vert.outs
    frag.ins = geom.outs

    vert.add_uniform('mat4 W', '_worldMatrix')
    vert.add_uniform('mat3 N', '_normalMatrix')

    vert.add_out('vec3 wpositionGeom')
    vert.add_out('vec3 wnormalGeom')

    vert.add_include('../../Shaders/compiled.glsl')

    if mat_state.data.is_elem('tex'):
        vert.add_out('vec2 texCoordGeom')
        vert.write('texCoordGeom = tex;')

    vert.write('wpositionGeom = vec3(W * vec4(pos, 1.0)) / voxelgiDimensions.x;')
    vert.write('wnormalGeom = normalize(N * nor);')
    vert.write('gl_Position = vec4(0.0, 0.0, 0.0, 1.0);')

    if is_shadows:
        vert.add_out('vec4 lampPosGeom')
        vert.add_uniform('mat4 LWVP', '_biasLampWorldViewProjectionMatrix')
        vert.write('lampPosGeom = LWVP * vec4(pos, 1.0);')

    geom.add_out('vec3 wposition')
    geom.add_out('vec3 wnormal')
    if is_shadows:
        geom.add_out('vec4 lampPos')
    if mat_state.data.is_elem('tex'):
        geom.add_out('vec2 texCoord')

    geom.write('const vec3 p1 = wpositionGeom[1] - wpositionGeom[0];')
    geom.write('const vec3 p2 = wpositionGeom[2] - wpositionGeom[0];')
    geom.write('const vec3 p = abs(cross(p1, p2));')
    geom.write('for (uint i = 0; i < 3; ++i) {')
    geom.write('    wposition = wpositionGeom[i];')
    geom.write('    wnormal = wnormalGeom[i];')
    if is_shadows:
        geom.write('    lampPos = lampPosGeom[i];')
    if mat_state.data.is_elem('tex'):
        geom.write('    texCoord = texCoordGeom[i];')
    geom.write('    if (p.z > p.x && p.z > p.y) {')
    geom.write('        gl_Position = vec4(wposition.x, wposition.y, 0.0, 1.0);')
    geom.write('    }')
    geom.write('    else if (p.x > p.y && p.x > p.z) {')
    geom.write('        gl_Position = vec4(wposition.y, wposition.z, 0.0, 1.0);')
    geom.write('    }')
    geom.write('    else {')
    geom.write('        gl_Position = vec4(wposition.x, wposition.z, 0.0, 1.0);')
    geom.write('    }')
    geom.write('    EmitVertex();')
    geom.write('}')
    geom.write('EndPrimitive();')

    frag.write('float visibility = 1.0;')
    if is_shadows:
        frag.add_uniform('sampler2D shadowMap')
        #frag.add_uniform('bool receiveShadow')
        frag.add_uniform('float shadowsBias', '_lampShadowsBias')
        # frag.write('if (receiveShadow && lampPos.w > 0.0) {')
        frag.write('if (lampPos.w > 0.0) {')
        frag.write('    vec3 lpos = lampPos.xyz / lampPos.w;')
        frag.write('    if (texture(shadowMap, lpos.xy).r < lpos.z - shadowsBias) visibility = 0.0;')
        frag.write('}')

    frag.add_include('../../Shaders/compiled.glsl')
    frag.add_include('../../Shaders/std/math.glsl')
    frag.write_header('#extension GL_ARB_shader_image_load_store : enable')

    frag.add_uniform('layout(RGBA8) image3D voxels')
    frag.add_uniform('vec3 lightPos', '_lampPosition')
    frag.add_uniform('vec3 lightColor', '_lampColor')

    frag.write('if (!isInsideCube(wposition)) return;')

    frag.write('vec3 basecol;')
    frag.write('float roughness;') #
    frag.write('float metallic;') #
    frag.write('float occlusion;') #
    frag.write_pre = True
    frag.write('mat3 TBN;') # TODO: discard, parse basecolor only
    frag.write_pre = False
    cycles.parse(mat_state.nodes, vert, frag, geom, tesc, tese, parse_opacity=False, parse_displacement=False)
    frag.write('vec3 color = basecol * visibility * lightColor * max(dot(wnormal, normalize(lightPos - wposition * voxelgiDimensions.x)), 0.0) * attenuate(distance(wposition * voxelgiDimensions.x, lightPos));')
    frag.write('vec3 voxel = wposition * 0.5 + vec3(0.5);')
    frag.write('imageStore(voxels, ivec3(voxelgiResolution * voxel), vec4(color, 1.0));') # , alpha

    return con_voxel
