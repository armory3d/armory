import bpy
import nodes_renderpath
from bpy.types import Menu, Panel, UIList
from bpy.props import *
import make_renderer
import assets

def set_preset(preset):
    cam = bpy.context.camera
    if cam == None:
        return

    if preset == 'Forward Low':
        cam.rp_renderer = 'Forward'
        cam.rp_shadowmap = '1024'
        cam.rp_meshes = True
        cam.rp_translucency = False
        cam.rp_overlays = False
        cam.rp_decals = False
        cam.rp_hdr = False
        cam.rp_worldnodes = False
        cam.rp_stereo = False
        cam.rp_greasepencil = False
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
        cam.rp_shadowmap = '2048'
        cam.rp_meshes = True
        cam.rp_translucency = False
        cam.rp_overlays = False
        cam.rp_decals = False
        cam.rp_hdr = True
        cam.rp_worldnodes = True
        cam.rp_stereo = False
        cam.rp_greasepencil = False
        cam.rp_render_to_texture = True
        cam.rp_supersampling = '1'
        cam.rp_antialiasing = 'FXAA'
        cam.rp_compositornodes = True
        cam.rp_volumetriclight = False
        cam.rp_ssao = False
        cam.rp_ssr = False
        cam.rp_bloom = False
        cam.rp_motionblur = 'None'
    elif preset == 'Forward High':
        cam.rp_renderer = 'Forward'
        cam.rp_shadowmap = '4096'
        cam.rp_meshes = True
        cam.rp_translucency = True
        cam.rp_overlays = False
        cam.rp_decals = False
        cam.rp_hdr = True
        cam.rp_worldnodes = True
        cam.rp_stereo = False
        cam.rp_greasepencil = False
        cam.rp_render_to_texture = True
        cam.rp_supersampling = '1'
        cam.rp_antialiasing = 'SMAA'
        cam.rp_compositornodes = True
        cam.rp_volumetriclight = False
        cam.rp_ssao = True
        cam.rp_ssr = True
        cam.rp_bloom = False
        cam.rp_motionblur = 'None'
    elif preset == 'Deferred Low':
        cam.rp_renderer = 'Deferred'
        cam.rp_shadowmap = '2048'
        cam.rp_meshes = True
        cam.rp_translucency = False
        cam.rp_overlays = False
        cam.rp_decals = False
        cam.rp_hdr = True
        cam.rp_worldnodes = True
        cam.rp_stereo = False
        cam.rp_greasepencil = False
        cam.rp_render_to_texture = True
        cam.rp_supersampling = '1'
        cam.rp_antialiasing = 'FXAA'
        cam.rp_compositornodes = True
        cam.rp_volumetriclight = False
        cam.rp_ssao = True
        cam.rp_ssr = False
        cam.rp_bloom = False
        cam.rp_motionblur = 'None'
    elif preset == 'Deferred':
        cam.rp_renderer = 'Deferred'
        cam.rp_shadowmap = '2048'
        cam.rp_meshes = True
        cam.rp_translucency = False
        cam.rp_overlays = False
        cam.rp_decals = False
        cam.rp_hdr = True
        cam.rp_worldnodes = True
        cam.rp_stereo = False
        cam.rp_greasepencil = False
        cam.rp_render_to_texture = True
        cam.rp_supersampling = '1'
        cam.rp_antialiasing = 'SMAA'
        cam.rp_compositornodes = True
        cam.rp_volumetriclight = False
        cam.rp_ssao = True
        cam.rp_ssr = True
        cam.rp_bloom = True
        cam.rp_motionblur = 'None'
    elif preset == 'Deferred High':
        cam.rp_renderer = 'Deferred'
        cam.rp_shadowmap = '4096'
        cam.rp_meshes = True
        cam.rp_translucency = True
        cam.rp_overlays = False
        cam.rp_decals = False
        cam.rp_hdr = True
        cam.rp_worldnodes = True
        cam.rp_stereo = False
        cam.rp_greasepencil = False
        cam.rp_render_to_texture = True
        cam.rp_supersampling = '1'
        cam.rp_antialiasing = 'TAA'
        cam.rp_compositornodes = True
        cam.rp_volumetriclight = False
        cam.rp_ssao = True
        cam.rp_ssr = True
        cam.rp_bloom = True
        cam.rp_motionblur = 'None'
    elif preset == 'VR Low':
        cam.rp_renderer = 'Forward'
        cam.rp_shadowmap = '1024'
        cam.rp_meshes = True
        cam.rp_translucency = False
        cam.rp_overlays = False
        cam.rp_decals = False
        cam.rp_hdr = False
        cam.rp_worldnodes = True
        cam.rp_stereo = True
        cam.rp_greasepencil = False
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
        cam.rp_shadowmap = 'None'
        cam.rp_meshes = False
        cam.rp_translucency = False
        cam.rp_overlays = False
        cam.rp_decals = False
        cam.rp_hdr = False
        cam.rp_worldnodes = False
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

        if obj.type == 'CAMERA':
            layout.prop(dat, "rp_preset")
            layout.separator()
            layout.prop(dat, "rp_renderer")
            layout.prop(dat, "rp_shadowmap")
            layout.prop(dat, "rp_meshes")
            layout.prop(dat, "rp_translucency")
            layout.prop(dat, "rp_overlays")
            layout.prop(dat, "rp_decals")
            layout.prop(dat, "rp_hdr")
            layout.prop(dat, "rp_worldnodes")
            layout.prop(dat, "rp_stereo")
            # layout.prop(dat, "rp_greasepencil")

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
            
            layout.operator("arm.set_renderpath")

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
            layout.prop(wrd, 'generate_shadows')
            if wrd.generate_shadows:
                layout.prop(wrd, 'generate_pcss_state')
                if wrd.generate_pcss_state == 'On' or wrd.generate_pcss_state == 'Auto':
                    layout.prop(wrd, 'generate_pcss_rings')
            
            layout.prop(wrd, 'arm_samples_per_pixel')
            layout.prop(wrd, 'generate_gpu_skin')
            if wrd.generate_gpu_skin:
                layout.prop(wrd, 'generate_gpu_skin_max_bones')
            layout.prop(wrd, 'anisotropic_filtering_state')
            layout.prop(wrd, 'diffuse_model')
            layout.prop(wrd, 'tessellation_enabled')
            layout.prop(wrd, 'force_no_culling')
            layout.prop(wrd, 'voxelgi')
            if wrd.voxelgi:
                layout.prop(wrd, 'voxelgi_dimensions')

            
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
                
                layout.label('Screen-Space Ambient Occlusion')
                # layout.prop(wrd, 'generate_ssao')
                # if wrd.generate_ssao:
                layout.prop(wrd, 'generate_ssao_size')
                layout.prop(wrd, 'generate_ssao_strength')
                layout.prop(wrd, 'generate_ssao_texture_scale')
                
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
                
                layout.label('Screen-Space Reflections')
                # layout.prop(wrd, 'generate_ssr')
                # if wrd.generate_ssr:
                layout.prop(wrd, 'generate_ssr_ray_step')
                layout.prop(wrd, 'generate_ssr_min_ray_step')
                layout.prop(wrd, 'generate_ssr_search_dist')
                layout.prop(wrd, 'generate_ssr_falloff_exp')
                layout.prop(wrd, 'generate_ssr_jitter')
                layout.prop(wrd, 'generate_ssr_texture_scale')

                layout.label('Volumetric Light')
                # layout.prop(wrd, 'generate_volumetric_light')
                # if wrd.generate_volumetric_light:
                layout.prop(wrd, 'generate_volumetric_light_air_turbidity')
                layout.prop(wrd, 'generate_volumetric_light_air_color')

class ArmorySetRenderPathButton(bpy.types.Operator):
    '''Auto-generate render path based on settings'''
    bl_idname = 'arm.set_renderpath'
    bl_label = 'Set'
 
    def execute(self, context):
        if bpy.context.camera == None:
            return {'CANCELLED'}
        assets.invalidate_shader_cache(self, context)
        make_renderer.make_renderer(bpy.context.camera)
        bpy.context.camera.renderpath_path = 'armory_default'
        return {'FINISHED'}

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
