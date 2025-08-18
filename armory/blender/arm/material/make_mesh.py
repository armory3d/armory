from typing import Any, Callable, Optional

import bpy

import arm.assets as assets
import arm.material.mat_state as mat_state
import arm.material.mat_utils as mat_utils
import arm.material.cycles as cycles
import arm.material.make_tess as make_tess
import arm.material.make_particle as make_particle
import arm.material.make_cluster as make_cluster
import arm.material.make_finalize as make_finalize
import arm.material.make_attrib as make_attrib
import arm.material.shader as shader
import arm.utils

if arm.is_reload(__name__):
    assets = arm.reload_module(assets)
    mat_state = arm.reload_module(mat_state)
    mat_utils = arm.reload_module(mat_utils)
    cycles = arm.reload_module(cycles)
    make_tess = arm.reload_module(make_tess)
    make_particle = arm.reload_module(make_particle)
    make_cluster = arm.reload_module(make_cluster)
    make_finalize = arm.reload_module(make_finalize)
    make_attrib = arm.reload_module(make_attrib)
    shader = arm.reload_module(shader)
    arm.utils = arm.reload_module(arm.utils)
else:
    arm.enable_reload(__name__)

is_displacement = False

# User callbacks
write_material_attribs: Optional[Callable[[dict[str, Any], shader.Shader], bool]] = None
write_material_attribs_post: Optional[Callable[[dict[str, Any], shader.Shader], None]] = None
write_vertex_attribs: Optional[Callable[[shader.Shader], bool]] = None


def make(context_id, rpasses):
    wrd = bpy.data.worlds['Arm']
    rpdat = arm.utils.get_rp()
    rid = rpdat.rp_renderer

    con = { 'name': context_id, 'depth_write': True, 'compare_mode': 'less', 'cull_mode': 'clockwise' }

    # Blend context
    mat = mat_state.material
    blend = mat.arm_blending
    particle = mat.arm_particle_flag
    dprepass = rid == 'Forward' and rpdat.rp_depthprepass
    if blend:
        con['name'] = 'blend'
        con['blend_source'] = mat.arm_blending_source
        con['blend_destination'] = mat.arm_blending_destination
        con['blend_operation'] = mat.arm_blending_operation
        con['alpha_blend_source'] = mat.arm_blending_source_alpha
        con['alpha_blend_destination'] = mat.arm_blending_destination_alpha
        con['alpha_blend_operation'] = mat.arm_blending_operation_alpha
        con['depth_write'] = False
        con['compare_mode'] = 'less'
    elif particle:
        pass
    # Depth prepass was performed, exclude mat with depth read that
    # isn't part of depth prepass
    elif dprepass and not (rpdat.rp_depth_texture and mat.arm_depth_read):
        con['depth_write'] = False
        con['compare_mode'] = 'equal'
    else:
        con['depth_write'] = mat.arm_depth_write
        con['compare_mode'] = mat.arm_compare_mode

    attachment_format = 'RGBA32' if '_LDR' in wrd.world_defs else 'RGBA64'
    con['color_attachments'] = [attachment_format, attachment_format]
    if '_gbuffer2' in wrd.world_defs:
        con['color_attachments'].append(attachment_format)

    con_mesh = mat_state.data.add_context(con)
    mat_state.con_mesh = con_mesh

    if rid == 'Forward' or blend:
        if rpdat.arm_material_model == 'Mobile':
            make_forward_mobile(con_mesh)
        elif rpdat.arm_material_model == 'Solid':
            make_forward_solid(con_mesh)
        else:
            make_forward(con_mesh)
    elif rid == 'Deferred':
        make_deferred(con_mesh, rpasses)
    elif rid == 'Raytracer':
        make_raytracer(con_mesh)

    make_finalize.make(con_mesh)

    assets.vs_equal(con_mesh, assets.shader_cons['mesh_vert'])

    return con_mesh


