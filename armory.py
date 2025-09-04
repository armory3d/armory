# Armory 3D Engine
# https://github.com/armory3d/armory
bl_info = {
    "name": "Armory",
    "category": "Game Engine",
    "location": "Properties -> Render -> Armory Player",
    "description": "3D Game Engine for Blender",
    "author": "Armory3D.org",
    "version": (2025, 9, 0),
    "blender": (4, 5, 0),
    "doc_url": "https://github.com/armory3d/armory/wiki",
    "tracker_url": "https://github.com/armory3d/armory/issues"
}

from enum import IntEnum
import os
from pathlib import Path
import platform
import re
import shutil
import stat
import subprocess
import sys
import textwrap
import threading
import traceback
import typing
from typing import Callable, Optional
import webbrowser

import bpy
from bpy.app.handlers import persistent
from bpy.props import *
from bpy.types import Operator, AddonPreferences


class SDKSource(IntEnum):
    PREFS = 0
    LOCAL = 1
    ENV_VAR = 2


# Keep the value of these globals after addon reload
if "is_running" not in locals():
    is_running = False
    last_sdk_path = ""
    last_scripts_path = ""
    sdk_source = SDKSource.PREFS

update_error_msg = ''


def get_os():
    s = platform.system()
    if s == 'Windows':
        return 'win'
    elif s == 'Darwin':
        return 'mac'
    else:
        return 'linux'


def detect_sdk_path():
    """Auto-detect the SDK path after Armory installation."""
    # Do not overwrite the SDK path (this method gets
    # called after each registration, not after
    # installation only)
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons["armory"].preferences
    if addon_prefs.sdk_path != "":
        return

    win = bpy.context.window_manager.windows[0]
    area = win.screen.areas[0]
    area_type = area.type
    area.type = "INFO"
    with bpy.context.temp_override(window=win, screen=win.screen, area=area):
        bpy.ops.info.select_all(action='SELECT')
        bpy.ops.info.report_copy()
    area.type = area_type
    clipboard = bpy.context.window_manager.clipboard

    # If armory was installed multiple times in this session,
    # use the latest log entry.
    match = re.findall(r"^Modules Installed .* from '(.*armory.py)' into", clipboard, re.MULTILINE)
    if match:
        addon_prefs.sdk_path = os.path.dirname(match[-1])

def get_link_web_server(self):
    return self.get('link_web_server', 'http://localhost/')

def set_link_web_server(self, value):
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    if re.match(regex, value) is not None:
        self['link_web_server'] = value


