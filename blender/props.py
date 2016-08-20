import shutil
import bpy
import os
import json
import nodes_renderpath
from bpy.types import Menu, Panel, UIList
from bpy.props import *
import utils

def on_scene_update(context):
    edit_obj = bpy.context.edit_object
    if edit_obj is not None and edit_obj.is_updated_data is True:
        if edit_obj.type == 'MESH':
            edit_obj.data.geometry_cached = False
        elif edit_obj.type == 'ARMATURE':
            edit_obj.data.armature_cached = False

def invalidate_shader_cache(self, context):
    # compiled.glsl changed, recompile all shaders next time
    fp = utils.get_fp()
    if os.path.isdir(fp + '/compiled/ShaderResources'):
        shutil.rmtree(fp + '/compiled/ShaderResources')

def invalidate_compiled_data(self, context):
    fp = utils.get_fp()
    if os.path.isdir(fp + '/compiled/Assets'):
        shutil.rmtree(fp + '/compiled/Assets')
    if os.path.isdir(fp + '/compiled/ShaderResources'):
        shutil.rmtree(fp + '/compiled/ShaderResources')

def invalidate_geometry_data(self, context):
    fp = utils.get_fp()
    if os.path.isdir(fp + '/compiled/Assets/geoms'):
        shutil.rmtree(fp + '/compiled/Assets/geoms')

