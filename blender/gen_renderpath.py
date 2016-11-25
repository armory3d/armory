import bpy
import nodes_renderpath
from bpy.types import Menu, Panel, UIList
from bpy.props import *

def check_saved(self):
    if bpy.data.filepath == "":
        self.report({"ERROR"}, "Save blend file first")
        return False
    return True

class ReimportPathsMenu(bpy.types.Menu):
    bl_label = "OK?"
    bl_idname = "OBJECT_MT_reimport_paths_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("arm.reimport_paths")

class ReimportPathsButtonMenu(bpy.types.Operator):
    '''Reimport default render paths'''
    bl_label = "Reimport Defaults"
    bl_idname = "arm.reimport_paths_menu"
 
    def execute(self, context):
        bpy.ops.wm.call_menu(name=ReimportPathsMenu.bl_idname)
        return {"FINISHED"}

class ReimportPathsButton(bpy.types.Operator):
    '''Reimport default render paths'''
    bl_label = "Reimport Defaults"
    bl_idname = "arm.reimport_paths"
 
    def execute(self, context):
        nodes_renderpath.load_library()
        return{'FINISHED'}

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

        if obj.type == 'CAMERA':
            # layout.prop(obj.data, "rp_renderer")
            # layout.prop(obj.data, "rp_supersampling")
            # layout.prop(obj.data, "rp_antialiasing")
            # layout.prop(obj.data, "rp_shadowmap")
            # layout.prop(obj.data, "rp_hdr")
            # layout.prop(obj.data, "rp_worldnodes")
            # layout.prop(obj.data, "rp_compositornodes")
            # layout.prop(obj.data, "rp_volumetriclight")
            # layout.prop(obj.data, "rp_ssao")
            # layout.prop(obj.data, "rp_ssr")
            # layout.prop(obj.data, "rp_bloom")
            # layout.prop(obj.data, "rp_motionblur")
            # layout.prop(obj.data, "rp_translucency")
            # layout.prop(obj.data, "rp_decals")
            # layout.prop(obj.data, "rp_overlays")
            
            # layout.operator("arm.gen_renderpath")
            layout.operator("arm.reimport_paths_menu")

class EffectsRPDataPropsPanel(bpy.types.Panel):
    bl_label = "Armory Render Effects"
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
                layout.prop(wrd, 'generate_pcss')
                if wrd.generate_pcss:
                    layout.prop(wrd, 'generate_pcss_rings')
            
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

class ArmoryGenRenderPathButton(bpy.types.Operator):
    '''Auto-generate render path based on settings'''
    bl_idname = 'arm.gen_renderpath'
    bl_label = 'Generate Render Path'
 
    def execute(self, context):
        return{'FINISHED'}

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
