from typing import Callable, Optional

import os
import bpy

import arm.api
import arm.assets as assets
import arm.log as log
import arm.make_state as state
import arm.utils

if arm.is_reload(__name__):
    arm.api = arm.reload_module(arm.api)
    assets = arm.reload_module(assets)
    log = arm.reload_module(log)
    state = arm.reload_module(state)
    arm.utils = arm.reload_module(arm.utils)
else:
    arm.enable_reload(__name__)

callback: Optional[Callable[[], None]] = None


def add_world_defs():
    wrd = bpy.data.worlds['Arm']
    rpdat = arm.utils.get_rp()

    # Screen-space ray-traced shadows
    if rpdat.arm_ssrs:
        wrd.world_defs += '_SSRS'

    if rpdat.arm_micro_shadowing:
        wrd.world_defs += '_MicroShadowing'

    if rpdat.arm_two_sided_area_light:
        wrd.world_defs += '_TwoSidedAreaLight'

    # Store contexts
    if rpdat.rp_hdr == False:
        wrd.world_defs += '_LDR'

    if wrd.arm_light_ies_texture != '':
        wrd.world_defs += '_LightIES'
        assets.add_embedded_data('iestexture.png')

    if wrd.arm_light_clouds_texture != '':
        wrd.world_defs += '_LightClouds'
        assets.add_embedded_data('cloudstexture.png')

    if rpdat.rp_renderer == 'Deferred':
        assets.add_khafile_def('arm_deferred')
        wrd.world_defs += '_Deferred'

    # Shadows
    if rpdat.rp_shadows:
        wrd.world_defs += '_ShadowMap'
        if rpdat.rp_shadowmap_cascades != '1':
            wrd.world_defs += '_CSM'
            assets.add_khafile_def('arm_csm')
        if rpdat.rp_shadowmap_atlas:
            assets.add_khafile_def('arm_shadowmap_atlas')
            wrd.world_defs += '_ShadowMapAtlas'
            if rpdat.rp_shadowmap_atlas_single_map:
                assets.add_khafile_def('arm_shadowmap_atlas_single_map')
                wrd.world_defs += '_SingleAtlas'
            assets.add_khafile_def('rp_shadowmap_atlas_max_size_point={0}'.format(int(rpdat.rp_shadowmap_atlas_max_size_point)))
            assets.add_khafile_def('rp_shadowmap_atlas_max_size_spot={0}'.format(int(rpdat.rp_shadowmap_atlas_max_size_spot)))
            assets.add_khafile_def('rp_shadowmap_atlas_max_size_sun={0}'.format(int(rpdat.rp_shadowmap_atlas_max_size_sun)))
            assets.add_khafile_def('rp_shadowmap_atlas_max_size={0}'.format(int(rpdat.rp_shadowmap_atlas_max_size)))

            assets.add_khafile_def('rp_max_lights_cluster={0}'.format(int(rpdat.rp_max_lights_cluster)))
            assets.add_khafile_def('rp_max_lights={0}'.format(int(rpdat.rp_max_lights)))
            if rpdat.rp_shadowmap_atlas_lod:
                assets.add_khafile_def('arm_shadowmap_atlas_lod')
                assets.add_khafile_def('rp_shadowmap_atlas_lod_subdivisions={0}'.format(int(rpdat.rp_shadowmap_atlas_lod_subdivisions)))

    # SS
    if rpdat.rp_ssgi == 'RTGI' or rpdat.rp_ssgi == 'RTAO':
        if rpdat.rp_ssgi == 'RTGI':
            wrd.world_defs += '_RTGI'
        if rpdat.arm_ssgi_rays == '9':
            wrd.world_defs += '_SSGICone9'
    if rpdat.rp_autoexposure:
        wrd.world_defs += '_AutoExposure'

    # GI
    voxelgi = False
    voxelao = False
    has_voxels = arm.utils.voxel_support()
    if has_voxels and rpdat.arm_material_model == 'Full':
        if rpdat.rp_voxels == 'Voxel GI':
            voxelgi = True
        elif rpdat.rp_voxels == 'Voxel AO':
            voxelao = True

    if voxelgi or voxelao:
        assets.add_khafile_def('arm_voxelgi')# might be uneeded
        wrd.world_defs += "_VoxelCones" + rpdat.arm_voxelgi_cones
        if rpdat.arm_voxelgi_shadows:
            wrd.world_defs += '_VoxelShadow'

        if rpdat.arm_voxelgi_temporal:
            wrd.world_defs += '_VoxelTemporal'
            assets.add_khafile_def('arm_voxelgi_temporal')

        if voxelgi:
            wrd.world_defs += '_VoxelGI'
            if rpdat.arm_voxelgi_refraction:
                wrd.world_defs += '_VoxelRefract'
                assets.add_khafile_def('rp_voxelgi_refract')

            if rpdat.arm_voxelgi_bounces == '2':
                wrd.world_defs += '_VoxelBounces'
                assets.add_khafile_def('arm_voxelgi_bounces')

        elif voxelao:
            wrd.world_defs += '_VoxelAOvar' # Write a shader variant
            if rpdat.arm_voxelgi_occ == 0.0:
                wrd.world_defs += '_VoxelAONoTrace'


    if arm.utils.get_legacy_shaders() or 'ios' in state.target:
        wrd.world_defs += '_Legacy'
        assets.add_khafile_def('arm_legacy')

    # Light defines
    point_lights = 0
    for bo in bpy.data.objects: # TODO: temp
        if bo.arm_export and bo.type == 'LIGHT':
            light = bo.data
            if light.type == 'AREA' and '_LTC' not in wrd.world_defs:
                point_lights += 1
                wrd.world_defs += '_LTC'
                assets.add_khafile_def('arm_ltc')
            if light.type == 'SUN' and '_Sun' not in wrd.world_defs:
                wrd.world_defs += '_Sun'
            if light.type == 'POINT' or light.type == 'SPOT':
                point_lights += 1
                if light.type == 'SPOT' and '_Spot' not in wrd.world_defs:
                    wrd.world_defs += '_Spot'
                    assets.add_khafile_def('arm_spot')

    if not rpdat.rp_shadowmap_atlas:
        if point_lights == 1:
            wrd.world_defs += '_SinglePoint'
        elif point_lights > 1:
            wrd.world_defs += '_Clusters'
            assets.add_khafile_def('arm_clusters')
    else:
        wrd.world_defs += '_SMSizeUniform'
        wrd.world_defs += '_Clusters'
        assets.add_khafile_def('arm_clusters')

    if '_Rad' in wrd.world_defs and '_Brdf' not in wrd.world_defs:
        wrd.world_defs += '_Brdf'


