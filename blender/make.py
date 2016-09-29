import os
import sys
import shutil
import bpy
import platform
import json
from bpy.props import *
from props import *
import subprocess
import threading
import webbrowser
import write_data
import make_logic
import make_renderpath
import make_world
import path_tracer
from exporter import ArmoryExporter
import lib.make_datas
import lib.make_variants
import utils
import assets
# Server
import http.server
import socketserver
import space_armory
try:
    import bgame
except ImportError:
    pass

def init_armory_props():
    # First run
    if not 'Arm' in bpy.data.worlds:
        wrd = bpy.data.worlds.new('Arm')
        wrd.use_fake_user = True # Store data world object, add fake user to keep it alive
        wrd.ArmVersion = '16.9'
        # Take blend file name
        wrd.ArmProjectName = bpy.path.basename(bpy.context.blend_data.filepath).rsplit('.')[0]
        wrd.ArmProjectScene = bpy.data.scenes[0].name
        # Switch to Cycles
        for scene in bpy.data.scenes:
            if scene.render.engine != 'CYCLES':
                scene.render.engine = 'CYCLES'
            scene.render.fps = 60 # Default to 60fps for chromium update loop
        # Force camera far to at least 200 units for now, to prevent fighting with light far plane
        for c in bpy.data.cameras:
            if c.clip_end < 200:
                c.clip_end = 200
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
    # Path for embedded player
    if utils.with_chromium():
        bgame.set_url('file://' + utils.get_fp() + '/build/html5/index.html')

def get_export_scene_override(scene):
    # None for now
    override = {
        'window': None,
        'screen': None,
        'area': None,
        'region': None,
        'edit_object': None,
        'blend_data': None, # For live patching
        'scene': scene}
    return override

def compile_shader(raw_path, shader_name, defs):
    os.chdir(raw_path + './' + shader_name)
    fp = os.path.relpath(utils.get_fp())
    lib.make_datas.make(shader_name + '.shader.json', fp, defs)
    lib.make_variants.make(shader_name + '.shader.json', fp, defs)

def def_strings_to_array(strdefs):
    defs = strdefs.split('_')
    defs = defs[1:]
    defs = ['_' + d for d in defs] # Restore _
    return defs

def export_data(fp, sdk_path, is_play=False):
    raw_path = sdk_path + 'armory/raw/'
    assets_path = sdk_path + 'armory/Assets/'
    export_physics = bpy.data.worlds['Arm'].ArmPhysics != 'Disabled'
    assets.reset()

    # Build node trees
    # TODO: cache
    make_logic.buildNodeTrees()
    active_worlds = set()
    for scene in bpy.data.scenes:
        if scene.game_export and scene.world != None and scene.world.name != 'Arm':
            active_worlds.add(scene.world)
    world_outputs = make_world.buildNodeTrees(active_worlds)
    make_renderpath.buildNodeTrees(assets_path)
    for wout in world_outputs:
        make_world.write_output(wout)

    # Export scene data
    assets.embedded_data = sorted(list(set(assets.embedded_data)))
    physics_found = False
    for scene in bpy.data.scenes:
        if scene.game_export:
            asset_path = 'build/compiled/Assets/' + utils.safe_filename(scene.name) + '.arm'
            bpy.ops.export_scene.armory(
                get_export_scene_override(scene),
                filepath=asset_path)
            if physics_found == False and ArmoryExporter.export_physics:
                physics_found = True
            assets.add(asset_path)
    
    if physics_found == False: # Disable physics anyway if no rigid body exported
        export_physics = False
    
    # Clean compiled variants if cache is disabled
    if bpy.data.worlds['Arm'].ArmCacheShaders == False:
        if os.path.isdir('build/html5-resources'):
            shutil.rmtree('build/html5-resources')
        if os.path.isdir('build/compiled/Shaders'):
            shutil.rmtree('build/compiled/Shaders')
        if os.path.isdir('build/compiled/ShaderDatas'):
            shutil.rmtree('build/compiled/ShaderDatas')
    # Remove shader datas if shaders were deleted
    elif os.path.isdir('build/compiled/Shaders') == False and os.path.isdir('build/compiled/ShaderDatas') == True:
        shutil.rmtree('build/compiled/ShaderDatas')
    
    # Write referenced shader variants
    for ref in assets.shader_datas:
        # Data does not exist yet
        if not os.path.isfile(fp + '/' + ref):
            shader_name = ref.split('/')[3] # Extract from 'build/compiled/...'
            strdefs = ref[:-4] # Remove '.arm' extension
            defs = strdefs.split(shader_name) # 'name/name_def_def'
            if len(defs) > 2:
                strdefs = defs[2] # Appended defs
                defs = def_strings_to_array(strdefs)
            else:
                defs = []
            compile_shader(raw_path, shader_name, defs)
    
    # Reset path
    os.chdir(fp)

    # Write compiled.glsl
    write_data.write_compiledglsl()

    # Write khafile.js
    write_data.write_khafilejs(is_play, export_physics)

    # Write Main.hx
    write_data.write_main(is_play, play_project.in_viewport)

    # Copy ammo.js if necessary
    #if target_name == 'html5':
    if export_physics and bpy.data.worlds['Arm'].ArmPhysics == 'Bullet':
        ammojs_path = sdk_path + '/lib/haxebullet/js/ammo/ammo.js'
        if not os.path.isfile('build/html5/ammo.js'):
            shutil.copy(ammojs_path, 'build/html5')
        if not os.path.isfile('build/debug-html5/ammo.js'):
            shutil.copy(ammojs_path, 'build/debug-html5')

