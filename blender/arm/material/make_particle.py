
def write(vert):
    vert.add_uniform('mat4 pd', '_particleData')
    vert.write('spos.xyz += offp.xyz;')
    # var ptime = (count - p.i) * spawnRate;
    vert.write('float ptime = (pd[0][0] - offp.w) * pd[0][1];')
    # lifetime
    vert.write('if (offp.w > pd[0][0] || ptime < 0 || ptime > pd[0][2]) { spos.x = spos.y = spos.z = -99999; }')
    vert.write('ptime *= ptime;')
    vert.write('ptime /= 5;')
    # gxyz
    vert.write('spos.x += pd[1][0] * ptime;')
    vert.write('spos.y += pd[1][1] * ptime;')
    vert.write('spos.z += pd[1][2] * ptime;')
