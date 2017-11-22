import bpy
import arm.assets as assets
import arm.utils

def build():
    assets_path = arm.utils.get_sdk_path() + 'armory/Assets/'
    wrd = bpy.data.worlds['Arm']
    rpdat = arm.utils.get_rp()

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
        if '_EnvClouds' in wrd.world_defs:
            assets.add(assets_path + 'noise256.png')
            assets.add_embedded_data('noise256.png')

    if rpdat.rp_render_to_texture:
        assets.add_khafile_def('rp_render_to_texture')

        if rpdat.rp_compositornodes:
            assets.add_khafile_def('rp_compositornodes')
            compo_depth = False
            if wrd.arm_tonemap != 'Off':
                wrd.compo_defs = '_CTone' + wrd.arm_tonemap
            if rpdat.rp_antialiasing != 'Off':
                wrd.compo_defs += '_CFXAA'
            if wrd.arm_letterbox:
                wrd.compo_defs += '_CLetterbox'
            if wrd.arm_grain:
                wrd.compo_defs += '_CGrain'
            if bpy.data.scenes[0].cycles.film_exposure != 1.0:
                wrd.compo_defs += '_CExposure'
            if wrd.arm_fog:
                wrd.compo_defs += '_CFog'
                compo_depth = True
            if len(bpy.data.cameras) > 0 and bpy.data.cameras[0].dof_distance > 0.0:
                wrd.compo_defs += '_CDOF'
                compo_depth = True
            if compo_depth:
                wrd.compo_defs += '_CDepth'
            if wrd.arm_lens_texture != '':
                wrd.compo_defs += '_CLensTex'
                assets.add_embedded_data('lenstexture.jpg')
            if wrd.arm_fisheye:
                wrd.compo_defs += '_CFishEye'
            if wrd.arm_vignette:
                wrd.compo_defs += '_CVignette'
            if wrd.arm_lensflare:
                wrd.compo_defs += '_CGlare'
            assets.add_shader2('compositor_pass', 'compositor_pass')
        else:
            assets.add_shader2('copy_pass', 'copy_pass')

        assets.add_khafile_def('rp_antialiasing={0}'.format(rpdat.rp_antialiasing))

        if rpdat.rp_antialiasing == 'SMAA' or rpdat.rp_antialiasing == 'TAA':
            assets.add_shader2('smaa_edge_detect', 'smaa_edge_detect')
            assets.add_shader2('smaa_blend_weight', 'smaa_blend_weight')
            assets.add_shader2('smaa_neighborhood_blend', 'smaa_neighborhood_blend')
            assets.add(assets_path + 'smaa_area.png')
            assets.add(assets_path + 'smaa_search.png')
            assets.add_embedded_data('smaa_area.png')
            assets.add_embedded_data('smaa_search.png')
            wrd.world_defs += '_SMAA'
            if rpdat.rp_antialiasing == 'TAA':
                assets.add_shader2('taa_pass', 'taa_pass')
                assets.add_shader2('copy_pass', 'copy_pass')

        if rpdat.rp_antialiasing == 'TAA' or rpdat.rp_motionblur == 'Object':
            assets.add_khafile_def('arm_veloc')
            wrd.world_defs += '_Veloc'
            if rpdat.rp_antialiasing == 'TAA':
                assets.add_khafile_def('arm_taa')

        assets.add_khafile_def('rp_supersampling={0}'.format(rpdat.rp_supersampling))        
        if rpdat.rp_supersampling == '4':
            assets.add_shader2('supersample_resolve', 'supersample_resolve')

    if rpdat.rp_overlays:
        assets.add_khafile_def('rp_overlays')

    if rpdat.rp_translucency:
        assets.add_khafile_def('rp_translucency')
        assets.add_shader2('translucent_resolve', 'translucent_resolve')

    if rpdat.rp_stereo:
        assets.add_khafile_def('rp_stereo')
        assets.add_khafile_def('arm_vr')
        wrd.world_defs += '_VR'
        assets.add(assets_path + 'vr.png')
        assets.add_embedded_data('vr.png')

    assets.add_khafile_def('rp_gi={0}'.format(rpdat.rp_gi))
    if rpdat.rp_gi != 'Off':
        assets.add_khafile_def('rp_gi={0}'.format(rpdat.rp_gi))        
        assets.add_khafile_def('rp_voxelgi_resolution={0}'.format(rpdat.rp_voxelgi_resolution))
        assets.add_khafile_def('rp_voxelgi_resolution_z={0}'.format(rpdat.rp_voxelgi_resolution_z))
        if rpdat.rp_voxelgi_hdr:
            assets.add_khafile_def('rp_voxelgi_hdr')
        if rpdat.arm_voxelgi_shadows:
            assets.add_khafile_def('rp_voxelgi_shadows')
        if rpdat.arm_voxelgi_refraction:
            assets.add_khafile_def('rp_voxelgi_refraction')

    if rpdat.arm_rp_resolution != 'Display':
        assets.add_khafile_def('rp_resolution={0}'.format(rpdat.arm_rp_resolution))

    assets.add_khafile_def('rp_ssgi={0}'.format(rpdat.rp_ssgi))
    if rpdat.rp_ssgi != 'Off':
        wrd.world_defs += '_SSAO'
        if rpdat.rp_ssgi == 'SSAO':
            assets.add_shader2('ssao_pass', 'ssao_pass')
            assets.add_shader2('blur_edge_pass', 'blur_edge_pass')
            assets.add(assets_path + 'noise8.png')
            assets.add_embedded_data('noise8.png')
        else:
            assets.add_shader2('ssgi_pass', 'ssgi_pass')
            assets.add_shader2('ssgi_blur_pass', 'ssgi_blur_pass')

    if rpdat.rp_renderer == 'Deferred':
        assets.add_shader2('deferred_indirect', 'deferred_indirect')
        assets.add_shader2('deferred_light', 'deferred_light')
        assets.add_shader2('deferred_light_quad', 'deferred_light_quad')

    if rpdat.rp_rendercapture:
        assets.add_khafile_def('rp_rendercapture')
        assets.add_khafile_def('rp_rendercapture_format={0}'.format(wrd.rp_rendercapture_format))
        assets.add_shader2('copy_pass', 'copy_pass')
        
    if rpdat.rp_volumetriclight:
        assets.add_khafile_def('rp_volumetriclight')
        assets.add_shader2('volumetric_light_quad', 'volumetric_light_quad')
        assets.add_shader2('volumetric_light', 'volumetric_light')
        assets.add_shader2('blur_edge_pass', 'blur_edge_pass')

    if rpdat.rp_decals:
        assets.add_khafile_def('rp_decals')

    if rpdat.rp_ocean:
        assets.add_khafile_def('rp_ocean')
        assets.add_shader2('water_pass', 'water_pass')

    if rpdat.rp_blending_state != 'Off':
        assets.add_khafile_def('rp_blending')

    if rpdat.rp_bloom:
        assets.add_khafile_def('rp_bloom')
        assets.add_shader2('bloom_pass', 'bloom_pass')
        assets.add_shader2('blur_gaus_pass', 'blur_gaus_pass')

    if rpdat.rp_sss:
        assets.add_khafile_def('rp_sss')
        wrd.world_defs += '_SSS'
        assets.add_shader2('sss_pass', 'sss_pass')

    if rpdat.rp_ssr:
        assets.add_khafile_def('rp_ssr')
        assets.add_shader2('ssr_pass', 'ssr_pass')
        assets.add_shader2('blur_adaptive_pass', 'blur_adaptive_pass')
        if rpdat.arm_ssr_half_res:
            assets.add_khafile_def('rp_ssr_half')

    if rpdat.rp_motionblur != 'Off':
        assets.add_khafile_def('rp_motionblur={0}'.format(rpdat.rp_motionblur))
        assets.add_shader2('copy_pass', 'copy_pass')
        if rpdat.rp_motionblur == 'Camera':
            assets.add_shader2('motion_blur_pass', 'motion_blur_pass')
        else:
            assets.add_shader2('motion_blur_veloc_pass', 'motion_blur_veloc_pass')

    if rpdat.rp_compositornodes and rpdat.rp_autoexposure:
        assets.add_khafile_def('rp_autoexposure')

    if rpdat.rp_dynres:
        assets.add_khafile_def('rp_dynres')