class ArmoryAddonPreferences(AddonPreferences):
    bl_idname = __name__

    def sdk_path_update(self, context):
        if self.skip_update:
            return
        self.skip_update = True
        self.sdk_path = bpy.path.reduce_dirs([bpy.path.abspath(self.sdk_path)])[0] + '/'
        restart_armory(context)

    def ide_bin_update(self, context):
        if self.skip_update:
            return
        self.skip_update = True
        self.ide_bin = bpy.path.reduce_dirs([bpy.path.abspath(self.ide_bin)])[0]

    def ffmpeg_path_update(self, context):
        if self.skip_update or self.ffmpeg_path == '':
            return
        self.skip_update = True
        self.ffmpeg_path = bpy.path.reduce_dirs([bpy.path.abspath(self.ffmpeg_path)])[0]

    def renderdoc_path_update(self, context):
        if self.skip_update or self.renderdoc_path == '':
            return
        self.skip_update = True
        self.renderdoc_path = bpy.path.reduce_dirs([bpy.path.abspath(self.renderdoc_path)])[0]

    def android_sdk_path_update(self, context):
        if self.skip_update:
            return
        self.skip_update = True
        self.android_sdk_root_path = bpy.path.reduce_dirs([bpy.path.abspath(self.android_sdk_root_path)])[0]

    def android_apk_copy_update(self, context):
        if self.skip_update:
            return
        self.skip_update = True
        self.android_apk_copy_path = bpy.path.reduce_dirs([bpy.path.abspath(self.android_apk_copy_path)])[0]

    def html5_copy_path_update(self, context):
        if self.skip_update:
            return
        self.skip_update = True
        self.html5_copy_path = bpy.path.reduce_dirs([bpy.path.abspath(self.html5_copy_path)])[0]

    sdk_path: StringProperty(name="SDK Path", subtype="FILE_PATH", update=sdk_path_update, default="")
    update_submodules: BoolProperty(
        name="Update Submodules", default=True, description=(
            "If enabled, update the submodules to their most current commit after downloading the SDK."
            " Otherwise, the submodules are checked out at whatever commit the latest SDK references."
        )
    )

    show_advanced: BoolProperty(name="Show Advanced", default=False)
    tabs: EnumProperty(
        items=[('general', 'General', 'General Settings'),
               ('build', 'Build Preferences', 'Settings related to building the game'),
               ('debugconsole', 'Debug Console', 'Settings related to the in-game debug console'),
               ('dev', 'Developer Settings', 'Settings for Armory developers')],
        name='Tabs', default='general', description='Choose the settings page you want to see')

    ide_bin: StringProperty(name="Code Editor Executable", subtype="FILE_PATH", update=ide_bin_update, default="", description="Path to your editor's executable file")
    code_editor: EnumProperty(
        items = [('default', 'System Default', 'System Default'),
                 ('kodestudio', 'VS Code | Kode Studio', 'Visual Studio Code or Kode Studio'),
                 ('sublime', 'Sublime Text', 'Sublime Text'),
                 ('custom', "Custom", "Use a Custom Code Editor")],
        name="Code Editor", default='default', description='Use this editor for editing scripts')
    ui_scale: FloatProperty(name='UI Scale', description='Adjust UI scale for Armory tools', default=1.0, min=1.0, max=4.0)
    khamake_threads: IntProperty(name='Khamake Processes', description='Allow Khamake to spawn multiple processes for faster builds', default=4, min=1)
    khamake_threads_use_auto: BoolProperty(name='Auto', description='Let Khamake choose the number of processes automatically', default=False)
    compilation_server: BoolProperty(name='Compilation Server', description='Allow Haxe to create a local compilation server for faster builds', default=True)
    renderdoc_path: StringProperty(name="RenderDoc Path", description="Binary path", subtype="FILE_PATH", update=renderdoc_path_update, default="")
    ffmpeg_path: StringProperty(name="FFMPEG Path", description="Binary path", subtype="FILE_PATH", update=ffmpeg_path_update, default="")
    save_on_build: BoolProperty(name="Save on Build", description="Save .blend", default=False)
    open_build_directory: BoolProperty(name="Open Build Directory After Publishing", description="Open the build directory after successfully publishing the project", default=False)
    cmft_use_opencl: BoolProperty(
        name="CMFT: Use OpenCL", default=True,
        description=(
            "Whether to use OpenCL processing to generate radiance maps with CMFT."
            " If you experience extremely long build times caused by CMFT, try disabling this option."
            " For more information see https://github.com/armory3d/armory/issues/2760"
        ))
    legacy_shaders: BoolProperty(name="Legacy Shaders", description="Attempt to compile shaders runnable on older hardware, use this for WebGL1 or GLES2 support in mobile render path", default=False)
    relative_paths: BoolProperty(name="Generate Relative Paths", description="Write relative paths in khafile", default=False)
    viewport_controls: EnumProperty(
        items=[('qwerty', 'qwerty', 'qwerty'),
               ('azerty', 'azerty', 'azerty')],
        name="Viewport Controls", default='qwerty', description='Viewport camera mode controls')
    skip_update: BoolProperty(name="", default=False)
    # Debug Console
    debug_console_auto: BoolProperty(name="Enable Debug Console for new project", description="Enable Debug Console for new project", default=False)
    # Shortcuts
    items_enum_keyboard = [ ('192', '~', 'TILDE'),
                ('219', '[', 'OPEN BRACKET'),
                ('221', ']', 'CLOSE BRACKET'),
                ('192', '`', 'BACK QUOTE'),
                ('57', '(', 'OPEN BRACKET'),
                ('48', ')', 'CLOSE BRACKET'),
                ('56', '*', 'MULTIPLY'),
                ('190', '.', 'PERIOD'),
                ('188', ',', 'COMMA', ),
                ('191', '/', 'SLASH'),
                ('65', 'A', 'A'),
                ('66', 'B', 'B'),
                ('67', 'C', 'C'),
                ('68', 'D', 'D'),
                ('69', 'E', 'E'),
                ('70', 'F', 'F'),
                ('71', 'G', 'G'),
                ('72', 'H', 'H'),
                ('73', 'I', 'I'),
                ('74', 'J', 'J'),
                ('75', 'K', 'K'),
                ('76', 'L', 'L'),
                ('77', 'M', 'M'),
                ('78', 'N', 'N'),
                ('79', 'O', 'O'),
                ('80', 'P', 'P'),
                ('81', 'Q', 'Q'),
                ('82', 'R', 'R'),
                ('83', 'S', 'S'),
                ('84', 'T', 'T'),
                ('85', 'U', 'U'),
                ('86', 'V', 'V'),
                ('87', 'W', 'W'),
                ('88', 'X', 'X'),
                ('89', 'Y', 'Y'),
                ('90', 'Z', 'Z'),
                ('48', '0', '0'),
                ('49', '1', '1'),
                ('50', '2', '2'),
                ('51', '3', '3'),
                ('52', '4', '4'),
                ('53', '5', '5'),
                ('54', '6', '6'),
                ('55', '7', '7'),
                ('56', '8', '8'),
                ('57', '9', '9'),
                ('32', 'SPACE', 'SPACE'),
                ('8', 'BACKSPACE', 'BACKSPACE'),
                ('9', 'TAB', 'TAB'),
                ('13', 'ENTER', 'ENTER'),
                ('16', 'SHIFT', 'SHIFT'),
                ('17', 'CONTROL', 'CONTROL'),
                ('18', 'ALT', 'ALT'),
                ('27', 'ESCAPE', 'ESCAPE'),
                ('46', 'DELETE', 'DELETE'),
                ('33', 'PAGE UP', 'PAGE UP'),
                ('34', 'PAGE DOWN', 'PAGE DOWN'),
                ('38', 'UP', 'UP'),
                ('39', 'RIGHT', 'RIGHT'),
                ('37', 'LEFT', 'LEFT'),
                ('40', 'DOWN', 'DOWN'),
                ('96', 'NUMPAD 0', 'NUMPAD 0'),
                ('97', 'NUMPAD 1', 'NUMPAD 1'),
                ('98', 'NUMPAD 2', 'NUMPAD 2'),
                ('99', 'NUMPAD 3', 'NUMPAD 3'),
                ('100', 'NUMPAD 4', 'NUMPAD 4'),
                ('101', 'NUMPAD 5', 'NUMPAD 5'),
                ('102', 'NUMPAD 6', 'NUMPAD 6'),
                ('103', 'NUMPAD 7', 'NUMPAD 7'),
                ('104', 'NUMPAD 8', 'NUMPAD 8'),
                ('106', 'NUMPAD *', 'NUMPAD *'),
                ('110', 'NUMPAD /', 'NUMPAD /'),
                ('107', 'NUMPAD +', 'NUMPAD +'),
                ('108', 'NUMPAD -', 'NUMPAD -'),
                ('109', 'NUMPAD .', 'NUMPAD .')]
    debug_console_visible_sc: EnumProperty(items = items_enum_keyboard,
        name="Visible / Invisible Shortcut", description="Shortcut to display the console", default='192')
    debug_console_scale_in_sc: EnumProperty(items = items_enum_keyboard,
        name="Scale In Shortcut", description="Shortcut to scale in on the console", default='219')
    debug_console_scale_out_sc: EnumProperty(items = items_enum_keyboard,
        name="Scale Out Shortcut", description="Shortcut to scale out on the console", default='221')
    # Android Settings
    android_sdk_root_path: StringProperty(name="Android SDK Path", description="Path to the Android SDK installation directory", default="", subtype="FILE_PATH", update=android_sdk_path_update)
    android_open_build_apk_directory: BoolProperty(name="Open Build APK Directory", description="Open the build APK directory after successfully assemble", default=False)
    android_apk_copy_path: StringProperty(name="Copy APK To Folder", description="Copy the APK file to the folder after build", default="", subtype="FILE_PATH", update=android_apk_copy_update)
    android_apk_copy_open_directory: BoolProperty(name="Open Directory After Copy", description="Open the directory after copy the APK file", default=False)
    # HTML5 Settings
    html5_copy_path: StringProperty(name="HTML5 Copy Path", description="Path to copy project after successfully publish", default="", subtype="FILE_PATH", update=html5_copy_path_update)
    link_web_server: StringProperty(name="Url To Web Server", description="Url to the web server that runs the local server", default="http://localhost/", set=set_link_web_server, get=get_link_web_server)
    html5_server_port: IntProperty(name="Web Server Port", description="The port number of the local web server", default=8040, min=1024, max=65535)
    html5_server_log: BoolProperty(name="Enable Http Log", description="Enable logging of http requests to local web server", default=True)

    # Developer options
    profile_exporter: BoolProperty(
        name="Exporter Profiling", default=False,
        description="Run profiling when exporting the scene. A file named 'profile_exporter.prof' with the results will"
                    " be saved into the SDK directory and can be opened with tools such as SnakeViz")
    khamake_debug: BoolProperty(
        name="Set Khamake Flag: --debug", default=False,
        description="Set the --debug flag when running Khamake. Useful for debugging HLSL shaders with RenderDoc")
    haxe_times: BoolProperty(
        name="Set Haxe Flag: --times", default=False,
        description="Set the --times flag when running Haxe.")
    use_armory_py_symlink: BoolProperty(
        name="Symlink armory.py", default=False,
        description=("Automatically symlink the registered armory.py with the original armory.py from the SDK for faster"
                     " development. Warning: this will invalidate the installation if the SDK is removed"),
        update=lambda self, context: update_armory_py(get_sdk_path(context)),
    )

    def draw(self, context):
        self.skip_update = False
        layout = self.layout
        layout.label(text="Welcome to Armory!")

        # Compare version Blender and Armory (major, minor)
        if bpy.app.version[0] != 3 or bpy.app.version[1] != 6:
            box = layout.box().column()
            box.label(text="Warning: For Armory to work correctly, you need Blender 3.6 LTS.")

        layout.prop(self, "sdk_path")
        sdk_path = get_sdk_path(context)
        if os.path.exists(sdk_path + '/armory') or os.path.exists(sdk_path + '/armory_backup'):
            sdk_exists = True
        else:
            sdk_exists = False
        if not sdk_exists:
            layout.label(text="The directory will be created.")
        elif sdk_source != SDKSource.PREFS:
            row = layout.row()
            row.alert = True
            if sdk_source == SDKSource.LOCAL:
                row.label(text=f'Using local SDK from {sdk_path}')
            elif sdk_source == SDKSource.ENV_VAR:
                row.label(text=f'Using SDK from "ARMSDK" environment variable: {sdk_path}')

        box = layout.box().column()

        row = box.row(align=True)
        row.label(text="Armory SDK Manager")
        col = row.column()
        col.alignment = "RIGHT"
        col.operator("arm_addon.help", icon="URL")

        box.label(text="Note: Development version may run unstable!")
        box.separator()

        box.prop(self, "update_submodules")

        row = box.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("arm_addon.print_version_info", icon="INFO")
        if sdk_exists:
            row.operator("arm_addon.update", icon="FILE_REFRESH")
        else:
            row.operator("arm_addon.install", icon="IMPORT")
        row.operator("arm_addon.restore", icon="LOOP_BACK")

        if update_error_msg != '':
            col = box.column(align=True)
            col.scale_y = 0.8
            col.alignment = 'EXPAND'
            col.alert = True

            # Roughly estimate how much text fits in the current region's
            # width (approximation of box width)
            textwrap_width = int(bpy.context.region.width / 6)

            col.label(text='An error occured:')
            lines = textwrap.wrap(update_error_msg, width=textwrap_width, break_long_words=True, initial_indent='  ', subsequent_indent='  ')
            for line in lines:
                col.label(text=line)

        box.label(text="Check console for download progress. Please restart Blender after successful SDK update.")

        col = layout.column(align=(not self.show_advanced))
        col.prop(self, "show_advanced")
        if self.show_advanced:
            box_main = col.box()

            # Use a row to expand the prop horizontally
            row = box_main.row()
            row.scale_y = 1.2
            row.ui_units_y = 1.4
            row.prop(self, "tabs", expand=True)

            box = box_main.column()

            if self.tabs == "general":
                box.prop(self, "code_editor")
                if self.code_editor != "default":
                    box.prop(self, "ide_bin")
                box.prop(self, "renderdoc_path")
                box.prop(self, "ffmpeg_path")
                box.prop(self, "viewport_controls")
                box.prop(self, "ui_scale")
                box.prop(self, "legacy_shaders")
                box.prop(self, "relative_paths")

            elif self.tabs == "build":
                box.label(text="Build Preferences")
                row = box.split(factor=0.8, align=True)
                _col = row.column(align=True)
                _col.enabled = not self.khamake_threads_use_auto
                _col.prop(self, "khamake_threads")
                row.prop(self, "khamake_threads_use_auto", toggle=True)
                box.prop(self, "compilation_server")
                box.prop(self, "open_build_directory")
                box.prop(self, "save_on_build")

                box.separator()
                box.prop(self, "cmft_use_opencl")

                box = box_main.column()
                box.label(text="Android Settings")
                box.prop(self, "android_sdk_root_path")
                box.prop(self, "android_open_build_apk_directory")
                box.prop(self, "android_apk_copy_path")
                box.prop(self, "android_apk_copy_open_directory")

                box = box_main.column()
                box.label(text="HTML5 Settings")
                box.prop(self, "html5_copy_path")
                box.prop(self, "link_web_server")
                box.prop(self, "html5_server_port")
                box.prop(self, "html5_server_log")

            elif self.tabs == "debugconsole":
                box.label(text="Debug Console")
                box.prop(self, "debug_console_auto")
                box.label(text="Note: The following settings will be applied if Debug Console is enabled in the project settings")
                box.prop(self, "debug_console_visible_sc")
                box.prop(self, "debug_console_scale_in_sc")
                box.prop(self, "debug_console_scale_out_sc")

            elif self.tabs == "dev":
                col = box.column(align=True)
                col.label(icon="ERROR", text="Warning: The following settings are meant for Armory developers and might slow")
                col.label(icon="BLANK1", text="down Armory or make it unstable. Only change them if you know what you are doing.")
                box.separator()

                col = box.column(align=True)
                col.prop(self, "profile_exporter")
                col.prop(self, "khamake_debug")
                col.prop(self, "haxe_times")

                col = box.column(align=True)
                col.prop(self, "use_armory_py_symlink")

    @staticmethod
    def get_prefs() -> 'ArmoryAddonPreferences':
        preferences = bpy.context.preferences
        return typing.cast(ArmoryAddonPreferences, preferences.addons["armory"].preferences)