def make_base(con_mesh, parse_opacity):
    global is_displacement
    global write_vertex_attribs

    vert = con_mesh.make_vert()
    frag = con_mesh.make_frag()
    geom = None
    tesc = None
    tese = None

    billboard = mat_state.material.arm_billboard
    if billboard == 'spherical':
        vert.add_uniform('mat3 N', '_normalMatrixSphere')
    elif billboard == 'cylindrical':
        vert.add_uniform('mat3 N', '_normalMatrixCylinder')
    else:
        vert.add_uniform('mat3 N', '_normalMatrix')
    vert.write_attrib('vec4 spos = vec4(pos.xyz, 1.0);')

    vattr_written = False
    rpdat = arm.utils.get_rp()
    is_displacement = mat_utils.disp_linked(mat_state.output_node)
    wrd = bpy.data.worlds['Arm']
    if is_displacement:
        if rpdat.arm_rp_displacement == 'Vertex':
            frag.ins = vert.outs
        else: # Tessellation
            tesc = con_mesh.make_tesc()
            tese = con_mesh.make_tese()
            tesc.ins = vert.outs
            tese.ins = tesc.outs
            frag.ins = tese.outs
            make_tess.tesc_levels(tesc, rpdat.arm_tess_mesh_inner, rpdat.arm_tess_mesh_outer)
            make_tess.interpolate(tese, 'wposition', 3, declare_out=True)
            make_tess.interpolate(tese, 'wnormal', 3, declare_out=True, normalize=True)

    # No displacement
    else:
        frag.ins = vert.outs
        if write_vertex_attribs is not None:
            vattr_written = write_vertex_attribs(vert)

    vert.add_include('compiled.inc')
    frag.add_include('compiled.inc')

    attribs_written = False
    if write_material_attribs is not None:
        attribs_written = write_material_attribs(con_mesh, frag)
    if not attribs_written:
        _write_material_attribs_default(frag, parse_opacity)
        cycles.parse(mat_state.nodes, con_mesh, vert, frag, geom, tesc, tese, parse_opacity=parse_opacity)
    if write_material_attribs_post is not None:
        write_material_attribs_post(con_mesh, frag)

    vert.add_out('vec3 wnormal')
    make_attrib.write_norpos(con_mesh, vert)
    frag.write_attrib('vec3 n = normalize(wnormal);')

    if mat_state.material.arm_two_sided:
        frag.write('if (!gl_FrontFacing) n *= -1;')  # Flip normal when drawing back-face

    if not is_displacement and not vattr_written:
        make_attrib.write_vertpos(vert)

    make_attrib.write_tex_coords(con_mesh, vert, frag, tese)

    if con_mesh.is_elem('col'):
        vert.add_out('vec3 vcolor')
        vert.write_attrib('vcolor = col.rgb;')
        if tese is not None:
            tese.write_pre = True
            make_tess.interpolate(tese, 'vcolor', 3, declare_out=frag.contains('vcolor'))
            tese.write_pre = False

    if con_mesh.is_elem('tang'):
        if tese is not None:
            tese.add_out('mat3 TBN')
            tese.write_attrib('vec3 wbitangent = normalize(cross(wnormal, wtangent));')
            tese.write_attrib('TBN = mat3(wtangent, wbitangent, wnormal);')
        else:
            vert.add_out('mat3 TBN')
            vert.write_attrib('vec3 tangent = normalize(N * tang.xyz);')
            vert.write_attrib('vec3 bitangent = normalize(cross(wnormal, tangent));')
            vert.write_attrib('TBN = mat3(tangent, bitangent, wnormal);')

    if is_displacement:
        if rpdat.arm_rp_displacement == 'Vertex':
            sh = vert
        else:
            sh = tese
        if(con_mesh.is_elem('ipos')):
            vert.write('wposition = vec4(W * spos).xyz;')
        sh.add_uniform('mat4 VP', '_viewProjectionMatrix')
        sh.write('wposition += wnormal * disp;')
        sh.write('gl_Position = VP * vec4(wposition, 1.0);')


