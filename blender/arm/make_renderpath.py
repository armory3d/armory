import bpy
import arm.assets as assets
import arm.utils
import arm.log as log
import arm.make_state as state
import arm.api

callback = None

def add_world_defs():
    wrd = bpy.data.worlds['Arm']
    rpdat = arm.utils.get_rp()

    # Screen-space ray-traced shadows
    if rpdat.arm_ssrs:
        wrd.world_defs += '_SSRS'

    if rpdat.arm_two_sided_area_lamp:
        wrd.world_defs += '_TwoSidedAreaLamp'

    # Store contexts
    if rpdat.rp_hdr == False:
        wrd.world_defs += '_LDR'

    # Alternative models
    if rpdat.arm_diffuse_model == 'OrenNayar':
        wrd.world_defs += '_OrenNayar'

    # TODO: Lamp texture test..
    if wrd.arm_lamp_texture != '':
        wrd.world_defs += '_LampColTex'

    if wrd.arm_lamp_ies_texture != '':
        wrd.world_defs += '_LampIES'
        assets.add_embedded_data('iestexture.png')

    if wrd.arm_lamp_clouds_texture != '':
        wrd.world_defs += '_LampClouds'
        assets.add_embedded_data('cloudstexture.png')

    if rpdat.rp_renderer == 'Deferred':
        assets.add_khafile_def('arm_deferred')
        wrd.world_defs += '_Deferred'

    # GI
    voxelgi = False
    voxelao = False
    has_voxels = arm.utils.voxel_support()
    if has_voxels:
        if rpdat.rp_gi == 'Voxel GI':
            voxelgi = True
        elif rpdat.rp_gi == 'Voxel AO':
            voxelao = True
    # Shadows
    if rpdat.rp_shadowmap == 'Off':
        wrd.world_defs += '_NoShadows'
        assets.add_khafile_def('arm_no_shadows')
    else:
        if rpdat.rp_shadowmap_cascades != '1':
            if voxelgi:
                log.warn('Disabling shadow cascades - Voxel GI does not support cascades yet')
            else:
                wrd.world_defs += '_CSM'
                assets.add_khafile_def('arm_csm')
    # SS
    # if rpdat.rp_dfrs:
    #     wrd.world_defs += '_DFRS'
    #     assets.add_khafile_def('arm_sdf')
    # if rpdat.rp_dfao:
    #     wrd.world_defs += '_DFAO'
    #     assets.add_khafile_def('arm_sdf')
    # if rpdat.rp_dfgi:
    #     wrd.world_defs += '_DFGI'
    #     assets.add_khafile_def('arm_sdf')
    if rpdat.rp_ssgi == 'RTGI' or rpdat.rp_ssgi == 'RTAO':
        if rpdat.rp_ssgi == 'RTGI':
            wrd.world_defs += '_RTGI'
        if rpdat.arm_ssgi_rays == '9':
            wrd.world_defs += '_SSGICone9'
    if rpdat.rp_autoexposure:
        wrd.world_defs += '_AutoExposure'

    if voxelgi or voxelao:
        assets.add_khafile_def('arm_voxelgi')
        wrd.world_defs += '_VoxelCones' + rpdat.arm_voxelgi_cones
        if rpdat.arm_voxelgi_revoxelize:
            assets.add_khafile_def('arm_voxelgi_revox')
            if rpdat.arm_voxelgi_camera:
                wrd.world_defs += '_VoxelGICam'
            if rpdat.arm_voxelgi_temporal:
                assets.add_khafile_def('arm_voxelgi_temporal')
                wrd.world_defs += '_VoxelGITemporal'

        if voxelgi:
            wrd.world_defs += '_VoxelGI'
            assets.add_shader_external(arm.utils.get_sdk_path() + '/armory/Shaders/voxel_light/voxel_light.comp.glsl')
            if rpdat.arm_voxelgi_bounces != "1":
                assets.add_khafile_def('rp_gi_bounces={0}'.format(rpdat.arm_voxelgi_bounces))
                assets.add_shader_external(arm.utils.get_sdk_path() + '/armory/Shaders/voxel_bounce/voxel_bounce.comp.glsl')
            if rpdat.arm_voxelgi_shadows:
                wrd.world_defs += '_VoxelGIDirect'
                wrd.world_defs += '_VoxelGIShadow'
            if rpdat.arm_voxelgi_refraction:
                wrd.world_defs += '_VoxelGIDirect'
                wrd.world_defs += '_VoxelGIRefract'
            if rpdat.rp_voxelgi_relight:
                assets.add_khafile_def('rp_voxelgi_relight')
        elif voxelao:
            wrd.world_defs += '_VoxelAO'

    if arm.utils.get_gapi().startswith('direct3d'): # Flip Y axis in drawQuad command
        wrd.world_defs += '_InvY'

    if arm.utils.get_legacy_shaders() and not state.is_viewport:
        wrd.world_defs += '_Legacy'

    # Area lamps
    lamps = bpy.data.lights if bpy.app.version >= (2, 80, 1) else bpy.data.lamps
    for lamp in lamps:
        if lamp.type == 'AREA':
            wrd.world_defs += '_LTC'
            assets.add_khafile_def('arm_ltc')
            break

    if '_Rad' in wrd.world_defs or '_VoxelGI' in wrd.world_defs:
        wrd.world_defs += '_Brdf'
    if '_Brdf' in wrd.world_defs or '_VoxelAO' in wrd.world_defs:
        wrd.world_defs += '_IndPos'