def get_fp():
    if bpy.data.filepath == '':
        return ''
    s = bpy.data.filepath.split(os.path.sep)
    s.pop()
    return os.path.sep.join(s)


def same_path(path1: str, path2: str) -> bool:
    """Compare whether two paths point to the same location."""
    if os.path.exists(path1) and os.path.exists(path2):
        return os.path.samefile(path1, path2)

    p1 = os.path.realpath(os.path.normpath(os.path.normcase(path1)))
    p2 = os.path.realpath(os.path.normpath(os.path.normcase(path2)))
    return p1 == p2


def get_sdk_path(context: bpy.context) -> str:
    """Returns the absolute path of the currently set Armory SDK.

    The path is read from the following sources in that priority (the
    topmost source is used if valid):
        1. Environment variable 'ARMSDK' (must be an absolute path).
           Useful to temporarily override the SDK path, e.g. when
           running from the command line.
        2. Local SDK in /armsdk relative to the current file.
        3. The SDK path specified in the add-on preferences.
    """
    global sdk_source

    sdk_envvar = os.environ.get('ARMSDK')
    if sdk_envvar is not None and os.path.isabs(sdk_envvar) and os.path.isdir(sdk_envvar) and os.path.exists(sdk_envvar):
        sdk_source = SDKSource.ENV_VAR
        return sdk_envvar

    fp = get_fp()
    if fp != '':  # blend file is not saved
        local_sdk = os.path.join(fp, 'armsdk')
        if os.path.exists(local_sdk):
            sdk_source = SDKSource.LOCAL
            return local_sdk

    sdk_source = SDKSource.PREFS
    preferences = context.preferences
    addon_prefs = preferences.addons["armory"].preferences
    return addon_prefs.sdk_path

