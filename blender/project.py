import os
import sys
import shutil
import bpy
import platform
import json
from bpy.props import *
import subprocess
import threading
import webbrowser
import write_data
import nodes_logic
import nodes_renderpath
import nodes_world
import path_tracer
from exporter import ArmoryExporter
import lib.make_resources
import lib.make_variants
import utils
import assets

def init_armory_props():
    # First run
    wrd = bpy.data.worlds[0]
    if wrd.ArmVersion == '':
        wrd.use_fake_user = True # Store data in worlds[0], add fake user to keep it alive
        wrd.ArmVersion = '16.8'
        # Take blend file name
        wrd.ArmProjectName = bpy.path.basename(bpy.context.blend_data.filepath).rsplit('.')[0]
        wrd.ArmProjectScene = bpy.data.scenes[0].name
        # Switch to Cycles
        if bpy.data.scenes[0].render.engine == 'BLENDER_RENDER':
            for scene in bpy.data.scenes:
                scene.render.engine = 'CYCLES'
        # Use nodes
        for w in bpy.data.worlds:
            w.use_nodes = True
        for s in bpy.data.scenes:
            s.use_nodes = True
        for l in bpy.data.lamps:
            l.use_nodes = True
        for m in bpy.data.materials:
            m.use_nodes = True
    utils.fetch_script_names()

# Play button in 3D View panel
def draw_play_item(self, context):
    layout = self.layout
    if play_project.playproc == None and play_project.compileproc == None:
        layout.operator("arm.play_in_viewport")
    else:
        layout.operator("arm.stop")

# Info panel in header
def draw_info_item(self, context):
    layout = self.layout
    layout.label(ArmoryProjectPanel.info_text)

# Menu in render region
class ArmoryProjectPanel(bpy.types.Panel):
    bl_label = "Armory Project"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    info_text = 'Ready'
 
    def draw(self, context):
        layout = self.layout
        wrd = bpy.data.worlds[0]
        layout.prop_search(wrd, "ArmProjectScene", bpy.data, "scenes", "Start Scene")
        layout.prop(wrd, 'ArmProjectName')
        layout.prop(wrd, 'ArmProjectPackage')
        row = layout.row()
        row.prop(wrd, 'ArmProjectWidth')
        row.prop(wrd, 'ArmProjectHeight')
        layout.prop(wrd, 'ArmProjectSamplesPerPixel')
        layout.prop(wrd, 'ArmPhysics')
        layout.operator("arm.kode")

class ArmoryBuildPanel(bpy.types.Panel):
    bl_label = "Armory Build"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
 
    def draw(self, context):
        layout = self.layout
        wrd = bpy.data.worlds[0]
        layout.prop(wrd, 'ArmProjectTarget')
        layout.operator("arm.build")
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("arm.folder")
        row.operator("arm.clean")
        layout.prop_search(wrd, "ArmKhafile", bpy.data, "texts", "Khafile")
        layout.prop(wrd, 'ArmCacheShaders')
        layout.prop(wrd, 'ArmMinimize')
        layout.prop(wrd, 'ArmOptimizeGeometry')
        layout.prop(wrd, 'ArmSampledAnimation')
        layout.prop(wrd, 'ArmDeinterleavedBuffers')

class ArmoryPlayPanel(bpy.types.Panel):
    bl_label = "Armory Play"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
 
    def draw(self, context):
        layout = self.layout
        wrd = bpy.data.worlds[0]
        layout.operator("arm.play")
        layout.prop(wrd, 'ArmPlayRuntime')
        layout.prop(wrd, 'ArmPlayViewportCamera')
        if wrd.ArmPlayViewportCamera:
            layout.prop(wrd, 'ArmPlayViewportNavigation')

        layout.prop(wrd, 'ArmPlayConsole')
        layout.prop(wrd, 'ArmPlayDeveloperTools')

def get_export_scene_override(scene):
    # None for now
    override = {
        'window': None,
        'screen': None,
        'area': None,
        'region': None,
        'edit_object': None,
        'scene': scene}
    return override

def compile_shader(raw_path, shader_name, defs):
    os.chdir(raw_path + './' + shader_name)
    fp = os.path.relpath(utils.get_fp())
    lib.make_resources.make(shader_name + '.shader.json', fp, bpy.data.worlds[0].ArmMinimize, defs)
    lib.make_variants.make(shader_name + '.shader.json', fp, defs)