def build():
    rpdat = arm.utils.get_rp()
    if rpdat.rp_driver != 'Armory' and arm.api.drivers[rpdat.rp_driver]['make_rpath'] != None:
        arm.api.drivers[rpdat.rp_driver]['make_rpath']()
        return

    assets_path = arm.utils.get_sdk_path() + 'armory/Assets/'
    wrd = bpy.data.worlds['Arm']

    add_world_defs()

    mobile_mat = rpdat.arm_material_model == 'Mobile' or rpdat.arm_material_model == 'Solid'
    if not mobile_mat:
        # Always include
        assets.add(assets_path + 'brdf.png')
        assets.add_embedded_data('brdf.png')

    if rpdat.rp_hdr:
        assets.add_khafile_def('rp_hdr')

    assets.add_khafile_def('rp_renderer={0}'.format(rpdat.rp_renderer))
    if rpdat.rp_depthprepass:
        assets.add_khafile_def('rp_depthprepass')

    if rpdat.rp_shadowmap != 'Off':
        assets.add_khafile_def('rp_shadowmap')
        assets.add_khafile_def('rp_shadowmap_size={0}'.format(rpdat.rp_shadowmap))

    assets.add_khafile_def('rp_background={0}'.format(rpdat.rp_background))
    if rpdat.rp_background == 'World':
        assets.add_shader_pass('world_pass')
        if '_EnvClouds' in wrd.world_defs:
            assets.add(assets_path + 'noise256.png')
            assets.add_embedded_data('noise256.png')

    if rpdat.rp_renderer == 'Deferred' and not rpdat.rp_compositornodes:
            assets.add_shader_pass('copy_pass')
    if rpdat.rp_renderer == 'Forward' and not rpdat.rp_compositornodes and rpdat.rp_render_to_texture:
            assets.add_shader_pass('copy_pass')

    if rpdat.rp_render_to_texture:
        assets.add_khafile_def('rp_render_to_texture')

        if rpdat.rp_compositornodes:
            assets.add_khafile_def('rp_compositornodes')
            compo_depth = False
            if rpdat.arm_tonemap != 'Off':
                wrd.compo_defs = '_CTone' + rpdat.arm_tonemap
            if rpdat.rp_antialiasing == 'FXAA':
                wrd.compo_defs += '_CFXAA'
            if rpdat.arm_letterbox:
                wrd.compo_defs += '_CLetterbox'
            if rpdat.arm_grain:
                wrd.compo_defs += '_CGrain'
            if rpdat.arm_sharpen:
                wrd.compo_defs += '_CSharpen'
            if bpy.data.scenes[0].cycles.film_exposure != 1.0:
                wrd.compo_defs += '_CExposure'
            if rpdat.arm_fog:
                wrd.compo_defs += '_CFog'
                compo_depth = True
            if len(bpy.data.cameras) > 0 and bpy.data.cameras[0].dof_distance > 0.0:
                wrd.compo_defs += '_CDOF'
                compo_depth = True
            if compo_depth:
                wrd.compo_defs += '_CDepth'
                assets.add_khafile_def('rp_compositordepth')
            if rpdat.arm_lens_texture != '':
                wrd.compo_defs += '_CLensTex'
                assets.add_embedded_data('lenstexture.jpg')
            if rpdat.arm_fisheye:
                wrd.compo_defs += '_CFishEye'
            if rpdat.arm_vignette:
                wrd.compo_defs += '_CVignette'
            if rpdat.arm_lensflare:
                wrd.compo_defs += '_CGlare'
            if rpdat.arm_lut_texture != '':
                wrd.compo_defs += '_CLUT'
                assets.add_embedded_data('luttexture.jpg')
            if '_CDOF' in wrd.compo_defs or '_CFXAA' in wrd.compo_defs or '_CSharpen' in wrd.compo_defs:
                wrd.compo_defs += '_CTexStep'
            assets.add_shader_pass('compositor_pass')

        assets.add_khafile_def('rp_antialiasing={0}'.format(rpdat.rp_antialiasing))

        if rpdat.rp_antialiasing == 'SMAA' or rpdat.rp_antialiasing == 'TAA':
            assets.add_shader_pass('smaa_edge_detect')
            assets.add_shader_pass('smaa_blend_weight')
            assets.add_shader_pass('smaa_neighborhood_blend')
            assets.add(assets_path + 'smaa_area.png')
            assets.add(assets_path + 'smaa_search.png')
            assets.add_embedded_data('smaa_area.png')
            assets.add_embedded_data('smaa_search.png')
            wrd.world_defs += '_SMAA'
            if rpdat.rp_antialiasing == 'TAA':
                assets.add_shader_pass('taa_pass')
                assets.add_shader_pass('copy_pass')

        if rpdat.rp_antialiasing == 'TAA' or rpdat.rp_motionblur == 'Object':
            assets.add_khafile_def('arm_veloc')
            wrd.world_defs += '_Veloc'
            if rpdat.rp_antialiasing == 'TAA':
                assets.add_khafile_def('arm_taa')

        assets.add_khafile_def('rp_supersampling={0}'.format(rpdat.rp_supersampling))        
        if rpdat.rp_supersampling == '4':
            assets.add_shader_pass('supersample_resolve')

    if rpdat.rp_overlays:
        assets.add_khafile_def('rp_overlays')

    if rpdat.rp_translucency:
        assets.add_khafile_def('rp_translucency')
        assets.add_shader_pass('translucent_resolve')

    if rpdat.rp_stereo:
        assets.add_khafile_def('rp_stereo')
        assets.add_khafile_def('arm_vr')
        wrd.world_defs += '_VR'
        assets.add(assets_path + 'vr.png')
        assets.add_embedded_data('vr.png')

    rp_gi = rpdat.rp_gi
    has_voxels = arm.utils.voxel_support()
    if not has_voxels:
        rp_gi = 'Off'
    assets.add_khafile_def('rp_gi={0}'.format(rp_gi))
    if rpdat.rp_gi != 'Off':
        if has_voxels:
            assets.add_khafile_def('rp_gi={0}'.format(rpdat.rp_gi))        
            assets.add_khafile_def('rp_voxelgi_resolution={0}'.format(rpdat.rp_voxelgi_resolution))
            assets.add_khafile_def('rp_voxelgi_resolution_z={0}'.format(rpdat.rp_voxelgi_resolution_z))
            if rpdat.rp_voxelgi_hdr:
                assets.add_khafile_def('rp_voxelgi_hdr')
            if rpdat.arm_voxelgi_shadows:
                assets.add_khafile_def('rp_voxelgi_shadows')
            if rpdat.arm_voxelgi_refraction:
                assets.add_khafile_def('rp_voxelgi_refraction')
        else:
            log.warn('Disabling Voxel GI - unsupported target - use Krom instead')

    if rpdat.arm_rp_resolution == 'Custom':
        assets.add_khafile_def('rp_resolution_filter={0}'.format(rpdat.arm_rp_resolution_filter))

    assets.add_khafile_def('rp_ssgi={0}'.format(rpdat.rp_ssgi))
    if rpdat.rp_ssgi != 'Off':
        wrd.world_defs += '_SSAO'
        if rpdat.rp_ssgi == 'SSAO':
            assets.add_shader_pass('ssao_pass')
            assets.add_shader_pass('blur_edge_pass')
            assets.add(assets_path + 'noise8.png')
            assets.add_embedded_data('noise8.png')
        else:
            assets.add_shader_pass('ssgi_pass')
            assets.add_shader_pass('ssgi_blur_pass')

    if rpdat.rp_renderer == 'Deferred':
        assets.add_shader_pass('deferred_indirect')
        assets.add_shader_pass('deferred_light')
        assets.add_shader_pass('deferred_light_quad')
        
    if rpdat.rp_volumetriclight:
        assets.add_khafile_def('rp_volumetriclight')
        assets.add_shader_pass('volumetric_light_quad')
        assets.add_shader_pass('volumetric_light')
        assets.add_shader_pass('blur_bilat_pass')
        assets.add_shader_pass('blur_bilat_blend_pass')
        assets.add(assets_path + 'blue_noise64.png')
        assets.add_embedded_data('blue_noise64.png')

    if rpdat.rp_decals:
        assets.add_khafile_def('rp_decals')

    if rpdat.rp_ocean:
        assets.add_khafile_def('rp_ocean')
        assets.add_shader_pass('water_pass')

    if rpdat.rp_blending_state != 'Off':
        assets.add_khafile_def('rp_blending')

    if rpdat.rp_bloom:
        assets.add_khafile_def('rp_bloom')
        assets.add_shader_pass('bloom_pass')
        assets.add_shader_pass('blur_gaus_pass')

    if rpdat.rp_sss:
        assets.add_khafile_def('rp_sss')
        wrd.world_defs += '_SSS'
        assets.add_shader_pass('sss_pass')

    if rpdat.rp_ssr:
        assets.add_khafile_def('rp_ssr')
        assets.add_shader_pass('ssr_pass')
        assets.add_shader_pass('blur_adaptive_pass')
        if rpdat.arm_ssr_half_res:
            assets.add_khafile_def('rp_ssr_half')
        if rpdat.rp_ssr_z_only:
            wrd.world_defs += '_SSRZOnly'

    if rpdat.rp_motionblur != 'Off':
        assets.add_khafile_def('rp_motionblur={0}'.format(rpdat.rp_motionblur))
        assets.add_shader_pass('copy_pass')
        if rpdat.rp_motionblur == 'Camera':
            assets.add_shader_pass('motion_blur_pass')
        else:
            assets.add_shader_pass('motion_blur_veloc_pass')

    if rpdat.rp_compositornodes and rpdat.rp_autoexposure:
        assets.add_khafile_def('rp_autoexposure')

    if rpdat.rp_dynres:
        assets.add_khafile_def('rp_dynres')

    if rpdat.arm_soft_shadows == 'On':
        if rpdat.rp_shadowmap_cascades == '1':
            assets.add_shader_pass('dilate_pass')
            assets.add_shader_pass('visibility_pass')
            assets.add_shader_pass('blur_shadow_pass')
            assets.add_khafile_def('rp_soft_shadows')
            wrd.world_defs += '_SoftShadows'
            if rpdat.arm_soft_shadows_penumbra != 1:
                wrd.world_defs += '_PenumbraScale'
        else:
            log.warn('Disabling soft shadows - "Armory Render Path - Cascades" requires to be set to 1 for now')

    gbuffer2_direct = '_SSS' in wrd.world_defs or '_Hair' in wrd.world_defs or rpdat.arm_voxelgi_refraction
    gbuffer2 = '_Veloc' in wrd.world_defs or gbuffer2_direct
    if gbuffer2:
        assets.add_khafile_def('rp_gbuffer2')
        wrd.world_defs += '_gbuffer2'
        if gbuffer2_direct:
            assets.add_khafile_def('rp_gbuffer2_direct')
            wrd.world_defs += '_gbuffer2direct'

    if callback != None:
        callback()