def initProperties():
    # For project
    bpy.types.World.ArmVersion = StringProperty(name = "ArmVersion", default="")
    bpy.types.World.ArmProjectTarget = EnumProperty(
        items = [('html5', 'HTML5', 'html5'), 
                 ('windows', 'Windows', 'windows'), 
                 ('osx', 'OSX', 'osx'),
                 ('linux', 'Linux', 'linux'), 
                 ('ios', 'iOS', 'ios'),
                 ('android-native', 'Android', 'android-native')],
        name = "Target", default='html5')
    bpy.types.World.ArmProjectName = StringProperty(name = "Name", default="ArmoryGame")
    bpy.types.World.ArmProjectPackage = StringProperty(name = "Package", default="game")
    bpy.types.World.ArmProjectScene = StringProperty(name = "Scene")
    bpy.types.World.ArmProjectSamplesPerPixel = IntProperty(name = "Samples per Pixel", default=1)
    bpy.types.World.ArmPhysics = EnumProperty(
        items = [('Disabled', 'Disabled', 'Disabled'), 
                 ('Bullet', 'Bullet', 'Bullet')],
        name = "Physics", default='Bullet')
    bpy.types.World.ArmKhafile = StringProperty(name = "Khafile")
    bpy.types.World.ArmMinimize = BoolProperty(name="Minimize Data", default=True, update=invalidate_compiled_data)
    bpy.types.World.ArmOptimizeGeometry = BoolProperty(name="Optimize Geometry", default=False, update=invalidate_geometry_data)
    bpy.types.World.ArmSampledAnimation = BoolProperty(name="Sampled Animation", default=False, update=invalidate_compiled_data)
    bpy.types.World.ArmDeinterleavedBuffers = BoolProperty(name="Deinterleaved Buffers", default=False)
    bpy.types.World.ArmCacheShaders = BoolProperty(name="Cache Shaders", default=True)
    bpy.types.World.ArmPlayViewportCamera = BoolProperty(name="Viewport Camera", default=False)
    bpy.types.World.ArmPlayViewportNavigation = EnumProperty(
        items = [('None', 'None', 'None'), 
                 ('Walk', 'Walk', 'Walk')],
        name = "Navigation", default='Walk')
    bpy.types.World.ArmPlayConsole = BoolProperty(name="Debug Console", default=False)
    bpy.types.World.ArmPlayDeveloperTools = BoolProperty(name="Developer Tools", default=False)
    bpy.types.World.ArmPlayRuntime = EnumProperty(
        items = [('Electron', 'Electron', 'Electron'), 
                 ('Browser', 'Browser', 'Browser'),
                 ('Native', 'Native', 'Native'),
                 ('Krom', 'Krom', 'Krom')],
        name = "Runtime", default='Electron')

    # For object
    bpy.types.Object.instanced_children = bpy.props.BoolProperty(name="Instanced Children", default=False)
    bpy.types.Object.instanced_children_loc_x = bpy.props.BoolProperty(name="X", default=True)
    bpy.types.Object.instanced_children_loc_y = bpy.props.BoolProperty(name="Y", default=True)
    bpy.types.Object.instanced_children_loc_z = bpy.props.BoolProperty(name="Z", default=True)
    bpy.types.Object.instanced_children_rot_x = bpy.props.BoolProperty(name="X", default=False)
    bpy.types.Object.instanced_children_rot_y = bpy.props.BoolProperty(name="Y", default=False)
    bpy.types.Object.instanced_children_rot_z = bpy.props.BoolProperty(name="Z", default=False)
    bpy.types.Object.instanced_children_scale_x = bpy.props.BoolProperty(name="X", default=False)
    bpy.types.Object.instanced_children_scale_y = bpy.props.BoolProperty(name="Y", default=False)
    bpy.types.Object.instanced_children_scale_z = bpy.props.BoolProperty(name="Z", default=False)
    bpy.types.Object.override_material = bpy.props.BoolProperty(name="Override Material", default=False)
    bpy.types.Object.override_material_name = bpy.props.StringProperty(name="Name", default="")
    bpy.types.Object.game_export = bpy.props.BoolProperty(name="Export", default=True)
    bpy.types.Object.spawn = bpy.props.BoolProperty(name="Spawn", description="Auto-add this node when creating scene", default=True)
    # For geometry
    bpy.types.Mesh.geometry_cached = bpy.props.BoolProperty(name="Geometry Cached", default=False)
    bpy.types.Mesh.geometry_cached_verts = bpy.props.IntProperty(name="Last Verts", default=0)
    bpy.types.Mesh.geometry_cached_edges = bpy.props.IntProperty(name="Last Edges", default=0)
    bpy.types.Mesh.static_usage = bpy.props.BoolProperty(name="Static Usage", default=True)
    bpy.types.Curve.static_usage = bpy.props.BoolProperty(name="Static Usage", default=True)
    # For armature
    bpy.types.Armature.armature_cached = bpy.props.BoolProperty(name="Armature Cached", default=False)
    # For camera
    bpy.types.Camera.frustum_culling = bpy.props.BoolProperty(name="Frustum Culling", default=True)
    bpy.types.Camera.pipeline_path = bpy.props.StringProperty(name="Render Path", default="deferred_path")
    bpy.types.Camera.pipeline_id = bpy.props.StringProperty(name="Pipeline ID", default="deferred")
	# TODO: Specify multiple material ids, merge ids from multiple cameras 
    bpy.types.Camera.pipeline_passes = bpy.props.StringProperty(name="Pipeline passes", default="")
    bpy.types.Camera.geometry_context = bpy.props.StringProperty(name="Geometry", default="geom")
    bpy.types.Camera.geometry_context_empty = bpy.props.StringProperty(name="Geometry Empty", default="depthwrite")
    bpy.types.Camera.shadows_context = bpy.props.StringProperty(name="Shadows", default="shadowmap")
    bpy.types.Camera.translucent_context = bpy.props.StringProperty(name="Translucent", default="translucent")
    bpy.types.Camera.overlay_context = bpy.props.StringProperty(name="Overlay", default="overlay")
    bpy.types.Camera.is_probe = bpy.props.BoolProperty(name="Probe", default=False)
    bpy.types.Camera.probe_generate_radiance = bpy.props.BoolProperty(name="Generate Radiance", default=False)
    bpy.types.Camera.probe_texture = bpy.props.StringProperty(name="Texture", default="")
    bpy.types.Camera.probe_num_mips = bpy.props.IntProperty(name="Number of mips", default=0)
    bpy.types.Camera.probe_volume = bpy.props.StringProperty(name="Volume", default="")
    bpy.types.Camera.probe_strength = bpy.props.FloatProperty(name="Strength", default=1.0)
    bpy.types.Camera.probe_blending = bpy.props.FloatProperty(name="Blending", default=0.0)
	# TODO: move to world
    bpy.types.Camera.world_envtex_name = bpy.props.StringProperty(name="Environment Texture", default='')
    bpy.types.Camera.world_envtex_num_mips = bpy.props.IntProperty(name="Number of mips", default=0)
    bpy.types.Camera.world_envtex_color = bpy.props.FloatVectorProperty(name="Environment Color", size=4, default=[0,0,0,1])
    bpy.types.Camera.world_envtex_strength = bpy.props.FloatProperty(name="Environment Strength", default=1.0)
    bpy.types.Camera.world_envtex_sun_direction = bpy.props.FloatVectorProperty(name="Sun Direction", size=3, default=[0,0,0])
    bpy.types.Camera.world_envtex_turbidity = bpy.props.FloatProperty(name="Turbidity", default=1.0)
    bpy.types.Camera.world_envtex_ground_albedo = bpy.props.FloatProperty(name="Ground Albedo", default=0.0)
    bpy.types.Camera.last_decal_context = bpy.props.StringProperty(name="Decal Context", default='')
    bpy.types.World.world_defs = bpy.props.StringProperty(name="World Shader Defs", default='')
    bpy.types.World.generate_radiance = bpy.props.BoolProperty(name="Radiance Probes", default=True, update=invalidate_shader_cache)
    bpy.types.World.generate_clouds = bpy.props.BoolProperty(name="Clouds", default=False, update=invalidate_shader_cache)
    bpy.types.World.generate_clouds_density = bpy.props.FloatProperty(name="Density", default=0.6, min=0.0, max=10.0, update=invalidate_shader_cache)
    bpy.types.World.generate_clouds_size = bpy.props.FloatProperty(name="Size", default=1.0, min=0.0, max=10.0, update=invalidate_shader_cache)
    bpy.types.World.generate_clouds_lower = bpy.props.FloatProperty(name="Lower", default=2.0, min=1.0, max=10.0, update=invalidate_shader_cache)
    bpy.types.World.generate_clouds_upper = bpy.props.FloatProperty(name="Upper", default=3.5, min=1.0, max=10.0, update=invalidate_shader_cache)
    bpy.types.World.generate_clouds_wind = bpy.props.FloatVectorProperty(name="Wind", default=[0.2, 0.06], size=2, update=invalidate_shader_cache)
    bpy.types.World.generate_clouds_secondary = bpy.props.FloatProperty(name="Secondary", default=0.0, min=0.0, max=10.0, update=invalidate_shader_cache)
    bpy.types.World.generate_clouds_precipitation = bpy.props.FloatProperty(name="Precipitation", default=1.0, min=0.0, max=2.0, update=invalidate_shader_cache)
    bpy.types.World.generate_clouds_eccentricity = bpy.props.FloatProperty(name="Eccentricity", default=0.6, min=0.0, max=1.0, update=invalidate_shader_cache)
    bpy.types.World.shadowmap_size = bpy.props.IntProperty(name="Shadowmap Size", default=0, update=invalidate_shader_cache)
    bpy.types.World.scripts_list = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.World.bundled_scripts_list = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.World.generate_ocean = bpy.props.BoolProperty(name="Ocean", default=False, update=invalidate_shader_cache)
    bpy.types.World.generate_ocean_base_color = bpy.props.FloatVectorProperty(name="Base Color", size=3, default=[0.1, 0.19, 0.37], subtype='COLOR', update=invalidate_shader_cache)
    bpy.types.World.generate_ocean_water_color = bpy.props.FloatVectorProperty(name="Water Color", size=3, default=[0.6, 0.7, 0.9], subtype='COLOR', update=invalidate_shader_cache)
    bpy.types.World.generate_ocean_level = bpy.props.FloatProperty(name="Level", default=0.0, update=invalidate_shader_cache)
    bpy.types.World.generate_ocean_amplitude = bpy.props.FloatProperty(name="Amplitude", default=2.5, update=invalidate_shader_cache)
    bpy.types.World.generate_ocean_height = bpy.props.FloatProperty(name="Height", default=0.6, update=invalidate_shader_cache)
    bpy.types.World.generate_ocean_choppy = bpy.props.FloatProperty(name="Choppy", default=4.0, update=invalidate_shader_cache)
    bpy.types.World.generate_ocean_speed = bpy.props.FloatProperty(name="Speed", default=1.0, update=invalidate_shader_cache)
    bpy.types.World.generate_ocean_freq = bpy.props.FloatProperty(name="Freq", default=0.16, update=invalidate_shader_cache)
    bpy.types.World.generate_ocean_fade = bpy.props.FloatProperty(name="Fade", default=1.8, update=invalidate_shader_cache)
    bpy.types.World.generate_ssao = bpy.props.BoolProperty(name="SSAO", description="Screen-Space Ambient Occlusion", default=True, update=invalidate_shader_cache)
    bpy.types.World.generate_ssao_size = bpy.props.FloatProperty(name="Size", default=0.08, update=invalidate_shader_cache)
    bpy.types.World.generate_ssao_strength = bpy.props.FloatProperty(name="Strength", default=0.30, update=invalidate_shader_cache)
    bpy.types.World.generate_ssao_texture_scale = bpy.props.FloatProperty(name="Texture Scale", default=1.0, min=0.0, max=1.0, update=invalidate_shader_cache)
    bpy.types.World.generate_shadows = bpy.props.BoolProperty(name="Shadows", default=True, update=invalidate_shader_cache)
    bpy.types.World.generate_bloom = bpy.props.BoolProperty(name="Bloom", default=True, update=invalidate_shader_cache)
    bpy.types.World.generate_bloom_treshold = bpy.props.FloatProperty(name="Treshold", default=3.0, update=invalidate_shader_cache)
    bpy.types.World.generate_bloom_strength = bpy.props.FloatProperty(name="Strength", default=0.15, update=invalidate_shader_cache)
    bpy.types.World.generate_motion_blur = bpy.props.BoolProperty(name="Motion Blur", default=True, update=invalidate_shader_cache)
    bpy.types.World.generate_motion_blur_intensity = bpy.props.FloatProperty(name="Intensity", default=1.0, update=invalidate_shader_cache)
    bpy.types.World.generate_ssr = bpy.props.BoolProperty(name="SSR", description="Screen-Space Reflections", default=True, update=invalidate_shader_cache)
    bpy.types.World.generate_ssr_ray_step = bpy.props.FloatProperty(name="Ray Step", default=0.04, update=invalidate_shader_cache)
    bpy.types.World.generate_ssr_min_ray_step = bpy.props.FloatProperty(name="Ray Step Min", default=0.05, update=invalidate_shader_cache)
    bpy.types.World.generate_ssr_search_dist = bpy.props.FloatProperty(name="Search Dist", default=5.0, update=invalidate_shader_cache)
    bpy.types.World.generate_ssr_falloff_exp = bpy.props.FloatProperty(name="Falloff Exp", default=5.0, update=invalidate_shader_cache)
    bpy.types.World.generate_ssr_jitter = bpy.props.FloatProperty(name="Jitter", default=0.6, update=invalidate_shader_cache)
    bpy.types.World.generate_ssr_texture_scale = bpy.props.FloatProperty(name="Texture Scale", default=0.5, min=0.0, max=1.0, update=invalidate_shader_cache)
    bpy.types.World.generate_letterbox = bpy.props.BoolProperty(name="Letterbox", default=False, update=invalidate_shader_cache)
    bpy.types.World.generate_letterbox_size = bpy.props.FloatProperty(name="Size", default=0.1, update=invalidate_shader_cache)
    bpy.types.World.generate_grain = bpy.props.BoolProperty(name="Film Grain", default=False, update=invalidate_shader_cache)
    bpy.types.World.generate_grain_strength = bpy.props.FloatProperty(name="Strength", default=2.0, update=invalidate_shader_cache)
    bpy.types.World.generate_fog = bpy.props.BoolProperty(name="Volumetric Fog", default=False, update=invalidate_shader_cache)
    bpy.types.World.generate_fog_color = bpy.props.FloatVectorProperty(name="Color", size=3, subtype='COLOR', default=[0.5, 0.6, 0.7], update=invalidate_shader_cache)
    bpy.types.World.generate_fog_amounta = bpy.props.FloatProperty(name="Amount A", default=0.25, update=invalidate_shader_cache)
    bpy.types.World.generate_fog_amountb = bpy.props.FloatProperty(name="Amount B", default=0.5, update=invalidate_shader_cache)
    # For material
    bpy.types.Material.receive_shadow = bpy.props.BoolProperty(name="Receive Shadow", default=True)
    bpy.types.Material.override_shader = bpy.props.BoolProperty(name="Override Shader", default=False)
    bpy.types.Material.override_shader_name = bpy.props.StringProperty(name="Name", default='')
    bpy.types.Material.override_shader_context = bpy.props.BoolProperty(name="Override Context", default=False)
    bpy.types.Material.override_shader_context_name = bpy.props.StringProperty(name="Name", default='')
    bpy.types.Material.stencil_mask = bpy.props.IntProperty(name="Stencil Mask", default=0)
    bpy.types.Material.export_tangents = bpy.props.BoolProperty(name="Export Tangents", default=False)
    bpy.types.Material.skip_context = bpy.props.StringProperty(name="Skip Context", default='')
    bpy.types.Material.overlay = bpy.props.BoolProperty(name="X-Ray", default=False)
    bpy.types.Material.override_cull = bpy.props.BoolProperty(name="Override Cull-Mode", default=False)
    bpy.types.Material.override_cull_mode = EnumProperty(
        items = [('none', 'None', 'None'),
                 ('clockwise', 'Clockwise', 'Clockwise'),
                 ('counter_clockwise', 'Counter-Clockwise', 'Counter-Clockwise')],
        name = "Cull-Mode", default='clockwise')
    bpy.types.Material.override_compare = bpy.props.BoolProperty(name="Override Compare-Mode", default=False)
    bpy.types.Material.override_compare_mode = EnumProperty(
        items = [('Always', 'Always', 'Always'),
                 ('Less', 'Less', 'Less')],
        name = "Compare-Mode", default='Less')
    bpy.types.Material.override_depthwrite = bpy.props.BoolProperty(name="Override Depth-Write", default=False)
    bpy.types.Material.override_depthwrite_mode = EnumProperty(
        items = [('True', 'True', 'True'),
                 ('False', 'False', 'False')],
        name = "Depth-Write", default='True')
    # For scene
    bpy.types.Scene.game_export = bpy.props.BoolProperty(name="Export", default=True)
    # For light
    bpy.types.Lamp.light_clip_start = bpy.props.FloatProperty(name="Clip Start", default=0.1)
    bpy.types.Lamp.light_clip_end = bpy.props.FloatProperty(name="Clip End", default=50.0)
    bpy.types.Lamp.light_fov = bpy.props.FloatProperty(name="FoV", default=0.785)
    bpy.types.Lamp.light_shadows_bias = bpy.props.FloatProperty(name="Shadows Bias", default=0.0001)