def def_strings_to_array(strdefs):
    defs = strdefs.split('_')
    defs = defs[1:]
    defs = ['_' + d for d in defs] # Restore _
    return defs

def export_game_data(fp, sdk_path):
    raw_path = sdk_path + 'armory/raw/'
    assets_path = sdk_path + 'armory/Assets/'

    shader_references = []
    # shader_references_defs = [] # Defs to go with referenced shaders
    asset_references = []
    assets.reset()

    # Build node trees
    # TODO: cache
    nodes_logic.buildNodeTrees()
    world_outputs = nodes_world.buildNodeTrees()
    linked_assets = nodes_renderpath.buildNodeTrees(shader_references, asset_references, assets_path)
    for wout in world_outputs:
        nodes_world.write_output(wout, asset_references, shader_references)

    # TODO: Set armatures to center of world so skin transform is zero
    armatures = []
    for o in bpy.data.objects:
        if o.type == 'ARMATURE':
            a = {}
            a['armature'] = o
            a['x'] = o.location.x
            a['y'] = o.location.y
            a['z'] = o.location.z
            armatures.append(a)
            o.location.x = 0
            o.location.y = 0
            o.location.z = 0

    # Export scene data
    for scene in bpy.data.scenes:
        if scene.game_export:
            asset_path = 'compiled/Assets/' + scene.name + '.arm'
            bpy.ops.export_scene.armory(
                get_export_scene_override(scene),
                filepath=asset_path)
            shader_references += ArmoryExporter.shader_references
            asset_references += ArmoryExporter.asset_references
            assets.add(asset_path)

    # Move armatures back
    for a in armatures:
        a['armature'].location.x = a['x']
        a['armature'].location.y = a['y']
        a['armature'].location.z = a['z']
    
    # Clean compiled variants if cache is disabled
    if bpy.data.worlds[0].ArmCacheShaders == False:
        if os.path.isdir('build/html5-resources'):
            shutil.rmtree('build/html5-resources')
        if os.path.isdir('compiled/Shaders'):
            shutil.rmtree('compiled/Shaders')
        if os.path.isdir('compiled/ShaderResources'):
            shutil.rmtree('compiled/ShaderResources')
    # Remove shader resources if shaders were deleted
    elif os.path.isdir('compiled/Shaders') == False and os.path.isdir('compiled/ShaderResources') == True:
        shutil.rmtree('compiled/ShaderResources')
    
    # Write referenced shader variants
    # Assume asset_references contains shader resources only for now
    for ref in asset_references:
        # Resource does not exist yet
        os.chdir(fp)
        if not os.path.exists(ref):
            shader_name = ref.split('/')[2]
            strdefs = ref[:-4] # Remove '.arm' extension
            defs = strdefs.split(shader_name) # 'name/name_def_def'
            if len(defs) > 2:
                strdefs = defs[2] # Appended defs
                defs = def_strings_to_array(strdefs)
            else:
                defs = []
            compile_shader(raw_path, shader_name, defs)
            # for i in range(0, len(defs)):
                # defs[i] += '=1'
            # shader_references_defs.append(defs)
    
    # After defs has been parsed, add linked assets from shader resources
    asset_references += linked_assets
    # Reset path
    os.chdir(fp)

    # Write compiled.glsl
    clip_start = bpy.data.cameras[0].clip_start # Same clip values for all cameras for now
    clip_end = bpy.data.cameras[0].clip_end
    shadowmap_size = bpy.data.worlds[0].shadowmap_size
    write_data.write_compiledglsl(clip_start, clip_end, shadowmap_size)

    # Write khafile.js
    write_data.write_khafilejs(shader_references, asset_references)

    # Write Main.hx
    write_data.write_main()

def print_info(text):
    ArmoryProjectPanel.info_text = text
    # for area in bpy.context.screen.areas:
        # if area.type == 'INFO':
            # area.tag_redraw()

