import shutil
import bpy
import os
import json
import subprocess
import nodes_renderpath
from bpy.types import Menu, Panel, UIList
from bpy.props import *
from traits_clip import *
from traits_action import *
import utils
import make
import space_armory
import time
last_time = time.time()
try:
    import bgame
except ImportError:
    pass

def on_scene_update_post(context):
    global last_time

    if time.time() - last_time >= (1 / bpy.context.scene.render.fps): # Use frame rate for update frequency for now
        last_time = time.time()

        # Tag redraw if playing in space_armory
        make.play_project.chromium_running = False
        if space_armory.SPACEARMORY_HT_header.is_paused == False:
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_GAME':
                    area.tag_redraw()
                    make.play_project.chromium_running = True

        # Auto patch on every operator change
        if (make.play_project.playproc != None or make.play_project.chromium_running) and \
           bpy.data.worlds['Arm'].ArmPlayLivePatch and \
           bpy.data.worlds['Arm'].ArmPlayAutoBuild and \
           len(bpy.context.window_manager.operators) > 0 and \
           on_scene_update_post.last_operator != bpy.context.window_manager.operators[-1]:
            on_scene_update_post.last_operator = bpy.context.window_manager.operators[-1]
            make.patch_project()
            make.compile_project()

        # Check if chromium is running
        if utils.with_chromium():
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_GAME':
                    # Read chromium console
                    if bgame.get_console_updated() == 1:
                        make.armory_space_log(bgame.get_console())
                    break

        # New output has been logged
        if make.armory_log.tag_redraw:
            make.armory_log.tag_redraw = False
            for area in bpy.context.screen.areas:
                if area.type == 'INFO':
                    area.tag_redraw()
                    break

        # Player finished, redraw play buttons
        if make.play_project.playproc_finished:
            make.play_project.playproc_finished = False
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D' or area.type == 'PROPERTIES':
                    area.tag_redraw()

        # Compilation finished
        if make.play_project.compileproc_finished:
            make.play_project.compileproc_finished = False
            # Notify embedded player
            if make.play_project.chromium_running:
                bgame.call_js('armory.Scene.patch();')
            # Switch to armory space
            elif utils.with_chromium() and make.play_project.in_viewport:
                make.play_project.play_area.type = 'VIEW_GAME'

    edit_obj = bpy.context.edit_object
    if edit_obj != None and edit_obj.is_updated_data:
        if edit_obj.type == 'MESH':
            edit_obj.data.mesh_cached = False
        elif edit_obj.type == 'ARMATURE':
            edit_obj.data.armature_cached = False

on_scene_update_post.last_operator = None

def on_load_pre(context):
    bpy.ops.arm_addon.stop('EXEC_DEFAULT')

def invalidate_shader_cache(self, context):
    # compiled.glsl changed, recompile all shaders next time
    if invalidate_shader_cache.enabled:
        fp = utils.get_fp()
        if os.path.isdir(fp + '/build/compiled/ShaderDatas'):
            shutil.rmtree(fp + '/build/compiled/ShaderDatas')
invalidate_shader_cache.enabled = True # Disable invalidating during build process

def invalidate_compiled_data(self, context):
    fp = utils.get_fp()
    if os.path.isdir(fp + '/build/compiled/Assets'):
        shutil.rmtree(fp + '/build/compiled/Assets')
    if os.path.isdir(fp + '/build/compiled/ShaderDatas'):
        shutil.rmtree(fp + '/build/compiled/ShaderDatas')

def invalidate_mesh_data(self, context):
    fp = utils.get_fp()
    if os.path.isdir(fp + '/build/compiled/Assets/meshes'):
        shutil.rmtree(fp + '/build/compiled/Assets/meshes')

