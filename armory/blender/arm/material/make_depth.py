import bpy

import arm.material.cycles as cycles
import arm.material.mat_state as mat_state
import arm.material.mat_utils as mat_utils
import arm.material.make_skin as make_skin
import arm.material.make_inst as make_inst
import arm.material.make_tess as make_tess
import arm.material.make_mesh as make_mesh
import arm.material.make_attrib as make_attrib
import arm.material.make_particle as make_particle
import arm.material.make_finalize as make_finalize
import arm.material.make_morph_target as make_morph_target
import arm.assets as assets
import arm.utils

if arm.is_reload(__name__):
    cycles = arm.reload_module(cycles)
    mat_state = arm.reload_module(mat_state)
    mat_utils = arm.reload_module(mat_utils)
    make_skin = arm.reload_module(make_skin)
    make_inst = arm.reload_module(make_inst)
    make_tess = arm.reload_module(make_tess)
    make_particle = arm.reload_module(make_particle)
    make_finalize = arm.reload_module(make_finalize)
    assets = arm.reload_module(assets)
    arm.utils = arm.reload_module(arm.utils)
else:
    arm.enable_reload(__name__)


def make(context_id, rpasses, shadowmap=False, shadowmap_transparent=False):

    is_disp = mat_utils.disp_linked(mat_state.output_node)

    vs = [{'name': 'pos', 'data': 'short4norm'}]
    if is_disp or shadowmap_transparent:
        vs.append({'name': 'nor', 'data': 'short2norm'})

    if shadowmap_transparent:
        con_depth = mat_state.data.add_context({
            'name': context_id,
            'vertex_elements': vs,
            'depth_write': False,
            'depth_read': True,
            'compare_mode': 'less',
            'cull_mode': 'clockwise',
            'blend_source': 'blend_zero',
            'blend_destination': 'source_color',
            'blend_operation': 'add',
            'color_writes_red': [True],
            'color_writes_green': [True],
            'color_writes_blue': [True],
            'color_writes_alpha': [True]
        })
    else:
        con_depth = mat_state.data.add_context({
            'name': context_id,
            'vertex_elements': vs,
            'depth_write': True,
            'depth_read': False,
            'compare_mode': 'less',
            'cull_mode': 'clockwise',
            'color_writes_red': [False],
            'color_writes_green': [False],
            'color_writes_blue': [False],
            'color_writes_alpha': [False]
        })

    vert = con_depth.make_vert()
    frag = con_depth.make_frag()
    geom = None
    tesc = None
    tese = None

    vert.write_attrib('vec4 spos = vec4(pos.xyz, 1.0);')
    vert.add_include('compiled.inc')
    frag.add_include('compiled.inc')

    parse_opacity = 'translucent' in rpasses or 'refraction' in rpasses or mat_state.material.arm_discard

    parse_custom_particle = (cycles.node_by_name(mat_state.nodes, 'ArmCustomParticleNode') is not None)

    if shadowmap_transparent:
        billboard = mat_state.material.arm_billboard
        if billboard == 'spherical':
            vert.add_uniform('mat3 N', '_normalMatrixSphere')
        elif billboard == 'cylindrical':
            vert.add_uniform('mat3 N', '_normalMatrixCylinder')
        else:
            vert.add_uniform('mat3 N', '_normalMatrix')
        make_mesh._write_material_attribs_default(frag, parse_opacity) #TODO remove duplicate parsing
        vert.add_out('vec3 wnormal')
        make_attrib.write_norpos(con_depth, vert)
        frag.write_attrib('vec3 n = normalize(wnormal);')
        cycles.parse(mat_state.nodes, con_depth, vert, frag, geom, tesc, tese, basecol_only=True, parse_opacity=True)
    elif parse_opacity:
        frag.write('float opacity;')
        frag.write('float ior;')
    if(con_depth).is_elem('morph'):
        make_morph_target.morph_pos(vert)

    if con_depth.is_elem('bone'):
        make_skin.skin_pos(vert)

    if (not is_disp and parse_custom_particle):
        cycles.parse(mat_state.nodes, con_depth, vert, frag, geom, tesc, tese, parse_surface=False, parse_opacity=parse_opacity)

    if con_depth.is_elem('ipos'):
        make_inst.inst_pos(con_depth, vert)

    rpdat = arm.utils.get_rp()
    if mat_state.material.arm_particle_flag and rpdat.arm_particles == 'On':
        make_particle.write(vert, shadowmap=shadowmap)

    if is_disp:
        if rpdat.arm_rp_displacement == 'Vertex':
            frag.ins = vert.outs
            vert.add_uniform('mat3 N', '_normalMatrix')
            vert.write('vec3 wnormal = normalize(N * vec3(nor.xy, pos.w));')
            if(con_depth.is_elem('ipos')):
                vert.write('wposition = vec4(W * spos).xyz;')
                if(con_depth.is_elem('irot')):
                    vert.write('wnormal = normalize(N * mirot * vec3(nor.xy, pos.w));')
            if not shadowmap_transparent:
                cycles.parse(mat_state.nodes, con_depth, vert, frag, geom, tesc, tese, parse_surface=False, parse_opacity=parse_opacity)
            if con_depth.is_elem('tex'):
                vert.add_out('vec2 texCoord') ## vs only, remove out
                vert.add_uniform('float texUnpack', link='_texUnpack')
                vert.write_attrib('texCoord = tex * texUnpack;')
            if con_depth.is_elem('tex1'):
                vert.add_out('vec2 texCoord1') ## vs only, remove out
                vert.add_uniform('float texUnpack', link='_texUnpack')
                vert.write_attrib('texCoord1 = tex1 * texUnpack;')
            if con_depth.is_elem('col'):
                vert.add_out('vec3 vcolor')
                vert.write_attrib('vcolor = col.rgb;')
            vert.write('wposition += wnormal * disp;')
            if shadowmap:
                vert.add_uniform('mat4 LVP', '_lightViewProjectionMatrix')
                vert.write('gl_Position = LVP * vec4(wposition, 1.0);')
            else:
                vert.add_uniform('mat4 VP', '_viewProjectionMatrix')
                vert.write('gl_Position = VP * vec4(wposition, 1.0);')

        else: # Tessellation
            tesc = con_depth.make_tesc()
            tese = con_depth.make_tese()
            tesc.ins = vert.outs
            tese.ins = tesc.outs
            frag.ins = tese.outs

            vert.add_out('vec3 wnormal')
            vert.add_uniform('mat3 N', '_normalMatrix')
            vert.write('wnormal = normalize(N * vec3(nor.xy, pos.w));')

            make_tess.tesc_levels(tesc, rpdat.arm_tess_shadows_inner, rpdat.arm_tess_shadows_outer)
            make_tess.interpolate(tese, 'wposition', 3)
            make_tess.interpolate(tese, 'wnormal', 3, normalize=True)

            if not shadowmap_transparent:
                cycles.parse(mat_state.nodes, con_depth, vert, frag, geom, tesc, tese, parse_surface=False, parse_opacity=parse_opacity)

            if con_depth.is_elem('tex'):
                vert.add_out('vec2 texCoord')
                vert.add_uniform('float texUnpack', link='_texUnpack')
                vert.write('texCoord = tex * texUnpack;')
                tese.write_pre = True
                make_tess.interpolate(tese, 'texCoord', 2, declare_out=frag.contains('texCoord'))
                tese.write_pre = False

            if con_depth.is_elem('tex1'):
                vert.add_out('vec2 texCoord1')
                vert.write('texCoord1 = tex1;')
                tese.write_pre = True
                make_tess.interpolate(tese, 'texCoord1', 2, declare_out=frag.contains('texCoord1'))
                tese.write_pre = False

            if con_depth.is_elem('col'):
                vert.add_out('vec3 vcolor')
                vert.write('vcolor = col.rgb;')
                tese.write_pre = True
                make_tess.interpolate(tese, 'vcolor', 3, declare_out=frag.contains('vcolor'))
                tese.write_pre = False

            if shadowmap:
                tese.add_uniform('mat4 LVP', '_lightViewProjectionMatrix')
                tese.write('wposition += wnormal * disp;')
                tese.write('gl_Position = LVP * vec4(wposition, 1.0);')
            else:
                tese.add_uniform('mat4 VP', '_viewProjectionMatrix')
                tese.write('wposition += wnormal * disp;')
                tese.write('gl_Position = VP * vec4(wposition, 1.0);')
    # No displacement
    else:
        frag.ins = vert.outs
        billboard = mat_state.material.arm_billboard
        if shadowmap:
            if billboard == 'spherical':
                vert.add_uniform('mat4 LWVP', '_lightWorldViewProjectionMatrixSphere')
            elif billboard == 'cylindrical':
                vert.add_uniform('mat4 LWVP', '_lightWorldViewProjectionMatrixCylinder')
            else: # off
                vert.add_uniform('mat4 LWVP', '_lightWorldViewProjectionMatrix')
            vert.write('gl_Position = LWVP * spos;')
        else:
            if billboard == 'spherical':
                vert.add_uniform('mat4 WVP', '_worldViewProjectionMatrixSphere')
            elif billboard == 'cylindrical':
                vert.add_uniform('mat4 WVP', '_worldViewProjectionMatrixCylinder')
            else: # off
                vert.add_uniform('mat4 WVP', '_worldViewProjectionMatrix')
            vert.write('gl_Position = WVP * spos;')

        if parse_opacity:
            if not parse_custom_particle and not shadowmap_transparent:
                cycles.parse(mat_state.nodes, con_depth, vert, frag, geom, tesc, tese, parse_surface=False, parse_opacity=True)

            if con_depth.is_elem('tex'):
                vert.add_out('vec2 texCoord')
                vert.add_uniform('float texUnpack', link='_texUnpack')
                if mat_state.material.arm_tilesheet_flag:
                    vert.add_uniform('vec2 tilesheetOffset', '_tilesheetOffset')
                    vert.write('texCoord = tex * texUnpack + tilesheetOffset;')
                else:
                    vert.write('texCoord = tex * texUnpack;')

            if con_depth.is_elem('tex1'):
                vert.add_out('vec2 texCoord1')
                vert.write('texCoord1 = tex1;')

            if con_depth.is_elem('col'):
                vert.add_out('vec3 vcolor')
                vert.write('vcolor = col.rgb;')

    if shadowmap_transparent:
        frag.add_out('vec4 fragColor')
        vert.add_out('vec4 wvpposition')
        vert.write('wvpposition = gl_Position;')
        frag.write('float depth = (wvpposition.z / wvpposition.w) * 0.5 + 0.5;')
        frag.write('vec3 color = basecol;')
        frag.write('color *= 1.0 - opacity;')
        frag.write('fragColor = vec4(color, depth);')

    if parse_opacity and not shadowmap_transparent:
        if mat_state.material.arm_discard:
            opac = mat_state.material.arm_discard_opacity_shadows
        else:
            opac = '1.0'
        frag.write('if (opacity < {0}) discard;'.format(opac))

    make_finalize.make(con_depth)

    assets.vs_equal(con_depth, assets.shader_cons['depth_vert'])
    assets.fs_equal(con_depth, assets.shader_cons['depth_frag'])

    return con_depth
