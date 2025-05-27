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

    ramp_positions = []
    ramp_colors_b = []
    size_over_time_factor = 0

    use_rotations = False
    rotation_mode = 'NONE'
    rotation_factor_random = 0
    phase_factor = 0
    phase_factor_random = 0

    for obj in bpy.data.objects:
        for psys in obj.particle_systems:
            psettings = psys.settings

            if psettings.instance_object:
                if psettings.instance_object.active_material:
                    # FIXME: Different particle systems may share the same particle object. This ideally should check the correct `ParticleSystem` using an id or name in the particle's object material.
                    if psettings.instance_object.active_material.name.replace(".", "_") == vert.context.matname:
                        # Rotation data
                        use_rotations = psettings.use_rotations
                        rotation_mode = psettings.rotation_mode
                        rotation_factor_random = psettings.rotation_factor_random
                        phase_factor = psettings.phase_factor
                        phase_factor_random = psettings.phase_factor_random

                        # Texture slots data
                        if psettings.texture_slots and len(psettings.texture_slots.items()) != 0:
                            for tex_slot in psettings.texture_slots:
                                if not tex_slot: break
                                if not tex_slot.use_map_size: break # TODO: check also for other influences
                                if tex_slot.texture and tex_slot.texture.use_color_ramp:
                                    if tex_slot.texture.color_ramp and tex_slot.texture.color_ramp.elements:
                                        ramp_el_len = len(tex_slot.texture.color_ramp.elements.items())
                                        for element in tex_slot.texture.color_ramp.elements:
                                            ramp_positions.append(element.position)
                                            ramp_colors_b.append(element.color[2])
                                        size_over_time_factor = tex_slot.size_factor
                                        break

    # Outs
    out_index = True if particle_info != None and particle_info['index'] else False
    out_age = True if particle_info != None and particle_info['age'] else False
    out_lifetime = True if particle_info != None and particle_info['lifetime'] else False
    out_location = True if particle_info != None and particle_info['location'] else False
    out_size = True if particle_info != None and particle_info['size'] else False
    out_velocity = True if particle_info != None and particle_info['velocity'] else False
    out_angular_velocity = True if particle_info != None and particle_info['angular_velocity'] else False

    # Force Armory to create a new shader per material ID
    vert.write(f'#ifdef PARTICLE_ID_{vert.context.material.arm_material_id}')
    vert.write('#endif')

    vert.add_uniform('mat4 pd', '_particleData')
    vert.add_uniform('float pd_size_random', '_particleSizeRandom')
    vert.add_uniform('float pd_random', '_particleRandom')
    vert.add_uniform('float pd_size', '_particleSize')

    if ramp_el_len != 0:
        vert.add_const('float', 'P_SIZE_OVER_TIME_FACTOR', str(size_over_time_factor))
        for i in range(ramp_el_len):
            vert.add_const('float', f'P_RAMP_POSITION_{i}', str(ramp_positions[i]))
            vert.add_const('float', f'P_RAMP_COLOR_B_{i}', str(ramp_colors_b[i]))

    str_tex_hash = "float fhash(float n) { return fract(sin(n) * 43758.5453); }\n"
    vert.add_function(str_tex_hash)

    if (ramp_el_len != 0):
        str_ramp_scale = "float get_ramp_scale(float age) {\n"

        for i in range(ramp_el_len):
            if i == 0:
                str_ramp_scale += f"if (age <= P_RAMP_POSITION_{i + 1})"
            elif i == ramp_el_len - 1:
                str_ramp_scale += f"return P_RAMP_COLOR_B_{ramp_el_len - 1};"
                break
            else:
                str_ramp_scale += f"else if (age <= P_RAMP_POSITION_{i + 1})"
            str_ramp_scale += f""" {{
                float t = (age - P_RAMP_POSITION_{i}) / (P_RAMP_POSITION_{i + 1} - P_RAMP_POSITION_{i});
                return mix(P_RAMP_COLOR_B_{i}, P_RAMP_COLOR_B_{i + 1}, t);
            }}
            """

        str_ramp_scale += "}\n"
        vert.add_function(str_ramp_scale)

    prep = 'float '
    if out_age:
        prep = ''
        vert.add_out('float p_age')
    # var p_age = lapTime - p.i * spawnRate
    vert.write(prep + 'p_age = pd[3][3] - gl_InstanceID * pd[0][1];')

    # Loop
    # pd[0][0] - animtime, loop stored in sign
    # vert.write('while (p_age < 0) p_age += pd[0][0];')
    vert.write('if (pd[0][0] > 0 && p_age < 0) p_age += (int(-p_age / pd[0][0]) + 1) * pd[0][0];')

    # lifetime
    prep = 'float '
    if out_lifetime:
        prep = ''
        vert.add_out('float p_lifetime')
    vert.write(prep + 'p_lifetime = pd[0][2] * (1 - (fhash(gl_InstanceID + 4 * pd[0][3] + pd_random) * pd[2][3]));')
    # clip with nan
    vert.write('if (p_age < 0 || p_age > p_lifetime) {')
    vert.write('    gl_Position /= 0.0;')
    vert.write('    return;')
    vert.write('}')

    if (ramp_el_len != 0):
        vert.write('float n_age = clamp(p_age / p_lifetime, 0.0, 1.0);')
        vert.write(f'spos.xyz *= 1 + (get_ramp_scale(n_age) - 1) * {size_over_time_factor};')
    vert.write('spos.xyz *= 1 - (fhash(gl_InstanceID + 3 * pd[0][3] + pd_random) * pd_size_random);')

    # vert.write('p_age /= 2;') # Match

    # object_align_factor / 2 + gxyz
    prep = 'vec3 '
    if out_velocity:
        prep = ''
        vert.add_out('vec3 p_velocity')
    vert.write(prep + 'p_velocity = vec3(pd[1][0] * (1 / pd_size), pd[1][1] * (1 / pd_size), pd[1][2] * (1 / pd_size));')

    vert.write('p_velocity.x += (fhash(gl_InstanceID + pd_random)                * 2.0 / pd_size - 1.0 / pd_size) * pd[1][3];')
    vert.write('p_velocity.y += (fhash(gl_InstanceID + pd_random +     pd[0][3]) * 2.0 / pd_size - 1.0 / pd_size) * pd[1][3];')
    vert.write('p_velocity.z += (fhash(gl_InstanceID + pd_random + 2 * pd[0][3]) * 2.0 / pd_size - 1.0 / pd_size) * pd[1][3];')

    # factor_random = pd[1][3]
    # p.i = gl_InstanceID
    # particles.length = pd[0][3]

    # gxyz
    vert.write('p_velocity.x += (pd[2][0] / (2 * pd_size)) * p_age;')
    vert.write('p_velocity.y += (pd[2][1] / (2 * pd_size)) * p_age;')
    vert.write('p_velocity.z += (pd[2][2] / (2 * pd_size)) * p_age;')

    prep = 'vec3 '
    if out_location:
        prep = ''
        vert.add_out('vec3 p_location')
    vert.write(prep + 'p_location = p_velocity * p_age;')

    vert.write('spos.xyz += p_location;')

    # Rotation
    if use_rotations:
        if rotation_mode != 'NONE':
            vert.write(f'float p_angle = ({phase_factor} + (fhash(gl_InstanceID + pd_random + 5 * pd[0][3])) * {phase_factor_random});')
            vert.write('p_angle *= 3.141592;')
            vert.write('float c = cos(p_angle);')
            vert.write('float s = sin(p_angle);')
            vert.write('vec3 center = spos.xyz - p_location;')

            match rotation_mode:
                case 'OB_X':
                    vert.write('vec3 rz = vec3(center.y, -center.x, center.z);')
                    vert.write('vec2 rotation = vec2(rz.y * c - rz.z * s, rz.y * s + rz.z * c);')
                    vert.write('spos.xyz = vec3(rz.x, rotation.x, rotation.y) + p_location;')

                    if (not shadowmap):
                        vert.write('wnormal = vec3(wnormal.y, -wnormal.x, wnormal.z);')
                        vert.write('vec2 n_rot = vec2(wnormal.y * c - wnormal.z * s, wnormal.y * s + wnormal.z * c);')
                        vert.write('wnormal = normalize(vec3(wnormal.x, n_rot.x, n_rot.y));')
                case 'OB_Y':
                    vert.write('vec2 rotation = vec2(center.x * c + center.z * s, -center.x * s + center.z * c);')
                    vert.write('spos.xyz = vec3(rotation.x, center.y, rotation.y) + p_location;')

                    if (not shadowmap):
                        vert.write('wnormal = normalize(vec3(wnormal.x * c + wnormal.z * s, wnormal.y, -wnormal.x * s + wnormal.z * c));')
                case 'OB_Z':
                    vert.write('vec3 rz = vec3(center.y, -center.x, center.z);')
                    vert.write('vec3 ry = vec3(-rz.z, rz.y, rz.x);')
                    vert.write('vec2 rotation = vec2(ry.x * c - ry.y * s, ry.x * s + ry.y * c);')
                    vert.write('spos.xyz = vec3(rotation.x, rotation.y, ry.z) + p_location;')

                    if (not shadowmap):
                        vert.write('wnormal = vec3(wnormal.y, -wnormal.x, wnormal.z);')
                        vert.write('wnormal = vec3(-wnormal.z, wnormal.y, wnormal.x);')
                        vert.write('vec2 n_rot = vec2(wnormal.x * c - wnormal.y * s, wnormal.x * s + wnormal.y * c);')
                        vert.write('wnormal = normalize(vec3(n_rot.x, n_rot.y, wnormal.z));')
                case 'VEL':
                    vert.write('vec3 forward = -normalize(p_velocity);')
                    vert.write('if (length(forward) > 1e-5) {')
                    vert.write('vec3 world_up = vec3(0.0, 0.0, 1.0);')

                    vert.write('if (abs(dot(forward, world_up)) > 0.999) {')
                    vert.write('world_up = vec3(-1.0, 0.0, 0.0);')
                    vert.write('}')

                    vert.write('vec3 right = cross(world_up, forward);')
                    vert.write('if (length(right) < 1e-5) {')
                    vert.write('forward = -forward;')
                    vert.write('right = cross(world_up, forward);')
                    vert.write('}')
                    vert.write('right = normalize(right);')
                    vert.write('vec3 up = normalize(cross(forward, right));')

                    vert.write('mat3 rot = mat3(right, -forward, up);')
                    vert.write('mat3 phase = mat3(vec3(c, 0.0, -s), vec3(0.0, 1.0, 0.0), vec3(s, 0.0, c));')
                    vert.write('mat3 final_rot = rot * phase;')
                    vert.write('spos.xyz = final_rot * center + p_location;')

                    if (not shadowmap):
                        vert.write('wnormal = normalize(final_rot * wnormal);')
                    vert.write('}')

            if rotation_factor_random != 0:
                str_rotate_around = '''vec3 rotate_around(vec3 v, vec3 angle) {
                    // Rotate around X
                    float cx = cos(angle.x);
                    float sx = sin(angle.x);
                    v = vec3(v.x, v.y * cx - v.z * sx, v.y * sx + v.z * cx);

                    // Rotate around Y
                    float cy = cos(angle.y);
                    float sy = sin(angle.y);
                    v = vec3(v.x * cy + v.z * sy, v.y, -v.x * sy + v.z * cy);

                    // Rotate around Z
                    float cz = cos(angle.z);
                    float sz = sin(angle.z);
                    v = vec3(v.x * cz - v.y * sz, v.x * sz + v.y * cz, v.z);

                    return v;
                }'''
                vert.add_function(str_rotate_around)

                vert.write(f'''vec3 r_angle = vec3((fhash(gl_InstanceID + pd_random + 6 * pd[0][3]) * 4 - 2) * {rotation_factor_random},
                           (fhash(gl_InstanceID + pd_random + 7 * pd[0][3]) * 4 - 2) * {rotation_factor_random},
                           (fhash(gl_InstanceID + pd_random + 8 * pd[0][3]) * 4 - 2) * {rotation_factor_random});''')
                vert.write('vec3 r_center = spos.xyz - p_location;')
                vert.write('r_center = rotate_around(r_center, r_angle);')
                vert.write('spos.xyz = r_center + p_location;')

                if not shadowmap:
                    vert.write('wnormal = normalize(rotate_around(wnormal, r_angle));')

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
