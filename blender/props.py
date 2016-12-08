import bpy
from bpy.props import *
from props_traits_clip import *
from props_traits_action import *
import props_ui
import assets
import log
import armutils
try:
    import barmory
except ImportError:
    pass

arm_ver = '16.12'
def init_properties():
    global arm_ver
    bpy.types.World.arm_progress = bpy.props.FloatProperty(name="Progress", description="Current build progress", default=100.0, min=0.0, max=100.0, soft_min=0.0, soft_max=100.0, subtype='PERCENTAGE', get=log.get_progress)
    bpy.types.World.arm_version = StringProperty(name="Version", description="Armory SDK version", default=arm_ver)
    target_prop = EnumProperty(
        items = [('html5', 'HTML5', 'html5'),
                 ('windows', 'Windows', 'windows'),
                 ('macos', 'MacOS', 'macos'),
                 ('linux', 'Linux', 'linux'),
                 ('ios', 'iOS', 'ios'),
                 ('android-native', 'Android', 'android-native'),
                 ('krom', 'Krom', 'krom')],
        name="Target", default='html5',
        description='Build paltform')
    bpy.types.World.arm_project_target = target_prop
    bpy.types.World.arm_project_name = StringProperty(name="Name", description="Exported project name", default="")
    bpy.types.World.arm_project_package = StringProperty(name="Package", description="Package name for scripts", default="arm")
    bpy.types.World.arm_play_active_scene = BoolProperty(name="Play Active Scene", description="Load currently edited scene when launching player", default=True)
    bpy.types.World.arm_project_scene = StringProperty(name="Scene", description="Scene to load when launching player")
    bpy.types.World.arm_project_samples_per_pixel = IntProperty(name="Samples per Pixel", description="MSAA samples usable for render paths drawing directly to framebuffer", default=1)
    bpy.types.World.arm_physics = EnumProperty(
        items = [('Disabled', 'Disabled', 'Disabled'), 
                 ('Bullet', 'Bullet', 'Bullet')],
        name = "Physics", default='Bullet')
    bpy.types.World.arm_navigation = EnumProperty(
        items = [('Disabled', 'Disabled', 'Disabled'), 
                 ('Recast', 'Recast', 'Recast')],
        name = "Navigation", default='Recast')
    bpy.types.World.arm_khafile = StringProperty(name = "Khafile", description="Source appended to khafile.js")
    bpy.types.World.arm_command_line = StringProperty(name = "Command Line", description="Commands appended to khamake")
    bpy.types.World.arm_minimize = BoolProperty(name="Minimize Data", description="Export scene data in binary", default=True, update=assets.invalidate_compiled_data)
    bpy.types.World.arm_optimize_mesh = BoolProperty(name="Optimize Meshes", description="Export more efficient geometry indices, can prolong build times", default=False, update=assets.invalidate_mesh_data)
    bpy.types.World.arm_sampled_animation = BoolProperty(name="Sampled Animation", description="Export object animation as raw matrices", default=False, update=assets.invalidate_compiled_data)
    bpy.types.World.arm_deinterleaved_buffers = BoolProperty(name="Deinterleaved Buffers", description="Use deinterleaved vertex buffers", default=False)
    bpy.types.World.arm_export_hide_render = BoolProperty(name="Export Hidden Renders", description="Export hidden objects", default=True)
    bpy.types.World.arm_spawn_all_layers = BoolProperty(name="Spawn All Layers", description="Spawn objects from all scene layers", default=False)
    bpy.types.World.arm_play_advanced = BoolProperty(name="Advanced", default=False)
    bpy.types.World.arm_build_advanced = BoolProperty(name="Advanced", default=False)
    bpy.types.World.arm_project_advanced = BoolProperty(name="Advanced", default=False)
    bpy.types.World.arm_object_advanced = BoolProperty(name="Advanced", default=False)
    bpy.types.World.arm_material_advanced = BoolProperty(name="Advanced", default=False)
    bpy.types.World.arm_camera_effects_advanced = BoolProperty(name="Advanced", default=False)
    bpy.types.World.arm_lod_advanced = BoolProperty(name="Advanced", default=False)
    bpy.types.World.arm_lod_gen_levels = IntProperty(name="Levels", description="Number of levels to generate", default=3, min=1)
    bpy.types.World.arm_lod_gen_ratio = FloatProperty(name="Decimate Ratio", description="Decimate ratio", default=0.8)
    bpy.types.World.arm_cache_shaders = BoolProperty(name="Cache Shaders", description="Do not rebuild existing shaders", default=True, update=assets.invalidate_shader_cache)
    #bpy.types.World.arm_cache_envmaps = BoolProperty(name="Cache Envmaps", description="Do not remove prefiltered maps when cleaning project", default=True)
    bpy.types.World.arm_play_live_patch = BoolProperty(name="Live Patching", description="Sync running player data to Blender", default=True)
    bpy.types.World.arm_play_auto_build = BoolProperty(name="Auto Build", description="Rebuild scene on operator changes", default=True)
    bpy.types.World.arm_play_viewport_camera = BoolProperty(name="Viewport Camera", description="Start player at viewport camera position", default=False)
    bpy.types.World.arm_play_viewport_navigation = EnumProperty(
        items=[('None', 'None', 'None'),
               ('Walk', 'Walk', 'Walk')],
        name="Navigation", description="Enable camera controls", default='Walk')
    bpy.types.World.arm_play_console = BoolProperty(name="Debug Console", description="Show inspector in player", default=False)
    bpy.types.World.arm_play_runtime = EnumProperty(
        items=[('Electron', 'Electron', 'Electron'), 
               ('Browser', 'Browser', 'Browser'),
               ('Native', 'C++', 'Native'),
               ('Krom', 'Krom', 'Krom')],
        name="Runtime", description="Player runtime used when launching in new window", default='Krom')
    bpy.types.World.arm_loadbar = BoolProperty(name="Load Bar", description="Show asset loading progress on published builds", default=True)

    # For object
    bpy.types.Object.instanced_children = bpy.props.BoolProperty(name="Instanced Children", description="Use instaced rendering", default=False)
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
    bpy.types.Object.game_export = bpy.props.BoolProperty(name="Export", description="Export object data", default=True)
    bpy.types.Object.game_visible = bpy.props.BoolProperty(name="Visible", description="Render this object", default=True)
    bpy.types.Object.spawn = bpy.props.BoolProperty(name="Spawn", description="Auto-add this object when creating scene", default=True)
    bpy.types.Object.mobile = bpy.props.BoolProperty(name="Mobile", description="Object moves during gameplay", default=True)
    # - Clips
    bpy.types.Object.bone_animation_enabled = bpy.props.BoolProperty(name="Bone Animation", description="Enable skinning", default=True)
    bpy.types.Object.object_animation_enabled = bpy.props.BoolProperty(name="Object Animation", description="Enable timeline animation", default=True)
    bpy.types.Object.edit_tracks_prop = bpy.props.BoolProperty(name="Edit Clips", description="Manually set animation frames", default=False)
    bpy.types.Object.start_track_name_prop = bpy.props.StringProperty(name="Start Track", description="Play this track by default", default="")
    bpy.types.Object.my_cliptraitlist = bpy.props.CollectionProperty(type=ListClipTraitItem)
    bpy.types.Object.cliptraitlist_index = bpy.props.IntProperty(name="Clip index", default=0)
    # - Actions
    bpy.types.Object.edit_actions_prop = bpy.props.BoolProperty(name="Edit Actions", description="Manually set used actions", default=False)
    bpy.types.Object.start_action_name_prop = bpy.props.StringProperty(name="Start Action", description="Play this action by default", default="")
    # For speakers
    bpy.types.Speaker.loop = bpy.props.BoolProperty(name="Loop", description="Loop this sound", default=False)
    bpy.types.Speaker.stream = bpy.props.BoolProperty(name="Stream", description="Stream this sound", default=False)
    # For mesh
    bpy.types.Mesh.mesh_cached = bpy.props.BoolProperty(name="Mesh Cached", description="No need to reexport mesh data", default=False)
    bpy.types.Mesh.mesh_cached_verts = bpy.props.IntProperty(name="Last Verts", description="Number of vertices in last export", default=0)
    bpy.types.Mesh.mesh_cached_edges = bpy.props.IntProperty(name="Last Edges", description="Number of edges in last export", default=0)
    bpy.types.Mesh.dynamic_usage = bpy.props.BoolProperty(name="Dynamic Data Usage", description="Mesh data can change at runtime", default=False)
    bpy.types.Mesh.data_compressed = bpy.props.BoolProperty(name="Compress Data", description="Pack data into zip file", default=False)
    bpy.types.Curve.mesh_cached = bpy.props.BoolProperty(name="Mesh Cached", description="No need to reexport curve data", default=False)
    bpy.types.Curve.data_compressed = bpy.props.BoolProperty(name="Compress Data", description="Pack data into zip file", default=False)
    bpy.types.Curve.dynamic_usage = bpy.props.BoolProperty(name="Dynamic Data Usage", description="Curve data can change at runtime", default=False)
    bpy.types.MetaBall.mesh_cached = bpy.props.BoolProperty(name="Mesh Cached", description="No need to reexport metaball data", default=False)
    bpy.types.MetaBall.data_compressed = bpy.props.BoolProperty(name="Compress Data", description="Pack data into zip file", default=False)
    bpy.types.MetaBall.dynamic_usage = bpy.props.BoolProperty(name="Dynamic Data Usage", description="Metaball data can change at runtime", default=False)
    # For grease pencil
    bpy.types.GreasePencil.data_cached = bpy.props.BoolProperty(name="GP Cached", description="No need to reexport grease pencil data", default=False)
    bpy.types.GreasePencil.data_compressed = bpy.props.BoolProperty(name="Compress Data", description="Pack data into zip file", default=True)
    # For armature
    bpy.types.Armature.data_cached = bpy.props.BoolProperty(name="Armature Cached", description="No need to reexport armature data", default=False)
    bpy.types.Armature.data_compressed = bpy.props.BoolProperty(name="Compress Data", description="Pack data into zip file", default=False)
    # Actions
    bpy.types.Armature.edit_actions = bpy.props.BoolProperty(name="Edit Actions", description="Manually set used actions", default=False)
    bpy.types.Armature.my_actiontraitlist = bpy.props.CollectionProperty(type=ListActionTraitItem)
    bpy.types.Armature.actiontraitlist_index = bpy.props.IntProperty(name="Action index", default=0)
    # For camera
    bpy.types.Camera.frustum_culling = bpy.props.BoolProperty(name="Frustum Culling", description="Perform frustum culling for this camera", default=True)
    bpy.types.Camera.renderpath_path = bpy.props.StringProperty(name="Render Path", description="Render path nodes used for this camera", default="deferred_path_low")
    bpy.types.Camera.renderpath_id = bpy.props.StringProperty(name="Render Path ID", description="Asset ID", default="deferred")
    # TODO: Specify multiple material ids, merge ids from multiple cameras 
    bpy.types.Camera.renderpath_passes = bpy.props.StringProperty(name="Render Path Passes", description="Referenced render passes", default="")
    bpy.types.Camera.mesh_context = bpy.props.StringProperty(name="Mesh", default="mesh")
    bpy.types.Camera.mesh_context_empty = bpy.props.StringProperty(name="Mesh Empty", default="") # depthwrite
    bpy.types.Camera.shadows_context = bpy.props.StringProperty(name="Shadows", default="shadowmap")
    bpy.types.Camera.translucent_context = bpy.props.StringProperty(name="Translucent", default="translucent")
    bpy.types.Camera.overlay_context = bpy.props.StringProperty(name="Overlay", default="overlay")
    bpy.types.Camera.is_probe = bpy.props.BoolProperty(name="Probe", description="Render this camera as environment probe using Cycles", default=False)
    bpy.types.Camera.probe_generate_radiance = bpy.props.BoolProperty(name="Generate Radiance", description="Generate radiance textures", default=False)
    bpy.types.Camera.probe_texture = bpy.props.StringProperty(name="Texture", default="")
    bpy.types.Camera.probe_num_mips = bpy.props.IntProperty(name="Number of mips", default=0)
    bpy.types.Camera.probe_volume = bpy.props.StringProperty(name="Volume", default="")
    bpy.types.Camera.probe_strength = bpy.props.FloatProperty(name="Strength", default=1.0)
    bpy.types.Camera.probe_blending = bpy.props.FloatProperty(name="Blending", default=0.0)
    bpy.types.Camera.is_mirror = bpy.props.BoolProperty(name="Mirror", description="Render this camera into texture", default=False)
    bpy.types.Camera.mirror_resolution_x = bpy.props.FloatProperty(name="X", default=512.0)
    bpy.types.Camera.mirror_resolution_y = bpy.props.FloatProperty(name="Y", default=256.0)
    bpy.types.Camera.last_decal_context = bpy.props.StringProperty(name="Decal Context", default='')
    # Render path generator
    bpy.types.Camera.rp_renderer = EnumProperty(
        items=[('Forward', 'Forward', 'Forward'), 
               ('Deferred', 'Deferred', 'Deferred')],
        name="Renderer", description="Renderer type", default='Deferred')
    bpy.types.Camera.rp_depthprepass = bpy.props.BoolProperty(name="Depth Prepass", description="Depth Prepass for mesh context", default=True)
    bpy.types.Camera.rp_hdr = bpy.props.BoolProperty(name="HDR", description="Render in HDR Space", default=True)
    bpy.types.Camera.rp_worldnodes = bpy.props.BoolProperty(name="World Nodes", description="Draw world nodes", default=True)
    bpy.types.Camera.rp_compositornodes = bpy.props.BoolProperty(name="Compositor Nodes", description="Draw compositor nodes", default=True)
    bpy.types.Camera.rp_shadowmap = EnumProperty(
        items=[('None', 'None', 'None'),
               ('512', '512', '512'),
               ('1024', '1024', '1024'),
               ('2048', '2048', '2048'),
               ('4096', '4096', '4096')],
        name="Shadow Map", description="Shadow map resolution", default='2048')
    bpy.types.Camera.rp_supersampling = EnumProperty(
        items=[('1X', '1X', '1X'),
               ('2X', '2X', '2X'),
               ('4X', '4X', '4X')],
        name="Super Sampling", description="Screen resolution multiplier", default='1X')
    bpy.types.Camera.rp_antialiasing = EnumProperty(
        items=[('None', 'None', 'None'),
               ('FXAA', 'FXAA', 'FXAA'),
               ('SMAA', 'SMAA', 'SMAA'),
               ('TAA', 'TAA', 'TAA')],
        name="Anti Aliasing", description="Post-process anti aliasing technique", default='SMAA')
    bpy.types.Camera.rp_volumetriclight = bpy.props.BoolProperty(name="Volumetric Light", description="Use volumetric lighting", default=False)
    bpy.types.Camera.rp_ssao = bpy.props.BoolProperty(name="SSAO", description="Screen space ambient occlusion", default=True)
    bpy.types.Camera.rp_ssr = bpy.props.BoolProperty(name="SSR", description="Screen space reflections", default=True)
    bpy.types.Camera.rp_bloom = bpy.props.BoolProperty(name="Bloom", description="Bloom processing", default=True)
    bpy.types.Camera.rp_motionblur = bpy.props.BoolProperty(name="Motion Blur", description="Motion blur processing", default=False)
    bpy.types.Camera.rp_translucency = bpy.props.BoolProperty(name="Translucency", description="Order independent translucency", default=False)
    bpy.types.Camera.rp_decals = bpy.props.BoolProperty(name="Decals", description="Render decals", default=False)
    bpy.types.Camera.rp_overlays = bpy.props.BoolProperty(name="Overlays", description="Render overlays", default=False)

    # For world
    bpy.types.World.world_envtex_name = bpy.props.StringProperty(name="Environment Texture", default='')
    bpy.types.World.world_envtex_irr_name = bpy.props.StringProperty(name="Environment Irradiance", default='')
    bpy.types.World.world_envtex_num_mips = bpy.props.IntProperty(name="Number of mips", default=0)
    bpy.types.World.world_envtex_color = bpy.props.FloatVectorProperty(name="Environment Color", size=4, default=[0,0,0,1])
    bpy.types.World.world_envtex_strength = bpy.props.FloatProperty(name="Environment Strength", default=1.0)
    bpy.types.World.world_envtex_sun_direction = bpy.props.FloatVectorProperty(name="Sun Direction", size=3, default=[0,0,0])
    bpy.types.World.world_envtex_turbidity = bpy.props.FloatProperty(name="Turbidity", default=1.0)
    bpy.types.World.world_envtex_ground_albedo = bpy.props.FloatProperty(name="Ground Albedo", default=0.0)
    bpy.types.World.world_defs = bpy.props.StringProperty(name="World Shader Defs", default='')
    bpy.types.World.generate_radiance = bpy.props.BoolProperty(name="Probe Radiance", default=True, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_radiance_size = EnumProperty(
        items=[('512', '512', '512'),
               ('1024', '1024', '1024'), 
               ('2048', '2048', '2048')],
        name="Probe Size", description="Prefiltered map size", default='1024', update=assets.invalidate_envmap_data)
    bpy.types.World.generate_radiance_sky = bpy.props.BoolProperty(name="Sky Radiance", default=True, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_radiance_sky_type = EnumProperty(
        items=[('Fake', 'Fake', 'Fake'), 
               ('Hosek', 'Hosek', 'Hosek')],
        name="Type", description="Prefiltered maps to be used for radiance", default='Hosek', update=assets.invalidate_envmap_data)
    bpy.types.World.generate_clouds = bpy.props.BoolProperty(name="Clouds", default=False, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_clouds_density = bpy.props.FloatProperty(name="Density", default=0.5, min=0.0, max=10.0, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_clouds_size = bpy.props.FloatProperty(name="Size", default=1.0, min=0.0, max=10.0, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_clouds_lower = bpy.props.FloatProperty(name="Lower", default=2.0, min=1.0, max=10.0, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_clouds_upper = bpy.props.FloatProperty(name="Upper", default=3.5, min=1.0, max=10.0, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_clouds_wind = bpy.props.FloatVectorProperty(name="Wind", default=[0.2, 0.06], size=2, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_clouds_secondary = bpy.props.FloatProperty(name="Secondary", default=0.0, min=0.0, max=10.0, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_clouds_precipitation = bpy.props.FloatProperty(name="Precipitation", default=1.0, min=0.0, max=2.0, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_clouds_eccentricity = bpy.props.FloatProperty(name="Eccentricity", default=0.6, min=0.0, max=1.0, update=assets.invalidate_shader_cache)
    bpy.types.World.shadowmap_size = bpy.props.IntProperty(name="Shadowmap Size", default=0, update=assets.invalidate_shader_cache)
    bpy.types.World.scripts_list = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.World.bundled_scripts_list = bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.World.generate_ocean = bpy.props.BoolProperty(name="Ocean", default=False, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_ocean_base_color = bpy.props.FloatVectorProperty(name="Base Color", size=3, default=[0.1, 0.19, 0.37], subtype='COLOR', update=assets.invalidate_shader_cache)
    bpy.types.World.generate_ocean_water_color = bpy.props.FloatVectorProperty(name="Water Color", size=3, default=[0.6, 0.7, 0.9], subtype='COLOR', update=assets.invalidate_shader_cache)
    bpy.types.World.generate_ocean_level = bpy.props.FloatProperty(name="Level", default=0.0, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_ocean_amplitude = bpy.props.FloatProperty(name="Amplitude", default=2.5, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_ocean_height = bpy.props.FloatProperty(name="Height", default=0.6, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_ocean_choppy = bpy.props.FloatProperty(name="Choppy", default=4.0, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_ocean_speed = bpy.props.FloatProperty(name="Speed", default=1.0, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_ocean_freq = bpy.props.FloatProperty(name="Freq", default=0.16, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_ocean_fade = bpy.props.FloatProperty(name="Fade", default=1.8, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_ssao = bpy.props.BoolProperty(name="SSAO", description="Screen-Space Ambient Occlusion", default=True, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_ssao_size = bpy.props.FloatProperty(name="Size", default=0.12, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_ssao_strength = bpy.props.FloatProperty(name="Strength", default=0.25, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_ssao_texture_scale = bpy.props.FloatProperty(name="Texture Scale", default=1.0, min=0.0, max=1.0, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_shadows = bpy.props.BoolProperty(name="Shadows", default=True, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_bloom = bpy.props.BoolProperty(name="Bloom", default=True, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_bloom_threshold = bpy.props.FloatProperty(name="Threshold", default=20.0, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_bloom_strength = bpy.props.FloatProperty(name="Strength", default=0.5, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_bloom_radius = bpy.props.FloatProperty(name="Radius", default=0.5, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_motion_blur = bpy.props.BoolProperty(name="Motion Blur", default=True, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_motion_blur_intensity = bpy.props.FloatProperty(name="Intensity", default=1.0, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_ssr = bpy.props.BoolProperty(name="SSR", description="Screen-Space Reflections", default=True, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_ssr_ray_step = bpy.props.FloatProperty(name="Ray Step", default=0.04, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_ssr_min_ray_step = bpy.props.FloatProperty(name="Ray Step Min", default=0.05, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_ssr_search_dist = bpy.props.FloatProperty(name="Search Dist", default=5.0, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_ssr_falloff_exp = bpy.props.FloatProperty(name="Falloff Exp", default=5.0, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_ssr_jitter = bpy.props.FloatProperty(name="Jitter", default=0.6, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_ssr_texture_scale = bpy.props.FloatProperty(name="Texture Scale", default=1.0, min=0.0, max=1.0, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_volumetric_light = bpy.props.BoolProperty(name="Volumetric Light", description="", default=True, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_volumetric_light_air_turbidity = bpy.props.FloatProperty(name="Air Turbidity", default=1.0, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_volumetric_light_air_color = bpy.props.FloatVectorProperty(name="Air Color", size=3, default=[1.0, 1.0, 1.0], subtype='COLOR', update=assets.invalidate_shader_cache)
    bpy.types.World.generate_pcss_state = EnumProperty(
        items=[('On', 'On', 'On'),
               ('Off', 'Off', 'Off'), 
               ('Auto', 'Auto', 'Auto')],
        name="Soft Shadows", description="Percentage Closer Soft Shadows", default='Off', update=assets.invalidate_shader_cache)
    bpy.types.World.generate_pcss_rings = bpy.props.IntProperty(name="Rings", description="", default=20, update=assets.invalidate_shader_cache)
    # Compositor
    bpy.types.World.generate_letterbox = bpy.props.BoolProperty(name="Letterbox", default=False, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_letterbox_size = bpy.props.FloatProperty(name="Size", default=0.1, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_grain = bpy.props.BoolProperty(name="Film Grain", default=False, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_grain_strength = bpy.props.FloatProperty(name="Strength", default=2.0, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_fog = bpy.props.BoolProperty(name="Volumetric Fog", default=False, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_fog_color = bpy.props.FloatVectorProperty(name="Color", size=3, subtype='COLOR', default=[0.5, 0.6, 0.7], update=assets.invalidate_shader_cache)
    bpy.types.World.generate_fog_amounta = bpy.props.FloatProperty(name="Amount A", default=0.25, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_fog_amountb = bpy.props.FloatProperty(name="Amount B", default=0.5, update=assets.invalidate_shader_cache)
    # Skin
    bpy.types.World.generate_gpu_skin = bpy.props.BoolProperty(name="GPU Skinning", description="Calculate skinning on GPU", default=True, update=assets.invalidate_shader_cache)
    bpy.types.World.generate_gpu_skin_max_bones = bpy.props.IntProperty(name="Max Bones", default=50, min=1, max=84, update=assets.invalidate_shader_cache)
    # Material override flags
    bpy.types.World.anisotropic_filtering_state = EnumProperty(
        items=[('On', 'On', 'On'),
               ('Off', 'Off', 'Off'), 
               ('Auto', 'Auto', 'Auto')],
        name="Anisotropic Filtering", description="Texture filtering", default='On')
    bpy.types.World.force_no_culling = bpy.props.BoolProperty(name="Force No Culling", default=False)
    bpy.types.World.tessellation_enabled = bpy.props.BoolProperty(name="Tessellation", description="Enable tessellation for height maps on supported targets", default=True)
    # Lighting flags
    bpy.types.World.diffuse_model = EnumProperty(
        items=[('Lambert', 'Lambert', 'Lambert'),
               ('Oren Nayar', 'Oren Nayar', 'Oren Nayar')],
        name="Diffuse", description="Diffuse model", default='Lambert', update=assets.invalidate_shader_cache)
    bpy.types.World.voxelgi = bpy.props.BoolProperty(name="VGI", description="Voxel-based Global Illumination", default=False, update=assets.invalidate_shader_cache)
    bpy.types.World.voxelgi_dimensions = bpy.props.FloatVectorProperty(name="Dimensions", description="3D texture size", size=3, default=[128, 128, 128], update=assets.invalidate_shader_cache)
    # For material
    bpy.types.Material.cast_shadow = bpy.props.BoolProperty(name="Cast Shadow", default=True)
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
    bpy.types.Material.height_tess = bpy.props.BoolProperty(name="Tessellated Displacement", description="Use tessellation shaders to subdivide and displace surface", default=True)
    bpy.types.Material.height_tess_inner = bpy.props.IntProperty(name="Inner Level", description="Inner tessellation level for mesh", default=14)
    bpy.types.Material.height_tess_outer = bpy.props.IntProperty(name="Outer Level", description="Outer tessellation level for mesh", default=14)
    bpy.types.Material.height_tess_shadows = bpy.props.BoolProperty(name="Tessellated Shadows", description="Use tessellation shaders when rendering shadow maps", default=True)
    bpy.types.Material.height_tess_shadows_inner = bpy.props.IntProperty(name="Inner Level", description="Inner tessellation level for shadows", default=7)
    bpy.types.Material.height_tess_shadows_outer = bpy.props.IntProperty(name="Outer Level", description="Outer tessellation level for shadows", default=7)
    bpy.types.Material.transluc_shadows = bpy.props.BoolProperty(name="Translucent Shadows", description="Cast shadows for translucent surfaces", default=True)
    # For scene
    bpy.types.Scene.game_export = bpy.props.BoolProperty(name="Export", description="Export scene data", default=True)
    bpy.types.Scene.gp_export = bpy.props.BoolProperty(name="Export Grease Pencil", description="Export grease pencil data", default=True)
    bpy.types.Scene.data_compressed = bpy.props.BoolProperty(name="Compress Data", description="Pack data into zip file", default=False)
    # For lamp
    bpy.types.Lamp.lamp_clip_start = bpy.props.FloatProperty(name="Clip Start", default=0.1)
    bpy.types.Lamp.lamp_clip_end = bpy.props.FloatProperty(name="Clip End", default=50.0)
    bpy.types.Lamp.lamp_fov = bpy.props.FloatProperty(name="Field of View", default=0.84)
    bpy.types.Lamp.lamp_shadows_bias = bpy.props.FloatProperty(name="Shadows Bias", description="Depth offset for shadow acne", default=0.0002)
    bpy.types.Lamp.lamp_omni_shadows = bpy.props.BoolProperty(name="Omnidirectional Shadows", description="Fakes omnidirectional shadows by creating 6 directional lights - will result in preformance loss - usable for deferred renderers only", default=False)

    if not 'Arm' in bpy.data.worlds:
        wrd = bpy.data.worlds.new('Arm')
        wrd.use_fake_user = True # Store data world object, add fake user to keep it alive

def init_properties_on_save():
    wrd = bpy.data.worlds['Arm']
    if wrd.arm_project_name == '':
        # Take blend file name
        wrd.arm_project_name = bpy.path.basename(bpy.context.blend_data.filepath).rsplit('.')[0]
        wrd.arm_project_scene = bpy.data.scenes[0].name
        # Switch to Cycles
        for scene in bpy.data.scenes:
            # if scene.render.engine != 'CYCLES':
                # scene.render.engine = 'CYCLES'
            scene.render.fps = 60 # Default to 60fps for chromium update loop
        # Force camera far to at least 200 units for now, to prevent fighting with light far plane
        for c in bpy.data.cameras:
            if c.clip_end < 200:
                c.clip_end = 200
        # Move default lamp a little further to keep fov low for now
        if 'Lamp' in bpy.data.objects:
            loc = bpy.data.objects['Lamp'].location
            if int(loc.x) == 4 and int(loc.y) == 1 and int(loc.z) == 5:
                loc.x = 11.0
                loc.y = 4.0
                loc.z = 16.0
        # Use nodes
        for w in bpy.data.worlds:
            w.use_nodes = True
        for s in bpy.data.scenes:
            s.use_nodes = True
        for l in bpy.data.lamps:
            l.use_nodes = True
        for m in bpy.data.materials:
            m.use_nodes = True

        init_properties_on_load()

def init_properties_on_load():
    global arm_ver    
    
    if not 'Arm' in bpy.data.worlds:
        init_properties()

    armutils.fetch_script_names()
    
    wrd = bpy.data.worlds['Arm']

    # Outdated project
    if int(wrd.arm_version.replace(".", "")) < int(arm_ver.replace(".", "")):
        wrd.arm_version = arm_ver

    # Set url for embedded player
    if armutils.with_krom():
        barmory.set_files_location(armutils.get_fp() + '/build/krom')

def register():
    init_properties()

def unregister():
    pass