def armory_log(text=None):
    if text == None:
        text = ''
    print(text)
    text = (text[:80] + '..') if len(text) > 80 else text # Limit str size
    ArmoryProjectPanel.info_text = text
    armory_log.tag_redraw = True    
armory_log.tag_redraw = False

def armory_progress(value):
    ArmoryProjectPanel.progress = value
    armory_log.tag_redraw = True 

def armory_space_log(text=None):
    if text == None:
        text = ''
    print(text)
    text = (text[:80] + '..') if len(text) > 80 else text # Limit str size
    space_armory.SPACEARMORY_HT_header.info_text = text

def get_kha_target(target_name): # TODO: remove
    if target_name == 'macos':
        return 'osx'
    return target_name

def compile_project(target_name=None, is_publish=False, watch=False):
    sdk_path =  utils.get_sdk_path()
    ffmpeg_path = utils.get_ffmpeg_path()

    # Set build command
    if target_name == None:
        target_name = bpy.data.worlds['Arm'].ArmProjectTarget

    if utils.get_os() == 'win':
        node_path = sdk_path + '/nodejs/node.exe'
        khamake_path = sdk_path + '/kode_studio/KodeStudio-win32/resources/app/extensions/kha/Kha/make'
    elif utils.get_os() == 'mac':
        node_path = sdk_path + '/nodejs/node-osx'
        khamake_path = sdk_path + '/kode_studio/Kode Studio.app/Contents/Resources/app/extensions/kha/Kha/make'
    else:
        node_path = sdk_path + '/nodejs/node-linux64'
        khamake_path = sdk_path + '/kode_studio/KodeStudio-linux64/resources/app/extensions/kha/Kha/make'
    
    kha_target_name = get_kha_target(target_name)
    cmd = [node_path, khamake_path, kha_target_name]

    if ffmpeg_path != '':
        cmd.append('--ffmpeg')
        cmd.append('"' + ffmpeg_path + '"')

    # armory_log("Building, see console...")

    if make.play_project.chromium_running:
        if play_project.compileproc == None: # Already compiling
            # Patch running game, stay silent, disable krafix and haxe
            # cmd.append('--silent')
            cmd.append('--noproject')
            cmd.append('--haxe')
            cmd.append('""')
            cmd.append('--krafix')
            cmd.append('""')
            # Khamake throws error when krafix is not found, hide for now
            play_project.compileproc = subprocess.Popen(cmd, stderr=subprocess.PIPE)
            threading.Timer(0.1, watch_patch).start()
            return play_project.compileproc
    elif watch == True:
        play_project.compileproc = subprocess.Popen(cmd)
        threading.Timer(0.1, watch_compile, ['build']).start()
        return play_project.compileproc
    else:
        return subprocess.Popen(cmd)

# For live patching
def patch_project():
    sdk_path = utils.get_sdk_path()
    fp = utils.get_fp()
    os.chdir(fp)
    export_data(fp, sdk_path, is_play=True)

