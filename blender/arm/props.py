import bpy
from bpy.props import *
import re
import multiprocessing

import arm.assets as assets
import arm.logicnode.replacement
import arm.logicnode.tree_variables
import arm.make
import arm.nodes_logic
import arm.utils
import arm.utils_vs

if arm.is_reload(__name__):
    assets = arm.reload_module(assets)
    arm.logicnode.replacement = arm.reload_module(arm.logicnode.replacement)
    arm.logicnode.tree_variables = arm.reload_module(arm.logicnode.tree_variables)
    arm.make = arm.reload_module(arm.make)
    arm.nodes_logic = arm.reload_module(arm.nodes_logic)
    arm.utils = arm.reload_module(arm.utils)
    arm.utils_vs = arm.reload_module(arm.utils_vs)
else:
    arm.enable_reload(__name__)

# Armory version
arm_version = '2023.3'
arm_commit = '$Id$'

def get_project_html5_copy(self):
    return self.get('arm_project_html5_copy', False)

def set_project_html5_copy(self, value):
    self['arm_project_html5_copy'] = value
    if not value:
        self['arm_project_html5_start_browser'] = False

def get_project_html5_start_browser(self):
    return self.get('arm_project_html5_start_browser', False)

def set_project_html5_start_browser(self, value):
    self['arm_project_html5_start_browser'] = value

def set_project_name(self, value):
    value = arm.utils.safestr(value)
    if len(value) > 0:
        self['arm_project_name'] = value
    else:
        self['arm_project_name'] = arm.utils.blend_name()

def get_project_name(self):
    return self.get('arm_project_name', arm.utils.blend_name())

def set_project_package(self, value):
    value = arm.utils.safestr(value).replace('.', '_')
    if (len(value) > 0) and (not value.isdigit()) and (not value[0].isdigit()):
        self['arm_project_package'] = value

def get_project_package(self):
    return self.get('arm_project_package', 'arm')

def set_version(self, value):
    value = value.strip().replace(' ', '')
    if re.match(r'^\d+(\.\d+){1,3}$', value) is not None:
        check = True
        v_i = value.split('.')
        for item in v_i:
            try:
                i = int(item)
            except ValueError:
                check = False
                break
        if check:
            self['arm_project_version'] = value

def get_version(self):
    return self.get('arm_project_version', '1.0.0')

def set_project_bundle(self, value):
    value = arm.utils.safestr(value)
    v_a = value.strip().split('.')
    if (len(value) > 0) and (not value.isdigit()) and (not value[0].isdigit()) and (len(v_a) > 1):
        check = True
        for item in v_a:
            if (item.isdigit()) or (item[0].isdigit()):
                check = False
                break
        if check:
            self['arm_project_bundle'] = value

def get_project_bundle(self):
    return self.get('arm_project_bundle', 'org.armory3d')

def get_android_build_apk(self):
    if len(arm.utils.get_android_sdk_root_path()) > 0:
        return self.get('arm_project_android_build_apk', False)
    else:
        set_android_build_apk(self, False)
        return False

def set_android_build_apk(self, value):
    self['arm_project_android_build_apk'] = value
    if not value:
        wrd = bpy.data.worlds['Arm']
        wrd.arm_project_android_rename_apk = False
        wrd.arm_project_android_copy_apk = False
        wrd.arm_project_android_run_avd = False

def get_win_build_arch(self):
    if self.get('arm_project_win_build_arch', -1) == -1:
        if arm.utils.get_os_is_windows_64():
            return 0
        else:
            return 1
    else:
        return self.get('arm_project_win_build_arch', 'x64')

def set_win_build_arch(self, value):
    self['arm_project_win_build_arch'] = value

def set_win_build(self, value):
    if arm.utils.get_os_is_windows():
        self['arm_project_win_build'] = value
    else:
        self['arm_project_win_build'] = 0
    if (self['arm_project_win_build'] == 0) or (self['arm_project_win_build'] == 1):
        wrd = bpy.data.worlds['Arm']
        wrd.arm_project_win_build_open = False

def get_win_build(self):
    if arm.utils.get_os_is_windows():
        return self.get('arm_project_win_build', 0)
    else:
        return 0