def make_deferred(con_mesh, rpasses):
    wrd = bpy.data.worlds['Arm']
    rpdat = arm.utils.get_rp()

    arm_discard = mat_state.material.arm_discard
    parse_opacity = arm_discard or 'translucent' or 'refraction' in rpasses

    make_base(con_mesh, parse_opacity=parse_opacity)

    frag = con_mesh.frag
    vert = con_mesh.vert
    tese = con_mesh.tese

    if parse_opacity:
        if arm_discard:
            opac = mat_state.material.arm_discard_opacity
        else:
            opac = '0.9999' # 1.0 - eps
        frag.write('if (opacity < {0}) discard;'.format(opac))

    frag.add_out(f'vec4 fragColor[GBUF_SIZE]')

    if '_gbuffer2' in wrd.world_defs:
        if '_Veloc' in wrd.world_defs:
            if tese is None:
                vert.add_uniform('mat4 prevWVP', link='_prevWorldViewProjectionMatrix')
                vert.add_out('vec4 wvpposition')
                vert.add_out('vec4 prevwvpposition')
                vert.write('wvpposition = gl_Position;')
                if is_displacement:
                    vert.add_uniform('mat4 invW', link='_inverseWorldMatrix')
                    vert.write('prevwvpposition = prevWVP * (invW * vec4(wposition, 1.0));')
                else:
                    vert.write('prevwvpposition = prevWVP * spos;')
            else:
                tese.add_out('vec4 wvpposition')
                tese.add_out('vec4 prevwvpposition')
                tese.write('wvpposition = gl_Position;')
                if is_displacement:
                    tese.add_uniform('mat4 invW', link='_inverseWorldMatrix')
                    tese.add_uniform('mat4 prevWVP', '_prevWorldViewProjectionMatrix')
                    tese.write('prevwvpposition = prevWVP * (invW * vec4(wposition, 1.0));')
                else:
                    vert.add_uniform('mat4 prevW', link='_prevWorldMatrix')
                    vert.add_out('vec3 prevwposition')
                    vert.write('prevwposition = vec4(prevW * spos).xyz;')
                    tese.add_uniform('mat4 prevVP', '_prevViewProjectionMatrix')
                    make_tess.interpolate(tese, 'prevwposition', 3)
                    tese.write('prevwvpposition = prevVP * vec4(prevwposition, 1.0);')

    # Pack gbuffer
    frag.add_include('std/gbuffer.glsl')

    frag.write('n /= (abs(n.x) + abs(n.y) + abs(n.z));')
    frag.write('n.xy = n.z >= 0.0 ? n.xy : octahedronWrap(n.xy);')

    is_shadeless = mat_state.emission_type == mat_state.EmissionType.SHADELESS
    if is_shadeless or '_SSS' in wrd.world_defs or '_Hair' in wrd.world_defs:
        frag.write('uint matid = 0;')
        if is_shadeless:
            frag.write('matid = 1;')
            frag.write('basecol = emissionCol;')
        if '_SSS' in wrd.world_defs or '_Hair' in wrd.world_defs:
            frag.add_uniform('int materialID')
            frag.write('if (materialID == 2) matid = 2;')
    else:
        frag.write('const uint matid = 0;')

    frag.write('fragColor[GBUF_IDX_0] = vec4(n.xy, roughness, packFloatInt16(metallic, matid));')
    frag.write('fragColor[GBUF_IDX_1] = vec4(basecol, packFloat2(occlusion, specular));')

    if '_gbuffer2' in wrd.world_defs:
        if '_Veloc' in wrd.world_defs:
            frag.write('vec2 posa = (wvpposition.xy / wvpposition.w) * 0.5 + 0.5;')
            frag.write('vec2 posb = (prevwvpposition.xy / prevwvpposition.w) * 0.5 + 0.5;')
            frag.write('fragColor[GBUF_IDX_2].rg = vec2(posa - posb);')
            frag.write('fragColor[GBUF_IDX_2].b = 0.0;')

        if mat_state.material.arm_ignore_irradiance:
            frag.write('fragColor[GBUF_IDX_2].b = 1.0;')

    # Even if the material doesn't use emission we need to write to the
    # emission buffer (if used) to prevent undefined behaviour
    frag.write('#ifdef _EmissionShaded')
    frag.write('fragColor[GBUF_IDX_EMISSION] = vec4(emissionCol, 0.0);')  #Alpha channel is unused at the moment
    frag.write('#endif')

    if '_SSRefraction' in wrd.world_defs or '_VoxelRefract' in wrd.world_defs:
        frag.write('fragColor[GBUF_IDX_REFRACTION] = vec4(1.0, 1.0, 0.0, 0.0);')

    return con_mesh


def make_raytracer(con_mesh):
    con_mesh.data['vertex_elements'] = [{'name': 'pos', 'data': 'float3'}, {'name': 'nor', 'data': 'float3'}, {'name': 'tex', 'data': 'float2'}]
    wrd = bpy.data.worlds['Arm']
    vert = con_mesh.make_vert()
    frag = con_mesh.make_frag()
    vert.add_out('vec3 n')
    vert.add_out('vec2 uv')
    vert.write('n = nor;')
    vert.write('uv = tex;')
    vert.write('gl_Position = vec4(pos.xyz, 1.0);')


