import bpy
from bpy.props import *
import os
import shutil
import arm.props_ui as props_ui
import arm.assets as assets
import arm.log as log
import arm.utils
import arm.make
import arm.make_renderer as make_renderer
import arm.props_renderpath as props_renderpath
import arm.proxy
try:
    import barmory
except ImportError:
    pass

# Armory version
arm_version = '17.10'

def update_preset(self, context):
    make_renderer.set_preset(self, context, self.rp_preset)

def invalidate_mesh_cache(self, context):
    if context.object == None or context.object.data == None:
        return
    context.object.data.arm_cached = False

def invalidate_instance_cache(self, context):
    if context.object == None or context.object.data == None:
        return
    invalidate_mesh_cache(self, context)
    for slot in context.object.material_slots:
        slot.material.is_cached = False

def update_mat_cache(self, context):
    if self.is_cached == True:
        self.lock_cache = True
    else:
        pass

def proxy_sync_loc(self, context):
    if context.object == None or context.object.proxy == None:
        return
    if context.object.arm_proxy_sync_loc:
        arm.proxy.sync_location(context.object)

def proxy_sync_rot(self, context):
    if context.object == None or context.object.proxy == None:
        return
    if context.object.arm_proxy_sync_rot:
        arm.proxy.sync_rotation(context.object)

def proxy_sync_scale(self, context):
    if context.object == None or context.object.proxy == None:
        return
    if context.object.arm_proxy_sync_scale:
        arm.proxy.sync_scale(context.object)

def proxy_sync_materials(self, context):
    if context.object == None or context.object.proxy == None:
        return
    if context.object.arm_proxy_sync_materials:
        arm.proxy.sync_materials(context.object)

def proxy_sync_modifiers(self, context):
    if context.object == None or context.object.proxy == None:
        return
    if context.object.arm_proxy_sync_modifiers:
        arm.proxy.sync_modifiers(context.object)

def proxy_sync_traits(self, context):
    if context.object == None or context.object.proxy == None:
        return
    if context.object.arm_proxy_sync_traits:
        arm.proxy.sync_traits(context.object)

