import arm.material.mat_state as mat_state
import arm.material.make_skin as make_skin
import arm.material.make_particle as make_particle
import arm.material.make_inst as make_inst
import arm.utils
import arm.material.cycles as cycles

def write_vertpos(vert):
    billboard = mat_state.material.arm_billboard
    particle = mat_state.material.arm_particle_flag
    # Particles
    if particle:
        if arm.utils.get_rp().arm_particles == 'On':
            make_particle.write(vert, particle_info=cycles.particle_info)
        # Billboards
        if billboard == 'spherical':
            vert.add_uniform('mat4 WV', '_worldViewMatrix')
            vert.add_uniform('mat4 P', '_projectionMatrix')
            vert.write('gl_Position = P * (WV * vec4(0.0, 0.0, spos.z, 1.0) + vec4(spos.x, spos.y, 0.0, 0.0));')
        else:
            vert.add_uniform('mat4 WVP', '_worldViewProjectionMatrix')
            vert.write('gl_Position = WVP * spos;')
    else:
        # Billboards
        if billboard == 'spherical':
            vert.add_uniform('mat4 WVP', '_worldViewProjectionMatrixSphere')
        elif billboard == 'cylindrical':
            vert.add_uniform('mat4 WVP', '_worldViewProjectionMatrixCylinder')
        else: # off
            vert.add_uniform('mat4 WVP', '_worldViewProjectionMatrix')
        vert.write('gl_Position = WVP * spos;')

def write_norpos(con_mesh, vert, declare=False, write_nor=True):
    prep = ''
    if declare:
        prep = 'vec3 '
    vert.write_pre = True
    is_bone = con_mesh.is_elem('bone')
    if is_bone:
        make_skin.skin_pos(vert)
    if write_nor:
        if is_bone:
            make_skin.skin_nor(vert, prep)
        else:
            vert.write(prep + 'wnormal = normalize(N * vec3(nor.xy, pos.w));')
    if con_mesh.is_elem('ipos'):
        make_inst.inst_pos(con_mesh, vert)
    vert.write_pre = False
