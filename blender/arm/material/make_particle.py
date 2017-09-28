
def write(vert):

    vert.add_uniform('mat4 pd', '_particleData')

    str_tex_hash = "float fhash(float n) { return fract(sin(n) * 43758.5453); }"
    vert.add_function(str_tex_hash)
    
    # var ptime = (count - p.i) * spawnRate;
    vert.write('float ptime = (pd[0][0] - gl_InstanceID) * pd[0][1];')
    # ptime -= ptime * fhash(i) * r.lifetime_random;
    vert.write('ptime -= ptime * fhash(gl_InstanceID) * pd[2][3];')

    # lifetime
    # todo: properly discard
    vert.write('if (gl_InstanceID > pd[0][0] || ptime < 0 || ptime > pd[0][2]) { spos.x = spos.y = spos.z = -99999; }')

    vert.write('ptime /= 2;')
    
    # object_align_factor / 2 + gxyz
    vert.write('vec3 ppos = vec3(pd[1][0], pd[1][1], pd[1][2]);')

    # factor_random = pd[1][3]
    # p.i = gl_InstanceID
    # particles.length = pd[0][3]
    vert.write('ppos.x += fhash(gl_InstanceID)                * pd[1][3] - pd[1][3] / 2;')
    vert.write('ppos.y += fhash(gl_InstanceID +     pd[0][3]) * pd[1][3] - pd[1][3] / 2;')
    vert.write('ppos.z += fhash(gl_InstanceID + 2 * pd[0][3]) * pd[1][3] - pd[1][3] / 2;')

    # gxyz
    vert.write('ppos.x += (pd[2][0] * ptime) / 5;')
    vert.write('ppos.y += (pd[2][1] * ptime) / 5;')
    vert.write('ppos.z += (pd[2][2] * ptime) / 5;')

    vert.write('ppos.x *= ptime;')
    vert.write('ppos.y *= ptime;')
    vert.write('ppos.z *= ptime;')

    vert.write('spos.xyz += ppos;')

def write_tilesheet(vert):
    # tilesx, tilesy, framerate - pd[3][0], pd[3][1], pd[3][2]
    vert.write('int frame = int((ptime / 2) / pd[3][2]);')
    vert.write('int tx = frame % int(pd[3][0]);')
    vert.write('int ty = int(frame / pd[3][0]);')
    vert.write('vec2 tilesheetOffset = vec2(tx * (1 / pd[3][0]), ty * (1 / pd[3][1]));')
    vert.write('texCoord = tex + tilesheetOffset;')
    # vert.write('texCoord = tex;')
