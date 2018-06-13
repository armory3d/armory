import bpy
from bpy.props import *
import os
import shutil
import arm.props_ui as props_ui
import arm.assets as assets
import arm.log as log
import arm.utils
import arm.make
import arm.props_renderpath as props_renderpath
import arm.proxy

# Armory version
arm_version = '0.5'
arm_commit = '$Id$'

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

def invalidate_compiler_cache(self, context):
    bpy.data.worlds['Arm'].arm_recompile = True

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
    bpy.types.World.arm_recompile = BoolProperty(name="Recompile", description="Recompile sources on next play", default=True)
    bpy.types.World.arm_version = StringProperty(name="Version", description="Armory SDK version", default="")
    bpy.types.World.arm_commit = StringProperty(name="Version Commit", description="Armory SDK version", default="")
    bpy.types.World.arm_project_name = StringProperty(name="Name", description="Exported project name", default="", update=invalidate_compiler_cache)
    bpy.types.World.arm_project_package = StringProperty(name="Package", description="Package name for scripts", default="arm", update=invalidate_compiler_cache)
    bpy.types.World.arm_project_version = StringProperty(name="Version", description="Exported project version", default="1.0", update=invalidate_compiler_cache)
    bpy.types.World.arm_project_bundle = StringProperty(name="Bundle", description="Exported project bundle", default="", update=invalidate_compiler_cache)
    bpy.types.World.arm_project_icon = StringProperty(name="Icon", description="Exported project icon", default="", subtype="FILE_PATH", update=invalidate_compiler_cache)
    bpy.types.World.arm_project_root = StringProperty(name="Root", description="Set root folder for linked assets", default="", subtype="FILE_PATH", update=invalidate_compiler_cache)
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
    bpy.types.World.arm_formatlib = EnumProperty(
        items = [('Disabled', 'Disabled', 'Disabled'), 
                 ('Enabled', 'Enabled', 'Enabled')],
        name = "Format", default='Disabled', description="Include Format library")
    bpy.types.World.arm_audio = EnumProperty(
        items = [('Disabled', 'Disabled', 'Disabled'), 
                 ('Enabled', 'Enabled', 'Enabled')],
        name = "Audio", default='Enabled')
    bpy.types.World.arm_khafile = StringProperty(name="Khafile", description="Source appended to khafile.js", update=invalidate_compiler_cache)
    bpy.types.World.arm_khamake = StringProperty(name="Khamake", description="Command line params appended to khamake", update=invalidate_compiler_cache)
    bpy.types.World.arm_texture_quality = FloatProperty(name="Texture Quality", default=1.0, min=0.0, max=1.0, subtype='FACTOR', update=invalidate_compiler_cache)
    bpy.types.World.arm_sound_quality = FloatProperty(name="Sound Quality", default=0.9, min=0.0, max=1.0, subtype='FACTOR', update=invalidate_compiler_cache)
    bpy.types.World.arm_minimize = BoolProperty(name="Minimize Data", description="Export scene data in binary", default=True, update=assets.invalidate_compiled_data)
    bpy.types.World.arm_minify_js = BoolProperty(name="Minify JS", description="Minimize JavaScript output when publishing", default=True)
    bpy.types.World.arm_optimize_mesh = BoolProperty(name="Optimize Meshes", description="Export more efficient geometry indices, can prolong build times", default=False, update=assets.invalidate_mesh_data)
    bpy.types.World.arm_sampled_animation = BoolProperty(name="Sampled Animation", description="Export object animation as raw matrices", default=False, update=assets.invalidate_compiled_data)
    bpy.types.World.arm_deinterleaved_buffers = BoolProperty(name="Deinterleaved Buffers", description="Use deinterleaved vertex buffers", default=False, update=invalidate_compiler_cache)
    bpy.types.World.arm_export_tangents = BoolProperty(name="Export Tangents", description="Precompute tangents for normal mapping, otherwise computed in shader", default=True, update=assets.invalidate_compiled_data)
    bpy.types.World.arm_batch_meshes = BoolProperty(name="Batch Meshes", description="Group meshes by materials to speed up rendering", default=False, update=invalidate_compiler_cache)
    bpy.types.World.arm_batch_materials = BoolProperty(name="Batch Materials", description="Marge similar materials into single pipeline state", default=False, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_stream_scene = BoolProperty(name="Stream Scene", description="Stream scene content", default=False, update=invalidate_compiler_cache)
    bpy.types.World.arm_lod_gen_levels = IntProperty(name="Levels", description="Number of levels to generate", default=3, min=1)
    bpy.types.World.arm_lod_gen_ratio = FloatProperty(name="Decimate Ratio", description="Decimate ratio", default=0.8)
    bpy.types.World.arm_cache_shaders = BoolProperty(name="Cache Shaders", description="Do not rebuild existing shaders", default=True)
    bpy.types.World.arm_cache_compiler = BoolProperty(name="Cache Compiler", description="Only recompile sources when required", default=True)
    bpy.types.World.arm_gpu_processing = BoolProperty(name="GPU Processing", description="Utilize GPU for asset pre-processing at build time", default=True, update=assets.invalidate_compiled_data)
    bpy.types.World.arm_play_camera = EnumProperty(
        items=[('Scene', 'Scene', 'Scene'),
               ('Viewport', 'Viewport', 'Viewport'),
               # ('Viewport Shared', 'Shared', 'Viewport Shared')
               ],
        name="Camera", description="Viewport camera", default='Scene')
    bpy.types.World.arm_play_console = BoolProperty(name="Debug Console", description="Show inspector in player and enable debug draw", default=False, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_play_runtime = EnumProperty(
        items=[('Browser', 'Browser', 'Browser'),
               ('Native', 'C++', 'Native'),
               ('Krom', 'Krom', 'Krom')],
        name="Runtime", description="Player runtime used when launching in new window", default='Krom', update=assets.invalidate_shader_cache)
    bpy.types.World.arm_loadscreen = BoolProperty(name="Loading Screen", description="Show asset loading progress on published builds", default=True)
    bpy.types.World.arm_vsync = BoolProperty(name="VSync", description="Vertical Synchronization", default=True, update=invalidate_compiler_cache)
    bpy.types.World.arm_dce = BoolProperty(name="DCE", description="Enable dead code elimination for publish builds", default=True, update=invalidate_compiler_cache)
    bpy.types.World.arm_asset_compression = BoolProperty(name="Asset Compression", description="Enable scene data compression", default=False, update=invalidate_compiler_cache)
    bpy.types.World.arm_write_config = BoolProperty(name="Write Config", description="Allow this project to be configured at runtime via a JSON file", default=False, update=invalidate_compiler_cache)
    bpy.types.World.arm_winmode = EnumProperty(
        items = [('Window', 'Window', 'Window'),
                 ('BorderlessWindow', 'Borderless', 'BorderlessWindow'),
                 ('Fullscreen', 'Fullscreen', 'Fullscreen')],
        name="Mode", default='Window', description='Window mode to start in', update=invalidate_compiler_cache)
    bpy.types.World.arm_winorient = EnumProperty(
        items = [('Multi', 'Multi', 'Multi'),
                 ('Portrait', 'Portrait', 'Portrait'),
                 ('Landscape', 'Landscape', 'Landscape')],
        name="Orientation", default='Landscape', description='Set screen orientation on mobile devices')
    bpy.types.World.arm_winresize = BoolProperty(name="Resizable", description="Allow window resize", default=False, update=invalidate_compiler_cache)
    bpy.types.World.arm_winmaximize = BoolProperty(name="Maximizable", description="Allow window maximize", default=False, update=invalidate_compiler_cache)
    bpy.types.World.arm_winminimize = BoolProperty(name="Minimizable", description="Allow window minimize", default=True, update=invalidate_compiler_cache)
    # For object
    bpy.types.Object.arm_instanced = BoolProperty(name="Instanced Children", description="Use instaced rendering", default=False, update=invalidate_instance_cache)
    bpy.types.Object.arm_instanced_loc_x = BoolProperty(name="X", default=True)
    bpy.types.Object.arm_instanced_loc_y = BoolProperty(name="Y", default=True)
    bpy.types.Object.arm_instanced_loc_z = BoolProperty(name="Z", default=True)
    # bpy.types.Object.arm_instanced_rot_x = BoolProperty(name="X", default=False)
    # bpy.types.Object.arm_instanced_rot_y = BoolProperty(name="Y", default=False)
    # bpy.types.Object.arm_instanced_rot_z = BoolProperty(name="Z", default=False)
    # bpy.types.Object.arm_instanced_scale_x = BoolProperty(name="X", default=False)
    # bpy.types.Object.arm_instanced_scale_y = BoolProperty(name="Y", default=False)
    # bpy.types.Object.arm_instanced_scale_z = BoolProperty(name="Z", default=False)
    bpy.types.Object.arm_export = BoolProperty(name="Export", description="Export object data", default=True)
    bpy.types.Object.arm_spawn = BoolProperty(name="Spawn", description="Auto-add this object when creating scene", default=True)
    bpy.types.Object.arm_mobile = BoolProperty(name="Mobile", description="Object moves during gameplay", default=False)
    bpy.types.Object.arm_visible = BoolProperty(name="Visible", description="Render this object", default=True)
    bpy.types.Object.arm_soft_body_margin = FloatProperty(name="Soft Body Margin", description="Collision margin", default=0.04)
    bpy.types.Object.arm_rb_linear_factor = FloatVectorProperty(name="Linear Factor", size=3, description="Set to 0 to lock axis", default=[1,1,1])
    bpy.types.Object.arm_rb_angular_factor = FloatVectorProperty(name="Angular Factor", size=3, description="Set to 0 to lock axis", default=[1,1,1])
    bpy.types.Object.arm_rb_trigger = BoolProperty(name="Trigger", description="Disable contact response", default=False)
    bpy.types.Object.arm_rb_terrain = BoolProperty(name="Terrain", description="Set rigid body collision shape to terrain", default=False)
    bpy.types.Object.arm_rb_force_deactivation = BoolProperty(name="Force Deactivation", description="Force deactivation on all rigid bodies for performance", default=True)
    bpy.types.Object.arm_rb_deactivation_time = FloatProperty(name="Deactivation Time", description="Delay putting rigid body into sleep", default=0.0)
    bpy.types.Object.arm_animation_enabled = BoolProperty(name="Animation", description="Enable skinning & timeline animation", default=True)
    bpy.types.Object.arm_tilesheet = StringProperty(name="Tilesheet", description="Set tilesheet animation", default='')
    bpy.types.Object.arm_tilesheet_action = StringProperty(name="Tilesheet Action", description="Set startup action", default='')
    bpy.types.Object.arm_proxy_sync_loc = BoolProperty(name="Location", description="Keep location synchronized with proxy object", default=True, update=proxy_sync_loc)
    bpy.types.Object.arm_proxy_sync_rot = BoolProperty(name="Rotation", description="Keep rotation synchronized with proxy object", default=True, update=proxy_sync_rot)
    bpy.types.Object.arm_proxy_sync_scale = BoolProperty(name="Scale", description="Keep scale synchronized with proxy object", default=True, update=proxy_sync_scale)
    bpy.types.Object.arm_proxy_sync_materials = BoolProperty(name="Materials", description="Keep materials synchronized with proxy object", default=True, update=proxy_sync_materials)
    bpy.types.Object.arm_proxy_sync_modifiers = BoolProperty(name="Modifiers", description="Keep modifiers synchronized with proxy object", default=True, update=proxy_sync_modifiers)
    bpy.types.Object.arm_proxy_sync_traits = BoolProperty(name="Traits", description="Keep traits synchronized with proxy object", default=True, update=proxy_sync_traits)
    bpy.types.Object.arm_cached = BoolProperty(name="Object Cached", description="No need to reexport object data", default=True)
    # For speakers
    bpy.types.Speaker.arm_play_on_start = BoolProperty(name="Play on Start", description="Play this sound automatically", default=False)
    bpy.types.Speaker.arm_loop = BoolProperty(name="Loop", description="Loop this sound", default=False)
    bpy.types.Speaker.arm_stream = BoolProperty(name="Stream", description="Stream this sound", default=False)
    # For mesh
    bpy.types.Mesh.arm_cached = BoolProperty(name="Mesh Cached", description="No need to reexport mesh data", default=False)
    bpy.types.Mesh.arm_aabb = FloatVectorProperty(name="AABB", size=3, default=[0,0,0])
    bpy.types.Mesh.arm_dynamic_usage = BoolProperty(name="Dynamic Usage", description="Mesh data can change at runtime", default=False)
    bpy.types.Mesh.arm_compress = BoolProperty(name="Compress", description="Pack data into zip file", default=False)
    # bpy.types.Mesh.arm_sdfgen = BoolProperty(name="Generate SDF", description="Make signed distance field data", default=False, update=invalidate_mesh_cache)
    bpy.types.Curve.arm_cached = BoolProperty(name="Mesh Cached", description="No need to reexport curve data", default=False)
    bpy.types.Curve.arm_compress = BoolProperty(name="Compress", description="Pack data into zip file", default=False)
    bpy.types.Curve.arm_dynamic_usage = BoolProperty(name="Dynamic Data Usage", description="Curve data can change at runtime", default=False)
    bpy.types.MetaBall.arm_cached = BoolProperty(name="Mesh Cached", description="No need to reexport metaball data", default=False)
    bpy.types.MetaBall.arm_compress = BoolProperty(name="Compress", description="Pack data into zip file", default=False)
    bpy.types.MetaBall.arm_dynamic_usage = BoolProperty(name="Dynamic Data Usage", description="Metaball data can change at runtime", default=False)
    # For grease pencil
    # bpy.types.GreasePencil.arm_cached = BoolProperty(name="GP Cached", description="No need to reexport grease pencil data", default=False)
    # bpy.types.GreasePencil.arm_compress = BoolProperty(name="Compress", description="Pack data into zip file", default=True)
    # For armature
    bpy.types.Armature.arm_cached = BoolProperty(name="Armature Cached", description="No need to reexport armature data", default=False)
    bpy.types.Armature.arm_compress = BoolProperty(name="Compress", description="Pack data into zip file", default=False)
    # For camera
    bpy.types.Camera.arm_frustum_culling = BoolProperty(name="Frustum Culling", description="Perform frustum culling for this camera", default=True)
    bpy.types.Camera.arm_render_to_texture = BoolProperty(name="Render to Texture", description="Render this camera into texture", default=False)
    bpy.types.Camera.arm_texture_resolution_x = FloatProperty(name="X", default=512.0)
    bpy.types.Camera.arm_texture_resolution_y = FloatProperty(name="Y", default=256.0)

    # Render path generator
    bpy.types.World.rp_search = StringProperty(name="Search", default='')
    bpy.types.World.rp_preset = EnumProperty(
        items=[('Low', 'Low', 'Low'),
               ('VR', 'VR', 'VR'),
               ('Mobile', 'Mobile', 'Mobile'),
               ('Forward', 'Forward', 'Forward'),
               ('Deferred', 'Deferred', 'Deferred'),
               ('Max (Game)', 'Max (Game)', 'Max (Game)'),
               ('Max (Render)', 'Max (Render)', 'Max (Render)'),
               ('Lightmap', 'Lightmap', 'Lightmap'),
               ],
        name="Preset", description="Render path preset", default='Deferred', update=props_renderpath.update_preset)
    bpy.types.World.arm_envtex_name = StringProperty(name="Environment Texture", default='')
    bpy.types.World.arm_envtex_irr_name = StringProperty(name="Environment Irradiance", default='')
    bpy.types.World.arm_envtex_num_mips = IntProperty(name="Number of mips", default=0)
    bpy.types.World.arm_envtex_color = FloatVectorProperty(name="Environment Color", size=4, default=[0,0,0,1])
    bpy.types.World.arm_envtex_strength = FloatProperty(name="Environment Strength", default=1.0)
    bpy.types.World.arm_envtex_sun_direction = FloatVectorProperty(name="Sun Direction", size=3, default=[0,0,0])
    bpy.types.World.arm_envtex_turbidity = FloatProperty(name="Turbidity", default=1.0)
    bpy.types.World.arm_envtex_ground_albedo = FloatProperty(name="Ground Albedo", default=0.0)
    bpy.types.Material.arm_cast_shadow = BoolProperty(name="Cast Shadow", default=True)
    bpy.types.Material.arm_receive_shadow = BoolProperty(name="Receive Shadow", default=True)
    bpy.types.Material.arm_overlay = BoolProperty(name="Overlay", default=False)
    bpy.types.Material.arm_decal = BoolProperty(name="Decal", default=False)
    bpy.types.Material.arm_two_sided = BoolProperty(name="Two-Sided", description="Flip normal when drawing back-face", default=False)
    bpy.types.Material.arm_cull_mode = EnumProperty(
        items=[('none', 'Both', 'None'),
               ('clockwise', 'Front', 'Clockwise'),
               ('counter_clockwise', 'Back', 'Counter-Clockwise')],
        name="", default='clockwise', description="Draw geometry faces")
    bpy.types.Material.arm_discard = BoolProperty(name="Discard", default=False, description="Do not render fragments below specified opacity threshold")
    bpy.types.Material.arm_discard_opacity = FloatProperty(name="Mesh Opacity", default=0.2, min=0, max=1)
    bpy.types.Material.arm_discard_opacity_shadows = FloatProperty(name="Shadows Opacity", default=0.1, min=0, max=1)
    bpy.types.Material.arm_custom_material = StringProperty(name="Custom Material", description="Write custom material", default='')
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
    bpy.types.Material.arm_particle_fade = BoolProperty(name="Particle Fade", description="Fade particles in and out", default=False)
    bpy.types.Material.arm_tilesheet_mat = BoolProperty(name="Tilesheet", description="Generate tilesheet shaders", default=False)
    bpy.types.Material.arm_blending = BoolProperty(name="Blending", description="Enable additive blending", default=False)
    # For scene
    bpy.types.Scene.arm_export = BoolProperty(name="Export", description="Export scene data", default=True)
    # bpy.types.Scene.arm_gp_export = BoolProperty(name="Export GP", description="Export grease pencil data", default=True)
    bpy.types.Scene.arm_compress = BoolProperty(name="Compress", description="Pack data into zip file", default=False)
    # For lamp
    bpy.types.Lamp.arm_clip_start = FloatProperty(name="Clip Start", default=0.1)
    bpy.types.Lamp.arm_clip_end = FloatProperty(name="Clip End", default=50.0)
    bpy.types.Lamp.arm_fov = FloatProperty(name="Field of View", default=0.84)
    bpy.types.Lamp.arm_shadows_bias = FloatProperty(name="Bias", description="Depth offset to fight shadow acne", default=1.0)
    bpy.types.World.arm_lamp_texture = StringProperty(name="Mask Texture", default="")
    bpy.types.World.arm_lamp_ies_texture = StringProperty(name="IES Texture", default="")
    bpy.types.World.arm_lamp_clouds_texture = StringProperty(name="Clouds Texture", default="")

    bpy.types.World.arm_rpcache_list = CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.World.arm_scripts_list = CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.World.arm_bundled_scripts_list = CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.World.arm_canvas_list = CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.World.arm_wasm_list = CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.World.world_defs = StringProperty(name="World Shader Defs", default='')
    bpy.types.World.compo_defs = StringProperty(name="Compositor Shader Defs", default='')
    bpy.types.Material.export_uvs = BoolProperty(name="Export UVs", default=False)
    bpy.types.Material.export_vcols = BoolProperty(name="Export VCols", default=False)
    bpy.types.Material.export_tangents = BoolProperty(name="Export Tangents", default=False)
    bpy.types.Material.arm_skip_context = StringProperty(name="Skip Context", default='')
    bpy.types.Material.arm_material_id = IntProperty(name="ID", default=0)
    bpy.types.NodeSocket.is_uniform = BoolProperty(name="Is Uniform", description="Mark node sockets to be processed as material uniforms", default=False)
    bpy.types.NodeTree.is_cached = BoolProperty(name="Node Tree Cached", description="No need to reexport node tree", default=False)
    bpy.types.Material.signature = StringProperty(name="Signature", description="Unique string generated from material nodes", default="")
    bpy.types.Material.is_cached = BoolProperty(name="Material Cached", description="No need to reexport material data", default=False, update=update_mat_cache)
    bpy.types.Material.lock_cache = BoolProperty(name="Lock Material Cache", description="Prevent is_cached from updating", default=False)
    bpy.types.ShaderNodeRGB.arm_material_param = BoolProperty(name="Parameter", description="Control this node from script", default=False)
    bpy.types.ShaderNodeValue.arm_material_param = BoolProperty(name="Parameter", description="Control this node from script", default=False)
    bpy.types.ShaderNodeTexImage.arm_material_param = BoolProperty(name="Parameter", description="Control this node from script", default=False)
    # Particles
    bpy.types.ParticleSettings.arm_gpu_sim = BoolProperty(name="GPU Simulation", description="Calculate particle simulation on GPU", default=False, update=assets.invalidate_shader_cache)
    bpy.types.ParticleSettings.arm_count_mult = FloatProperty(name="Multiply Count", description="Multiply particle count when rendering in Armory", default=1.0)
    bpy.types.ParticleSettings.arm_loop = BoolProperty(name="Loop", description="Loop this particle system", default=False)

    create_wrd()

def create_wrd():
    if not 'Arm' in bpy.data.worlds:
        wrd = bpy.data.worlds.new('Arm')
        wrd.use_fake_user = True # Store data world object, add fake user to keep it alive
        wrd.arm_version = arm_version
        wrd.arm_commit = arm_commit

def init_properties_on_save():
    wrd = bpy.data.worlds['Arm']
    if wrd.arm_project_name == '':
        # Take blend file name
        wrd.arm_project_name = arm.utils.blend_name()
        init_properties_on_load()

def init_properties_on_load():
    global arm_version    
    if not 'Arm' in bpy.data.worlds:
        init_properties()
    arm.utils.fetch_script_names()
    wrd = bpy.data.worlds['Arm']
    # Outdated project
    if bpy.data.filepath != '' and (wrd.arm_version != arm_version or wrd.arm_commit != arm_commit): # Call on project load only
        print('Project updated to sdk v' + arm_version)
        wrd.arm_version = arm_version
        wrd.arm_commit = arm_commit
        arm.make.clean()

def register():
    init_properties()
    arm.utils.fetch_bundled_script_names()

def unregister():
    pass