def apply_unix_permissions(sdk):
    """Apply permissions to executable files in Linux and macOS

    The .zip format does not preserve file permissions and will
    cause every subprocess of Armory3D to not work at all. This
    workaround fixes the issue so Armory releases will work.
    """
    if get_os() == 'linux':
        paths=[
            os.path.join(sdk, "lib/armory_tools/cmft/cmft-linux64"),
            os.path.join(sdk, "Krom/Krom"),
            # NodeJS
            os.path.join(sdk, "nodejs/node-linux32"),
            os.path.join(sdk, "nodejs/node-linux64"),
            os.path.join(sdk, "nodejs/node-linuxarm"),
            # Kha tools x64
            os.path.join(sdk, "Kha/Tools/linux_x64/haxe"),
            os.path.join(sdk, "Kha/Tools/linux_x64/lame"),
            os.path.join(sdk, "Kha/Tools/linux_x64/oggenc"),
            # Kha tools arm64
            os.path.join(sdk, "Kha/Tools/linux_arm64/haxe"),
            os.path.join(sdk, "Kha/Tools/linux_arm64/lame"),
            os.path.join(sdk, "Kha/Tools/linux_arm64/oggenc"),
            # Kinc tools x64
            os.path.join(sdk, "Kha/Kinc/Tools/linux_x64/kmake"),
            os.path.join(sdk, "Kha/Kinc/Tools/linux_x64/kraffiti"),
            os.path.join(sdk, "Kha/Kinc/Tools/linux_x64/krafix"),
            # Kinc tools arm
            os.path.join(sdk, "Kha/Kinc/Tools/linux_arm/kmake"),
            os.path.join(sdk, "Kha/Kinc/Tools/linux_arm/kraffiti"),
            os.path.join(sdk, "Kha/Kinc/Tools/linux_arm/krafix"),
            # Kinc tools arm64
            os.path.join(sdk, "Kha/Kinc/Tools/linux_arm64/kmake"),
            os.path.join(sdk, "Kha/Kinc/Tools/linux_arm64/kraffiti"),
            os.path.join(sdk, "Kha/Kinc/Tools/linux_arm64/krafix"),
        ]
        for path in paths:
            os.chmod(path, 0o777)

    if get_os() == 'mac':
        paths=[
            os.path.join(sdk, "lib/armory_tools/cmft/cmft-osx"),
            os.path.join(sdk, "nodejs/node-osx"),
            os.path.join(sdk, "Krom/Krom.app/Contents/MacOS/Krom"),
            # Kha tools
            os.path.join(sdk, "Kha/Tools/macos/haxe"),
            os.path.join(sdk, "Kha/Tools/macos/lame"),
            os.path.join(sdk, "Kha/Tools/macos/oggenc"),
            # Kinc tools
            os.path.join(sdk, "Kha/Kinc/Tools/macos/kmake"),
            os.path.join(sdk, "Kha/Kinc/Tools/macos/kraffiti"),
            os.path.join(sdk, "Kha/Kinc/Tools/macos/krafix"),
        ]
        for path in paths:
            os.chmod(path, 0o777)

