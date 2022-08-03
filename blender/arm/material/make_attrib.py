from typing import Optional

import arm.material.cycles as cycles
import arm.material.mat_state as mat_state
import arm.material.make_skin as make_skin
import arm.material.make_particle as make_particle
import arm.material.make_inst as make_inst
import arm.material.make_tess as make_tess
import arm.material.make_morph_target as make_morph_target
from arm.material.shader import Shader, ShaderContext
import arm.utils

if arm.is_reload(__name__):
    cycles = arm.reload_module(cycles)
    mat_state = arm.reload_module(mat_state)
    make_skin = arm.reload_module(make_skin)
    make_particle = arm.reload_module(make_particle)
    make_inst = arm.reload_module(make_inst)
    make_tess = arm.reload_module(make_tess)
    make_morph_target = arm.reload_module(make_morph_target)
    arm.material.shader = arm.reload_module(arm.material.shader)
    from arm.material.shader import Shader, ShaderContext
    arm.utils = arm.reload_module(arm.utils)
else:
    arm.enable_reload(__name__)


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


def write_norpos(con_mesh: ShaderContext, vert: Shader, declare=False, write_nor=True):
    is_bone = con_mesh.is_elem('bone')
    is_morph = con_mesh.is_elem('morph')
    if is_morph:
        make_morph_target.morph_pos(vert)
    if is_bone:
        make_skin.skin_pos(vert)
    if write_nor:
        prep = 'vec3 ' if declare else ''
        if is_morph:
            make_morph_target.morph_nor(vert, is_bone, prep)
        if is_bone:
            make_skin.skin_nor(vert, is_morph, prep)
        if not is_morph and not is_bone:
            vert.write_attrib(prep + 'wnormal = normalize(N * vec3(nor.xy, pos.w));')
    if con_mesh.is_elem('ipos'):
        make_inst.inst_pos(con_mesh, vert)


def write_tex_coords(con_mesh: ShaderContext, vert: Shader, frag: Shader, tese: Optional[Shader]):
    rpdat = arm.utils.get_rp()

    if con_mesh.is_elem('tex'):
        vert.add_out('vec2 texCoord')
        vert.add_uniform('float texUnpack', link='_texUnpack')
        if mat_state.material.arm_tilesheet_flag:
            if mat_state.material.arm_particle_flag and rpdat.arm_particles == 'On':
                make_particle.write_tilesheet(vert)
            else:
                vert.add_uniform('vec2 tilesheetOffset', '_tilesheetOffset')
                vert.write_attrib('texCoord = tex * texUnpack + tilesheetOffset;')
        else:
            vert.write_attrib('texCoord = tex * texUnpack;')

        if tese is not None:
            tese.write_pre = True
            make_tess.interpolate(tese, 'texCoord', 2, declare_out=frag.contains('texCoord'))
            tese.write_pre = False

    if con_mesh.is_elem('tex1'):
        vert.add_out('vec2 texCoord1')
        vert.add_uniform('float texUnpack', link='_texUnpack')
        vert.write_attrib('texCoord1 = tex1 * texUnpack;')
        if tese is not None:
            tese.write_pre = True
            make_tess.interpolate(tese, 'texCoord1', 2, declare_out=frag.contains('texCoord1'))
            tese.write_pre = False
