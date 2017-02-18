# http://simonstechblog.blogspot.sk/2013/01/implementing-voxel-cone-tracing.html
# http://leifnode.com/2015/05/voxel-cone-traced-global-illumination/
# http://www.seas.upenn.edu/%7Epcozzi/OpenGLInsights/OpenGLInsights-SparseVoxelization.pdf
# https://github.com/Cigg/Voxel-Cone-Tracing
# https://research.nvidia.com/sites/default/files/publications/GIVoxels-pg2011-authors.pdf

import material.cycles as cycles
import material.mat_state as mat_state
import material.mat_utils as mat_utils

def make(context_id):
    con_voxel = mat_state.data.add_context({ 'name': context_id, 'depth_write': False, 'compare_mode': 'always', 'cull_mode': 'none' })

    vert = con_voxel.make_vert()
    frag = con_voxel.make_frag()
    geom = con_voxel.make_geom()
    tesc = None
    tese = None

    geom.ins = vert.outs
    frag.ins = geom.outs

    vert.add_uniform('mat4 LWVP', '_lampWorldViewProjectionMatrix')
    vert.add_uniform('mat4 W', '_worldMatrix')

    vert.add_out('vec4 lampPos')
    # vert.add_out('vec2 texuv')

    # vert.write('texuv = tex;')
    vert.write('lampPos = LWVP * vec4(pos, 1.0);')
    vert.write('gl_Position = W * vec4(pos, 1.0);')

    geom.add_uniform('mat4 PX', '_projectionXMatrix')
    geom.add_uniform('mat4 PY', '_projectionYMatrix')
    geom.add_uniform('mat4 PZ', '_projectionZMatrix')

    #geom.add_out('vec2 geom_texuv')
    geom.add_out('flat int geom_axis')
    geom.add_out('vec4 geom_lampPos')

    geom.write('vec3 p1 = gl_in[1].gl_Position.xyz - gl_in[0].gl_Position.xyz;')
    geom.write('vec3 p2 = gl_in[2].gl_Position.xyz - gl_in[0].gl_Position.xyz;')
    geom.write('vec3 absnor = abs(normalize(cross(p1, p2)));')
    
    geom.write('mat4 P; // Dominant axis')
    geom.write('if (absnor.x >= absnor.y && absnor.x >= absnor.z) {')
    geom.write('    geom_axis = 1;')
    geom.write('    P = PX;')
    geom.write('}')
    geom.write('else if (absnor.y >= absnor.x && absnor.y >= absnor.z) {')
    geom.write('    geom_axis = 2;')
    geom.write('    P = PY;')
    geom.write('}')
    geom.write('else {')
    geom.write('    geom_axis = 3;')
    geom.write('    P = PZ;')
    geom.write('}')

    geom.write('for (int i = 0; i < gl_in.length(); i++) {')
    geom.write('    vec3 middlePos = gl_in[0].gl_Position.xyz / 3.0 + gl_in[1].gl_Position.xyz / 3.0 + gl_in[2].gl_Position.xyz / 3.0;')
    #geom.write('    geom_texuv = texuv[i];')
    geom.write('    geom_lampPos = lampPos[i];')
    geom.write('    gl_Position = P * gl_in[i].gl_Position;')
    geom.write('    EmitVertex();')
    geom.write('}')
    geom.write('EndPrimitive();')

    frag.write_header('#extension GL_ARB_shader_image_load_store : enable')
    
    frag.add_uniform('layout(RGBA8) image3D voxels')
    #frag.add_uniform('sampler2D sbase')
    #frag.add_uniform('vec4 baseCol')
    #frag.add_uniform('sampler2D shadowMap')

    frag.write('const int voxelDimensions = 128;')


    frag.write('vec3 basecol;')
    frag.write('float roughness;')
    frag.write('float metallic;')
    frag.write('float occlusion;')
    cycles.parse(mat_state.nodes, vert, frag, geom, tesc, tese, parse_opacity=False, parse_displacement=False)
    frag.write('vec4 matCol = vec4(basecol, 1.0);')

    # vec3 lampPos = geom_lampPos.xyz / geom_lampPos.w;
    # lampPos.xy = lampPos.xy * 0.5 + 0.5;
    # float distanceFromLight = texture(shadowMap, lampPos.xy).r * 2.0 - 1.0;
    # const float shadowsBias = 0.0001;
    # float visibility = float(distanceFromLight > lampPos.z - shadowsBias);
    frag.write('float visibility = 1.0;')

    frag.write('ivec3 camPos = ivec3(gl_FragCoord.x, gl_FragCoord.y, voxelDimensions * gl_FragCoord.z);')
    frag.write('ivec3 texPos;')
    frag.write('if (geom_axis == 1) {')
    frag.write('    texPos.x = voxelDimensions - camPos.z;')
    frag.write('    texPos.z = camPos.x;')
    frag.write('    texPos.y = camPos.y;')
    frag.write('}')
    frag.write('else if (geom_axis == 2) {')
    frag.write('    texPos.z = camPos.y;')
    frag.write('    texPos.y = voxelDimensions - camPos.z;')
    frag.write('    texPos.x = camPos.x;')
    frag.write('}')
    frag.write('else {')
    frag.write('    texPos = camPos;')
    frag.write('}')
    frag.write('texPos.z = voxelDimensions - texPos.z - 1;')
    frag.write('imageStore(voxels, texPos, vec4(matCol.rgb * visibility, 1.0));')

    return con_voxel
