import bpy
from bpy.types import Menu, Panel, UIList
from bpy.props import *
import arm.nodes_renderpath as nodes_renderpath
import arm.make_renderer as make_renderer
import arm.assets as assets

updating_preset = False

def set_preset(self, context, preset):
    global updating_preset

    cam = bpy.context.camera
    if cam == None:
        return

    wrd = bpy.data.worlds['Arm']

    updating_preset = True

    if preset == 'Low':
        cam.rp_renderer = 'Forward'
        cam.rp_materials = 'Full'
        cam.rp_shadowmap = '1024'
        cam.rp_meshes = True
        cam.rp_translucency_state = 'Off'
        cam.rp_overlays_state = 'Off'
        cam.rp_decals_state = 'Off'
        cam.rp_hdr = False
        cam.rp_worldnodes = False
        cam.rp_clearbackground = True
        cam.rp_stereo = False
        cam.rp_greasepencil = False
        cam.rp_voxelgi = False
        cam.rp_render_to_texture = False
        cam.rp_supersampling = '1'
        cam.rp_antialiasing = 'None'
        cam.rp_compositornodes = False
        cam.rp_volumetriclight = False
        cam.rp_ssao = False
        cam.rp_ssr = False
        cam.rp_bloom = False
        cam.rp_motionblur = 'None'
    elif preset == 'Forward':
        cam.rp_renderer = 'Forward'
        cam.rp_materials = 'Full'
        cam.rp_shadowmap = '2048'
        cam.rp_meshes = True
        cam.rp_translucency_state = 'Auto'
        cam.rp_overlays_state = 'Auto'
        cam.rp_decals_state = 'Auto'
        cam.rp_hdr = True
        cam.rp_worldnodes = True
        cam.rp_clearbackground = False
        cam.rp_stereo = False
        cam.rp_greasepencil = False
        cam.rp_voxelgi = False
        cam.rp_render_to_texture = True
        cam.rp_supersampling = '1'
        cam.rp_antialiasing = 'SMAA'
        cam.rp_compositornodes = True
        cam.rp_volumetriclight = False
        cam.rp_ssao = True
        cam.rp_ssr = True
        cam.rp_bloom = False
        cam.rp_motionblur = 'None'
    elif preset == 'Deferred':
        cam.rp_renderer = 'Deferred'
        cam.rp_shadowmap = '2048'
        cam.rp_meshes = True
        cam.rp_translucency_state = 'Auto'
        cam.rp_overlays_state = 'Auto'
        cam.rp_decals_state = 'Auto'
        cam.rp_hdr = True
        cam.rp_worldnodes = True
        cam.rp_clearbackground = False
        cam.rp_stereo = False
        cam.rp_greasepencil = False
        cam.rp_voxelgi = False
        cam.rp_render_to_texture = True
        cam.rp_supersampling = '1'
        cam.rp_antialiasing = 'FXAA'
        cam.rp_compositornodes = True
        cam.rp_volumetriclight = False
        cam.rp_ssao = True
        cam.rp_ssr = False
        cam.rp_bloom = False
        cam.rp_motionblur = 'None'
    elif preset == 'Max':
        cam.rp_renderer = 'Deferred'
        cam.rp_shadowmap = '4096'
        cam.rp_meshes = True
        cam.rp_translucency_state = 'Auto'
        cam.rp_overlays_state = 'Auto'
        cam.rp_decals_state = 'Auto'
        cam.rp_hdr = True
        cam.rp_worldnodes = True
        cam.rp_clearbackground = False
        cam.rp_stereo = False
        cam.rp_greasepencil = False
        cam.rp_voxelgi = False
        cam.rp_render_to_texture = True
        cam.rp_supersampling = '1'
        cam.rp_antialiasing = 'TAA'
        cam.rp_compositornodes = True
        cam.rp_volumetriclight = False
        cam.rp_ssao = True
        cam.rp_ssr = True
        cam.rp_bloom = False
        cam.rp_motionblur = 'None'
    elif preset == 'Render Capture':
        cam.rp_renderer = 'Deferred'
        cam.rp_shadowmap = '8192'
        cam.rp_meshes = True
        cam.rp_translucency_state = 'Auto'
        cam.rp_overlays_state = 'Auto'
        cam.rp_decals_state = 'Auto'
        cam.rp_hdr = True
        cam.rp_worldnodes = True
        cam.rp_clearbackground = False
        cam.rp_stereo = False
        cam.rp_greasepencil = False
        cam.rp_voxelgi = True
        cam.rp_voxelgi_resolution[0] = 256
        cam.rp_voxelgi_resolution[1] = 256
        cam.rp_voxelgi_resolution[2] = 256
        cam.rp_render_to_texture = True
        cam.rp_supersampling = '2'
        cam.rp_antialiasing = 'TAA'
        cam.rp_compositornodes = True
        cam.rp_volumetriclight = False
        cam.rp_ssao = True
        cam.rp_ssr = True
        cam.rp_bloom = True
        cam.rp_motionblur = 'None'
        wrd.lighting_model = 'Cycles'
        wrd.generate_pcss_state = 'On'
    elif preset == 'Deferred Plus':
        cam.rp_renderer = 'Deferred Plus'
        cam.rp_shadowmap = '4096'
        cam.rp_meshes = True
        cam.rp_translucency_state = 'Auto'
        cam.rp_overlays_state = 'Auto'
        cam.rp_decals_state = 'Auto'
        cam.rp_hdr = True
        cam.rp_worldnodes = True
        cam.rp_clearbackground = False
        cam.rp_stereo = False
        cam.rp_greasepencil = False
        cam.rp_voxelgi = False
        cam.rp_render_to_texture = True
        cam.rp_supersampling = '1'
        cam.rp_antialiasing = 'TAA'
        cam.rp_compositornodes = True
        cam.rp_volumetriclight = False
        cam.rp_ssao = True
        cam.rp_ssr = True
        cam.rp_bloom = False
        cam.rp_motionblur = 'None'
    elif preset == 'VR Low':
        cam.rp_renderer = 'Forward'
        cam.rp_materials = 'Restricted'
        cam.rp_shadowmap = '1024'
        cam.rp_meshes = True
        cam.rp_translucency_state = 'Off'
        cam.rp_overlays_state = 'Off'
        cam.rp_decals_state = 'Off'
        cam.rp_hdr = False
        cam.rp_worldnodes = False
        cam.rp_clearbackground = True
        cam.rp_stereo = True
        cam.rp_greasepencil = False
        cam.rp_voxelgi = False
        cam.rp_render_to_texture = False
        cam.rp_supersampling = '1'
        cam.rp_antialiasing = 'None'
        cam.rp_compositornodes = False
        cam.rp_volumetriclight = False
        cam.rp_ssao = False
        cam.rp_ssr = False
        cam.rp_bloom = False
        cam.rp_motionblur = 'None'
    elif preset == 'Grease Pencil':
        cam.rp_renderer = 'Forward'
        cam.rp_materials = 'Restricted'
        cam.rp_shadowmap = 'None'
        cam.rp_meshes = False
        cam.rp_translucency_state = 'Off'
        cam.rp_overlays_state = 'Off'
        cam.rp_decals_state = 'Off'
        cam.rp_hdr = False
        cam.rp_worldnodes = False
        cam.rp_clearbackground = True
        cam.rp_stereo = False
        cam.rp_greasepencil = True
        cam.rp_render_to_texture = False
        cam.rp_supersampling = '1'
        cam.rp_antialiasing = 'None'
        cam.rp_compositornodes = False
        cam.rp_volumetriclight = False
        cam.rp_ssao = False
        cam.rp_ssr = False
        cam.rp_bloom = False
        cam.rp_motionblur = 'None'

    updating_preset = False
    set_renderpath(self, context)