def make_forward_mobile(con_mesh):
    wrd = bpy.data.worlds['Arm']
    vert = con_mesh.make_vert()
    frag = con_mesh.make_frag()
    geom = None
    tesc = None
    tese = None

    vert.add_uniform('mat3 N', '_normalMatrix')
    vert.write_attrib('vec4 spos = vec4(pos.xyz, 1.0);')
    frag.ins = vert.outs

    vert.add_include('compiled.inc')
    frag.add_include('compiled.inc')

    arm_discard = mat_state.material.arm_discard
    blend = mat_state.material.arm_blending
    is_transluc = mat_utils.is_transluc(mat_state.material)
    parse_opacity = (blend and is_transluc) or arm_discard

    _write_material_attribs_default(frag, parse_opacity)
    cycles.parse(mat_state.nodes, con_mesh, vert, frag, geom, tesc, tese, parse_opacity=parse_opacity, parse_displacement=False)

    if arm_discard:
        opac = mat_state.material.arm_discard_opacity
        frag.write('if (opacity < {0}) discard;'.format(opac))

    make_attrib.write_tex_coords(con_mesh, vert, frag, tese)

    if con_mesh.is_elem('col'):
        vert.add_out('vec3 vcolor')
        vert.write('vcolor = col.rgb;')

    if con_mesh.is_elem('tang'):
        vert.add_out('mat3 TBN')
        make_attrib.write_norpos(con_mesh, vert, declare=True)
        vert.write('vec3 tangent = normalize(N * tang.xyz);')
        vert.write('vec3 bitangent = normalize(cross(wnormal, tangent));')
        vert.write('TBN = mat3(tangent, bitangent, wnormal);')
    else:
        vert.add_out('vec3 wnormal')
        make_attrib.write_norpos(con_mesh, vert)
        frag.write_attrib('vec3 n = normalize(wnormal);')

    if mat_state.material.arm_two_sided:
        frag.write('if (!gl_FrontFacing) n *= -1;')  # Flip normal when drawing back-face

    make_attrib.write_vertpos(vert)

    frag.add_include('std/math.glsl')
    frag.add_include('std/brdf.glsl')

    frag.add_out('vec4 fragColor')
    blend = mat_state.material.arm_blending
    if blend:
        if parse_opacity:
            frag.write('fragColor = vec4(basecol, opacity);')
        else:
            frag.write('fragColor = vec4(basecol, 1.0);')
        return

    is_shadows = '_ShadowMap' in wrd.world_defs
    is_shadows_atlas = '_ShadowMapAtlas' in wrd.world_defs
    shadowmap_sun = 'shadowMap'
    if is_shadows_atlas:
        is_single_atlas = '_SingleAtlas' in wrd.world_defs
        shadowmap_sun = 'shadowMapAtlasSun' if not is_single_atlas else 'shadowMapAtlas'
        frag.add_uniform('vec2 smSizeUniform', '_shadowMapSize', included=True)
    frag.write('vec3 direct = vec3(0.0);')

    if '_Sun' in wrd.world_defs:
        frag.add_uniform('vec3 sunCol', '_sunColor')
        frag.add_uniform('vec3 sunDir', '_sunDirection')
        frag.write('float svisibility = 1.0;')
        frag.write('float sdotNL = max(dot(n, sunDir), 0.0);')
        if is_shadows:
            vert.add_out('vec4 lightPosition')
            vert.add_uniform('mat4 LWVP', '_biasLightWorldViewProjectionMatrixSun')
            vert.write('lightPosition = LWVP * spos;')
            frag.add_uniform('bool receiveShadow')
            frag.add_uniform(f'sampler2DShadow {shadowmap_sun}')
            frag.add_uniform('float shadowsBias', '_sunShadowsBias')

            frag.write('if (receiveShadow) {')
            if '_CSM' in wrd.world_defs:
                frag.add_include('std/shadows.glsl')
                frag.add_uniform('vec4 casData[shadowmapCascades * 4 + 4]', '_cascadeData', included=True)
                frag.add_uniform('vec3 eye', '_cameraPosition')
                frag.write(f'svisibility = shadowTestCascade({shadowmap_sun}, eye, wposition + n * shadowsBias * 10, shadowsBias);')
            else:
                frag.write('if (lightPosition.w > 0.0) {')
                frag.write('    vec3 lPos = lightPosition.xyz / lightPosition.w;')
                if '_Legacy' in wrd.world_defs:
                    frag.write(f'    svisibility = float(texture({shadowmap_sun}, vec2(lPos.xy)).r > lPos.z - shadowsBias);')
                else:
                    frag.write(f'    svisibility = texture({shadowmap_sun}, vec3(lPos.xy, lPos.z - shadowsBias)).r;')
                frag.write('}')
            frag.write('}') # receiveShadow
        frag.write('direct += basecol * sdotNL * sunCol * svisibility;')

    if '_SinglePoint' in wrd.world_defs:
        frag.add_uniform('vec3 pointPos', '_pointPosition')
        frag.add_uniform('vec3 pointCol', '_pointColor')
        if '_Spot' in wrd.world_defs:
            frag.add_uniform('vec3 spotDir', link='_spotDirection')
            frag.add_uniform('vec3 spotRight', link='_spotRight')
            frag.add_uniform('vec4 spotData', link='_spotData')
        frag.write('float visibility = 1.0;')
        frag.write('vec3 ld = pointPos - wposition;')
        frag.write('vec3 l = normalize(ld);')
        frag.write('float dotNL = max(dot(n, l), 0.0);')
        if is_shadows:
            frag.add_uniform('bool receiveShadow')
            frag.add_uniform('float pointBias', link='_pointShadowsBias')
            frag.add_include('std/shadows.glsl')

            frag.write('if (receiveShadow) {')
            if '_Spot' in wrd.world_defs:
                vert.add_out('vec4 spotPosition')
                vert.add_uniform('mat4 LWVPSpotArray[1]', link='_biasLightWorldViewProjectionMatrixSpotArray')
                vert.write('spotPosition = LWVPSpotArray[0] * spos;')
                frag.add_uniform('sampler2DShadow shadowMapSpot[1]')
                frag.write('if (spotPosition.w > 0.0) {')
                frag.write('    vec3 lPos = spotPosition.xyz / spotPosition.w;')
                if '_Legacy' in wrd.world_defs:
                    frag.write('    visibility = float(texture(shadowMapSpot[0], vec2(lPos.xy)).r > lPos.z - pointBias);')
                else:
                    frag.write('    visibility = texture(shadowMapSpot[0], vec3(lPos.xy, lPos.z - pointBias)).r;')
                frag.write('}')
            else:
                frag.add_uniform('vec2 lightProj', link='_lightPlaneProj')
                frag.add_uniform('samplerCubeShadow shadowMapPoint[1]')
                frag.write('const float s = shadowmapCubePcfSize;') # TODO: incorrect...
                frag.write('float compare = lpToDepth(ld, lightProj) - pointBias * 1.5;')
                frag.write('#ifdef _InvY')
                frag.write('l.y = -l.y;')
                frag.write('#endif')
                if '_Legacy' in wrd.world_defs:
                    frag.write('visibility = float(texture(shadowMapPoint[0], vec3(-l + n * pointBias * 20)).r > compare);')
                else:
                    frag.write('visibility = texture(shadowMapPoint[0], vec4(-l + n * pointBias * 20, compare)).r;')
            frag.write('}') # receiveShadow

        frag.write('direct += basecol * dotNL * pointCol * attenuate(distance(wposition, pointPos)) * visibility;')

    if '_Clusters' in wrd.world_defs:
        frag.add_include('std/light_mobile.glsl')
        frag.write('vec3 albedo = basecol;')
        frag.write('vec3 f0 = surfaceF0(basecol, metallic);')
        make_cluster.write(vert, frag)

    if '_Irr' in wrd.world_defs:
        frag.add_include('std/shirr.glsl')
        frag.add_uniform('vec4 shirr[7]', link='_envmapIrradiance')
        env_str = 'shIrradiance(n, shirr)'
    else:
        env_str = '0.5'

    frag.add_uniform('float envmapStrength', link='_envmapStrength')
    frag.write('fragColor = vec4(direct + basecol * {0} * envmapStrength, 1.0);'.format(env_str))

    if '_LDR' in wrd.world_defs:
        frag.write('fragColor.rgb = pow(fragColor.rgb, vec3(1.0 / 2.2));')


