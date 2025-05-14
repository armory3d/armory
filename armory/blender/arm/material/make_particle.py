import arm.log
import arm.utils
import arm.material.mat_state as mat_state
import bpy

if arm.is_reload(__name__):
    arm.utils = arm.reload_module(arm.utils)
    mat_state = arm.reload_module(mat_state)
else:
    arm.enable_reload(__name__)


def write(vert, particle_info=None, shadowmap=False):
    ramp_el_len = 0

    # TODO: get the proper psettings from current system
    # Getting closer...
    for obj in bpy.data.objects:
        for psys in obj.particle_systems:
            psettings = psys.settings

            if psettings.instance_object:
                for mat_slot in psettings.instance_object.material_slots:
                    arm.log.debug("instanced object mat_name: " + mat_slot.material.name)

            if psettings.texture_slots:
                for tex_slot in psettings.texture_slots:
                    if tex_slot and tex_slot.texture and tex_slot.texture.use_color_ramp:
                        if tex_slot.texture.color_ramp and tex_slot.texture.color_ramp.elements:
                            ramp_el_len = len(tex_slot.texture.color_ramp.elements.items())

    arm.log.debug("vert mat_name: " + str(vert.context.matname))

    # HINT: maybe the particle system can be reached by accessing the vert->material

    # Outs
    out_index = True if particle_info != None and particle_info['index'] else False
    out_age = True if particle_info != None and particle_info['age'] else False
    out_lifetime = True if particle_info != None and particle_info['lifetime'] else False
    out_location = True if particle_info != None and particle_info['location'] else False
    out_size = True if particle_info != None and particle_info['size'] else False
    out_velocity = True if particle_info != None and particle_info['velocity'] else False
    out_angular_velocity = True if particle_info != None and particle_info['angular_velocity'] else False

    vert.add_uniform('mat4 pd', '_particleData')

    if (ramp_el_len != 0):
        vert.add_uniform('float p_size_factor', '_particleRampSizeFactor')
        # TODO: use data from Python creating constants, instead of creating uniforms from Haxe ?
        vert.add_uniform(f'float p_ramp_positions[{ramp_el_len}]', '_particleRampPositions')
        vert.add_uniform(f'float p_ramp_colors[{ramp_el_len}]', '_particleRampColors')

    str_tex_hash = "float fhash(float n) { return fract(sin(n) * 43758.5453); }\n"
    vert.add_function(str_tex_hash)

    # TODO: do the for loop in python then generate hardcoded blocks in the vertex shader ?
    if (ramp_el_len != 0):
        str_tex_ramp_scale = f"""float get_ramp_scale(float age) {{
            for (int i = 0; i < {ramp_el_len} - 1; ++i) {{
                float pos_a = p_ramp_positions[i];
                float pos_b = p_ramp_positions[i + 1];

                if (age >= pos_a && age <= pos_b) {{
                    float t = (age - pos_a) / (pos_b - pos_a);
                    float scale_a = p_ramp_colors[i];
                    float scale_b = p_ramp_colors[i + 1];
                    return mix(scale_a, scale_b, t);
                }}
            }}

            return p_ramp_colors[{ramp_el_len} - 1];
        }}
        """
        vert.add_function(str_tex_ramp_scale)

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

    if (ramp_el_len != 0):
        vert.write('float n_age = clamp(p_age / p_lifetime, 0.0, 1.0);')
        vert.write('spos.xyz *= get_ramp_scale(n_age);')

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
        vert.add_out('float p_index')
        vert.write('p_index = gl_InstanceID;')

def write_tilesheet(vert):
    # tilesx, tilesy, framerate - pd[3][0], pd[3][1], pd[3][2]
    vert.write('int frame = int((p_age) / pd[3][2]);')
    vert.write('int tx = frame % int(pd[3][0]);')
    vert.write('int ty = int(frame / pd[3][0]);')
    vert.write('vec2 tilesheetOffset = vec2(tx * (1 / pd[3][0]), ty * (1 / pd[3][1]));')
    vert.write('texCoord = tex * texUnpack + tilesheetOffset;')
    # vert.write('texCoord = tex;')
