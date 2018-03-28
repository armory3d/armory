# Armory 3D Engine
# https://github.com/armory3d/armory
bl_info = {
    "name": "Armory",
    "category": "Render",
    "location": "Properties -> Render -> Armory Player",
    "description": "3D Game Engine for Blender",
    "author": "Armory3D.org",
    "version": (13, 0, 0),
    "blender": (2, 79, 0),
    "wiki_url": "http://armory3d.org/manual",
    "tracker_url": "https://github.com/armory3d/armory/issues"
}

import os
import sys
import stat
import shutil
import webbrowser
import subprocess
import bpy
import platform
from bpy.types import Operator, AddonPreferences
from bpy.props import *
from bpy.app.handlers import persistent

with_krom = False

def get_os():
    s = platform.system()
    if s == 'Windows':
        return 'win'
    elif s == 'Darwin':
        return 'mac'
    else:
        return 'linux'

class ArmoryAddonPreferences(AddonPreferences):
    bl_idname = __name__

    def sdk_path_update(self, context):
        if self.skip_update:
            return
        self.skip_update = True
        self.sdk_path = bpy.path.reduce_dirs([bpy.path.abspath(self.sdk_path)])[0] + '/'

    def ffmpeg_path_update(self, context):
        if self.skip_update:
            return
        self.skip_update = True
        self.ffmpeg_path = bpy.path.reduce_dirs([bpy.path.abspath(self.ffmpeg_path)])[0]

    def renderdoc_path_update(self, context):
        if self.skip_update:
            return
        self.skip_update = True
        self.renderdoc_path = bpy.path.reduce_dirs([bpy.path.abspath(self.renderdoc_path)])[0]

    sdk_bundled = BoolProperty(name="Bundled SDK", default=True)
    sdk_path = StringProperty(name="SDK Path", subtype="FILE_PATH", update=sdk_path_update, default="")
    show_advanced = BoolProperty(name="Show Advanced", default=False)
    player_gapi_win = EnumProperty(
        items = [('opengl', 'Auto', 'opengl'),
                 ('opengl', 'OpenGL', 'opengl'),
                 ('direct3d11', 'Direct3D11', 'direct3d11')],
        name="Player Graphics API", default='opengl', description='Use this graphics API when launching the game in Krom player(F5)')
    player_gapi_linux = EnumProperty(
        items = [('opengl', 'Auto', 'opengl'),
                 ('opengl', 'OpenGL', 'opengl')],
        name="Player Graphics API", default='opengl', description='Use this graphics API when launching the game in Krom player(F5)')
    player_gapi_mac = EnumProperty(
        items = [('opengl', 'Auto', 'opengl'),
                 ('opengl', 'OpenGL', 'opengl')],
        name="Player Graphics API", default='opengl', description='Use this graphics API when launching the game in Krom player(F5)')
    code_editor = EnumProperty(
        items = [('kodestudio', 'Kode Studio', 'kodestudio'),
                 ('default', 'System Default', 'default')],
        name="Code Editor", default='kodestudio', description='Use this editor for editing scripts')
    ui_scale = FloatProperty(name='UI Scale', description='Adjust UI scale for Armory tools', default=1.0, min=1.0, max=4.0)
    renderdoc_path = StringProperty(name="RenderDoc Path", description="Binary path", subtype="FILE_PATH", update=renderdoc_path_update, default="")
    ffmpeg_path = StringProperty(name="FFMPEG Path", description="Binary path", subtype="FILE_PATH", update=ffmpeg_path_update, default="")
    save_on_build = BoolProperty(name="Save on Build", description="Save .blend", default=True)
    legacy_shaders = BoolProperty(name="Legacy Shaders", description="Attempt to compile shaders runnable on older hardware", default=False)
    viewport_controls = EnumProperty(
        items=[('qwerty', 'qwerty', 'qwerty'),
               ('azerty', 'azerty', 'azerty')],
        name="Viewport Controls", default='qwerty', description='Viewport camera mode controls')
    skip_update = BoolProperty(name="", default=False)

    def draw(self, context):
        global with_krom
        self.skip_update = False
        layout = self.layout
        layout.label(text="Welcome to Armory! Click 'Save User Settings' at the bottom to keep Armory enabled.")
        if with_krom:
            layout.prop(self, "sdk_bundled")
            if not self.sdk_bundled:
                layout.prop(self, "sdk_path")
        else:
            layout.prop(self, "sdk_path")
        layout.prop(self, "show_advanced")
        if self.show_advanced:
            box = layout.box().column()
            box.prop(self, "player_gapi_" + get_os())
            box.prop(self, "code_editor")
            box.prop(self, "renderdoc_path")
            box.prop(self, "ffmpeg_path")
            box.prop(self, "viewport_controls")
            box.prop(self, "ui_scale")
            box.prop(self, "save_on_build")
            box.prop(self, "legacy_shaders")
            
            box = layout.box().column()
            box.label("Armory Updater")
            box.label("Note: Development version may run unstable!")
            row = box.row(align=True)
            row.alignment = 'EXPAND'
            row.operator("arm_addon.install_git", icon="URL")
            row.operator("arm_addon.update", icon="FILE_REFRESH")
            row.operator("arm_addon.restore")
            box.label("Please restart Blender after successful SDK update.")