def make_forward_solid(con_mesh):
    wrd = bpy.data.worlds['Arm']
    vert = con_mesh.make_vert()
    frag = con_mesh.make_frag()
    geom = None
    tesc = None
    tese = None

    for e in con_mesh.data['vertex_elements']:
        if e['name'] == 'nor':
            con_mesh.data['vertex_elements'].remove(e)
            break

    vert.write_attrib('vec4 spos = vec4(pos.xyz, 1.0);')
    frag.ins = vert.outs

    vert.add_include('compiled.inc')
    frag.add_include('compiled.inc')

    arm_discard = mat_state.material.arm_discard
    blend = mat_state.material.arm_blending
    is_transluc = mat_utils.is_transluc(mat_state.material)
    parse_opacity = (blend and is_transluc) or arm_discard

    _write_material_attribs_default(frag, parse_opacity)
    cycles.parse(mat_state.nodes, con_mesh, vert, frag, geom, tesc, tese, parse_opacity=parse_opacity, parse_displacement=False, basecol_only=True)

    if arm_discard:
        opac = mat_state.material.arm_discard_opacity
        frag.write('if (opacity < {0}) discard;'.format(opac))

    if con_mesh.is_elem('tex'):
        vert.add_out('vec2 texCoord')
        vert.add_uniform('float texUnpack', link='_texUnpack')
        if mat_state.material.arm_tilesheet_flag:
            vert.add_uniform('vec2 tilesheetOffset', '_tilesheetOffset')
            vert.write('texCoord = tex * texUnpack + tilesheetOffset;')
        else:
            vert.write('texCoord = tex * texUnpack;')

    if con_mesh.is_elem('col'):
        vert.add_out('vec3 vcolor')
        vert.write('vcolor = col.rgb;')

    make_attrib.write_norpos(con_mesh, vert, write_nor=False)
    make_attrib.write_vertpos(vert)

    frag.add_out('vec4 fragColor')
    if blend and parse_opacity:
        frag.write('fragColor = vec4(basecol, opacity);')
    else:
        frag.write('fragColor = vec4(basecol, 1.0);')

    if '_LDR' in wrd.world_defs:
        frag.write('fragColor.rgb = pow(fragColor.rgb, vec3(1.0 / 2.2));')