# Menu in object region
class ObjectPropsPanel(bpy.types.Panel):
    bl_label = "Armory Props"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
 
    def draw(self, context):
        layout = self.layout
        obj = bpy.context.object
        layout.prop(obj, 'spawn')
        layout.prop(obj, 'game_export')
        if obj.type == 'MESH':
            layout.prop(obj, 'instanced_children')
            if obj.instanced_children:
                layout.label('Location')
                row = layout.row()
                row.prop(obj, 'instanced_children_loc_x')
                row.prop(obj, 'instanced_children_loc_y')
                row.prop(obj, 'instanced_children_loc_z')
                layout.label('Rotation')
                row = layout.row()
                row.prop(obj, 'instanced_children_rot_x')
                row.prop(obj, 'instanced_children_rot_y')
                row.prop(obj, 'instanced_children_rot_z')
                layout.label('Scale')
                row = layout.row()
                row.prop(obj, 'instanced_children_scale_x')
                row.prop(obj, 'instanced_children_scale_y')
                row.prop(obj, 'instanced_children_scale_z')
            layout.prop(obj, 'override_material')
            if obj.override_material:
                layout.prop(obj, 'override_material_name')

# Menu in modifiers region
class ModifiersPropsPanel(bpy.types.Panel):
    bl_label = "Armory Props"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "modifier"
 
    def draw(self, context):
        layout = self.layout
        obj = bpy.context.object

        # Assume as first modifier
        if len(obj.modifiers) > 0 and obj.modifiers[0].type == 'OCEAN':
            layout.prop(bpy.data.worlds[0], 'generate_ocean_base_color')
            layout.prop(bpy.data.worlds[0], 'generate_ocean_water_color')
            layout.prop(bpy.data.worlds[0], 'generate_ocean_fade')