def get_sdk_path(context):
    global with_krom
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons["armory"].preferences
    if with_krom and addon_prefs.sdk_bundled:
        if get_os() == 'mac':
            # SDK on MacOS is located in .app folder due to security
            p = bpy.app.binary_path
            if p.endswith('Contents/MacOS/blender'):
                return p[:-len('Contents/MacOS/blender')] + '/armsdk/'
            else:
                return p[:-len('Contents/MacOS/./blender')] + '/armsdk/'
        elif get_os() == 'linux':
            # /blender
            return bpy.app.binary_path.rsplit('/', 1)[0] + '/armsdk/'
        else:
            # /blender.exe
            return bpy.app.binary_path.replace('\\', '/').rsplit('/', 1)[0] + '/armsdk/'
    else:
        return addon_prefs.sdk_path

def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def update_repo(p, n, gitn = ''):
    if gitn == '':
        gitn = n
    if not os.path.exists(p + '/' + n + '_backup'):
        os.rename(p + '/' + n, p + '/' + n + '_backup')
    if os.path.exists(p + '/' + n):
        shutil.rmtree(p + '/' + n, onerror=remove_readonly)
    subprocess.Popen(['git', 'clone', 'https://github.com/armory3d/' + gitn, p + '/' + n, '--depth=1'])

def restore_repo(p, n):
    if os.path.exists(p + '/' + n + '_backup'):
        if os.path.exists(p + '/' + n):
            shutil.rmtree(p + '/' + n, onerror=remove_readonly)
        os.rename(p + '/' + n + '_backup', p + '/' + n)

class ArmAddonStartButton(bpy.types.Operator):
    '''Start Armory integration'''
    bl_idname = "arm_addon.start"
    bl_label = "Start"
    running = False
    play_in_viewport = False

    def execute(self, context):
        sdk_path = get_sdk_path(context)
        if sdk_path == "":
            self.report({"ERROR"}, "Configure SDK path first")
            return {"CANCELLED"}

        scripts_path = sdk_path + "/armory/blender/"
        sys.path.append(scripts_path)
        import start
        start.register()
        ArmAddonStartButton.running = True

        if not hasattr(bpy.app.handlers, 'scene_update_post'): # 2.8
            bpy.types.VIEW3D_HT_header.remove(draw_view3d_header)

        return {"FINISHED"}

class ArmAddonStopButton(bpy.types.Operator):
    '''Stop Armory integration'''
    bl_idname = "arm_addon.stop"
    bl_label = "Stop"
 
    def execute(self, context):
        import start
        start.unregister()
        ArmAddonStartButton.running = False
        return {"FINISHED"}

class ArmAddonUpdateButton(bpy.types.Operator):
    '''Update Armory SDK'''
    bl_idname = "arm_addon.update"
    bl_label = "Update SDK"
    bl_description = "Update to the latest development version"
 
    def execute(self, context):
        p = get_sdk_path(context)
        if p == "":
            self.report({"ERROR"}, "Configure SDK path first")
            return {"CANCELLED"}
        self.report({'INFO'}, 'Updating, check console for details. Please restart Blender after successful SDK update.')
        print('Armory (add-on v' + str(bl_info['version']) + '): Cloning [armory, iron, haxebullet, haxerecast, zui] repositories')
        os.chdir(p)
        update_repo(p, 'armory')
        update_repo(p, 'iron')
        update_repo(p, 'lib/haxebullet', 'haxebullet')
        update_repo(p, 'lib/haxerecast', 'haxerecast')
        update_repo(p, 'lib/zui', 'zui')
        update_repo(p, 'lib/armory_tools', 'armory_tools')
        update_repo(p, 'lib/iron_format', 'iron_format')
        return {"FINISHED"}

class ArmAddonRestoreButton(bpy.types.Operator):
    '''Update Armory SDK'''
    bl_idname = "arm_addon.restore"
    bl_label = "Restore SDK"
    bl_description = "Restore stable version"
 
    def execute(self, context):
        p = get_sdk_path(context)
        if p == "":
            self.report({"ERROR"}, "Configure SDK path first")
            return {"CANCELLED"}
        os.chdir(p)
        restore_repo(p, 'armory')
        restore_repo(p, 'iron')
        restore_repo(p, 'lib/haxebullet')
        restore_repo(p, 'lib/haxerecast')
        restore_repo(p, 'lib/zui')
        restore_repo(p, 'lib/armory_tools')
        restore_repo(p, 'lib/iron_format')
        self.report({'INFO'}, 'Restored stable version')
        return {"FINISHED"}

class ArmAddonInstallGitButton(bpy.types.Operator):
    '''Install Git'''
    bl_idname = "arm_addon.install_git"
    bl_label = "Install Git"
    bl_description = "Git is required for Armory Updater to work"
 
    def execute(self, context):
        webbrowser.open('https://git-scm.com')
        return {"FINISHED"}

@persistent
def on_scene_update_post(scene):
    if hasattr(bpy.app.handlers, 'scene_update_post'):
        bpy.app.handlers.scene_update_post.remove(on_scene_update_post)
    bpy.ops.arm_addon.start()

def draw_view3d_header(self, context):
    layout = self.layout
    layout.operator("arm_addon.start")

def register():
    global with_krom
    import importlib.util
    if importlib.util.find_spec('barmory') != None:
        with_krom = True
    bpy.utils.register_module(__name__)
    if hasattr(bpy.app.handlers, 'scene_update_post'):
        bpy.app.handlers.scene_update_post.append(on_scene_update_post)
    else: # 2.8
        bpy.types.VIEW3D_HT_header.append(draw_view3d_header)

def unregister():
    bpy.ops.arm_addon.stop()
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