def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def run_proc(cmd: list[str], done: Optional[Callable[[bool], None]] = None):
    def fn(p, done):
        p.wait()
        if done is not None:
            done(False)
    p = None

    try:
        p = subprocess.Popen(cmd)
    except OSError as err:
        if done is not None:
            done(True)
        print("Running command:", *cmd, "\n")
        if err.errno == 12:
            print("Make sure there is enough space for the SDK (at least 500mb)")
        elif err.errno == 13:
            print("Permission denied, try modifying the permission of the sdk folder")
        else:
            print("error: " + str(err))
    except Exception as err:
        if done is not None:
            done(True)
        print("Running command:", *cmd, "\n")
        print("error:", str(err), "\n")
    else:
        threading.Thread(target=fn, args=(p, done)).start()

    return p


def set_update_error(msg: str, err: Exception):
    traceback.print_exception(type(err), err, err.__traceback__)

    global update_error_msg
    update_error_msg = msg + ' The full error message has been printed to the console.'


def try_os_call(func: Callable, *args, **kwargs) -> bool:
    try:
        func(*args, **kwargs)
    except OSError as err:
        if hasattr(err, 'winerror'):
            if err.winerror == 32:  # file is used by another process (ERROR_SHARING_VIOLATION)
                set_update_error((
                    f'The file/path {err.filename} is used by at least one other process (ERROR_SHARING_VIOLATION).'
                    ' Please close all processes that reference it and try again.'
                ), err)
                return False

        set_update_error('There was an unknown error while updating/restoring the Armory SDK.', err)
        return False
    except Exception as err:
        set_update_error('There was an unknown error while updating/restoring the Armory SDK.', err)
        return False

    return True