def make_forward(con_mesh):
    wrd = bpy.data.worlds['Arm']
    rpdat = arm.utils.get_rp()
    blend = mat_state.material.arm_blending
    parse_opacity = blend or mat_utils.is_transluc(mat_state.material)

    make_forward_base(con_mesh, parse_opacity=parse_opacity)
    frag = con_mesh.frag

    if '_LTC' in wrd.world_defs:
        frag.add_uniform('vec3 lightArea0', '_lightArea0', included=True)
        frag.add_uniform('vec3 lightArea1', '_lightArea1', included=True)
        frag.add_uniform('vec3 lightArea2', '_lightArea2', included=True)
        frag.add_uniform('vec3 lightArea3', '_lightArea3', included=True)
        frag.add_uniform('sampler2D sltcMat', '_ltcMat', included=True)
        frag.add_uniform('sampler2D sltcMag', '_ltcMag', included=True)
        if '_ShadowMap' in wrd.world_defs:
            if '_SinglePoint' in wrd.world_defs:
                frag.add_uniform('mat4 LWVPSpot[0]', link='_biasLightViewProjectionMatrixSpot0', included=True)
                frag.add_uniform('sampler2DShadow shadowMapSpot[1]', included=True)
            if '_Clusters' in wrd.world_defs:
                frag.add_uniform('mat4 LWVPSpotArray[4]', link='_biasLightWorldViewProjectionMatrixSpotArray', included=True)
                frag.add_uniform('sampler2DShadow shadowMapSpot[4]', included=True)

    if not blend:
        mrt = 0  # mrt: multiple render targets
        if rpdat.rp_ssr:
            mrt = 1
        if rpdat.rp_ss_refraction or rpdat.arm_voxelgi_refract:
            mrt = 2
        if mrt != 0:
            # Store light gbuffer for post-processing
            frag.add_out(f'vec4 fragColor[{mrt}+1]')
            frag.add_include('std/gbuffer.glsl')
            frag.write('n /= (abs(n.x) + abs(n.y) + abs(n.z));')
            frag.write('n.xy = n.z >= 0.0 ? n.xy : octahedronWrap(n.xy);')
            frag.write('fragColor[0] = vec4(direct + indirect, packFloat2(occlusion, specular));')
            frag.write('fragColor[1] = vec4(n.xy, roughness, metallic);')
            if rpdat.rp_ss_refraction or rpdat.arm_voxelgi_refract:
                frag.write(f'fragColor[2] = vec4(1.0, 1.0, 0.0, 0.0);')

        else:
            frag.add_out('vec4 fragColor[1]')
            frag.write('fragColor[0] = vec4(direct + indirect, 1.0);')

        if '_LDR' in wrd.world_defs:
            frag.add_include('std/tonemap.glsl')
            frag.write('fragColor[0].rgb = tonemapFilmic(fragColor[0].rgb);')

    # Particle opacity
    if mat_state.material.arm_particle_flag and arm.utils.get_rp().arm_particles == 'GPU' and mat_state.material.arm_particle_fade:
        frag.write('fragColor[0].rgb *= p_fade;')