def compile_project(self, target_name=None):
    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons['armory'].preferences
    sdk_path = addon_prefs.sdk_path

    # Set build command
    if target_name == None:
        target_name = bpy.data.worlds[0].ArmProjectTarget

    # Copy ammo.js if necessary
    if target_name == 'html5' and bpy.data.worlds[0].ArmPhysics == 'Bullet':
        ammojs_path = sdk_path + '/haxebullet/js/ammo/ammo.js'
        if not os.path.isfile('build/html5/ammo.js'):
            shutil.copy(ammojs_path, 'build/html5')
        if not os.path.isfile('build/debug-html5/ammo.js'):
            shutil.copy(ammojs_path, 'build/debug-html5')

    if utils.get_os() == 'win':
        node_path = sdk_path + '/nodejs/node.exe'
        khamake_path = sdk_path + '/kode_studio/KodeStudio-win32/resources/app/extensions/kha/Kha/make'
    elif utils.get_os() == 'mac':
        node_path = sdk_path + '/nodejs/node-osx'
        khamake_path = sdk_path + '/kode_studio/Kode Studio.app/Contents/Resources/app/extensions/kha/Kha/make'
    else:
        node_path = sdk_path + '/nodejs/node-linux64'
        khamake_path = sdk_path + '/kode_studio/KodeStudio-linux64/resources/app/extensions/kha/Kha/make'
    
    cmd = [node_path, khamake_path, target_name, '--glsl2']
    # print_info("Building, see console...")
    return subprocess.Popen(cmd)

def build_project(self):
    # Save blend
    bpy.ops.wm.save_mainfile()
    
    # Get paths
    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons['armory'].preferences
    sdk_path = addon_prefs.sdk_path
    raw_path = sdk_path + '/armory/raw/'
    
    # Set dir
    s = bpy.data.filepath.split(os.path.sep)
    name = s.pop()
    name = name.split(".")
    name = name[0]
    fp = os.path.sep.join(s)
    os.chdir(fp)

    # Create directories
    if not os.path.exists('Sources'):
        os.makedirs('Sources')
    if not os.path.exists('Assets'):
        os.makedirs('Assets')
    if not os.path.isdir('build/html5'):
        os.makedirs('build/html5')
    if not os.path.isdir('build/debug-html5'):
        os.makedirs('build/debug-html5')

    # Compile path tracer shaders
    if len(bpy.data.cameras) > 0 and bpy.data.cameras[0].pipeline_path == 'pathtrace_path':
        path_tracer.compile(raw_path + 'pt_trace_pass/pt_trace_pass.frag.glsl')

    # Export data
    export_game_data(fp, sdk_path)

def stop_project(self):
    if play_project.playproc != None:
        play_project.playproc.terminate()
        play_project.playproc = None

def watch_play():
    if play_project.playproc == None:
        return
    if play_project.playproc.poll() == None:
        threading.Timer(0.5, watch_play).start()
    else:
        play_project.playproc = None

def watch_compile():
    return_code = play_project.compileproc.poll()
    if return_code == None:
        threading.Timer(0.1, watch_compile).start()
    else:
        play_project.compileproc = None
        if return_code == 0:
            on_compiled()
        else:
            # self.report({'ERROR'}, 'Build failed, check console')
            print('Build failed, check console')

def play_project(self, in_viewport):
    # Build data
    build_project(self)

    if in_viewport == False:
        # Windowed player
        wrd = bpy.data.worlds[0]
        x = 0
        y = 0
        w = wrd.ArmProjectWidth
        h = wrd.ArmProjectHeight
        winoff = 0
    else:
        # Player dimensions
        if utils.get_os() == 'win':
            psize = 1 # Scale in electron
            xoff = 0
            yoff = 6
        elif utils.get_os() == 'mac':
            psize = bpy.context.user_preferences.system.pixel_size
            xoff = 5
            yoff = 22
        else:
            psize = 1
            xoff = 0
            yoff = 6

        x = bpy.context.window.x + (bpy.context.area.x - xoff) / psize
        y = bpy.context.window.height + 45 - (bpy.context.area.y + bpy.context.area.height) / psize
        w = (bpy.context.area.width + xoff) / psize
        h = (bpy.context.area.height) / psize - 25
        winoff = bpy.context.window.y + bpy.context.window.height + yoff

    write_data.write_electronjs(x, y, w, h, winoff, in_viewport)
    write_data.write_indexhtml(w, h, in_viewport)

    # Compile
    play_project.compileproc = compile_project(self, target_name='html5')
    watch_compile()

