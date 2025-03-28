import arm.utils
import arm.material.mat_state as mat_state

if arm.is_reload(__name__):
    arm.utils = arm.reload_module(arm.utils)
    mat_state = arm.reload_module(mat_state)
else:
    arm.enable_reload(__name__)


def write(vert, particle_info=None, shadowmap=False):

    # Outs
    out_index = True if particle_info != None and particle_info['index'] else False
    out_age = True if particle_info != None and particle_info['age'] else False
    out_lifetime = True if particle_info != None and particle_info['lifetime'] else False
    out_location = True if particle_info != None and particle_info['location'] else False
    out_size = True if particle_info != None and particle_info['size'] else False
    out_velocity = True if particle_info != None and particle_info['velocity'] else False
    out_angular_velocity = True if particle_info != None and particle_info['angular_velocity'] else False

    vert.add_uniform('mat4 pd', '_particleData')

    str_tex_hash = "float fhash(float n) { return fract(sin(n) * 43758.5453); }\n"
    vert.add_function(str_tex_hash)

    prep = 'float '
    if out_age:
        prep = ''
        vert.add_out('float p_age')
    # var p_age = lapTime - p.i * spawnRate
    vert.write(prep + 'p_age = pd[3][3] - gl_InstanceID * pd[0][1];')
    # p_age -= p_age * fhash(i) * r.lifetime_random;
    vert.write('p_age -= p_age * fhash(gl_InstanceID) * pd[2][3];')

    # Loop
    # pd[0][0] - animtime, loop stored in sign
    # vert.write('while (p_age < 0) p_age += pd[0][0];')
    vert.write('if (pd[0][0] > 0 && p_age < 0) p_age += (int(-p_age / pd[0][0]) + 1) * pd[0][0];')

    # lifetime
    prep = 'float '
    if out_lifetime:
        prep = ''
        vert.add_out('float p_lifetime')
    vert.write(prep + 'p_lifetime = pd[0][2];')
    # clip with nan
    vert.write('if (p_age < 0 || p_age > p_lifetime) {')
    vert.write('    gl_Position /= 0.0;')
    vert.write('    return;')
    vert.write('}')

    # vert.write('p_age /= 2;') # Match

    # object_align_factor / 2 + gxyz
    prep = 'vec3 '
    if out_velocity:
        prep = ''
        vert.add_out('vec3 p_velocity')
    vert.write(prep + 'p_velocity = vec3(pd[1][0], pd[1][1], pd[1][2]);')

    vert.write('p_velocity.x += fhash(gl_InstanceID)                * pd[1][3] - pd[1][3] / 2;')
    vert.write('p_velocity.y += fhash(gl_InstanceID +     pd[0][3]) * pd[1][3] - pd[1][3] / 2;')
    vert.write('p_velocity.z += fhash(gl_InstanceID + 2 * pd[0][3]) * pd[1][3] - pd[1][3] / 2;')

    # factor_random = pd[1][3]
    # p.i = gl_InstanceID
    # particles.length = pd[0][3]

    # gxyz
    vert.write('p_velocity.x += (pd[2][0] * p_age) / 5;')
    vert.write('p_velocity.y += (pd[2][1] * p_age) / 5;')
    vert.write('p_velocity.z += (pd[2][2] * p_age) / 5;')

    prep = 'vec3 '
    if out_location:
        prep = ''
        vert.add_out('vec3 p_location')
    vert.write(prep + 'p_location = p_velocity * p_age;')

    vert.write('spos.xyz += p_location;')

    # Particle fade
    if mat_state.material.arm_particle_flag and arm.utils.get_rp().arm_particles == 'On' and mat_state.material.arm_particle_fade:
        vert.add_out('float p_fade')
        vert.write('p_fade = sin(min((p_age / 2) * 3.141592, 3.141592));')

    if out_index:
        vert.add_out('float p_index');
        vert.write('p_index = gl_InstanceID;')

def write_tilesheet(vert):
    # tilesx, tilesy, framerate - pd[3][0], pd[3][1], pd[3][2]
    vert.write('int frame = int((p_age) / pd[3][2]);')
    vert.write('int tx = frame % int(pd[3][0]);')
    vert.write('int ty = int(frame / pd[3][0]);')
    vert.write('vec2 tilesheetOffset = vec2(tx * (1 / pd[3][0]), ty * (1 / pd[3][1]));')
    vert.write('texCoord = tex * texUnpack + tilesheetOffset;')
    # vert.write('texCoord = tex;')