def make_forward_base(con_mesh, parse_opacity=False, transluc_pass=False):
    global is_displacement
    wrd = bpy.data.worlds['Arm']

    arm_discard = mat_state.material.arm_discard
    make_base(con_mesh, parse_opacity=(parse_opacity or arm_discard))

    blend = mat_state.material.arm_blending

    vert = con_mesh.vert
    frag = con_mesh.frag
    tese = con_mesh.tese

    if parse_opacity or arm_discard:
        if arm_discard or blend:
            opac = mat_state.material.arm_discard_opacity
            frag.write('if (opacity < {0}) discard;'.format(opac))
        elif transluc_pass:
            frag.write('if (opacity == 1.0) discard;')
        else:
            opac = '0.9999' # 1.0 - eps
            frag.write('if (opacity < {0}) discard;'.format(opac))

    if blend:
        frag.add_out('vec4 fragColor[1]')
        if parse_opacity:
            frag.write('fragColor[0] = vec4(basecol, opacity);')
        else:
            # frag.write('fragColor[0] = vec4(basecol * lightCol * visibility, 1.0);')
            frag.write('fragColor[0] = vec4(basecol, 1.0);')
        # TODO: Fade out fragments near depth buffer here
        return

    frag.write_attrib('vec3 vVec = normalize(eyeDir);')
    frag.write_attrib('float dotNV = max(dot(n, vVec), 0.0);')

    sh = tese if tese is not None else vert
    sh.add_out('vec3 eyeDir')
    sh.add_uniform('vec3 eye', '_cameraPosition')
    sh.write('eyeDir = eye - wposition;')

    frag.add_include('std/light.glsl')
    is_shadows = '_ShadowMap' in wrd.world_defs
    is_shadows_atlas = '_ShadowMapAtlas' in wrd.world_defs
    is_single_atlas = is_shadows_atlas and '_SingleAtlas' in wrd.world_defs
    shadowmap_sun = 'shadowMap'
    if is_shadows_atlas:
        shadowmap_sun = 'shadowMapAtlasSun' if not is_single_atlas else 'shadowMapAtlas'
        frag.add_uniform('vec2 smSizeUniform', '_shadowMapSize', included=True)

    frag.write('vec3 albedo = surfaceAlbedo(basecol, metallic);')
    frag.write('vec3 f0 = surfaceF0(basecol, metallic);')

    if '_Brdf' in wrd.world_defs:
        frag.add_uniform('sampler2D senvmapBrdf', link='$brdf.png')
        frag.write('vec2 envBRDF = texelFetch(senvmapBrdf, ivec2(vec2(dotNV, 1.0 - roughness) * 256.0), 0).xy;')

    if '_Irr' in wrd.world_defs:
        frag.add_include('std/shirr.glsl')
        frag.add_uniform('vec4 shirr[7]', link='_envmapIrradiance')
        frag.write('vec3 envl = shIrradiance(n, shirr);')
        if '_EnvTex' in wrd.world_defs:
            frag.write('envl /= PI;')
    else:
        frag.write('vec3 envl = vec3(0.0);')

    if '_Rad' in wrd.world_defs:
        frag.add_uniform('sampler2D senvmapRadiance', link='_envmapRadiance')
        frag.add_uniform('int envmapNumMipmaps', link='_envmapNumMipmaps')
        frag.write('vec3 reflectionWorld = reflect(-vVec, n);')
        frag.write('float lod = getMipFromRoughness(roughness, envmapNumMipmaps);')
        frag.write('vec3 prefilteredColor = textureLod(senvmapRadiance, envMapEquirect(reflectionWorld), lod).rgb;')

    if '_EnvLDR' in wrd.world_defs:
        frag.write('envl = pow(envl, vec3(2.2));')
        if '_Rad' in wrd.world_defs:
            frag.write('prefilteredColor = pow(prefilteredColor, vec3(2.2));')

    frag.write('envl *= albedo;')

    if '_Brdf' in wrd.world_defs:
        frag.write('envl.rgb *= 1.0 - (f0 * envBRDF.x + envBRDF.y);')
    if '_Rad' in wrd.world_defs:
        frag.write('envl += prefilteredColor * (f0 * envBRDF.x + envBRDF.y);')
    elif '_EnvCol' in wrd.world_defs:
        frag.add_uniform('vec3 backgroundCol', link='_backgroundCol')
        frag.write('envl += backgroundCol * (f0 * envBRDF.x + envBRDF.y);')

    frag.add_uniform('float envmapStrength', link='_envmapStrength')
    frag.write('envl *= envmapStrength * occlusion;')

    # Computing texCoord in vertex shader from pos.xy doesn't work
    if '_VoxelAOvar' in wrd.world_defs or '_VoxelGI' in wrd.world_defs:
        if parse_opacity:
            frag.add_include("std/conetrace.glsl")
            frag.add_uniform("float clipmaps[10 * voxelgiClipmapCount]", "_clipmaps")
            frag.add_uniform("sampler3D voxels")
            frag.add_uniform("sampler3D voxelsSDF")
            if '_VoxelShadow' in wrd.world_defs:
                frag.add_uniform("sampler2D voxels_shadows", top=True) #TODO remove when doing transparent shadows, this is just a dummy
        else:
            if '_VoxelShadow' in wrd.world_defs:
                frag.add_uniform("sampler2D voxels_shadows", top=True)
        vert.add_out('vec4 wvpposition')
        vert.write('wvpposition = gl_Position;')
        frag.write('vec2 texCoord = (wvpposition.xy / wvpposition.w) * 0.5 + 0.5;')

    if '_VoxelAOvar' in wrd.world_defs:
        if parse_opacity:
            frag.write('envl *= traceAO(wposition, wnormal, voxels, clipmaps);')
        else:
            frag.add_uniform("sampler2D voxels_ao");
            frag.write('envl *= textureLod(voxels_ao, texCoord, 0.0).rrr;')

    if '_VoxelGI' in wrd.world_defs:
        frag.write('vec3 indirect = vec3(0.0);')
    else:
        frag.write('vec3 indirect = envl;')

    if '_VoxelGI' in wrd.world_defs:
        if parse_opacity:
            frag.write("indirect = traceDiffuse(wposition, n, voxels, clipmaps).rgb * albedo * voxelgiDiff;")
            frag.write("if (roughness < 1.0 && specular > 0.0)")
            frag.write("    indirect += traceSpecular(wposition, n, voxels, voxelsSDF, vVec, roughness, clipmaps, gl_FragCoord.xy).rgb * specular * voxelgiRefl;")
        else:
            frag.add_uniform("sampler2D voxels_diffuse")
            frag.add_uniform("sampler2D voxels_specular")
            frag.write("indirect = textureLod(voxels_diffuse, texCoord, 0.0).rgb * albedo * voxelgiDiff;")
            frag.write("if (roughness < 1.0 && specular > 0.0)")
            frag.write("    indirect += textureLod(voxels_specular, texCoord, 0.0).rgb * specular * voxelgiRefl;")

    frag.write('vec3 direct = vec3(0.0);')

    if '_Sun' in wrd.world_defs:
        frag.add_uniform('vec3 sunCol', '_sunColor')
        frag.add_uniform('vec3 sunDir', '_sunDirection')
        frag.write('float svisibility = 0.0;')
        frag.write('vec3 sh = normalize(vVec + sunDir);')
        frag.write('float sdotNL = max(dot(n, sunDir), 0);')
        frag.write('float sdotNH = max(dot(n, sh), 0);')
        frag.write('float sdotVH = max(dot(vVec, sh), 0);')
        if is_shadows:
            frag.add_uniform('bool receiveShadow')
            frag.add_uniform(f'sampler2DShadow {shadowmap_sun}', top=True)
            frag.add_uniform('float shadowsBias', '_sunShadowsBias')
            frag.write('if (receiveShadow) {')
            if '_CSM' in wrd.world_defs:
                frag.add_include('std/shadows.glsl')
                frag.add_uniform('vec4 casData[shadowmapCascades * 4 + 4]', '_cascadeData', included=True)
                frag.add_uniform('vec3 eye', '_cameraPosition')
                frag.write(f'svisibility = shadowTestCascade({shadowmap_sun}, eye, wposition + n * shadowsBias * 10, shadowsBias);')
            else:
                if tese is not None:
                    tese.add_out('vec4 lightPosition')
                    tese.add_uniform('mat4 LVP', '_biasLightViewProjectionMatrix')
                    tese.write('lightPosition = LVP * vec4(wposition, 1.0);')
                else:
                    if is_displacement:
                        vert.add_out('vec4 lightPosition')
                        vert.add_uniform('mat4 LVP', '_biasLightViewProjectionMatrix')
                        vert.write('lightPosition = LVP * vec4(wposition, 1.0);')
                    else:
                        vert.add_out('vec4 lightPosition')
                        vert.add_uniform('mat4 LWVP', '_biasLightWorldViewProjectionMatrixSun')
                        vert.write('lightPosition = LWVP * spos;')
                frag.write('vec3 lPos = lightPosition.xyz / lightPosition.w;')
                frag.write('const vec2 smSize = shadowmapSize;')
                frag.write(f'svisibility = PCF({shadowmap_sun}, lPos.xy, lPos.z - shadowsBias, smSize);')
            frag.write('}') # receiveShadow
        if '_VoxelShadow' in wrd.world_defs:
            if parse_opacity:
                frag.write('svisibility *= traceShadow(wposition, n, voxels, voxelsSDF, sunDir, clipmaps, texCoord);')
            else:
                frag.write('svisibility *= textureLod(voxels_shadows, texCoord, 0.0).r * voxelgiShad;')
        frag.write('direct += (lambertDiffuseBRDF(albedo, sdotNL) + specularBRDF(f0, roughness, sdotNL, sdotNH, dotNV, sdotVH) * specular) * sunCol * svisibility;')
        # sun

    if '_SinglePoint' in wrd.world_defs:
        frag.add_uniform('vec3 pointPos', link='_pointPosition')
        frag.add_uniform('vec3 pointCol', link='_pointColor')
        if '_Spot' in wrd.world_defs:
            frag.add_uniform('vec3 spotDir', link='_spotDirection')
            frag.add_uniform('vec3 spotRight', link='_spotRight')
            frag.add_uniform('vec4 spotData', link='_spotData')
        if is_shadows:
            frag.add_uniform('bool receiveShadow')
            frag.add_uniform('float pointBias', link='_pointShadowsBias')
            if '_Spot' in wrd.world_defs:
                # Skip world matrix, already in world-space
                frag.add_uniform('mat4 LWVPSpot[1]', link='_biasLightViewProjectionMatrixSpotArray', included=True)
                frag.add_uniform('sampler2DShadow shadowMapSpot[1]', included=True)
                frag.add_uniform('sampler2D shadowMapSpotTransparent[1]', included=True)
            else:
                frag.add_uniform('vec2 lightProj', link='_lightPlaneProj', included=True)
                frag.add_uniform('samplerCubeShadow shadowMapPoint[1]', included=True)
                frag.add_uniform('samplerCube shadowMapPointTransparent[1]', included=True)
        frag.write('direct += sampleLight(')
        frag.write('  wposition, n, vVec, dotNV, pointPos, pointCol, albedo, roughness, specular, f0')
        if is_shadows:
            frag.write(', 0, pointBias, receiveShadow')
        if '_Spot' in wrd.world_defs:
            frag.write(', true, spotData.x, spotData.y, spotDir, spotData.zw, spotRight')
        if '_VoxelShadow' in wrd.world_defs:
            frag.write(', texCoord')
        if '_MicroShadowing' in wrd.world_defs:
            frag.write(', occlusion')
        if '_SSRS' in wrd.world_defs:
            frag.add_uniform('sampler2D gbufferD', top=True)
            frag.add_uniform('mat4 invVP', '_inverseViewProjectionMatrix')
            frag.add_uniform('vec3 eye', '_cameraPosition')
            frag.write(', gbufferD, invVP, eye')
        frag.write(');')

    if '_Clusters' in wrd.world_defs:
        make_cluster.write(vert, frag)

    if mat_state.emission_type != mat_state.EmissionType.NO_EMISSION:
        if mat_state.emission_type == mat_state.EmissionType.SHADELESS:
            frag.write('direct = vec3(0.0);')
        frag.write('indirect += emissionCol;')

    if '_VoxelRefract' in wrd.world_defs and parse_opacity:
        frag.add_include('std/conetrace.glsl')
        frag.add_uniform('float clipmaps[10 * voxelgiClipmapCount]', '_clipmaps')
        frag.add_uniform('sampler3D voxels')
        frag.add_uniform('sampler3D voxelsSDF')
        frag.write('if (opacity < 1.0) {')
        frag.write('    vec3 refraction = traceRefraction(wposition, n, voxels, voxelsSDF, vVec, ior, roughness, clipmaps, texCoord).rgb * voxelgiRefr;')
        frag.write('    indirect = mix(refraction, indirect, opacity);')
        frag.write('    direct = mix(refraction, direct, opacity);')
        frag.write('}')


def _write_material_attribs_default(frag: shader.Shader, parse_opacity: bool):
    frag.write('vec3 basecol;')
    frag.write('float roughness;')
    frag.write('float metallic;')
    frag.write('float occlusion;')
    frag.write('float specular;')
    # We may not use emission, but the attribute will then be removed
    # by the shader compiler
    frag.write('vec3 emissionCol;')
    if parse_opacity:
        frag.write('float opacity;')
        frag.write('float ior;')