def init_properties():
    global arm_version
    bpy.types.World.arm_recompile = BoolProperty(name="Recompile", description="Recompile sources on next play", default=True)
    bpy.types.World.arm_version = StringProperty(name="Version", description="Armory SDK version", default="")
    bpy.types.World.arm_commit = StringProperty(name="Version Commit", description="Armory SDK version", default="")
    bpy.types.World.arm_project_name = StringProperty(name="Name", description="Exported project name", default="", update=assets.invalidate_compiler_cache, set=set_project_name, get=get_project_name)
    bpy.types.World.arm_project_package = StringProperty(name="Package", description="Package name for scripts", default="arm", update=assets.invalidate_compiler_cache, set=set_project_package, get=get_project_package)
    bpy.types.World.arm_project_version = StringProperty(name="Version", description="Exported project version", default="1.0.0", update=assets.invalidate_compiler_cache, set=set_version, get=get_version)
    bpy.types.World.arm_project_version_autoinc = BoolProperty(name="Auto-increment Build Number", description="Auto-increment build number", default=True, update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_project_bundle = StringProperty(name="Bundle", description="Exported project bundle", default="org.armory3d", update=assets.invalidate_compiler_cache, set=set_project_bundle, get=get_project_bundle)
    # Android Settings
    bpy.types.World.arm_project_android_sdk_min = IntProperty(name="Minimal Version SDK", description="Minimal Version Android SDK", default=23, min=14, max=30, update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_project_android_sdk_target = IntProperty(name="Target Version SDK", description="Target Version Android SDK", default=26, min=26, max=30, update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_project_android_sdk_compile = IntProperty(name="Maximal Version SDK", description="Maximal Android SDK Version", default=30, min=26, max=30, update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_project_android_build_apk = BoolProperty(name="Building APK After Publishing", description="Starting APK build after publishing", default=False, update=assets.invalidate_compiler_cache, get=get_android_build_apk, set=set_android_build_apk)
    bpy.types.World.arm_project_android_rename_apk = BoolProperty(name="Rename APK To Project Name", description="Rename APK file to project name + version after build", default=False, update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_project_android_copy_apk = BoolProperty(name="Copy APK To Specified Folder", description="Copy the APK file to the folder specified in the settings after build", default=False, update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_project_android_run_avd = BoolProperty(name="Run Emulator After Building APK", description="Starting android emulator after APK build", default=False, update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_project_android_list_avd = EnumProperty(
        items=[(' ', ' ', ' ')],
        name="Emulator", update=assets.invalidate_compiler_cache)
    # HTML5 Settings
    bpy.types.World.arm_project_html5_copy = BoolProperty(name="Copy Files To Specified Folder", description="Copy files to the folder specified in the settings after publish", default=False, update=assets.invalidate_compiler_cache, set=set_project_html5_copy, get=get_project_html5_copy)
    bpy.types.World.arm_project_html5_start_browser = BoolProperty(name="Run Browser After Copy", description="Run browser after copy", default=False, update=assets.invalidate_compiler_cache, set=set_project_html5_start_browser, get=get_project_html5_start_browser)
    bpy.types.World.arm_project_html5_popupmenu_in_browser = BoolProperty(name="Disable Browser Context Menu", description="Disable the browser context menu for the canvas element on the page", default=False, update=assets.invalidate_compiler_cache)
    # Windows Settings
    bpy.types.World.arm_project_win_list_vs = EnumProperty(
        items=arm.utils_vs.supported_versions,
        name="Visual Studio Version", default='17', update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_project_win_build = EnumProperty(
        items=[('nothing', 'Nothing', 'Nothing'),
               ('open', 'Open in Visual Studio', 'Open in Visual Studio'),
               ('compile', 'Compile', 'Compile the application'),
               ('compile_and_run', 'Compile and Run', 'Compile and run the application')],
        name="Action After Publishing", update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_project_win_build_mode = EnumProperty(
        items=[('Debug', 'Debug', 'Debug'),
               ('Release', 'Release', 'Release')],
        name="Mode", default='Debug', update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_project_win_build_arch = EnumProperty(
        items=[('x64', 'x64', 'x64'),
               ('x86', 'x86', 'x86')],
        name="Architecture", update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_project_win_build_log = EnumProperty(
        items=[('Summary', 'Summary', 'Show the error and warning summary at the end'),
               ('NoSummary', 'No Summary', 'Don\'t show the error and warning summary at the end'),
               ('WarningsAndErrorsOnly', 'Warnings and Errors Only', 'Show only warnings and errors'),
               ('WarningsOnly', 'Warnings Only', 'Show only warnings'),
               ('ErrorsOnly', 'Errors Only', 'Show only errors')],
        name="Compile Log Parameter", update=assets.invalidate_compiler_cache,
        default="Summary")
    bpy.types.World.arm_project_win_build_cpu = IntProperty(name="CPU Count", description="Specifies the maximum number of concurrent processes to use when building", default=1, min=1, max=multiprocessing.cpu_count())
    bpy.types.World.arm_project_win_build_open = BoolProperty(name="Open Build Directory", description="Open the build directory after successfully assemble", default=False)

    bpy.types.World.arm_project_icon = StringProperty(name="Icon (PNG)", description="Exported project icon, must be a PNG image", default="", subtype="FILE_PATH", update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_project_root = StringProperty(name="Root", description="Set root folder for linked assets", default="", subtype="DIR_PATH", update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_physics = EnumProperty(
        items=[('Disabled', 'Disabled', 'Disabled'),
               ('Auto', 'Auto', 'Auto'),
               ('Enabled', 'Enabled', 'Enabled')],
        name="Physics", default='Auto', update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_physics_engine = EnumProperty(
        items=[('Bullet', 'Bullet', 'Bullet'),
               ('Oimo', 'Oimo', 'Oimo')],
        name="Physics Engine", default='Bullet', update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_navigation = EnumProperty(
        items=[('Disabled', 'Disabled', 'Disabled'),
               ('Auto', 'Auto', 'Auto'),
               ('Enabled', 'Enabled', 'Enabled')],
        name="Navigation", default='Auto', update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_navigation_engine = EnumProperty(
        items=[('Recast', 'Recast', 'Recast')],
        name="Navigation Engine", default='Recast')
    bpy.types.World.arm_ui = EnumProperty(
        items=[('Disabled', 'Disabled', 'Disabled'),
               ('Enabled', 'Enabled', 'Enabled'),
               ('Auto', 'Auto', 'Auto')],
        name="Zui", default='Auto', description="Include UI library", update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_network = EnumProperty(
        items=[('Disabled', 'Disabled', 'Disabled'),
               ('Enabled', 'Enabled', 'Enabled'),
               ('Auto', 'Auto', 'Auto')],
        name="Networking", default='Auto', description="Include Network library", update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_audio = EnumProperty(
        items=[('Disabled', 'Disabled', 'Disabled'),
               ('Enabled', 'Enabled', 'Enabled')],
        name="Audio", default='Enabled', update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_khafile = PointerProperty(name="Append Khafile", description="Source appended to the project's khafile.js after it is generated", update=assets.invalidate_compiler_cache, type=bpy.types.Text)
    bpy.types.World.arm_texture_quality = FloatProperty(name="Texture Quality", default=1.0, min=0.0, max=1.0, subtype='FACTOR', update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_sound_quality = FloatProperty(name="Sound Quality", default=0.9, min=0.0, max=1.0, subtype='FACTOR', update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_copy_override = BoolProperty(name="Copy Override", description="Overrides any existing files when copying", default=False, update=assets.invalidate_compiled_data)
    bpy.types.World.arm_minimize = BoolProperty(name="Binary Scene Data", description="Export scene data in binary", default=True, update=assets.invalidate_compiled_data)
    bpy.types.World.arm_minify_js = BoolProperty(name="Minify JS", description="Minimize JavaScript output when publishing", default=True)
    bpy.types.World.arm_no_traces = BoolProperty(name="No Traces", description="Don't compile trace calls in the program when publishing", default=False)
    bpy.types.World.arm_optimize_data = BoolProperty(name="Optimize Data", description="Export more efficient geometry and shader data when publishing, prolongs build times", default=True, update=assets.invalidate_compiled_data)
    bpy.types.World.arm_deinterleaved_buffers = BoolProperty(name="Deinterleaved Buffers", description="Use deinterleaved vertex buffers", default=False, update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_export_tangents = BoolProperty(name="Precompute Tangents", description="Precompute tangents for normal mapping, otherwise computed in shader", default=True, update=assets.invalidate_compiled_data)
    bpy.types.World.arm_batch_meshes = BoolProperty(name="Batch Meshes", description="Group meshes by materials to speed up rendering", default=False, update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_batch_materials = BoolProperty(name="Batch Materials", description="Marge similar materials into single pipeline state", default=False, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_stream_scene = BoolProperty(name="Stream Scene", description="Stream scene content", default=False, update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_lod_gen_levels = IntProperty(name="Levels", description="Number of levels to generate", default=3, min=1)
    bpy.types.World.arm_lod_gen_ratio = FloatProperty(name="Decimate Ratio", description="Decimate ratio", default=0.8)
    bpy.types.World.arm_cache_build = BoolProperty(name="Cache Build", description="Cache build files to speed up compilation", default=True)
    bpy.types.World.arm_assert_level = EnumProperty(
        items=[
            ('Warning', 'Warning', 'Warning level, warnings don\'t throw an ArmAssertException'),
            ('Error', 'Error', 'Error level. If assertions with this level fail, an ArmAssertException is thrown'),
            ('NoAssertions', 'No Assertions', 'Ignore all assertions'),
        ],
        name="Assertion Level", description="Ignore all assertions below this level (assertions are turned off completely for published builds)", default='Warning', update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_assert_quit = BoolProperty(name="Quit On Assertion Fail", description="Whether to close the game when an 'Error' level assertion fails", default=False, update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_live_patch = BoolProperty(name="Live Patch", description="Live patching for Krom", default=False)
    bpy.types.World.arm_clear_on_compile = BoolProperty(name="Clear Console", description="Clears the system console on compile", default=False)
    bpy.types.World.arm_play_camera = EnumProperty(
        items=[('Scene', 'Scene', 'Scene'),
               ('Viewport', 'Viewport', 'Viewport')],
        name="Camera", description="Viewport camera", default='Scene', update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_play_scene = PointerProperty(name="Scene", description="Scene to launch", update=assets.invalidate_compiler_cache, type=bpy.types.Scene)
    bpy.types.World.arm_play_renderpath = StringProperty(name="Render Path", description="Default renderpath for debugging", update=assets.invalidate_compiler_cache)
    # Debug Console
    bpy.types.World.arm_debug_console = BoolProperty(name="Enable", description="Show inspector in player and enable debug draw.\nRequires that Zui is not disabled", default=arm.utils.get_debug_console_auto(), update=assets.invalidate_shader_cache)
    bpy.types.World.arm_debug_console_position = EnumProperty(
        items=[('Left', 'Left', 'Left'),
               ('Center', 'Center', 'Center'),
               ('Right', 'Right', 'Right')],
        name="Position", description="Position Debug Console", default='Right', update=assets.invalidate_shader_cache)
    bpy.types.World.arm_debug_console_scale = FloatProperty(name="Scale Console", description="Scale Debug Console", default=1.0, min=0.3, max=10.0, subtype='FACTOR', update=assets.invalidate_shader_cache)
    bpy.types.World.arm_debug_console_visible = BoolProperty(name="Visible", description="Setting the console visibility at application start", default=True, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_debug_console_trace_pos = BoolProperty(name="Print With Position", description="Whether to prepend the position of print/trace statements to the printed text", default=True)
    bpy.types.World.arm_verbose_output = BoolProperty(name="Verbose Output", description="Print additional information to the console during compilation", default=False)
    bpy.types.World.arm_runtime = EnumProperty(
        items=[('Krom', 'Krom', 'Krom'),
               ('Browser', 'Browser', 'Browser')],
        name="Runtime", description="Runtime to use when launching the game", default='Krom', update=assets.invalidate_shader_cache)
    bpy.types.World.arm_loadscreen = BoolProperty(name="Loading Screen", description="Show asset loading progress on published builds", default=True)
    bpy.types.World.arm_vsync = BoolProperty(name="VSync", description="Vertical Synchronization", default=True, update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_dce = BoolProperty(name="DCE", description="Enable dead code elimination for publish builds", default=True, update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_asset_compression = BoolProperty(name="Asset Compression", description="Enable scene data compression with LZ4 when publishing. Warning: This will slow down export!", default=False, update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_single_data_file = BoolProperty(name="Single Data File", description="Pack exported meshes and materials into single file", default=False, update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_write_config = BoolProperty(name="Write Config", description="Allow this project to be configured at runtime via a JSON file", default=False, update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_compiler_inline = BoolProperty(name="Compiler Inline", description="Favor speed over size", default=True, update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_winmode = EnumProperty(
        items = [('Window', 'Window', 'Window'),
                 ('Fullscreen', 'Fullscreen', 'Fullscreen')],
        name="Mode", default='Window', description='Window mode to start in', update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_winorient = EnumProperty(
        items = [('Multi', 'Multi', 'Multi'),
                 ('Portrait', 'Portrait', 'Portrait'),
                 ('Landscape', 'Landscape', 'Landscape')],
        name="Orientation", default='Landscape', description='Set screen orientation on mobile devices')
    bpy.types.World.arm_winresize = BoolProperty(name="Resizable", description="Allow window resize", default=False, update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_winmaximize = BoolProperty(name="Maximizable", description="Allow window maximize", default=False, update=assets.invalidate_compiler_cache)
    bpy.types.World.arm_winminimize = BoolProperty(name="Minimizable", description="Allow window minimize", default=True, update=assets.invalidate_compiler_cache)
    # For object
    bpy.types.Object.arm_instanced = EnumProperty(
        items = [('Off', 'Off', 'No instancing of children'),
                 ('Loc', 'Loc', 'Instances use their unique position (ipos)'),
                 ('Loc + Rot', 'Loc + Rot', 'Instances use their unique position and rotation (ipos and irot)'),
                 ('Loc + Scale', 'Loc + Scale', 'Instances use their unique position and scale (ipos and iscl)'),
                 ('Loc + Rot + Scale', 'Loc + Rot + Scale', 'Instances use their unique position, rotation and scale (ipos, irot, iscl)')],
        name="Instanced Children", default='Off',
        description='Whether to use instancing to draw the children of this object. If enabled, this option defines what attributes may vary between the instances',
        update=assets.invalidate_instance_cache,
        override={'LIBRARY_OVERRIDABLE'})
    bpy.types.Object.arm_export = BoolProperty(name="Export", description="Export object data", default=True, override={'LIBRARY_OVERRIDABLE'})
    bpy.types.Object.arm_spawn = BoolProperty(name="Spawn", description="Auto-add this object when creating scene", default=True, override={'LIBRARY_OVERRIDABLE'})
    bpy.types.Object.arm_mobile = BoolProperty(name="Mobile", description="Object moves during gameplay", default=False, override={'LIBRARY_OVERRIDABLE'})
    bpy.types.Object.arm_visible = BoolProperty(name="Visible", description="Render this object", default=True, override={'LIBRARY_OVERRIDABLE'})
    bpy.types.Object.arm_soft_body_margin = FloatProperty(name="Soft Body Margin", description="Collision margin", default=0.04)
    bpy.types.Object.arm_rb_linear_factor = FloatVectorProperty(name="Linear Factor", size=3, description="Set to 0 to lock axis", default=[1,1,1])
    bpy.types.Object.arm_rb_angular_factor = FloatVectorProperty(name="Angular Factor", size=3, description="Set to 0 to lock axis", default=[1,1,1])
    bpy.types.Object.arm_rb_angular_friction = FloatProperty(name="Angular Friction", description="Angular Friction", default=0.1)
    bpy.types.Object.arm_rb_trigger = BoolProperty(name="Trigger", description="Disable contact response", default=False)
    bpy.types.Object.arm_rb_deactivation_time = FloatProperty(name="Deactivation Time", description="Delay putting rigid body into sleep", default=0.0)
    bpy.types.Object.arm_rb_ccd = BoolProperty(name="Continuous Collision Detection", description="Improve collision for fast moving objects", default=False)
    bpy.types.Object.arm_rb_collision_filter_mask = bpy.props.BoolVectorProperty(
            name="Collision Collections Filter Mask",
            description="Collision collections rigid body interacts with",
            default=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False),
            size=20,
            subtype='LAYER')
    bpy.types.Object.arm_relative_physics_constraint = BoolProperty(name="Relative Physics Constraint", description="Add physics constraint relative to the parent object or collection when spawned", default=False)
    bpy.types.Object.arm_animation_enabled = BoolProperty(name="Animation", description="Enable skinning & timeline animation", default=True)
    bpy.types.Object.arm_tilesheet = StringProperty(name="Tilesheet", description="Set tilesheet animation", default='')
    bpy.types.Object.arm_tilesheet_action = StringProperty(name="Tilesheet Action", description="Set startup action", default='')
    # For speakers
    bpy.types.Speaker.arm_play_on_start = BoolProperty(name="Play on Start", description="Play this sound automatically", default=False)
    bpy.types.Speaker.arm_loop = BoolProperty(name="Loop", description="Loop this sound", default=False)
    bpy.types.Speaker.arm_stream = BoolProperty(name="Stream", description="Stream this sound", default=False)
    # For mesh
    bpy.types.Mesh.arm_cached = BoolProperty(name="Mesh Cached", description="No need to reexport mesh data", default=False)
    bpy.types.Mesh.arm_aabb = FloatVectorProperty(name="AABB", size=3, default=[0,0,0])
    bpy.types.Mesh.arm_dynamic_usage = BoolProperty(name="Dynamic Usage", description="Mesh data can change at runtime", default=False)
    bpy.types.Curve.arm_cached = BoolProperty(name="Mesh Cached", description="No need to reexport curve data", default=False)
    bpy.types.Curve.arm_aabb = FloatVectorProperty(name="AABB", size=3, default=[0,0,0])
    bpy.types.Curve.arm_dynamic_usage = BoolProperty(name="Dynamic Data Usage", description="Curve data can change at runtime", default=False)
    bpy.types.MetaBall.arm_cached = BoolProperty(name="Mesh Cached", description="No need to reexport metaball data", default=False)
    bpy.types.MetaBall.arm_aabb = FloatVectorProperty(name="AABB", size=3, default=[0,0,0])
    bpy.types.MetaBall.arm_dynamic_usage = BoolProperty(name="Dynamic Data Usage", description="Metaball data can change at runtime", default=False)
    # For armature
    bpy.types.Armature.arm_cached = BoolProperty(name="Armature Cached", description="No need to reexport armature data", default=False)
    bpy.types.Armature.arm_autobake = BoolProperty(name="Auto Bake", description="Bake constraints automatically", default=True)
    bpy.types.Armature.arm_relative_bone_constraints = BoolProperty(name="Relative Bone Constraints", description="Constraint are applied relative to Armature's parent", default=False)
    # For camera
    bpy.types.Camera.arm_frustum_culling = BoolProperty(name="Frustum Culling", description="Perform frustum culling for this camera", default=True)

    # Render path generator
    bpy.types.World.rp_preset = EnumProperty(
        items=[('Desktop', 'Desktop', 'Desktop'),
               ('Mobile', 'Mobile', 'Mobile'),
               ('Max', 'Max', 'Max'),
               ('2D/Baked', '2D/Baked', '2D/Baked'),
               ],
        name="Preset", description="Render path preset", default='Desktop')
    bpy.types.World.arm_envtex_name = StringProperty(name="Environment Texture", default='')
    bpy.types.World.arm_envtex_irr_name = StringProperty(name="Environment Irradiance", default='')
    bpy.types.World.arm_envtex_num_mips = IntProperty(name="Number of mips", default=0)
    bpy.types.World.arm_envtex_color = FloatVectorProperty(name="Environment Color", size=4, default=[0,0,0,1])
    bpy.types.World.arm_envtex_strength = FloatProperty(name="Environment Strength", default=1.0)
    bpy.types.World.arm_envtex_sun_direction = FloatVectorProperty(name="Sun Direction", size=3, default=[0,0,0])
    bpy.types.World.arm_envtex_turbidity = FloatProperty(name="Turbidity", default=1.0)
    bpy.types.World.arm_envtex_ground_albedo = FloatProperty(name="Ground Albedo", default=0.0)
    bpy.types.World.arm_nishita_density = FloatVectorProperty(name="Nishita Density", size=3, default=[1, 1, 1])
    bpy.types.Material.arm_cast_shadow = BoolProperty(name="Cast Shadow", default=True)
    bpy.types.Material.arm_receive_shadow = BoolProperty(name="Receive Shadow", description="Requires forward render path", default=True)
    bpy.types.Material.arm_depth_read = BoolProperty(name="Read Depth", description="Allow this material to read from a depth texture which is copied from the depth buffer. The meshes using this material will be drawn after all meshes that don't read from the depth texture", default=False)
    bpy.types.Material.arm_overlay = BoolProperty(name="Overlay", default=False)
    bpy.types.Material.arm_decal = BoolProperty(name="Decal", default=False)
    bpy.types.Material.arm_two_sided = BoolProperty(name="Two-Sided", description="Flip normal when drawing back-face", default=False)
    bpy.types.Material.arm_ignore_irradiance = BoolProperty(name="Ignore Irradiance", description="Ignore irradiance for material", default=False)
    bpy.types.Material.arm_cull_mode = EnumProperty(
        items=[('none', 'Both', 'None'),
               ('clockwise', 'Front', 'Clockwise'),
               ('counter_clockwise', 'Back', 'Counter-Clockwise')],
        name="Cull Mode", default='clockwise', description="Draw geometry faces")
    bpy.types.Material.arm_discard = BoolProperty(name="Alpha Test", default=False, description="Do not render fragments below specified opacity threshold")
    bpy.types.Material.arm_discard_opacity = FloatProperty(name="Mesh Opacity", default=0.2, min=0, max=1)
    bpy.types.Material.arm_discard_opacity_shadows = FloatProperty(name="Shadows Opacity", default=0.1, min=0, max=1)
    bpy.types.Material.arm_custom_material = StringProperty(name="Custom Material", description="Write custom material", default='')
    bpy.types.Material.arm_billboard = EnumProperty(
        items=[('off', 'Off', 'Off'),
               ('spherical', 'Spherical', 'Spherical'),
               ('cylindrical', 'Cylindrical', 'Cylindrical')],
        name="Billboard", default='off', description="Track camera", update=assets.invalidate_shader_cache)
    bpy.types.Material.arm_tilesheet_flag = BoolProperty(name="Tilesheet Flag", description="This material is used for tilesheet", default=False)
    bpy.types.Material.arm_particle_flag = BoolProperty(name="Particle Flag", description="This material is used for particles", default=False)
    bpy.types.Material.arm_particle_fade = BoolProperty(name="Particle Fade", description="Fade particles in and out", default=False)
    bpy.types.Material.arm_blending = BoolProperty(name="Blending", description="Enable additive blending", default=False)
    bpy.types.Material.arm_blending_source = EnumProperty(
        items=[('blend_one', 'One', 'One'),
               ('blend_zero', 'Zero', 'Zero'),
               ('source_alpha', 'Source Alpha', 'Source Alpha'),
               ('destination_alpha', 'Destination Alpha', 'Destination Alpha'),
               ('inverse_source_alpha', 'Inverse Source Alpha', 'Inverse Source Alpha'),
               ('inverse_destination_alpha', 'Inverse Destination Alpha', 'Inverse Destination Alpha'),
               ('source_color', 'Source Color', 'Source Color'),
               ('destination_color', 'Destination Color', 'Destination Color'),
               ('inverse_source_color', 'Inverse Source Color', 'Inverse Source Color'),
               ('inverse_destination_color', 'Inverse Destination Color', 'Inverse Destination Color')],
        name='Source', default='blend_one', description='Blending factor', update=assets.invalidate_shader_cache)
    bpy.types.Material.arm_blending_destination = EnumProperty(
        items=[('blend_one', 'One', 'One'),
               ('blend_zero', 'Zero', 'Zero'),
               ('source_alpha', 'Source Alpha', 'Source Alpha'),
               ('destination_alpha', 'Destination Alpha', 'Destination Alpha'),
               ('inverse_source_alpha', 'Inverse Source Alpha', 'Inverse Source Alpha'),
               ('inverse_destination_alpha', 'Inverse Destination Alpha', 'Inverse Destination Alpha'),
               ('source_color', 'Source Color', 'Source Color'),
               ('destination_color', 'Destination Color', 'Destination Color'),
               ('inverse_source_color', 'Inverse Source Color', 'Inverse Source Color'),
               ('inverse_destination_color', 'Inverse Destination Color', 'Inverse Destination Color')],
        name='Destination', default='blend_one', description='Blending factor', update=assets.invalidate_shader_cache)
    bpy.types.Material.arm_blending_operation = EnumProperty(
        items=[('add', 'Add', 'Add'),
               ('subtract', 'Subtract', 'Subtract'),
               ('reverse_subtract', 'Reverse Subtract', 'Reverse Subtract'),
               ('min', 'Min', 'Min'),
               ('max', 'Max', 'Max')],
        name='Operation', default='add', description='Blending operation', update=assets.invalidate_shader_cache)
    bpy.types.Material.arm_blending_source_alpha = EnumProperty(
        items=[('blend_one', 'One', 'One'),
               ('blend_zero', 'Zero', 'Zero'),
               ('source_alpha', 'Source Alpha', 'Source Alpha'),
               ('destination_alpha', 'Destination Alpha', 'Destination Alpha'),
               ('inverse_source_alpha', 'Inverse Source Alpha', 'Inverse Source Alpha'),
               ('inverse_destination_alpha', 'Inverse Destination Alpha', 'Inverse Destination Alpha'),
               ('source_color', 'Source Color', 'Source Color'),
               ('destination_color', 'Destination Color', 'Destination Color'),
               ('inverse_source_color', 'Inverse Source Color', 'Inverse Source Color'),
               ('inverse_destination_color', 'Inverse Destination Color', 'Inverse Destination Color')],
        name='Source (Alpha)', default='blend_one', description='Blending factor', update=assets.invalidate_shader_cache)
    bpy.types.Material.arm_blending_destination_alpha = EnumProperty(
        items=[('blend_one', 'One', 'One'),
               ('blend_zero', 'Zero', 'Zero'),
               ('source_alpha', 'Source Alpha', 'Source Alpha'),
               ('destination_alpha', 'Destination Alpha', 'Destination Alpha'),
               ('inverse_source_alpha', 'Inverse Source Alpha', 'Inverse Source Alpha'),
               ('inverse_destination_alpha', 'Inverse Destination Alpha', 'Inverse Destination Alpha'),
               ('source_color', 'Source Color', 'Source Color'),
               ('destination_color', 'Destination Color', 'Destination Color'),
               ('inverse_source_color', 'Inverse Source Color', 'Inverse Source Color'),
               ('inverse_destination_color', 'Inverse Destination Color', 'Inverse Destination Color')],
        name='Destination (Alpha)', default='blend_one', description='Blending factor', update=assets.invalidate_shader_cache)
    bpy.types.Material.arm_blending_operation_alpha = EnumProperty(
        items=[('add', 'Add', 'Add'),
               ('subtract', 'Subtract', 'Subtract'),
               ('reverse_subtract', 'Reverse Subtract', 'Reverse Subtract'),
               ('min', 'Min', 'Min'),
               ('max', 'Max', 'Max')],
        name='Operation (Alpha)', default='add', description='Blending operation', update=assets.invalidate_shader_cache)
    # For scene
    bpy.types.Scene.arm_export = BoolProperty(name="Export", description="Export scene data", default=True)
    bpy.types.Scene.arm_terrain_textures = StringProperty(name="Textures", description="Set root folder for terrain assets", default="//Bundled/", subtype="DIR_PATH")
    bpy.types.Scene.arm_terrain_sectors = IntVectorProperty(name="Sectors", description="Number of sectors to generate", default=[1,1], size=2)
    bpy.types.Scene.arm_terrain_sector_size = FloatProperty(name="Sector Size", description="Dimensions for single sector", default=16)
    bpy.types.Scene.arm_terrain_height_scale = FloatProperty(name="Height Scale", description="Scale height from the 0-1 range", default=5)
    bpy.types.Scene.arm_terrain_object = PointerProperty(name="Object", type=bpy.types.Object, description="Terrain root object")
    # For light
    bpy.types.Light.arm_clip_start = FloatProperty(name="Clip Start", default=0.1)
    bpy.types.Light.arm_clip_end = FloatProperty(name="Clip End", default=50.0)
    bpy.types.Light.arm_fov = FloatProperty(name="Field of View", default=0.84)
    bpy.types.Light.arm_shadows_bias = FloatProperty(name="Bias", description="Depth offset to fight shadow acne", default=1.0)
    bpy.types.World.arm_light_ies_texture = StringProperty(name="IES Texture", default="")
    bpy.types.World.arm_light_clouds_texture = StringProperty(name="Clouds Texture", default="")

    bpy.types.World.arm_rpcache_list = CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.World.arm_scripts_list = CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.World.arm_bundled_scripts_list = CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.World.arm_canvas_list = CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.World.arm_wasm_list = CollectionProperty(type=bpy.types.PropertyGroup)
    bpy.types.World.world_defs = StringProperty(name="World Shader Defs", default='')
    bpy.types.World.compo_defs = StringProperty(name="Compositor Shader Defs", default='')

    bpy.types.World.arm_use_clouds = BoolProperty(name="Clouds", default=False, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_darken_clouds = BoolProperty(
        name="Darken Clouds at Night",
        description="Darkens the clouds when the sun is low. This setting is for artistic purposes and is not physically correct",
        default=False, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_clouds_lower = FloatProperty(name="Lower", default=1.0, min=0.1, max=10.0, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_clouds_upper = FloatProperty(name="Upper", default=1.0, min=0.1, max=10.0, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_clouds_wind = FloatVectorProperty(name="Wind", default=[1.0, 0.0], size=2, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_clouds_secondary = FloatProperty(name="Secondary", default=1.0, min=0.1, max=10.0, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_clouds_precipitation = FloatProperty(name="Precipitation", default=1.0, min=0.1, max=10.0, update=assets.invalidate_shader_cache)
    bpy.types.World.arm_clouds_steps = IntProperty(name="Steps", default=24, min=1, max=240, update=assets.invalidate_shader_cache)

    bpy.types.Material.export_uvs = BoolProperty(name="Export UVs", default=False)
    bpy.types.Material.export_vcols = BoolProperty(name="Export VCols", default=False)
    bpy.types.Material.export_tangents = BoolProperty(name="Export Tangents", default=False)
    bpy.types.Material.arm_skip_context = StringProperty(name="Skip Context", default='')
    bpy.types.Material.arm_material_id = IntProperty(name="ID", default=0)
    bpy.types.NodeSocket.is_uniform = BoolProperty(name="Is Uniform", description="Mark node sockets to be processed as material uniforms", default=False)
    bpy.types.NodeTree.arm_cached = BoolProperty(name="Node Tree Cached", description="No need to reexport node tree", default=False)
    bpy.types.Material.signature = StringProperty(name="Signature", description="Unique string generated from material nodes", default="")
    bpy.types.Material.arm_cached = BoolProperty(name="Material Cached", description="No need to reexport material data", default=False)
    bpy.types.Node.arm_material_param = BoolProperty(name="Parameter", description="Control this node from script", default=False)
    bpy.types.Node.arm_watch = BoolProperty(name="Watch", description="Watch value of this node in debug console", default=False)
    bpy.types.Node.arm_version = IntProperty(name="Node Version", description="The version of an instanced node", default=0)
    # Particles
    bpy.types.ParticleSettings.arm_count_mult = FloatProperty(name="Multiply Count", description="Multiply particle count when rendering in Armory", default=1.0)
    bpy.types.ParticleSettings.arm_loop = BoolProperty(name="Loop", description="Loop this particle system", default=False)

    create_wrd()

def create_wrd():
    if 'Arm' not in bpy.data.worlds:
        wrd = bpy.data.worlds.new('Arm')
        wrd.use_fake_user = True # Store data world object, add fake user to keep it alive
        wrd.arm_version = arm_version
        wrd.arm_commit = arm_commit

def init_properties_on_load():
    if 'Arm' not in bpy.data.worlds:
        init_properties()
    # New project?
    if bpy.data.filepath == '':
        wrd = bpy.data.worlds['Arm']
        wrd.arm_debug_console = arm.utils.get_debug_console_auto()
    arm.utils.fetch_script_names()

def update_armory_world():
    global arm_version
    wrd = bpy.data.worlds['Arm']

    # Outdated project
    file_version = tuple(map(int, wrd.arm_version.split('.')))
    sdk_version = tuple(map(int, arm_version.split('.')))
    if bpy.data.filepath != '' and (file_version < sdk_version or wrd.arm_commit != arm_commit):
        # This allows for seamless migration from earlier versions of Armory
        for rp in wrd.arm_rplist:  # TODO: deprecated
            if rp.rp_gi != 'Off':
                rp.rp_gi = 'Off'
                rp.rp_voxelao = True

        # For some breaking changes we need to use a special update
        # routine first before regularly replacing nodes
        if file_version < (2021, 8):
            arm.logicnode.replacement.node_compat_sdk2108()
        if file_version < (2022, 3):
            arm.logicnode.tree_variables.node_compat_sdk2203()
        if file_version < (2022, 9):
            arm.logicnode.tree_variables.node_compat_sdk2209()

        arm.logicnode.replacement.replace_all()

        print(f'Project updated to SDK v{arm_version}({arm_commit})')
        wrd.arm_version = arm_version
        wrd.arm_commit = arm_commit
        arm.make.clean()

def register():
    init_properties()
    arm.utils.fetch_bundled_script_names()

def unregister():
    pass
