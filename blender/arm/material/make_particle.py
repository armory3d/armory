
def write(vert):
    vert.add_uniform('mat4 pd', '_particleData')

    str_tex_hash = "float fhash(float n) { return fract(sin(n) * 43758.5453); }"
    vert.add_function(str_tex_hash)
    
    # var ptime = (count - p.i) * spawnRate;
    vert.write('float ptime = (pd[0][0] - offp.w) * pd[0][1];')
    # ptime -= ptime * fhash(i) * r.lifetime_random;
    vert.write('ptime -= ptime * fhash(offp.w) * pd[2][3];')

    # lifetime
    vert.write('if (offp.w > pd[0][0] || ptime < 0 || ptime > pd[0][2]) { spos.x = spos.y = spos.z = -99999; }')

    vert.write('ptime /= 2;')

    # volume/face pos
    vert.write('spos.xyz += offp.xyz;')
    
    # object_align_factor / 2 + gxyz
    vert.write('vec3 ppos = vec3(pd[1][0], pd[1][1], pd[1][2]);')

    # factor_random = pd[1][3]
    # p.i = offp.w
    # particles.length = pd[0][3]
    vert.write('ppos.x += fhash(offp.w)                * pd[1][3] - pd[1][3] / 2;')
    vert.write('ppos.y += fhash(offp.w +     pd[0][3]) * pd[1][3] - pd[1][3] / 2;')
    vert.write('ppos.z += fhash(offp.w + 2 * pd[0][3]) * pd[1][3] - pd[1][3] / 2;')

    # gxyz
    vert.write('ppos.x += (pd[2][0] * ptime) / 5;')
    vert.write('ppos.y += (pd[2][1] * ptime) / 5;')
    vert.write('ppos.z += (pd[2][2] * ptime) / 5;')

    vert.write('ppos.x *= ptime;')
    vert.write('ppos.y *= ptime;')
    vert.write('ppos.z *= ptime;')

    vert.write('spos.xyz += ppos;')