def init_properties():
    global arm_version
    bpy.types.World.arm_recompile = bpy.props.BoolProperty(name="Recompile", description="Recompile sources on next play", default=True)
    bpy.types.World.arm_progress = bpy.props.FloatProperty(name="Building", description="Current build progress", default=100.0, min=0.0, max=100.0, soft_min=0.0, soft_max=100.0, subtype='PERCENTAGE', get=log.get_progress)
    bpy.types.World.arm_version = StringProperty(name="Version", description="Armory SDK version", default="")
    bpy.types.World.arm_project_name = StringProperty(name="Name", description="Exported project name", default="")
    bpy.types.World.arm_project_package = StringProperty(name="Package", description="Package name for scripts", default="arm")
    bpy.types.World.arm_project_root = StringProperty(name="Root", description="Set root folder for linked assets", default="", subtype="FILE_PATH")
    bpy.types.World.arm_play_active_scene = BoolProperty(name="Play Active Scene", description="Load currently edited scene when launching player", default=True)
    bpy.types.World.arm_project_scene = StringProperty(name="Scene", description="Scene to load when launching player")  
    bpy.types.World.arm_physics = EnumProperty(
        items = [('Disabled', 'Disabled', 'Disabled'), 
                 ('Bullet', 'Bullet', 'Bullet'),
                 ('Oimo', 'Oimo', 'Oimo')],
        name = "Physics", default='Bullet')
    bpy.types.World.arm_navigation = EnumProperty(
        items = [('Disabled', 'Disabled', 'Disabled'), 
                 ('Recast', 'Recast', 'Recast')],
        name = "Navigation", default='Recast')
    bpy.types.World.arm_ui = EnumProperty(
        items = [('Disabled', 'Disabled', 'Disabled'), 
                 ('Enabled', 'Enabled', 'Enabled'),
                 ('Auto', 'Auto', 'Auto')],
        name = "Zui", default='Auto', description="Include UI library")
    bpy.types.World.arm_hscript = EnumProperty(
        items = [('Disabled', 'Disabled', 'Disabled'), 
                 ('Enabled', 'Enabled', 'Enabled')],
        name = "Hscript", default='Disabled', description="Include Hscript library")
    bpy.types.World.arm_khafile = StringProperty(name="Khafile", description="Source appended to khafile.js")
    bpy.types.World.arm_khamake = StringProperty(name="Khamake", description="Command line params appended to khamake")
    bpy.types.World.arm_texture_quality = bpy.props.FloatProperty(name="Texture Quality", default=1.0, min=0.0, max=1.0, subtype='FACTOR')
    bpy.types.World.arm_sound_quality = bpy.props.FloatProperty(name="Sound Quality", default=0.9, min=0.0, max=1.0, subtype='FACTOR')
    bpy.types.World.arm_minimize = BoolProperty(name="Minimize Data", description="Export scene data in binary", default=True, update=assets.invalidate_compiled_data)
    bpy.types.World.arm_optimize_mesh = BoolProperty(name="Optimize Meshes", description="Export more efficient geometry indices, can prolong build times", default=False, update=assets.invalidate_mesh_data)
    bpy.types.World.arm_sampled_animation = BoolProperty(name="Sampled Animation", description="Export object animation as raw matrices", default=False, update=assets.invalidate_compiled_data)
    bpy.types.World.arm_deinterleaved_buffers = BoolProperty(name="Deinterleaved Buffers", description="Use deinterleaved vertex buffers", default=False)
    bpy.types.World.arm_export_tangents = BoolProperty(name="Export Tangents", description="Precompute tangents for normal mapping, otherwise computed in shader", default=True, update=assets.invalidate_compiled_data)
    bpy.types.World.arm_batch_meshes = BoolProperty(name="Batch Meshes", description="Group meshes by materials to speed up rendering", default=False)
    bpy.types.World.arm_batch_materials = BoolProperty(name="Batch Materials", description="Marge similar materials into single pipeline state", default=False, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_stream_scene = BoolProperty(name="Stream Scene", description="Stream scene content", default=False)
    bpy.types.World.arm_lod_gen_levels = IntProperty(name="Levels", description="Number of levels to generate", default=3, min=1)
    bpy.types.World.arm_lod_gen_ratio = FloatProperty(name="Decimate Ratio", description="Decimate ratio", default=0.8)
    bpy.types.World.arm_cache_shaders = BoolProperty(name="Cache Shaders", description="Do not rebuild existing shaders", default=True, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_cache_compiler = BoolProperty(name="Cache Compiler", description="Only recompile sources when required", default=True)
    bpy.types.World.arm_gpu_processing = BoolProperty(name="GPU Processing", description="Utilize GPU for asset pre-processing at build time", default=True, update=assets.invalidate_compiled_data)
    bpy.types.World.arm_play_live_patch = BoolProperty(name="Live Patch", description="Sync running player data to Blender", default=True)
    bpy.types.World.arm_play_auto_build = BoolProperty(name="Auto Build", description="Rebuild scene on operator changes", default=True)
    bpy.types.World.arm_play_camera = EnumProperty(
        items=[('Scene', 'Scene', 'Scene'),
               ('Viewport', 'Viewport', 'Viewport'),
               ('Viewport Shared', 'Viewport Shared', 'Viewport Shared')
               ],
        name="Camera", description="Viewport camera", default='Scene')
    bpy.types.World.arm_play_console = BoolProperty(name="Debug Console", description="Show inspector in player", default=False)
    bpy.types.World.arm_play_runtime = EnumProperty(
        items=[('Browser', 'Browser', 'Browser'),
               ('Native', 'C++', 'Native'),
               ('Krom', 'Krom', 'Krom')],
        name="Runtime", description="Player runtime used when launching in new window", default='Krom', update=assets.invalidate_shader_cache)
    bpy.types.World.arm_loadbar = BoolProperty(name="Load Bar", description="Show asset loading progress on published builds", default=True)
    bpy.types.World.arm_vsync = BoolProperty(name="VSync", description="Vertical Synchronization", default=True)
    bpy.types.World.arm_dce = BoolProperty(name="DCE", description="Enable dead code elimination for publish builds", default=True)
    bpy.types.World.arm_asset_compression = BoolProperty(name="Asset Compression", description="Enable scene data compression", default=False)
    bpy.types.World.arm_winmode = EnumProperty(
        items = [('Window', 'Window', 'Window'),
                 ('BorderlessWindow', 'Borderless', 'BorderlessWindow'),
                 ('Fullscreen', 'Fullscreen', 'Fullscreen')],
        name="", default='Window', description='Window mode to start in')
    bpy.types.World.arm_winorient = EnumProperty(
        items = [('Multi', 'Multi', 'Multi'),
                 ('Portrait', 'Portrait', 'Portrait'),
                 ('Landscape', 'Landscape', 'Landscape')],
        name="Orientation", default='Multi', description='Set screen orientation on mobile devices')
    bpy.types.World.arm_winresize = BoolProperty(name="Resizable", description="Allow window resize", default=False)
    bpy.types.World.arm_winmaximize = BoolProperty(name="Maximizable", description="Allow window maximize", default=False)
    bpy.types.World.arm_winminimize = BoolProperty(name="Minimizable", description="Allow window minimize", default=True)
    # For object
    bpy.types.Object.arm_instanced = bpy.props.BoolProperty(name="Instanced Children", description="Use instaced rendering", default=False, update=invalidate_instance_cache)
    bpy.types.Object.arm_instanced_loc_x = bpy.props.BoolProperty(name="X", default=True)
    bpy.types.Object.arm_instanced_loc_y = bpy.props.BoolProperty(name="Y", default=True)
    bpy.types.Object.arm_instanced_loc_z = bpy.props.BoolProperty(name="Z", default=True)
    # bpy.types.Object.arm_instanced_rot_x = bpy.props.BoolProperty(name="X", default=False)
    # bpy.types.Object.arm_instanced_rot_y = bpy.props.BoolProperty(name="Y", default=False)
    # bpy.types.Object.arm_instanced_rot_z = bpy.props.BoolProperty(name="Z", default=False)
    # bpy.types.Object.arm_instanced_scale_x = bpy.props.BoolProperty(name="X", default=False)
    # bpy.types.Object.arm_instanced_scale_y = bpy.props.BoolProperty(name="Y", default=False)
    # bpy.types.Object.arm_instanced_scale_z = bpy.props.BoolProperty(name="Z", default=False)
    bpy.types.Object.arm_export = bpy.props.BoolProperty(name="Export", description="Export object data", default=True)
    bpy.types.Object.arm_spawn = bpy.props.BoolProperty(name="Spawn", description="Auto-add this object when creating scene", default=True)
    bpy.types.Object.arm_mobile = bpy.props.BoolProperty(name="Mobile", description="Object moves during gameplay", default=True)
    bpy.types.Object.arm_soft_body_margin = bpy.props.FloatProperty(name="Soft Body Margin", description="Collision margin", default=0.04)
    bpy.types.Object.arm_rb_linear_factor = bpy.props.FloatVectorProperty(name="Linear Factor", size=3, description="Set to 0 to lock axis", default=[1,1,1])
    bpy.types.Object.arm_rb_angular_factor = bpy.props.FloatVectorProperty(name="Angular Factor", size=3, description="Set to 0 to lock axis", default=[1,1,1])
    bpy.types.Object.arm_animation_enabled = bpy.props.BoolProperty(name="Animation", description="Enable skinning & timeline animation", default=True)
    bpy.types.Object.arm_tilesheet = bpy.props.StringProperty(name="Tilesheet", description="Set tilesheet animation", default='')
    bpy.types.Object.arm_tilesheet_action = bpy.props.StringProperty(name="Tilesheet Action", description="Set startup action", default='')
    bpy.types.Object.arm_proxy_sync_loc = bpy.props.BoolProperty(name="Location", description="Keep location synchronized with proxy object", default=True, update=proxy_sync_loc)
    bpy.types.Object.arm_proxy_sync_rot = bpy.props.BoolProperty(name="Rotation", description="Keep rotation synchronized with proxy object", default=True, update=proxy_sync_rot)
    bpy.types.Object.arm_proxy_sync_scale = bpy.props.BoolProperty(name="Scale", description="Keep scale synchronized with proxy object", default=True, update=proxy_sync_scale)
    bpy.types.Object.arm_proxy_sync_materials = bpy.props.BoolProperty(name="Materials", description="Keep materials synchronized with proxy object", default=True, update=proxy_sync_materials)
    bpy.types.Object.arm_proxy_sync_modifiers = bpy.props.BoolProperty(name="Modifiers", description="Keep modifiers synchronized with proxy object", default=True, update=proxy_sync_modifiers)
    bpy.types.Object.arm_proxy_sync_traits = bpy.props.BoolProperty(name="Traits", description="Keep traits synchronized with proxy object", default=True, update=proxy_sync_traits)
    # For speakers
    bpy.types.Speaker.arm_loop = bpy.props.BoolProperty(name="Loop", description="Loop this sound", default=False)
    bpy.types.Speaker.arm_stream = bpy.props.BoolProperty(name="Stream", description="Stream this sound", default=False)
    # For mesh
    bpy.types.Mesh.arm_cached = bpy.props.BoolProperty(name="Mesh Cached", description="No need to reexport mesh data", default=False)
    bpy.types.Mesh.arm_cached_verts = bpy.props.IntProperty(name="Last Verts", description="Number of vertices in last export", default=0)
    bpy.types.Mesh.arm_cached_edges = bpy.props.IntProperty(name="Last Edges", description="Number of edges in last export", default=0)
    bpy.types.Mesh.arm_aabb = bpy.props.FloatVectorProperty(name="AABB", size=3, default=[0,0,0])
    bpy.types.Mesh.arm_dynamic_usage = bpy.props.BoolProperty(name="Dynamic Usage", description="Mesh data can change at runtime", default=False)
    bpy.types.Mesh.arm_compress = bpy.props.BoolProperty(name="Compress", description="Pack data into zip file", default=False)
    bpy.types.Mesh.arm_sdfgen = bpy.props.BoolProperty(name="Generate SDF", description="Make signed distance field data", default=False, update=invalidate_mesh_cache)
    bpy.types.Curve.arm_cached = bpy.props.BoolProperty(name="Mesh Cached", description="No need to reexport curve data", default=False)
    bpy.types.Curve.arm_compress = bpy.props.BoolProperty(name="Compress", description="Pack data into zip file", default=False)
    bpy.types.Curve.arm_dynamic_usage = bpy.props.BoolProperty(name="Dynamic Data Usage", description="Curve data can change at runtime", default=False)
    bpy.types.MetaBall.arm_cached = bpy.props.BoolProperty(name="Mesh Cached", description="No need to reexport metaball data", default=False)
    bpy.types.MetaBall.arm_compress = bpy.props.BoolProperty(name="Compress", description="Pack data into zip file", default=False)
    bpy.types.MetaBall.arm_dynamic_usage = bpy.props.BoolProperty(name="Dynamic Data Usage", description="Metaball data can change at runtime", default=False)
    # For grease pencil
    bpy.types.GreasePencil.arm_cached = bpy.props.BoolProperty(name="GP Cached", description="No need to reexport grease pencil data", default=False)
    bpy.types.GreasePencil.arm_compress = bpy.props.BoolProperty(name="Compress", description="Pack data into zip file", default=True)
    # For armature
    bpy.types.Armature.arm_cached = bpy.props.BoolProperty(name="Armature Cached", description="No need to reexport armature data", default=False)
    bpy.types.Armature.arm_compress = bpy.props.BoolProperty(name="Compress", description="Pack data into zip file", default=False)
    # For camera
    bpy.types.Camera.arm_frustum_culling = bpy.props.BoolProperty(name="Frustum Culling", description="Perform frustum culling for this camera", default=True)
    bpy.types.Camera.arm_render_to_texture = bpy.props.BoolProperty(name="Render to Texture", description="Render this camera into texture", default=False)
    bpy.types.Camera.arm_texture_resolution_x = bpy.props.FloatProperty(name="X", default=512.0)
    bpy.types.Camera.arm_texture_resolution_y = bpy.props.FloatProperty(name="Y", default=256.0)

    # Render path generator
    bpy.types.World.rp_preset = EnumProperty(
        items=[('Low', 'Low', 'Low'),
               ('VR Low', 'VR Low', 'VR Low'),
               ('Mobile Low', 'Mobile Low', 'Mobile Low'),
               ('Forward', 'Forward', 'Forward'),
               ('Deferred', 'Deferred', 'Deferred'),
               ('Deferred Plus', 'Deferred Plus (experimental)', 'Deferred Plus'),
               ('Grease Pencil', 'Grease Pencil', 'Grease Pencil'),
               ('Render Capture', 'Render Capture', 'Render Capture'),
               ('Max', 'Max', 'Max'),
               ],
        name="Preset", description="Render path preset", default='Deferred', update=update_preset)
    bpy.types.World.arm_voxelgi_diff = bpy.props.FloatProperty(name="Diffuse", description="", default=1.0, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_voxelgi_diff_cones = EnumProperty(
        items=[('9', '9', '9'),
               ('5', '5', '5'),
               ],
        name="Diffuse Cones", description="", default='9', update=assets.invalidate_shader_cache)
    bpy.types.World.arm_voxelgi_spec = bpy.props.FloatProperty(name="Specular", description="", default=1.0, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_voxelgi_occ = bpy.props.FloatProperty(name="Occlussion", description="", default=1.0, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_voxelgi_env = bpy.props.FloatProperty(name="Env Map", description="Contribute light from environment map", default=0.0, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_voxelgi_step = bpy.props.FloatProperty(name="Step", description="Step size", default=1.0, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_voxelgi_offset_diff = bpy.props.FloatProperty(name="Diffuse Offset", description="Offset size", default=1.0, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_voxelgi_offset_spec = bpy.props.FloatProperty(name="Specular Offset", description="Step size", default=1.0, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_voxelgi_offset_shadow = bpy.props.FloatProperty(name="Shadow Offset", description="Step size", default=1.0, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_voxelgi_offset_refract = bpy.props.FloatProperty(name="Refract Offset", description="Step size", default=1.0, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_voxelgi_range = bpy.props.FloatProperty(name="Range", description="Maximum range", default=1.0, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_sss_width = bpy.props.FloatProperty(name="SSS Width", description="SSS blur strength", default=1.0, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_envtex_name = bpy.props.StringProperty(name="Environment Texture", default='')
    bpy.types.World.arm_envtex_irr_name = bpy.props.StringProperty(name="Environment Irradiance", default='')
    bpy.types.World.arm_envtex_num_mips = bpy.props.IntProperty(name="Number of mips", default=0)
    bpy.types.World.arm_envtex_color = bpy.props.FloatVectorProperty(name="Environment Color", size=4, default=[0,0,0,1])
    bpy.types.World.arm_envtex_strength = bpy.props.FloatProperty(name="Environment Strength", default=1.0)
    bpy.types.World.arm_envtex_sun_direction = bpy.props.FloatVectorProperty(name="Sun Direction", size=3, default=[0,0,0])
    bpy.types.World.arm_envtex_turbidity = bpy.props.FloatProperty(name="Turbidity", default=1.0)
    bpy.types.World.arm_envtex_ground_albedo = bpy.props.FloatProperty(name="Ground Albedo", default=0.0)
    bpy.types.World.arm_irradiance = bpy.props.BoolProperty(name="Irradiance", description="Generate spherical harmonics", default=True, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_radiance = bpy.props.BoolProperty(name="Radiance", description="Generate radiance textures", default=True, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_radiance_size = EnumProperty(
        items=[('512', '512', '512'),
               ('1024', '1024', '1024'), 
               ('2048', '2048', '2048')],
        name="", description="Prefiltered map size", default='1024', update=assets.invalidate_envmap_data)
    bpy.types.World.arm_radiance_sky = bpy.props.BoolProperty(name="Sky Radiance", default=True, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_radiance_sky_type = EnumProperty(
        items=[('Fake', 'Fake', 'Fake'), 
               ('Hosek', 'Hosek', 'Hosek')],
        name="", description="Prefiltered maps to be used for radiance", default='Hosek', update=assets.invalidate_envmap_data)
    bpy.types.World.arm_clouds_density = bpy.props.FloatProperty(name="Density", default=1.0, min=0.0, max=10.0, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_clouds_size = bpy.props.FloatProperty(name="Size", default=1.0, min=0.0, max=10.0, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_clouds_lower = bpy.props.FloatProperty(name="Lower", default=2.0, min=1.0, max=10.0, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_clouds_upper = bpy.props.FloatProperty(name="Upper", default=3.5, min=1.0, max=10.0, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_clouds_wind = bpy.props.FloatVectorProperty(name="Wind", default=[0.2, 0.06], size=2, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_clouds_secondary = bpy.props.FloatProperty(name="Secondary", default=0.0, min=0.0, max=10.0, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_clouds_precipitation = bpy.props.FloatProperty(name="Precipitation", default=1.0, min=0.0, max=2.0, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_clouds_eccentricity = bpy.props.FloatProperty(name="Eccentricity", default=0.6, min=0.0, max=1.0, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_ocean_base_color = bpy.props.FloatVectorProperty(name="Base Color", size=3, default=[0.1, 0.19, 0.37], subtype='COLOR', min=0, max=1, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_ocean_water_color = bpy.props.FloatVectorProperty(name="Water Color", size=3, default=[0.6, 0.7, 0.9], subtype='COLOR', min=0, max=1, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_ocean_level = bpy.props.FloatProperty(name="Level", default=0.0, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_ocean_amplitude = bpy.props.FloatProperty(name="Amplitude", default=2.5, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_ocean_height = bpy.props.FloatProperty(name="Height", default=0.6, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_ocean_choppy = bpy.props.FloatProperty(name="Choppy", default=4.0, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_ocean_speed = bpy.props.FloatProperty(name="Speed", default=1.5, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_ocean_freq = bpy.props.FloatProperty(name="Freq", default=0.16, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_ocean_fade = bpy.props.FloatProperty(name="Fade", default=1.8, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_ssao_size = bpy.props.FloatProperty(name="Size", default=0.12, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_ssao_strength = bpy.props.FloatProperty(name="Strength", default=0.1, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_bloom_threshold = bpy.props.FloatProperty(name="Threshold", default=5.0, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_bloom_strength = bpy.props.FloatProperty(name="Strength", default=1.0, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_bloom_radius = bpy.props.FloatProperty(name="Radius", default=1.0, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_motion_blur_intensity = bpy.props.FloatProperty(name="Intensity", default=1.0, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_ssr_ray_step = bpy.props.FloatProperty(name="Ray Step", default=0.04, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_ssr_min_ray_step = bpy.props.FloatProperty(name="Ray Step Min", default=0.05, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_ssr_search_dist = bpy.props.FloatProperty(name="Search Dist", default=5.0, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_ssr_falloff_exp = bpy.props.FloatProperty(name="Falloff Exp", default=5.0, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_ssr_jitter = bpy.props.FloatProperty(name="Jitter", default=0.6, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_volumetric_light_air_turbidity = bpy.props.FloatProperty(name="Air Turbidity", default=1.0, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_volumetric_light_air_color = bpy.props.FloatVectorProperty(name="Air Color", size=3, default=[1.0, 1.0, 1.0], subtype='COLOR', min=0, max=1, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_pcss_rings = bpy.props.IntProperty(name="Rings", description="", default=20, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_ssrs_ray_step = bpy.props.FloatProperty(name="Ray Step", default=0.01, update=assets.invalidate_shader_cache)
    bpy.types.World.rp_rendercapture_format = EnumProperty(
        items=[('8bit', '8bit', '8bit'),
               ('16bit', '16bit', '16bit'),
               ('32bit', '32bit', '32bit')],
        name="Capture Format", description="Bits per color channel", default='8bit', update=props_renderpath.update_renderpath)
    # Compositor
    bpy.types.World.arm_letterbox = bpy.props.BoolProperty(name="Letterbox", default=False, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_letterbox_size = bpy.props.FloatProperty(name="Size", default=0.1, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_grain = bpy.props.BoolProperty(name="Film Grain", default=False, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_grain_strength = bpy.props.FloatProperty(name="Strength", default=2.0, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_fog = bpy.props.BoolProperty(name="Volumetric Fog", default=False, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_fog_color = bpy.props.FloatVectorProperty(name="Color", size=3, subtype='COLOR', default=[0.5, 0.6, 0.7], min=0, max=1, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_fog_amounta = bpy.props.FloatProperty(name="Amount A", default=0.25, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_fog_amountb = bpy.props.FloatProperty(name="Amount B", default=0.5, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_tonemap = EnumProperty(
        items=[('None', 'None', 'None'),
               ('Filmic', 'Filmic', 'Filmic'),
               ('Filmic2', 'Filmic2', 'Filmic2'),
               ('Reinhard', 'Reinhard', 'Reinhard'),
               ('Uncharted', 'Uncharted', 'Uncharted')],
        name='Tonemap', description='Tonemapping operator', default='Filmic', update=assets.invalidate_shader_cache)
    bpy.types.World.arm_lamp_texture = bpy.props.StringProperty(name="Mask Texture", default="")
    bpy.types.World.arm_lamp_ies_texture = bpy.props.StringProperty(name="IES Texture", default="")
    bpy.types.World.arm_lamp_clouds_texture = bpy.props.StringProperty(name="Clouds Texture", default="")
    bpy.types.World.arm_lens_texture = bpy.props.StringProperty(name="Lens Texture", default="")
    bpy.types.World.arm_fisheye = bpy.props.BoolProperty(name="Fish Eye", default=False, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_vignette = bpy.props.BoolProperty(name="Vignette", default=False, update=assets.invalidate_shader_cache)
    # Skin
    bpy.types.World.arm_skin = EnumProperty(
        items=[('GPU (Dual-Quat)', 'GPU (Dual-Quat)', 'GPU (Dual-Quat)'),
               ('GPU (Matrix)', 'GPU (Matrix)', 'GPU (Matrix)'),
               ('CPU', 'CPU', 'CPU')],
        name='Skinning', description='Skinning method', default='GPU (Dual-Quat)', update=assets.invalidate_shader_cache)
    bpy.types.World.arm_skin_max_bones_auto = bpy.props.BoolProperty(name="Auto Bones", description="Calculate amount of maximum bones based on armatures", default=True, update=assets.invalidate_compiled_data)
    bpy.types.World.arm_skin_max_bones = bpy.props.IntProperty(name="Max Bones", default=50, min=1, max=3000, update=assets.invalidate_shader_cache)
    # Material override flags
    bpy.types.World.arm_culling = bpy.props.BoolProperty(name="Culling", default=True)
    bpy.types.World.arm_two_sided_area_lamp = bpy.props.BoolProperty(name="Two-Sided Area Lamps", description="Emit light from both faces of area lamp", default=False, update=assets.invalidate_shader_cache)
    # For material
    bpy.types.Material.arm_cast_shadow = bpy.props.BoolProperty(name="Cast Shadow", default=True)
    bpy.types.Material.arm_receive_shadow = bpy.props.BoolProperty(name="Receive Shadow", default=True)
    bpy.types.Material.arm_overlay = bpy.props.BoolProperty(name="Overlay", default=False)
    bpy.types.Material.arm_decal = bpy.props.BoolProperty(name="Decal", default=False)
    bpy.types.Material.arm_two_sided = bpy.props.BoolProperty(name="Two-Sided", default=False)
    bpy.types.Material.arm_cull_mode = EnumProperty(
        items=[('none', 'Both', 'None'),
               ('clockwise', 'Front', 'Clockwise'),
               ('counter_clockwise', 'Back', 'Counter-Clockwise')],
        name="", default='clockwise', description="Draw geometry faces")
    bpy.types.Material.arm_discard = bpy.props.BoolProperty(name="Discard", default=False)
    bpy.types.Material.arm_discard_opacity = bpy.props.FloatProperty(name="Mesh Opacity", default=0.2, min=0, max=1)
    bpy.types.Material.arm_discard_opacity_shadows = bpy.props.FloatProperty(name="Shadows Opacity", default=0.1, min=0, max=1)
    bpy.types.Material.arm_tess = bpy.props.BoolProperty(name="Tess Displacement", description="Use tessellation shaders to subdivide and displace surface", default=True)
    bpy.types.Material.arm_tess_inner = bpy.props.IntProperty(name="Inner", description="Inner tessellation level for mesh", default=14)
    bpy.types.Material.arm_tess_outer = bpy.props.IntProperty(name="Outer", description="Outer tessellation level for mesh", default=14)
    bpy.types.Material.arm_tess_shadows = bpy.props.BoolProperty(name="Tess Shadows", description="Use tessellation shaders when rendering shadow maps", default=True)
    bpy.types.Material.arm_tess_shadows_inner = bpy.props.IntProperty(name="Inner", description="Inner tessellation level for shadows", default=7)
    bpy.types.Material.arm_tess_shadows_outer = bpy.props.IntProperty(name="Outer", description="Outer tessellation level for shadows", default=7)
    bpy.types.Material.arm_custom_material = bpy.props.StringProperty(name="Custom Material", description="Write custom material", default='')
    bpy.types.Material.arm_billboard = EnumProperty(
        items=[('off', 'Off', 'Off'),
               ('spherical', 'Spherical', 'Spherical'),
               ('cylindrical', 'Cylindrical', 'Cylindrical')],
        name="Billboard", default='off', description="Track camera", update=assets.invalidate_shader_cache)
    bpy.types.Material.arm_particle = EnumProperty(
        items=[('off', 'Off', 'Off'),
               ('gpu', 'GPU', 'GPU'),
               ('cpu', 'CPU', 'CPU')],
        name="Particle", default='off', description="Use this material for particle system rendering", update=assets.invalidate_shader_cache)
    bpy.types.Material.arm_particle_fade = bpy.props.BoolProperty(name="Particle Fade", description="Fade particles in and out", default=False)
    bpy.types.Material.arm_tilesheet_mat = bpy.props.BoolProperty(name="Tilesheet", description="Generate tilesheet shaders", default=False)
    bpy.types.Material.arm_blending = bpy.props.BoolProperty(name="Blending", description="Enable additive blending", default=False)
    # For scene
    bpy.types.Scene.arm_export = bpy.props.BoolProperty(name="Export", description="Export scene data", default=True)
    bpy.types.Scene.arm_gp_export = bpy.props.BoolProperty(name="Export GP", description="Export grease pencil data", default=True)
    bpy.types.Scene.arm_compress = bpy.props.BoolProperty(name="Compress", description="Pack data into zip file", default=False)
    # For lamp
    bpy.types.Lamp.arm_clip_start = bpy.props.FloatProperty(name="Clip Start", default=0.1)
    bpy.types.Lamp.arm_clip_end = bpy.props.FloatProperty(name="Clip End", default=50.0)
    bpy.types.Lamp.arm_fov = bpy.props.FloatProperty(name="Field of View", default=0.84)
    bpy.types.Lamp.arm_shadows_bias = bpy.props.FloatProperty(name="Bias", description="Depth offset for shadow acne", default=0.0001)
    bpy.types.Lamp.arm_omni_shadows = bpy.props.BoolProperty(name="Omni-Shadows", description="Draw shadows to all faces of the cube map", default=True)
    bpy.types.World.arm_pcfsize = bpy.props.FloatProperty(name="PCF Size", description="Filter size", default=0.001)

    bpy.types.World.arm_shadowmap_size_cache = bpy.props.IntProperty(name="Shadowmap Size", default=0, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_rpcache_list = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.World.arm_scripts_list = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.World.arm_bundled_scripts_list = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.World.arm_canvas_list = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.World.world_defs = bpy.props.StringProperty(name="World Shader Defs", default='')
    bpy.types.World.compo_defs = bpy.props.StringProperty(name="Compositor Shader Defs", default='')
    bpy.types.Material.export_uvs = bpy.props.BoolProperty(name="Export UVs", default=False)
    bpy.types.Material.export_vcols = bpy.props.BoolProperty(name="Export VCols", default=False)
    bpy.types.Material.export_tangents = bpy.props.BoolProperty(name="Export Tangents", default=False)
    bpy.types.Material.vertex_structure = bpy.props.StringProperty(name="Vertex Structure", default='')
    bpy.types.Material.arm_skip_context = bpy.props.StringProperty(name="Skip Context", default='')
    bpy.types.NodeSocket.is_uniform = bpy.props.BoolProperty(name="Is Uniform", description="Mark node sockets to be processed as material uniforms", default=False)
    bpy.types.NodeTree.is_cached = bpy.props.BoolProperty(name="Node Tree Cached", description="No need to reexport node tree", default=False)
    bpy.types.Material.signature = bpy.props.StringProperty(name="Signature", description="Unique string generated from material nodes", default="")
    bpy.types.Material.is_cached = bpy.props.BoolProperty(name="Material Cached", description="No need to reexport material data", default=False, update=update_mat_cache)
    bpy.types.Material.lock_cache = bpy.props.BoolProperty(name="Lock Material Cache", description="Prevent is_cached from updating", default=False)
    # Particles
    bpy.types.ParticleSettings.arm_gpu_sim = bpy.props.BoolProperty(name="GPU Simulation", description="Calculate particle simulation on GPU", default=False, update=assets.invalidate_shader_cache)
    bpy.types.ParticleSettings.arm_count_mult = bpy.props.FloatProperty(name="Multiply Count", description="Multiply particle count when rendering in Armory", default=1.0)
    bpy.types.ParticleSettings.arm_loop = bpy.props.BoolProperty(name="Loop", description="Loop this particle system", default=False)

    create_wrd()

def create_wrd():
    if not 'Arm' in bpy.data.worlds:
        wrd = bpy.data.worlds.new('Arm')
        wrd.use_fake_user = True # Store data world object, add fake user to keep it alive
        wrd.arm_version = arm_version

def init_properties_on_save():
    wrd = bpy.data.worlds['Arm']
    if wrd.arm_project_name == '':
        # Take blend file name
        wrd.arm_project_name = arm.utils.blend_name()
        wrd.arm_project_scene = bpy.data.scenes[0].name
        init_properties_on_load()

def init_properties_on_load():
    global arm_version    
    if not 'Arm' in bpy.data.worlds:
        init_properties()
    arm.utils.fetch_script_names()
    wrd = bpy.data.worlds['Arm']
    # Outdated project
    if bpy.data.filepath != '' and wrd.arm_version != arm_version: # Call on project load only
        print('Project updated to sdk v' + arm_version)
        # TODO: deprecated - Cycles profile merged into Full
        if arm_version == '17.10':
            if len(wrd.arm_rplist) > 0:
                rpdat = arm.utils.get_rp()
                if rpdat.arm_material_model == 'Solid':
                    rpdat.arm_material_model = 'Mobile'
                else:
                    rpdat.arm_material_model = 'Full'
        wrd.arm_version = arm_version
        arm.make.clean_project()
    # Set url for embedded player
    if arm.utils.with_krom():
        barmory.set_files_location(arm.utils.get_fp_build() + '/krom')

def register():
    init_properties()
    arm.utils.fetch_bundled_script_names()

def unregister():
    pass