def initProperties():
    # For project
    bpy.types.World.ArmVersion = StringProperty(name = "ArmVersion", default="")
    target_prop = EnumProperty(
        items = [('html5', 'HTML5', 'html5'), 
                 ('windows', 'Windows', 'windows'), 
                 ('macos', 'MacOS', 'macos'),
                 ('linux', 'Linux', 'linux'), 
                 ('ios', 'iOS', 'ios'),
                 ('android-native', 'Android', 'android-native')],
        name = "Target", default='html5')
    bpy.types.World.ArmProjectTarget = target_prop
    bpy.types.World.ArmPublishTarget = target_prop
    bpy.types.World.ArmProjectName = StringProperty(name = "Name", default="ArmoryGame")
    bpy.types.World.ArmProjectPackage = StringProperty(name = "Package", default="game")
    bpy.types.World.ArmPlayActiveScene = BoolProperty(name="Play Active Scene", default=True)
    bpy.types.World.ArmProjectScene = StringProperty(name = "Scene")
    bpy.types.World.ArmProjectSamplesPerPixel = IntProperty(name = "Samples per Pixel", default=1)
    bpy.types.World.ArmPhysics = EnumProperty(
        items = [('Disabled', 'Disabled', 'Disabled'), 
                 ('Bullet', 'Bullet', 'Bullet')],
        name = "Physics", default='Bullet')
    bpy.types.World.ArmNavigation = EnumProperty(
        items = [('Disabled', 'Disabled', 'Disabled'), 
                 ('Recast', 'Recast', 'Recast')],
        name = "Navigation", default='Disabled')
    bpy.types.World.ArmKhafile = StringProperty(name = "Khafile")
    bpy.types.World.ArmMinimize = BoolProperty(name="Minimize Data", default=True, update=invalidate_compiled_data)
    bpy.types.World.ArmOptimizeMesh = BoolProperty(name="Optimize Meshes", default=False, update=invalidate_mesh_data)
    bpy.types.World.ArmSampledAnimation = BoolProperty(name="Sampled Animation", default=False, update=invalidate_compiled_data)
    bpy.types.World.ArmDeinterleavedBuffers = BoolProperty(name="Deinterleaved Buffers", default=False)
    bpy.types.World.ArmExportHideRender = BoolProperty(name="Export Hidden Renders", default=False)
    bpy.types.World.ArmSpawnAllLayers = BoolProperty(name="Spawn All Layers", default=False)
    bpy.types.World.ArmCacheShaders = BoolProperty(name="Cache Shaders", default=True)
    bpy.types.World.ArmPlayLivePatch = BoolProperty(name="Live Patching", default=True)
    bpy.types.World.ArmPlayAutoBuild = BoolProperty(name="Auto Build", default=True)
    bpy.types.World.ArmPlayViewportCamera = BoolProperty(name="Viewport Camera", default=False)
    bpy.types.World.ArmPlayViewportNavigation = EnumProperty(
        items = [('None', 'None', 'None'), 
                 ('Walk', 'Walk', 'Walk')],
        name = "Navigation", default='Walk')
    bpy.types.World.ArmPlayConsole = BoolProperty(name="Debug Console", default=False)
    bpy.types.World.ArmPlayDeveloperTools = BoolProperty(name="Developer Tools", default=False)
    bpy.types.World.ArmPlayRuntime = EnumProperty(
        items = [('Electron', 'Electron', 'Electron'), 
                 ('Browser', 'Browser', 'Browser')],
                 # ('Native', 'Native', 'Native')],
                 #('Krom', 'Krom', 'Krom')],
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
    bpy.types.Object.game_visible = bpy.props.BoolProperty(name="Visible", default=True)
    bpy.types.Object.spawn = bpy.props.BoolProperty(name="Spawn", description="Auto-add this object when creating scene", default=True)
    bpy.types.Object.mobile = bpy.props.BoolProperty(name="Mobile", description="Object moves during gameplay", default=True)
    # - Clips
    bpy.types.Object.bone_animation_enabled = bpy.props.BoolProperty(name="Bone Animation", default=True)
    bpy.types.Object.object_animation_enabled = bpy.props.BoolProperty(name="Object Animation", default=True)
    bpy.types.Object.edit_tracks_prop = bpy.props.BoolProperty(name="Edit Clips", description="A name for this item", default=False)
    bpy.types.Object.start_track_name_prop = bpy.props.StringProperty(name="Start Track", description="A name for this item", default="")
    bpy.types.Object.my_cliptraitlist = bpy.props.CollectionProperty(type=ListClipTraitItem)
    bpy.types.Object.cliptraitlist_index = bpy.props.IntProperty(name="Index for my_list", default=0)
    # - Actions
    bpy.types.Object.edit_actions_prop = bpy.props.BoolProperty(name="Edit Actions", description="A name for this item", default=False)
    bpy.types.Object.start_action_name_prop = bpy.props.StringProperty(name="Start Action", description="A name for this item", default="")
    # For mesh
    bpy.types.Mesh.mesh_cached = bpy.props.BoolProperty(name="Mesh Cached", default=False)
    bpy.types.Mesh.mesh_cached_verts = bpy.props.IntProperty(name="Last Verts", default=0)
    bpy.types.Mesh.mesh_cached_edges = bpy.props.IntProperty(name="Last Edges", default=0)
    bpy.types.Mesh.static_usage = bpy.props.BoolProperty(name="Static Data Usage", default=True)
    bpy.types.Curve.mesh_cached = bpy.props.BoolProperty(name="Mesh Cached", default=False)
    bpy.types.Curve.static_usage = bpy.props.BoolProperty(name="Static Data Usage", default=True)
    # For armature
    bpy.types.Armature.armature_cached = bpy.props.BoolProperty(name="Armature Cached", default=False)
    # Actions
    bpy.types.Armature.edit_actions = bpy.props.BoolProperty(name="Edit Actions", default=False)
    bpy.types.Armature.my_actiontraitlist = bpy.props.CollectionProperty(type=ListActionTraitItem)
    bpy.types.Armature.actiontraitlist_index = bpy.props.IntProperty(name="Index for my_list", default=0)
    # For camera
    bpy.types.Camera.frustum_culling = bpy.props.BoolProperty(name="Frustum Culling", default=True)
    bpy.types.Camera.renderpath_path = bpy.props.StringProperty(name="Render Path", default="deferred_path")
    bpy.types.Camera.renderpath_id = bpy.props.StringProperty(name="Render Path ID", default="deferred")
	# TODO: Specify multiple material ids, merge ids from multiple cameras 
    bpy.types.Camera.renderpath_passes = bpy.props.StringProperty(name="Render Path Passes", default="")
    bpy.types.Camera.mesh_context = bpy.props.StringProperty(name="Mesh", default="mesh")
    bpy.types.Camera.mesh_context_empty = bpy.props.StringProperty(name="Mesh Empty", default="depthwrite")
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
    bpy.types.Camera.is_mirror = bpy.props.BoolProperty(name="Mirror", default=False)
    bpy.types.Camera.mirror_resolution_x = bpy.props.FloatProperty(name="X", default=512.0)
    bpy.types.Camera.mirror_resolution_y = bpy.props.FloatProperty(name="Y", default=256.0)
    bpy.types.Camera.last_decal_context = bpy.props.StringProperty(name="Decal Context", default='')
    # For world
    bpy.types.World.world_envtex_name = bpy.props.StringProperty(name="Environment Texture", default='')
    bpy.types.World.world_envtex_num_mips = bpy.props.IntProperty(name="Number of mips", default=0)
    bpy.types.World.world_envtex_color = bpy.props.FloatVectorProperty(name="Environment Color", size=4, default=[0,0,0,1])
    bpy.types.World.world_envtex_strength = bpy.props.FloatProperty(name="Environment Strength", default=1.0)
    bpy.types.World.world_envtex_sun_direction = bpy.props.FloatVectorProperty(name="Sun Direction", size=3, default=[0,0,0])
    bpy.types.World.world_envtex_turbidity = bpy.props.FloatProperty(name="Turbidity", default=1.0)
    bpy.types.World.world_envtex_ground_albedo = bpy.props.FloatProperty(name="Ground Albedo", default=0.0)
    bpy.types.World.world_defs = bpy.props.StringProperty(name="World Shader Defs", default='')
    bpy.types.World.generate_radiance = bpy.props.BoolProperty(name="Probe Radiance", default=True, update=invalidate_shader_cache)
    bpy.types.World.generate_radiance_sky = bpy.props.BoolProperty(name="Sky Radiance", default=False, update=invalidate_shader_cache)
    bpy.types.World.generate_clouds = bpy.props.BoolProperty(name="Clouds", default=False, update=invalidate_shader_cache)
    bpy.types.World.generate_clouds_density = bpy.props.FloatProperty(name="Density", default=0.5, min=0.0, max=10.0, update=invalidate_shader_cache)
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
    bpy.types.World.generate_ssao_size = bpy.props.FloatProperty(name="Size", default=0.12, update=invalidate_shader_cache)
    bpy.types.World.generate_ssao_strength = bpy.props.FloatProperty(name="Strength", default=0.25, update=invalidate_shader_cache)
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
    bpy.types.World.generate_ssr_texture_scale = bpy.props.FloatProperty(name="Texture Scale", default=1.0, min=0.0, max=1.0, update=invalidate_shader_cache)
    bpy.types.World.generate_volumetric_light = bpy.props.BoolProperty(name="Volumetric Light", description="", default=True, update=invalidate_shader_cache)
    bpy.types.World.generate_volumetric_light_air_turbidity = bpy.props.FloatProperty(name="Air Turbidity", default=1.0, update=invalidate_shader_cache)
    bpy.types.World.generate_volumetric_light_air_color = bpy.props.FloatVectorProperty(name="Air Color", size=3, default=[1.0, 1.0, 1.0], subtype='COLOR', update=invalidate_shader_cache)
    bpy.types.World.generate_pcss = bpy.props.BoolProperty(name="Percentage Closer Soft Shadows", description="", default=False, update=invalidate_shader_cache)
    bpy.types.World.generate_pcss_rings = bpy.props.IntProperty(name="Rings", description="", default=20, update=invalidate_shader_cache)
    # Compositor
    bpy.types.World.generate_letterbox = bpy.props.BoolProperty(name="Letterbox", default=False, update=invalidate_shader_cache)
    bpy.types.World.generate_letterbox_size = bpy.props.FloatProperty(name="Size", default=0.1, update=invalidate_shader_cache)
    bpy.types.World.generate_grain = bpy.props.BoolProperty(name="Film Grain", default=False, update=invalidate_shader_cache)
    bpy.types.World.generate_grain_strength = bpy.props.FloatProperty(name="Strength", default=2.0, update=invalidate_shader_cache)
    bpy.types.World.generate_fog = bpy.props.BoolProperty(name="Volumetric Fog", default=False, update=invalidate_shader_cache)
    bpy.types.World.generate_fog_color = bpy.props.FloatVectorProperty(name="Color", size=3, subtype='COLOR', default=[0.5, 0.6, 0.7], update=invalidate_shader_cache)
    bpy.types.World.generate_fog_amounta = bpy.props.FloatProperty(name="Amount A", default=0.25, update=invalidate_shader_cache)
    bpy.types.World.generate_fog_amountb = bpy.props.FloatProperty(name="Amount B", default=0.5, update=invalidate_shader_cache)
    # Skin
    bpy.types.World.generate_gpu_skin = bpy.props.BoolProperty(name="GPU Skinning", default=True, update=invalidate_shader_cache)
    bpy.types.World.generate_gpu_skin_max_bones = bpy.props.IntProperty(name="Max Bones", default=50, min=1, max=84, update=invalidate_shader_cache)
    # Material override flags
    bpy.types.World.force_no_culling = bpy.props.BoolProperty(name="Force No Culling", default=False)
    bpy.types.World.force_anisotropic_filtering = bpy.props.BoolProperty(name="Force Anisotropic Filtering", default=False)
    # Lighting flags
    bpy.types.World.diffuse_oren_nayar = bpy.props.BoolProperty(name="Oren Nayar Diffuse", default=False, update=invalidate_shader_cache)
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
    # For lamp
    bpy.types.Lamp.lamp_clip_start = bpy.props.FloatProperty(name="Clip Start", default=0.1)
    bpy.types.Lamp.lamp_clip_end = bpy.props.FloatProperty(name="Clip End", default=50.0)
    bpy.types.Lamp.lamp_fov = bpy.props.FloatProperty(name="FoV", default=0.785)
    bpy.types.Lamp.lamp_shadows_bias = bpy.props.FloatProperty(name="Shadows Bias", default=0.0001)

# Menu in object region
class ObjectPropsPanel(bpy.types.Panel):
    bl_label = "Armory Props"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
 
    def draw(self, context):
        layout = self.layout
        obj = bpy.context.object
        if obj == None:
            return
            
        if bpy.data.worlds['Arm'].ArmExportHideRender == False:
            layout.prop(obj, 'hide_render')
            hide = obj.hide_render
        else:
            layout.prop(obj, 'game_export')
            hide = not obj.game_export
        
        if hide:
            return
        
        layout.prop(obj, 'spawn')
        layout.prop(obj, 'game_visible')
        layout.prop(obj, 'mobile')
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

        if obj.type == 'ARMATURE':
            layout.prop(obj, 'bone_animation_enabled')
            if obj.bone_animation_enabled:
                layout.prop(obj, 'edit_actions_prop')
                if obj.edit_actions_prop:
                    layout.prop_search(obj, "start_action_name_prop", obj.data, "my_actiontraitlist", "Start Action")
        else:
            layout.prop(obj, 'object_animation_enabled')
        
        if (obj.type == 'ARMATURE' and obj.bone_animation_enabled) or (obj.type != 'ARMATURE' and obj.object_animation_enabled):
            layout.prop(obj, 'edit_tracks_prop')
            if obj.edit_tracks_prop:
                layout.prop_search(obj, "start_track_name_prop", obj, "my_cliptraitlist", "Start Clip")
                # Tracks list
                layout.label("Clips")
                animrow = layout.row()
                animrows = 2
                if len(obj.my_cliptraitlist) > 1:
                    animrows = 4
                
                row = layout.row()
                row.template_list("MY_UL_ClipTraitList", "The_List", obj, "my_cliptraitlist", obj, "cliptraitlist_index", rows=animrows)

                col = row.column(align=True)
                col.operator("my_cliptraitlist.new_item", icon='ZOOMIN', text="")
                col.operator("my_cliptraitlist.delete_item", icon='ZOOMOUT', text="")

                if len(obj.my_cliptraitlist) > 1:
                    col.separator()
                    col.operator("my_cliptraitlist.move_item", icon='TRIA_UP', text="").direction = 'UP'
                    col.operator("my_cliptraitlist.move_item", icon='TRIA_DOWN', text="").direction = 'DOWN'

                if obj.cliptraitlist_index >= 0 and len(obj.my_cliptraitlist) > 0:
                    animitem = obj.my_cliptraitlist[obj.cliptraitlist_index]         
                    row = layout.row()
                    row.prop(animitem, "start_prop")
                    row.prop(animitem, "end_prop")
                    layout.prop(animitem, "speed_prop")
                    layout.prop(animitem, "loop_prop")
                    layout.prop(animitem, "reflect_prop")

# Menu in modifiers region
class ModifiersPropsPanel(bpy.types.Panel):
    bl_label = "Armory Props"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "modifier"
 
    def draw(self, context):
        layout = self.layout
        obj = bpy.context.object
        if obj == None:
            return

        # Assume as first modifier
        if len(obj.modifiers) > 0 and obj.modifiers[0].type == 'OCEAN':
            layout.prop(bpy.data.worlds['Arm'], 'generate_ocean_base_color')
            layout.prop(bpy.data.worlds['Arm'], 'generate_ocean_water_color')
            layout.prop(bpy.data.worlds['Arm'], 'generate_ocean_fade')

# Menu in data region
class DataPropsPanel(bpy.types.Panel):
    bl_label = "Armory Props"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
 
    def draw(self, context):
        layout = self.layout
        obj = bpy.context.object
        if obj == None:
            return

        if obj.type == 'CAMERA':
            layout.prop(obj.data, 'is_probe')
            if obj.data.is_probe == True:
                layout.prop(obj.data, 'probe_texture')
                layout.prop_search(obj.data, "probe_volume", bpy.data, "objects")
                layout.prop(obj.data, 'probe_strength')
                layout.prop(obj.data, 'probe_blending')
            layout.prop(obj.data, 'is_mirror')
            if obj.data.is_mirror == True:
                layout.label('Resolution')
                layout.prop(obj.data, 'mirror_resolution_x')
                layout.prop(obj.data, 'mirror_resolution_y')
            layout.prop(obj.data, 'frustum_culling')
            layout.prop_search(obj.data, "renderpath_path", bpy.data, "node_groups")
            layout.operator("arm.reimport_paths_menu")
        elif obj.type == 'MESH' or obj.type == 'FONT':
            layout.prop(obj.data, 'static_usage')
            layout.operator("arm.invalidate_cache")
        elif obj.type == 'LAMP':
            layout.prop(obj.data, 'lamp_clip_start')
            layout.prop(obj.data, 'lamp_clip_end')
            layout.prop(obj.data, 'lamp_fov')
            layout.prop(obj.data, 'lamp_shadows_bias')
        elif obj.type == 'ARMATURE':
            layout.prop(obj.data, 'edit_actions')
            if obj.data.edit_actions:
                # Actions list
                layout.label("Actions")
                animrow = layout.row()
                animrows = 2
                if len(obj.data.my_actiontraitlist) > 1:
                    animrows = 4
                
                row = layout.row()
                row.template_list("MY_UL_ActionTraitList", "The_List", obj.data, "my_actiontraitlist", obj.data, "actiontraitlist_index", rows=animrows)

                col = row.column(align=True)
                col.operator("my_actiontraitlist.new_item", icon='ZOOMIN', text="")
                col.operator("my_actiontraitlist.delete_item", icon='ZOOMOUT', text="")

                if len(obj.data.my_actiontraitlist) > 1:
                    col.separator()
                    col.operator("my_actiontraitlist.move_item", icon='TRIA_UP', text="").direction = 'UP'
                    col.operator("my_actiontraitlist.move_item", icon='TRIA_DOWN', text="").direction = 'DOWN'

                if obj.data.actiontraitlist_index >= 0 and len(obj.data.my_actiontraitlist) > 0:
                    item = obj.data.my_actiontraitlist[obj.data.actiontraitlist_index]
                    item.name = item.action_name_prop
                    row = layout.row()
                    row.prop_search(item, "action_name_prop", bpy.data, "actions", "Action")

class ScenePropsPanel(bpy.types.Panel):
    bl_label = "Armory Props"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
 
    def draw(self, context):
        layout = self.layout
        scn = bpy.context.scene
        if scn == None:
            return
        layout.prop(scn, 'game_export')

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
        context.object.data.mesh_cached = False
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
        if mat == None:
            return

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
        # wrd = bpy.context.world
        wrd = bpy.data.worlds['Arm']
        layout.prop(wrd, 'generate_shadows')
        if wrd.generate_shadows:
            layout.prop(wrd, 'generate_pcss')
            if wrd.generate_pcss:
                layout.prop(wrd, 'generate_pcss_rings')
        layout.prop(wrd, 'generate_radiance')
        if wrd.generate_radiance:
            layout.prop(wrd, 'generate_radiance_sky')
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
        layout.prop(wrd, 'generate_bloom_treshold')
        layout.prop(wrd, 'generate_bloom_strength')
        
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

        layout.label('Flags')
        layout.prop(wrd, 'force_no_culling')
        layout.prop(wrd, 'force_anisotropic_filtering')
        layout.prop(wrd, 'diffuse_oren_nayar')

# Menu in render region
class ArmoryPlayPanel(bpy.types.Panel):
    bl_label = "Armory Play"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
 
    def draw(self, context):
        layout = self.layout
        wrd = bpy.data.worlds['Arm']
        if make.play_project.playproc == None and make.play_project.compileproc == None:
            layout.operator("arm.play", icon="PLAY")
        else:
            layout.operator("arm.stop", icon="MESH_PLANE")
        layout.prop(wrd, 'ArmPlayRuntime')
        layout.prop(wrd, 'ArmPlayViewportCamera')
        if wrd.ArmPlayViewportCamera:
            layout.prop(wrd, 'ArmPlayViewportNavigation')

        layout.prop(wrd, 'ArmPlayConsole')
        layout.prop(wrd, 'ArmPlayDeveloperTools')
        layout.prop(wrd, 'ArmPlayLivePatch')
        if wrd.ArmPlayLivePatch:
            layout.prop(wrd, 'ArmPlayAutoBuild')

class ArmoryBuildPanel(bpy.types.Panel):
    bl_label = "Armory Build"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
 
    def draw(self, context):
        layout = self.layout
        wrd = bpy.data.worlds['Arm']
        if make.play_project.playproc == None and make.play_project.compileproc == None and make.play_project.chromium_running == False:
            layout.operator("arm.build")
        else:
            layout.operator("arm.patch")
        layout.operator("arm.kode_studio")
        layout.operator("arm.clean")
        layout.prop(wrd, 'ArmProjectTarget')
        layout.prop(wrd, 'ArmCacheShaders')
        layout.prop(wrd, 'ArmMinimize')
        layout.prop(wrd, 'ArmOptimizeMesh')
        layout.prop(wrd, 'ArmSampledAnimation')
        layout.prop(wrd, 'ArmDeinterleavedBuffers')
        layout.prop(wrd, 'generate_gpu_skin')
        if wrd.generate_gpu_skin:
            layout.prop(wrd, 'generate_gpu_skin_max_bones')
        layout.prop(wrd, 'ArmProjectSamplesPerPixel')
        layout.label('Libraries')
        layout.prop(wrd, 'ArmPhysics')
        layout.prop(wrd, 'ArmNavigation')

class ArmoryProjectPanel(bpy.types.Panel):
    bl_label = "Armory Project"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    bl_options = {'DEFAULT_CLOSED'}
    info_text = 'Ready'
 
    def draw(self, context):
        layout = self.layout
        wrd = bpy.data.worlds['Arm']
        layout.prop(wrd, 'ArmProjectName')
        layout.prop(wrd, 'ArmProjectPackage')
        layout.prop_search(wrd, 'ArmKhafile', bpy.data, 'texts', 'Khafile')
        layout.prop(wrd, 'ArmPlayActiveScene')
        if wrd.ArmPlayActiveScene == False:
            layout.prop_search(wrd, 'ArmProjectScene', bpy.data, 'scenes', 'Scene')
        layout.prop(wrd, 'ArmExportHideRender')
        layout.prop(wrd, 'ArmSpawnAllLayers')
        layout.label('Publish Project')
        layout.operator('arm.publish')
        layout.prop(wrd, 'ArmPublishTarget')
        layout.label('Armory')
        layout.operator('arm.check_updates')
        layout.label('v' + wrd.ArmVersion)

class ArmoryPlayButton(bpy.types.Operator):
    bl_idname = 'arm.play'
    bl_label = 'Play'
 
    def execute(self, context):
        invalidate_shader_cache.enabled = False
        make.play_project(self, False)
        invalidate_shader_cache.enabled = True
        return{'FINISHED'}

class ArmoryPlayInViewportButton(bpy.types.Operator):
    bl_idname = 'arm.play_in_viewport'
    bl_label = 'Play in Viewport'
 
    def execute(self, context):
        invalidate_shader_cache.enabled = False
        if make.play_project.playproc == None:
            # Cancel viewport render
            for space in context.area.spaces:
                if space.type == 'VIEW_3D':
                    if space.viewport_shade == 'RENDERED':
                        space.viewport_shade = 'SOLID'
                    break
            make.play_project(self, True)
        else:
            make.patch_project()
            make.compile_project()
        invalidate_shader_cache.enabled = True
        return{'FINISHED'}

class ArmoryStopButton(bpy.types.Operator):
    bl_idname = 'arm.stop'
    bl_label = 'Stop'
 
    def execute(self, context):
        make.stop_project()
        return{'FINISHED'}

class ArmoryBuildButton(bpy.types.Operator):
    bl_idname = 'arm.build'
    bl_label = 'Build'
 
    def execute(self, context):
        invalidate_shader_cache.enabled = False
        make.build_project()
        make.compile_project()
        invalidate_shader_cache.enabled = True
        return{'FINISHED'}

class ArmoryPatchButton(bpy.types.Operator):
    bl_idname = 'arm.patch'
    bl_label = 'Live Patch'
 
    def execute(self, context):
        invalidate_shader_cache.enabled = False
        make.patch_project()
        make.compile_project()
        invalidate_shader_cache.enabled = True
        return{'FINISHED'}

class ArmoryFolderButton(bpy.types.Operator):
    bl_idname = 'arm.folder'
    bl_label = 'Project Folder'
 
    def execute(self, context):
        webbrowser.open('file://' + utils.get_fp())
        return{'FINISHED'}

class ArmoryCheckUpdatesButton(bpy.types.Operator):
    bl_idname = 'arm.check_updates'
    bl_label = 'Check for Updates'
 
    def execute(self, context):
        webbrowser.open("http://armory3d.org/manual")
        return{'FINISHED'}

class ArmoryKodeStudioButton(bpy.types.Operator):
    bl_idname = 'arm.kode_studio'
    bl_label = 'Kode Studio'
    bl_description = 'Open Project in Kode Studio'
 
    def execute(self, context):
        user_preferences = bpy.context.user_preferences
        addon_prefs = user_preferences.addons['armory'].preferences
        sdk_path = addon_prefs.sdk_path
        project_path = utils.get_fp()

        if utils.get_os() == 'win':
            kode_path = sdk_path + '/kode_studio/KodeStudio-win32/Kode Studio.exe'
        elif utils.get_os() == 'mac':
            kode_path = '"' + sdk_path + '/kode_studio/Kode Studio.app/Contents/MacOS/Electron"'
        else:
            kode_path = sdk_path + '/kode_studio/KodeStudio-linux64/kodestudio'

        subprocess.Popen([kode_path + ' ' + utils.get_fp()], shell=True)

        return{'FINISHED'}

class ArmoryCleanButton(bpy.types.Operator):
    bl_idname = 'arm.clean'
    bl_label = 'Clean'
 
    def execute(self, context):
        make.clean_project()
        return{'FINISHED'}

class ArmoryPublishButton(bpy.types.Operator):
    bl_idname = 'arm.publish'
    bl_label = 'Publish'
 
    def execute(self, context):
        make.publish_project()
        self.report({'INFO'}, 'Publishing project, check console for details.')
        return{'FINISHED'}

# Play button in 3D View panel
def draw_play_item(self, context):
    layout = self.layout
    if make.play_project.playproc == None and make.play_project.compileproc == None:
        layout.operator("arm.play_in_viewport", icon="PLAY")
    else:
        layout.operator("arm.stop", icon="MESH_PLANE")

# Info panel in header
def draw_info_item(self, context):
    layout = self.layout
    layout.label(ArmoryProjectPanel.info_text)

# Registration
arm_keymaps = []
def register():
    bpy.utils.register_module(__name__)
    initProperties()
    bpy.app.handlers.scene_update_post.append(on_scene_update_post)
    bpy.app.handlers.load_pre.append(on_load_pre)
    bpy.types.VIEW3D_HT_header.append(draw_play_item)
    bpy.types.INFO_HT_header.prepend(draw_info_item)

    # Key shortcuts
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Window', space_type='EMPTY', region_type="WINDOW")
    km.keymap_items.new(ArmoryPlayButton.bl_idname, type='F5', value='PRESS')
    km.keymap_items.new(ArmoryPlayInViewportButton.bl_idname, type='P', value='PRESS')
    arm_keymaps.append(km)

def unregister():
    bpy.types.VIEW3D_HT_header.remove(draw_play_item)
    bpy.types.INFO_HT_header.remove(draw_info_item)
    bpy.app.handlers.scene_update_post.remove(on_scene_update_post)
    bpy.app.handlers.load_pre.remove(on_load_pre)
    bpy.utils.unregister_module(__name__)
    
    # Key shortcuts
    wm = bpy.context.window_manager
    for km in arm_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    del arm_keymaps[:]