def set_renderpath(self, context):
    global updating_preset
    if updating_preset == True:
        return
    if bpy.context.camera == None:
        return
    # assets.invalidate_compiled_data(self, context)
    assets.invalidate_shader_cache(self, context)
    make_renderer.make_renderer(bpy.context.camera)
    bpy.context.camera.renderpath_path = 'armory_default'

# Menu in camera data region
class GenRPDataPropsPanel(bpy.types.Panel):
    bl_label = "Armory Render Path"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}
 
    def draw(self, context):
        layout = self.layout
        obj = bpy.context.object
        if obj == None:
            return

        dat = obj.data
        wrd = bpy.data.worlds['Arm']

        if obj.type == 'CAMERA':
            layout.prop(dat, "rp_preset")
            layout.separator()
            layout.prop(dat, "rp_renderer")
            layout.prop(dat, "rp_materials")
            layout.prop(wrd, 'lighting_model')
            layout.prop(dat, "rp_shadowmap")
            layout.prop(dat, "rp_meshes")
            layout.prop(dat, "rp_translucency_state")
            layout.prop(dat, "rp_overlays_state")
            layout.prop(dat, "rp_decals_state")
            layout.prop(dat, "rp_sss_state")
            if dat.rp_sss_state == 'On':
                layout.prop(wrd, 'sss_width')
            layout.prop(dat, "rp_hdr")
            layout.prop(dat, "rp_worldnodes")
            if not dat.rp_worldnodes:
                layout.prop(dat, "rp_clearbackground")
            layout.prop(dat, "rp_stereo")
            layout.prop(dat, "rp_greasepencil")
            layout.prop(dat, 'rp_voxelgi')
            if dat.rp_voxelgi:
                layout.prop(dat, 'rp_voxelgi_resolution')
                layout.prop(wrd, 'generate_voxelgi_dimensions')
                row = layout.row()
                row.prop(wrd, 'voxelgi_diff')
                row.prop(wrd, 'voxelgi_spec')
                row = layout.row()
                row.prop(wrd, 'voxelgi_occ')
                row.prop(wrd, 'voxelgi_env')
                row = layout.row()
                row.prop(wrd, 'voxelgi_step')
                row.prop(wrd, 'voxelgi_range')
                row = layout.row()
                row.prop(wrd, 'voxelgi_revoxelize')
                row.prop(wrd, 'voxelgi_multibounce')
                row.prop(dat, 'rp_voxelgi_hdr')

            layout.separator()
            layout.prop(dat, "rp_render_to_texture")
            if dat.rp_render_to_texture:
                layout.prop(dat, "rp_supersampling")
                layout.prop(dat, "rp_antialiasing")
                layout.prop(dat, "rp_compositornodes")
                layout.prop(dat, "rp_volumetriclight")
                layout.prop(dat, "rp_ssao")
                layout.prop(dat, "rp_ssr")
                layout.prop(dat, "rp_bloom")
                layout.prop(dat, "rp_motionblur")