# Menu in data region
class DataPropsPanel(bpy.types.Panel):
    bl_label = "Armory Props"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
 
    def draw(self, context):
        layout = self.layout
        obj = bpy.context.object

        if obj.type == 'CAMERA':
            layout.prop(obj.data, 'is_probe')
            if obj.data.is_probe == True:
                layout.prop(obj.data, 'probe_texture')
                layout.prop_search(obj.data, "probe_volume", bpy.data, "objects")
                layout.prop(obj.data, 'probe_strength')
                layout.prop(obj.data, 'probe_blending')
            layout.prop(obj.data, 'frustum_culling')
            layout.prop_search(obj.data, "pipeline_path", bpy.data, "node_groups")
            layout.operator("arm.reimport_paths_menu")
        elif obj.type == 'MESH' or obj.type == 'FONT':
            layout.prop(obj.data, 'static_usage')
            layout.operator("arm.invalidate_cache")
        elif obj.type == 'LAMP':
            layout.prop(obj.data, 'light_clip_start')
            layout.prop(obj.data, 'light_clip_end')
            layout.prop(obj.data, 'light_fov')
            layout.prop(obj.data, 'light_shadows_bias')

class ScenePropsPanel(bpy.types.Panel):
    bl_label = "Armory Props"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
 
    def draw(self, context):
        layout = self.layout
        obj = bpy.context.scene
        layout.prop(obj, 'game_export')