def build_project(is_play=False):
    # Clear flag
    play_project.in_viewport = False

    # Save blend
    bpy.ops.wm.save_mainfile()

    # Clean log
    armory_log()
    if utils.with_chromium():
        armory_space_log()

    # Set camera in active scene
    wrd = bpy.data.worlds['Arm']
    active_scene = bpy.context.screen.scene if wrd.ArmPlayActiveScene else bpy.data.scenes[wrd.ArmProjectScene]
    if active_scene.camera == None:
        for o in active_scene.objects:
            if o.type == 'CAMERA':
                active_scene.camera = o
                break

    # Get paths
    sdk_path = utils.get_sdk_path()
    raw_path = sdk_path + '/armory/raw/'
    
    # Set dir
    fp = utils.get_fp()
    os.chdir(fp)

    # Create directories
    if not os.path.exists('Sources'):
        os.makedirs('Sources')
    if not os.path.isdir('build/html5'):
        os.makedirs('build/html5')
    if not os.path.isdir('build/debug-html5'):
        os.makedirs('build/debug-html5')

    # Compile path tracer shaders
    if len(bpy.data.cameras) > 0 and bpy.data.cameras[0].renderpath_path == 'pathtrace_path':
        path_tracer.compile(raw_path + 'pt_trace_pass/pt_trace_pass.frag.glsl')

    # Save external scripts edited inside Blender
    write_texts = False
    for text in bpy.data.texts:
        if text.filepath != '' and text.is_dirty:
            write_texts = True
            break
    if write_texts:
        area = bpy.context.area
        old_type = area.type
        area.type = 'TEXT_EDITOR'
        for text in bpy.data.texts:
            if text.filepath != '' and text.is_dirty:
                area.spaces[0].text = text
                bpy.ops.text.save()
        area.type = old_type

    # Save internal Haxe scripts
    for text in bpy.data.texts:
        if text.filepath == '' and text.name[-3:] == '.hx':
            with open('Sources/' + bpy.data.worlds['Arm'].ArmProjectPackage + '/' + text.name, 'w') as f:
                f.write(text.as_string())

    # Save internal assets

    # Export data
    export_data(fp, sdk_path, is_play=is_play)

    if play_project.playproc == None:
        armory_progress(50)

def stop_project():
    if play_project.playproc != None:
        play_project.playproc.terminate()
        play_project.playproc = None

def watch_play():
    if play_project.playproc == None:
        return
    line = b''
    while play_project.playproc != None and play_project.playproc.poll() == None:
        char = play_project.playproc.stderr.read(1) # Read immediately one by one 
        if char == b'\n':
            msg = str(line).split('"', 1) # Extract message
            if len(msg) > 1:
                trace = msg[1].rsplit('"', 1)[0]
                armory_log(trace)
            line = b''
        else:
            line += char
    play_project.playproc = None
    play_project.playproc_finished = True
    armory_log()

def watch_compile(mode):
    play_project.compileproc.wait()
    armory_progress(100)
    result = play_project.compileproc.poll()
    play_project.compileproc = None
    play_project.compileproc_finished = True
    if result == 0:
        play_project.compileproc_success = True
        on_compiled(mode)
    else:
        play_project.compileproc_success = False
        armory_log('Build failed, check console')

def watch_patch():
    play_project.compileproc.wait()
    result = play_project.compileproc.poll()
    play_project.compileproc = None
    play_project.compileproc_finished = True

def play_project(self, in_viewport):
    if utils.with_chromium() and in_viewport and bpy.context.area.type == 'VIEW_3D':
        play_project.play_area = bpy.context.area

    # Build data
    build_project(is_play=True)
    play_project.in_viewport = in_viewport

    wrd = bpy.data.worlds['Arm']

    if wrd.ArmPlayRuntime == 'Native':
        compile_project(target_name='--run')
    else: # Electron, Browser
        if in_viewport == False:
            # Windowed player
            x = 0
            y = 0
            w, h = utils.get_render_resolution()
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
        play_project.compileproc = compile_project(target_name='html5')
        if in_viewport:
            mode = 'play_viewport'
        else:
            mode = 'play'
        threading.Timer(0.1, watch_compile, [mode]).start()