def on_compiled():
    print_info("Ready")
    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons['armory'].preferences
    sdk_path = addon_prefs.sdk_path
    electron_app_path = './build/electron.js'

    if utils.get_os() == 'win':
        electron_path = sdk_path + 'kode_studio/KodeStudio-win32/Kode Studio.exe'
    elif utils.get_os() == 'mac':
        # electron_path = sdk_path + 'kode_studio/Kode Studio.app/Contents/MacOS/Electron'
        electron_path = sdk_path + 'kode_studio/Electron.app/Contents/MacOS/Electron'
    else:
        electron_path = sdk_path + 'kode_studio/KodeStudio-linux64/kodestudio'

    play_project.playproc = subprocess.Popen([electron_path, '--chromedebug', '--remote-debugging-port=9222', electron_app_path])
    watch_play()
play_project.playproc = None
play_project.compileproc = None

def clean_project(self):
    os.chdir(utils.get_fp())
    
    # Remove build data
    if os.path.isdir('build'):
        shutil.rmtree('build')

    # Remove generated assets and shader variants
    if os.path.isdir('compiled'):
        shutil.rmtree('compiled')

    # Remove compiled nodes
    nodes_path = 'Sources/' + bpy.data.worlds[0].ArmProjectPackage.replace('.', '/') + '/node/'
    if os.path.isdir(nodes_path):
        shutil.rmtree(nodes_path)

    # Remove khafile/korefile
    if os.path.isfile('khafile.js'):
        os.remove('khafile.js')
    if os.path.isfile('korefile.js'):
        os.remove('korefile.js')

    self.report({'INFO'}, 'Done')

class ArmoryPlayButton(bpy.types.Operator):
    bl_idname = 'arm.play'
    bl_label = 'Play'
 
    def execute(self, context):
        play_project(self, False)
        return{'FINISHED'}

class ArmoryPlayInViewportButton(bpy.types.Operator):
    bl_idname = 'arm.play_in_viewport'
    bl_label = 'Play in Viewport'
 
    def execute(self, context):
        # Cancel viewport render
        for space in context.area.spaces:
            if space.type == 'VIEW_3D':
                if space.viewport_shade == 'RENDERED':
                    space.viewport_shade = 'SOLID'
                break
        play_project(self, True)
        return{'FINISHED'}

class ArmoryStopButton(bpy.types.Operator):
    bl_idname = 'arm.stop'
    bl_label = 'Stop'
 
    def execute(self, context):
        stop_project(self)
        return{'FINISHED'}

class ArmoryBuildButton(bpy.types.Operator):
    bl_idname = 'arm.build'
    bl_label = 'Build'
 
    def execute(self, context):
        build_project(self)
        compile_project(self)
        return{'FINISHED'}

class ArmoryFolderButton(bpy.types.Operator):
    bl_idname = 'arm.folder'
    bl_label = 'Project Folder'
 
    def execute(self, context):
        webbrowser.open('file://' + utils.get_fp())
        return{'FINISHED'}

class ArmoryKodeButton(bpy.types.Operator):
    bl_idname = 'arm.kode'
    bl_label = 'Open in Kode Studio'
 
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

        subprocess.Popen([kode_path, utils.get_fp()], shell=True)

        return{'FINISHED'}

class ArmoryCleanButton(bpy.types.Operator):
    bl_idname = 'arm.clean'
    bl_label = 'Clean Project'
 
    def execute(self, context):
        clean_project(self)
        return{'FINISHED'}

# Registration
arm_keymaps = []
def register():
    bpy.utils.register_module(__name__)
    init_armory_props()
    # Key shortcuts
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Window', space_type='EMPTY', region_type="WINDOW")
    km.keymap_items.new(ArmoryPlayInViewportButton.bl_idname, type='B', value='PRESS', ctrl=True, shift=True)
    km.keymap_items.new(ArmoryPlayButton.bl_idname, type='F5', value='PRESS')
    arm_keymaps.append(km)
    bpy.types.VIEW3D_HT_header.append(draw_play_item)
    bpy.types.INFO_HT_header.prepend(draw_info_item)

def unregister():
    bpy.types.VIEW3D_HT_header.remove(draw_play_item)
    bpy.types.INFO_HT_header.remove(draw_info_item)
    bpy.utils.unregister_module(__name__)
    wm = bpy.context.window_manager
    for km in arm_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    del arm_keymaps[:]