class PropsRPDataPropsPanel(bpy.types.Panel):
    bl_label = "Armory Render Props"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}
 
    def draw(self, context):
        layout = self.layout
        obj = bpy.context.object
        if obj == None:
            return

        wrd = bpy.data.worlds['Arm']

        if obj.type == 'CAMERA':
            layout.prop(wrd, 'generate_pcss_state')
            if wrd.generate_pcss_state == 'On' or wrd.generate_pcss_state == 'Auto':
                layout.prop(wrd, 'generate_pcss_rings')
            layout.prop(wrd, 'generate_ssrs')
            
            layout.prop(wrd, 'arm_samples_per_pixel')
            row = layout.row()
            row.prop(wrd, 'generate_gpu_skin')
            if wrd.generate_gpu_skin:
                row.prop(wrd, 'generate_gpu_skin_max_bones_auto')
                if not wrd.generate_gpu_skin_max_bones_auto:
                    layout.prop(wrd, 'generate_gpu_skin_max_bones')
            layout.prop(wrd, 'texture_filtering_state')
            layout.prop(wrd, 'tessellation_enabled')
            layout.prop(wrd, 'force_no_culling')
            layout.prop(wrd, 'generate_two_sided_area_lamp')
            
            layout.prop(wrd, 'arm_camera_props_advanced')
            if wrd.arm_camera_props_advanced:

                layout.prop(wrd, 'generate_clouds')
                if wrd.generate_clouds:
                    layout.prop(wrd, 'generate_clouds_density')
                    layout.prop(wrd, 'generate_clouds_size')
                    layout.prop(wrd, 'generate_clouds_lower')
                    layout.prop(wrd, 'generate_clouds_upper')
                    layout.prop(wrd, 'generate_clouds_wind')
                    layout.prop(wrd, 'generate_clouds_secondary')
                    layout.prop(wrd, 'generate_clouds_precipitation')
                    layout.prop(wrd, 'generate_clouds_eccentricity')
                
                layout.label('SSAO')
                # layout.prop(wrd, 'generate_ssao')
                # if wrd.generate_ssao:
                layout.prop(wrd, 'generate_ssao_size')
                layout.prop(wrd, 'generate_ssao_strength')
                layout.prop(wrd, 'generate_ssao_half_res')
                
                layout.label('Bloom')
                # layout.prop(wrd, 'generate_bloom')
                # if wrd.generate_bloom:
                layout.prop(wrd, 'generate_bloom_threshold')
                layout.prop(wrd, 'generate_bloom_strength')
                layout.prop(wrd, 'generate_bloom_radius')
                
                layout.label('Motion Blur')
                # layout.prop(wrd, 'generate_motion_blur')
                # if wrd.generate_motion_blur:
                layout.prop(wrd, 'generate_motion_blur_intensity')
                
                layout.label('SSR')
                # layout.prop(wrd, 'generate_ssr')
                # if wrd.generate_ssr:
                layout.prop(wrd, 'generate_ssr_ray_step')
                layout.prop(wrd, 'generate_ssr_min_ray_step')
                layout.prop(wrd, 'generate_ssr_search_dist')
                layout.prop(wrd, 'generate_ssr_falloff_exp')
                layout.prop(wrd, 'generate_ssr_jitter')
                layout.prop(wrd, 'generate_ssr_half_res')

                layout.label('SSRS')
                layout.prop(wrd, 'generate_ssrs_ray_step')

                layout.label('Volumetric Light')
                # layout.prop(wrd, 'generate_volumetric_light')
                # if wrd.generate_volumetric_light:
                layout.prop(wrd, 'generate_volumetric_light_air_turbidity')
                layout.prop(wrd, 'generate_volumetric_light_air_color')

def register():
    bpy.utils.register_class(GenRPDataPropsPanel)
    bpy.utils.register_class(PropsRPDataPropsPanel)

def unregister():
    bpy.utils.unregister_class(GenRPDataPropsPanel)
    bpy.utils.unregister_class(PropsRPDataPropsPanel)