play_project.in_viewport = False
play_project.playproc = None
play_project.compileproc = None
play_project.playproc_finished = False
play_project.compileproc_finished = False
play_project.compileproc_success = False
play_project.play_area = None
play_project.chromium_running = False
play_project.last_chromium_running = False

def run_server():
    Handler = http.server.SimpleHTTPRequestHandler
    try:
        httpd = socketserver.TCPServer(("", 8040), Handler)
        httpd.serve_forever()
    except:
        print('Server already running')

def on_compiled(mode): # build, play, play_viewport, publish
    armory_log()
    sdk_path = utils.get_sdk_path()

    # Print info
    if mode == 'publish':
        target_name = get_kha_target(bpy.data.worlds['Arm'].ArmPublishTarget)
        print('Project published')
        files_path = utils.get_fp() + '/build/' + target_name
        if target_name == 'html5':
            print('HTML5 files are located in ' + files_path)
        elif target_name == 'ios' or target_name == 'osx': # TODO: to macos
            print('XCode project files are located in ' + files_path + '-build')
        elif target_name == 'windows':
            print('VisualStudio 2015 project files are located in ' + files_path + '-build')
        elif target_name == 'android-native':
            print('Android Studio project files are located in ' + files_path + '-build')
        else:
            print('Makefiles are located in ' + files_path + '-build')
        return

    # Launch project in new window or frameless electron
    elif (mode =='play') or (mode == 'play_viewport' and utils.with_chromium() == False):
        wrd = bpy.data.worlds['Arm']
        if wrd.ArmPlayRuntime == 'Electron':
            electron_app_path = './build/electron.js'

            if utils.get_os() == 'win':
                electron_path = sdk_path + 'kode_studio/KodeStudio-win32/Kode Studio.exe'
            elif utils.get_os() == 'mac':
                # electron_path = sdk_path + 'kode_studio/Kode Studio.app/Contents/MacOS/Electron'
                electron_path = sdk_path + 'kode_studio/Electron.app/Contents/MacOS/Electron'
            else:
                electron_path = sdk_path + 'kode_studio/KodeStudio-linux64/kodestudio'

            play_project.playproc = subprocess.Popen([electron_path, '--chromedebug', '--remote-debugging-port=9222', '--enable-logging', electron_app_path], stderr=subprocess.PIPE)
            watch_play()
        elif wrd.ArmPlayRuntime == 'Browser':
            # Start server
            os.chdir(utils.get_fp())
            t = threading.Thread(name='localserver', target=run_server)
            t.daemon = True
            t.start()
            html5_app_path = 'http://localhost:8040/build/html5'
            webbrowser.open(html5_app_path)


def clean_project():
    os.chdir(utils.get_fp())
    
    wrd = bpy.data.worlds['Arm']

    # Preserve envmaps
    if not wrd.ArmCleanEnvmaps:
        envmaps_path = 'build/compiled/Assets/envmaps'
        if os.path.isdir(envmaps_path):
            shutil.move(envmaps_path, '.')

    # Remove build and compiled data
    if os.path.isdir('build'):
        shutil.rmtree('build')

    # Move envmaps back
    if not wrd.ArmCleanEnvmaps and os.path.isdir('envmaps'):
        os.makedirs('build/compiled/Assets')
        shutil.move('envmaps', 'build/compiled/Assets')

    # Remove compiled nodes
    nodes_path = 'Sources/' + wrd.ArmProjectPackage.replace('.', '/') + '/node/'
    if os.path.isdir(nodes_path):
        shutil.rmtree(nodes_path)

    # Remove khafile/korefile/Main.hx
    if os.path.isfile('khafile.js'):
        os.remove('khafile.js')
    if os.path.isfile('korefile.js'):
        os.remove('korefile.js')
    if os.path.isfile('Sources/Main.hx'):
        os.remove('Sources/Main.hx')

    print('Project cleaned')

def publish_project():
    # Force minimize data
    minimize = bpy.data.worlds['Arm'].ArmMinimize
    bpy.data.worlds['Arm'].ArmMinimize = True
    clean_project()
    build_project()
    play_project.compileproc = compile_project(target_name=bpy.data.worlds['Arm'].ArmPublishTarget, is_publish=True)
    threading.Timer(0.1, watch_compile, ['publish']).start()
    bpy.data.worlds['Arm'].ArmMinimize = minimize

# Registration
def register():
    init_armory_props()

def unregister():
    pass