class ReimportPathsMenu(bpy.types.Menu):
    bl_label = "OK?"
    bl_idname = "OBJECT_MT_reimport_paths_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("arm.reimport_paths")

class ReimportPathsButton(bpy.types.Operator):
    bl_label = "Reimport Paths"
    bl_idname = "arm.reimport_paths_menu"
 
    def execute(self, context):
        bpy.ops.wm.call_menu(name=ReimportPathsMenu.bl_idname)
        return {"FINISHED"}

class OBJECT_OT_REIMPORTPATHSButton(bpy.types.Operator):
    bl_idname = "arm.reimport_paths"
    bl_label = "Reimport Paths"
 
    def execute(self, context):
        nodes_renderpath.load_library()
        return{'FINISHED'}

class OBJECT_OT_INVALIDATECACHEButton(bpy.types.Operator):
    bl_idname = "arm.invalidate_cache"
    bl_label = "Invalidate Cache"
 
    def execute(self, context):
        context.object.data.geometry_cached = False
        return{'FINISHED'}

# Menu in materials region
class MatsPropsPanel(bpy.types.Panel):
    bl_label = "Armory Props"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
 
    def draw(self, context):
        layout = self.layout
        mat = bpy.context.material

        layout.prop(mat, 'receive_shadow')
        layout.prop(mat, 'override_shader')
        if mat.override_shader:
            layout.prop(mat, 'override_shader_name')
        layout.prop(mat, 'override_shader_context')
        if mat.override_shader_context:
            layout.prop(mat, 'override_shader_context_name')
        layout.prop(mat, 'override_cull')
        if mat.override_cull:
            layout.prop(mat, 'override_cull_mode')
        # layout.prop(mat, 'override_compare')
        # if mat.override_compare:
            # layout.prop(mat, 'override_compare_mode')
        # layout.prop(mat, 'override_depthwrite')
        # if mat.override_depthwrite:
            # layout.prop(mat, 'override_depthwrite_mode')
        layout.prop(mat, 'overlay')
        layout.prop(mat, 'stencil_mask')
        layout.prop(mat, 'skip_context')