def build():
    rpdat = arm.utils.get_rp()
    project_path = arm.utils.get_fp()

    if rpdat.rp_driver != 'Armory' and arm.api.drivers[rpdat.rp_driver]['make_rpath'] != None:
        arm.api.drivers[rpdat.rp_driver]['make_rpath']()
        return

    assets_path = arm.utils.get_sdk_path() + '/armory/Assets/'
    wrd = bpy.data.worlds['Arm']

    wrd.compo_defs = ''

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

    if rpdat.rp_shadows:
        assets.add_khafile_def('rp_shadowmap')
        assets.add_khafile_def('rp_shadowmap_cascade={0}'.format(arm.utils.get_cascade_size(rpdat)))
        assets.add_khafile_def('rp_shadowmap_cube={0}'.format(rpdat.rp_shadowmap_cube))

    if arm.utils.get_gapi() == 'metal':
        assets.add_shader_pass('clear_color_depth_pass')
        assets.add_shader_pass('clear_color_pass')
        assets.add_shader_pass('clear_depth_pass')

    assets.add_khafile_def('rp_background={0}'.format(rpdat.rp_background))
    if rpdat.rp_background == 'World':
        if '_EnvClouds' in wrd.world_defs:
            assets.add(assets_path + 'clouds_base.raw')
            assets.add_embedded_data('clouds_base.raw')
            assets.add(assets_path + 'clouds_detail.raw')
            assets.add_embedded_data('clouds_detail.raw')
            assets.add(assets_path + 'clouds_map.png')
            assets.add_embedded_data('clouds_map.png')

    if rpdat.rp_renderer == 'Deferred':
        assets.add_shader_pass('copy_pass')

    if rpdat.rp_render_to_texture:
        assets.add_khafile_def('rp_render_to_texture')

        if rpdat.rp_renderer == 'Forward' and not rpdat.rp_compositornodes:
            assets.add_shader_pass('copy_pass')

        if rpdat.rp_compositornodes:
            assets.add_khafile_def('rp_compositornodes')
            compo_depth = False
            if rpdat.arm_tonemap != 'Off':
                wrd.compo_defs = '_CTone' + rpdat.arm_tonemap
            if rpdat.rp_antialiasing == 'FXAA':
                wrd.compo_defs += '_CFXAA'
            if rpdat.arm_letterbox:
                wrd.compo_defs += '_CLetterbox'
            if rpdat.arm_distort:
                wrd.compo_defs += '_CDistort'
            if rpdat.arm_grain:
                wrd.compo_defs += '_CGrain'
            if rpdat.arm_sharpen:
                wrd.compo_defs += '_CSharpen'
            if bpy.data.scenes[0].view_settings.exposure != 0.0:
                wrd.compo_defs += '_CExposure'
            if rpdat.arm_fog:
                wrd.compo_defs += '_CFog'
                compo_depth = True

            focus_distance = 0.0
            if len(bpy.data.cameras) > 0 and bpy.data.cameras[0].dof.use_dof:
                focus_distance = bpy.data.cameras[0].dof.focus_distance

            if focus_distance > 0.0:
                wrd.compo_defs += '_CDOF'
                compo_depth = True
            if rpdat.arm_fisheye:
                wrd.compo_defs += '_CFishEye'
            if rpdat.arm_vignette:
                wrd.compo_defs += '_CVignette'
            if rpdat.arm_lensflare:
                wrd.compo_defs += '_CGlare'
                compo_depth = True
            if rpdat.arm_lens:
                if os.path.isfile(project_path + '/Bundled/' + rpdat.arm_lens_texture):
                    wrd.compo_defs += '_CLensTex'
                    assets.add_embedded_data(rpdat.arm_lens_texture)
                    if rpdat.arm_lens_texture_masking:
                        wrd.compo_defs += '_CLensTexMasking'
                else:
                    log.warn('Filepath for Lens texture is invalid.')
            if rpdat.arm_lut:
                if os.path.isfile(project_path + '/Bundled/' + rpdat.arm_lut_texture):
                    wrd.compo_defs += '_CLUT'
                    assets.add_embedded_data(rpdat.arm_lut_texture)
                else:
                    log.warn('Filepath for LUT texture is invalid.')
            if '_CDOF' in wrd.compo_defs or '_CFXAA' in wrd.compo_defs or '_CSharpen' in wrd.compo_defs:
                wrd.compo_defs += '_CTexStep'
            if '_CDOF' in wrd.compo_defs or '_CFog' in wrd.compo_defs or '_CGlare' in wrd.compo_defs:
                wrd.compo_defs += '_CCameraProj'
            if compo_depth:
                wrd.compo_defs += '_CDepth'
                assets.add_khafile_def('rp_compositordepth')
            if rpdat.rp_pp:
                wrd.compo_defs += '_CPostprocess'

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

        assets.add_khafile_def('rp_ssgi={0}'.format(rpdat.rp_ssgi))
        if rpdat.rp_ssgi != 'Off':
            wrd.world_defs += '_SSAO'
            if rpdat.rp_ssgi == 'SSAO':
                assets.add_shader_pass('ssao_pass')
                assets.add_shader_pass('blur_edge_pass')
            else:
                assets.add_shader_pass('ssgi_pass')
                assets.add_shader_pass('blur_edge_pass')
            if rpdat.arm_ssgi_half_res:
                assets.add_khafile_def('rp_ssgi_half')

        if rpdat.rp_bloom:
            assets.add_khafile_def('rp_bloom')
            assets.add_shader_pass('bloom_pass')

            if rpdat.arm_bloom_quality == 'low':
                wrd.compo_defs += '_BloomQualityLow'
            elif rpdat.arm_bloom_quality == 'medium':
                wrd.compo_defs += '_BloomQualityMedium'
            else:
                wrd.compo_defs += '_BloomQualityHigh'

            if rpdat.arm_bloom_anti_flicker:
                wrd.compo_defs += '_BloomAntiFlicker'

        if rpdat.rp_ssr:
            wrd.world_defs += '_SSR'
            assets.add_khafile_def('rp_ssr')
            assets.add_shader_pass('ssr_pass')
            assets.add_shader_pass('blur_adaptive_pass')
            if rpdat.arm_ssr_half_res:
                assets.add_khafile_def('rp_ssr_half')

    if rpdat.rp_overlays:
        assets.add_khafile_def('rp_overlays')

    if rpdat.rp_translucency:
        assets.add_khafile_def('rp_translucency')
        assets.add_shader_pass('translucent_resolve')

    if rpdat.rp_stereo:
        assets.add_khafile_def('rp_stereo')
        assets.add_khafile_def('arm_vr')
        wrd.world_defs += '_VR'

    has_voxels = arm.utils.voxel_support()
    if rpdat.rp_voxels != "Off" and has_voxels and rpdat.arm_material_model == 'Full':
        assets.add_khafile_def('rp_voxels={0}'.format(rpdat.rp_voxels))
        assets.add_khafile_def('rp_voxelgi_resolution={0}'.format(rpdat.rp_voxelgi_resolution))
        assets.add_khafile_def('rp_voxelgi_resolution_z={0}'.format(rpdat.rp_voxelgi_resolution_z))

    if rpdat.arm_rp_resolution == 'Custom':
        assets.add_khafile_def('rp_resolution_filter={0}'.format(rpdat.arm_rp_resolution_filter))

    if rpdat.rp_renderer == 'Deferred':
        if rpdat.arm_material_model == 'Full':
            assets.add_shader_pass('deferred_light')
        else: # mobile, solid
            assets.add_shader_pass('deferred_light_' + rpdat.arm_material_model.lower())
            assets.add_khafile_def('rp_material_' + rpdat.arm_material_model.lower())

    if len(bpy.data.lightprobes) > 0:
        wrd.world_defs += '_Probes'
        assets.add_khafile_def('rp_probes')
        assets.add_shader_pass('probe_planar')
        assets.add_shader_pass('probe_cubemap')
        assets.add_shader_pass('copy_pass')

    if rpdat.rp_volumetriclight:
        assets.add_khafile_def('rp_volumetriclight')
        assets.add_shader_pass('volumetric_light')
        assets.add_shader_pass('blur_bilat_pass')
        assets.add_shader_pass('blur_bilat_blend_pass')
        assets.add(assets_path + 'blue_noise64.png')
        assets.add_embedded_data('blue_noise64.png')

    if rpdat.rp_decals:
        assets.add_khafile_def('rp_decals')

    if rpdat.rp_water:
        assets.add_khafile_def('rp_water')
        assets.add_shader_pass('water_pass')
        assets.add_shader_pass('copy_pass')
        assets.add(assets_path + 'water_base.png')
        assets.add_embedded_data('water_base.png')
        assets.add(assets_path + 'water_detail.png')
        assets.add_embedded_data('water_detail.png')
        assets.add(assets_path + 'water_foam.png')
        assets.add_embedded_data('water_foam.png')

    if rpdat.rp_blending:
        assets.add_khafile_def('rp_blending')

    if rpdat.rp_depth_texture:
        assets.add_khafile_def('rp_depth_texture')
        assets.add_shader_pass('copy_pass')

    if rpdat.rp_sss:
        assets.add_khafile_def('rp_sss')
        wrd.world_defs += '_SSS'
        assets.add_shader_pass('sss_pass')

    if (rpdat.rp_ssr and rpdat.arm_ssr_half_res) or (rpdat.rp_ssgi != 'Off' and rpdat.arm_ssgi_half_res):
        assets.add_shader_pass('downsample_depth')

    if rpdat.rp_motionblur != 'Off':
        assets.add_khafile_def('rp_motionblur={0}'.format(rpdat.rp_motionblur))
        assets.add_shader_pass('copy_pass')
        if rpdat.rp_motionblur == 'Camera':
            assets.add_shader_pass('motion_blur_pass')
        else:
            assets.add_shader_pass('motion_blur_veloc_pass')

    if rpdat.rp_compositornodes and rpdat.rp_autoexposure:
        assets.add_khafile_def('rp_autoexposure')
        assets.add_shader_pass('histogram_pass')

    if rpdat.rp_dynres:
        assets.add_khafile_def('rp_dynres')

    if rpdat.rp_pp:
        assets.add_khafile_def('rp_pp')

    if rpdat.rp_chromatic_aberration:
        assets.add_shader_pass('copy_pass')
        assets.add_khafile_def('rp_chromatic_aberration')
        assets.add_shader_pass('chromatic_aberration_pass')

    ignoreIrr = False

    for obj in bpy.data.objects:
        if obj.type == "MESH":
            for slot in obj.material_slots:
                mat = slot.material

                if mat: #Check if not NoneType

                    if mat.arm_ignore_irradiance:
                        ignoreIrr = True

    if ignoreIrr:
        wrd.world_defs += '_IgnoreIrr'
    gbuffer2 = '_Veloc' in wrd.world_defs or '_IgnoreIrr' in wrd.world_defs
    if gbuffer2:
        assets.add_khafile_def('rp_gbuffer2')
        wrd.world_defs += '_gbuffer2'

    if callback is not None:
        callback()


def get_num_gbuffer_rts_deferred() -> int:
    """Return the number of render targets required for the G-Buffer."""
    wrd = bpy.data.worlds['Arm']

    num = 2
    for flag in ('_gbuffer2', '_EmissionShaded', '_VoxelRefract'):
        if flag in wrd.world_defs:
            num += 1
    return num