def git_clone(done: Callable[[bool], None], rootdir: str, gitn: str, subdir: str, recursive=False):
    rootdir = os.path.normpath(rootdir)
    path = rootdir + '/' + subdir if subdir != '' else rootdir

    if os.path.exists(path) and not os.path.exists(path + '_backup'):
        if not try_os_call(os.rename, path, path + '_backup'):
            return
    if os.path.exists(path):
        shutil.rmtree(path, onerror=remove_readonly)

    if recursive:
        run_proc(['git', 'clone', '--recursive', 'https://github.com/' + gitn, path, '--depth', '1', '--shallow-submodules', '--jobs', '4'], done)
    else:
        run_proc(['git', 'clone', 'https://github.com/' + gitn, path, '--depth', '1'], done)


def git_test(self: bpy.types.Operator, required_version=None):
    print('Testing if git is working...')
    try:
        p = subprocess.Popen(['git', '--version'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output, _ = p.communicate()
    except (OSError, Exception) as exception:
        print(str(exception))
    else:
        matched = re.match("git version ([0-9]+).([0-9]+).([0-9]+)", output.decode('utf-8'))
        if matched:
            if required_version is not None:
                matched_version = (int(matched.group(1)), int(matched.group(2)), int(matched.group(3)))
                if matched_version < required_version:
                    msg = f"Installed git version {matched_version} is too old, please update git to version {required_version} or above"
                    print(msg)
                    self.report({"ERROR"}, msg)
                    return False

            print('Git test succeeded.')
            return True

    msg = "Git test failed. Make sure git is installed (https://git-scm.com/downloads) or is working correctly."
    print(msg)
    self.report({"ERROR"}, msg)
    return False


def restore_repo(rootdir: str, subdir: str):
    rootdir = os.path.normpath(rootdir)
    path = rootdir + '/' + subdir if subdir != '' else rootdir
    if os.path.exists(path + '_backup'):
        if os.path.exists(path):
            if not try_os_call(shutil.rmtree, path, onerror=remove_readonly):
                return
        if not try_os_call(os.rename, path + '_backup', path):
            # TODO: if rmtree() succeeds but rename fails the SDK needs
            #   manual cleanup by the user, add message to UI
            return


class ArmAddonPrintVersionInfoButton(bpy.types.Operator):
    bl_idname = "arm_addon.print_version_info"
    bl_label = "Print Version Info"
    bl_description = "Print detailed information about the used SDK version to the console. This requires Git"

    def execute(self, context):
        sdk_path = get_sdk_path(context)
        if sdk_path == "":
            self.report({"ERROR"}, "Configure Armory SDK path first")
            return {"CANCELLED"}

        if not git_test(self):
            return {"CANCELLED"}

        if not os.path.exists(f'{sdk_path}/.git'):
            msg=f"{sdk_path}/.git not found"
            self.report({"ERROR"}, msg)
            return {"CANCELLED"}

        def print_version_info():
            print("==============================")
            print("| SDK: Current commit        |")
            print("==============================")
            subprocess.check_call(["git", "branch", "-v"], cwd=sdk_path)

            print("==============================")
            print("| Submodules: Current commit |")
            print("==============================")
            subprocess.check_call(["git", "submodule", "status", "--recursive"], cwd=sdk_path)

            print("==============================")
            print("| SDK: Modified files        |")
            print("==============================")
            subprocess.check_call(["git", "status", "--short"], cwd=sdk_path)

            print("==============================")
            print("| Submodules: Modified files |")
            print("==============================")
            subprocess.check_call(["git", "submodule", "foreach", "--recursive", "git status --short"], cwd=sdk_path)

            print("Done.")

        # Don't block UI
        threading.Thread(target=print_version_info).start()

        return {"FINISHED"}


class ArmAddonInstallButton(bpy.types.Operator):
    """Download and set up Armory SDK"""
    bl_idname = "arm_addon.install"
    bl_label = "Download and set up SDK"
    bl_description = "Download and set up the latest development version"

    def execute(self, context):
        download_sdk(self, context)
        return {"FINISHED"}


class ArmAddonUpdateButton(bpy.types.Operator):
    """Update Armory SDK"""
    bl_idname = "arm_addon.update"
    bl_label = "Update SDK"
    bl_description = "Update to the latest development version"

    def execute(self, context):
        download_sdk(self, context)
        return {"FINISHED"}


def download_sdk(self: bpy.types.Operator, context):
    global update_error_msg
    update_error_msg = ''

    sdk_path = get_sdk_path(context)
    if sdk_path == "":
        self.report({"ERROR"}, "Configure Armory SDK path first")
        return {"CANCELLED"}

    self.report({'INFO'}, 'Downloading Armory SDK, check console for details.')
    print('Armory (current add-on version' + str(bl_info['version']) + '): Cloning SDK repository recursively')
    if not os.path.exists(sdk_path):
        os.makedirs(sdk_path)
    if not git_test(self):
        return {"CANCELLED"}

    preferences = context.preferences
    addon_prefs = preferences.addons["armory"].preferences

    def done(failed: bool):
        if failed:
            self.report({"ERROR"}, "Failed updating the SDK submodules, check console for details.")
        else:
            update_armory_py(sdk_path)
            print('Armory SDK download completed, please restart Blender..')

    def done_clone(failed: bool):
        if failed:
            self.report({"ERROR"}, "Failed downloading Armory SDK, check console for details.")
            return

        if addon_prefs.update_submodules:
            if not git_test(self, (2, 34, 0)):
                # For some unknown (and seemingly not fixable) reason, git submodule update --remote
                # fails in earlier versions of Git with "fatal: Needed a single revision"
                done(True)
            else:
                prev_cwd = os.getcwd()
                os.chdir(sdk_path)
                run_proc(['git', 'submodule', 'update', '--remote', '--depth', '1', '--jobs', '4'], done)
                os.chdir(prev_cwd)
        else:
            done(False)

    git_clone(done_clone, sdk_path, 'armory3d/armsdk', '', recursive=True)


class ArmAddonRestoreButton(bpy.types.Operator):
    """Update Armory SDK"""
    bl_idname = "arm_addon.restore"
    bl_label = "Restore SDK"
    bl_description = "Restore stable version"

    def execute(self, context):
        sdk_path = get_sdk_path(context)
        if sdk_path == "":
            self.report({"ERROR"}, "Configure Armory SDK path first")
            return {"CANCELLED"}
        restore_repo(sdk_path, '')
        self.report({'INFO'}, 'Restored stable version')
        return {"FINISHED"}


class ArmAddonHelpButton(bpy.types.Operator):
    """Updater help"""
    bl_idname = "arm_addon.help"
    bl_label = "Help"
    bl_description = "Git is required for Armory Updater to work"

    def execute(self, context):
        webbrowser.open('https://github.com/armory3d/armory/wiki/gitversion')
        return {"FINISHED"}


def update_armory_py(sdk_path: str, force_relink=False):
    """Ensure that armory.py is up to date by copying it from the
    current SDK path (if 'use_armory_py_symlink' is true, a symlink is
    created instead). Note that because the current version of armory.py
    is already loaded as a Python module, this change lags one add-on
    reload behind.
    """
    addon_prefs = ArmoryAddonPreferences.get_prefs()
    arm_module_file = Path(sys.modules['armory'].__file__)

    if addon_prefs.use_armory_py_symlink:
        if not arm_module_file.is_symlink() or force_relink:
            arm_module_file.unlink(missing_ok=True)
            try:
                arm_module_file.symlink_to(Path(sdk_path) / 'armory.py')
            except OSError as err:
                if hasattr(err, 'winerror'):
                    if err.winerror == 1314:  # ERROR_PRIVILEGE_NOT_HELD
                        # Manually copy the file to "simulate" symlink
                        shutil.copy(Path(sdk_path) / 'armory.py', arm_module_file)
                    else:
                        raise err
                else:
                    raise err
    else:
        arm_module_file.unlink(missing_ok=True)
        shutil.copy(Path(sdk_path) / 'armory.py', arm_module_file)


def start_armory(sdk_path: str):
    global is_running
    global last_scripts_path
    global last_sdk_path

    if sdk_path == "":
        return

    armory_path = os.path.join(sdk_path, "armory")
    if not os.path.exists(armory_path):
        print("Armory load error: 'armory' folder not found in SDK path."
              " Please make sure the SDK path is correct or that the SDK"
              " was downloaded correctly.")
        return

    apply_unix_permissions(sdk_path)

    scripts_path = os.path.join(armory_path, "blender")
    sys.path.append(scripts_path)
    last_scripts_path = scripts_path

    update_armory_py(sdk_path, force_relink=True)

    import start
    if last_sdk_path != "":
        import importlib
        start = importlib.reload(start)

    use_local_sdk = (sdk_source == SDKSource.LOCAL)
    start.register(local_sdk=use_local_sdk)

    last_sdk_path = sdk_path
    is_running = True

    print(f'Running Armory SDK from {sdk_path}')


def stop_armory():
    global is_running

    if not is_running:
        return

    import start
    start.unregister()

    sys.path.remove(last_scripts_path)
    is_running = False


def restart_armory(context):
    old_sdk_source = sdk_source
    sdk_path = get_sdk_path(context)

    if sdk_path == "":
        if not is_running:
            print("Configure Armory SDK path first")
        stop_armory()
        return

    # Only restart Armory when the SDK path changed or it isn't running,
    # otherwise we can keep the currently running instance
    if not same_path(last_sdk_path, sdk_path) or sdk_source != old_sdk_source or not is_running:
        stop_armory()
        assert not is_running
        start_armory(sdk_path)


@persistent
def on_load_post(context):
    restart_armory(bpy.context)  # context is None, use bpy.context instead


def on_register_post():
    detect_sdk_path()
    restart_armory(bpy.context)


def register():
    bpy.utils.register_class(ArmoryAddonPreferences)
    bpy.utils.register_class(ArmAddonPrintVersionInfoButton)
    bpy.utils.register_class(ArmAddonInstallButton)
    bpy.utils.register_class(ArmAddonUpdateButton)
    bpy.utils.register_class(ArmAddonRestoreButton)
    bpy.utils.register_class(ArmAddonHelpButton)
    bpy.app.handlers.load_post.append(on_load_post)

    # Hack to avoid _RestrictContext
    bpy.app.timers.register(on_register_post, first_interval=0.01)


def unregister():
    stop_armory()
    bpy.utils.unregister_class(ArmoryAddonPreferences)
    bpy.utils.unregister_class(ArmAddonInstallButton)
    bpy.utils.unregister_class(ArmAddonPrintVersionInfoButton)
    bpy.utils.unregister_class(ArmAddonUpdateButton)
    bpy.utils.unregister_class(ArmAddonRestoreButton)
    bpy.utils.unregister_class(ArmAddonHelpButton)
    bpy.app.handlers.load_post.remove(on_load_post)


if __name__ == "__main__":
    register()