# Menu in world region
class WorldPropsPanel(bpy.types.Panel):
    bl_label = "Armory Props"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "world"
 
    def draw(self, context):
        layout = self.layout
        wrd = bpy.context.world
        layout.prop(wrd, 'generate_shadows')
        layout.prop(wrd, 'generate_radiance')
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
        layout.prop(wrd, 'generate_ssao')
        if wrd.generate_ssao:
            layout.prop(wrd, 'generate_ssao_size')
            layout.prop(wrd, 'generate_ssao_strength')
            layout.prop(wrd, 'generate_ssao_texture_scale')
        layout.prop(wrd, 'generate_bloom')
        if wrd.generate_bloom:
            layout.prop(wrd, 'generate_bloom_treshold')
            layout.prop(wrd, 'generate_bloom_strength')
        layout.prop(wrd, 'generate_motion_blur')
        if wrd.generate_motion_blur:
            layout.prop(wrd, 'generate_motion_blur_intensity')
        layout.prop(wrd, 'generate_ssr')
        if wrd.generate_ssr:
            layout.prop(wrd, 'generate_ssr_ray_step')
            layout.prop(wrd, 'generate_ssr_min_ray_step')
            layout.prop(wrd, 'generate_ssr_search_dist')
            layout.prop(wrd, 'generate_ssr_falloff_exp')
            layout.prop(wrd, 'generate_ssr_jitter')
            layout.prop(wrd, 'generate_ssr_texture_scale')
        
        layout.label('Compositor')
        layout.prop(wrd, 'generate_letterbox')
        if wrd.generate_letterbox:
            layout.prop(wrd, 'generate_letterbox_size')
        layout.prop(wrd, 'generate_grain')
        if wrd.generate_grain:
            layout.prop(wrd, 'generate_grain_strength')
        layout.prop(wrd, 'generate_fog')
        if wrd.generate_fog:
            layout.prop(wrd, 'generate_fog_color')
            layout.prop(wrd, 'generate_fog_amounta')
            layout.prop(wrd, 'generate_fog_amountb')

# Registration
def register():
    bpy.utils.register_module(__name__)
    initProperties()
    bpy.app.handlers.scene_update_post.append(on_scene_update)

def unregister():
    bpy.app.handlers.scene_update_post.remove(on_scene_update)
    bpy.utils.unregister_module(__name__)
