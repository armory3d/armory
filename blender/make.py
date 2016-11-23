import os
import shutil
import bpy
import json
from bpy.props import *
import subprocess
import threading
import webbrowser
import write_data
import make_logic
import make_renderpath
import make_world
import make_utils
import make_state as state
import path_tracer
from exporter import ArmoryExporter
import armutils
import assets
import log
import lib.make_datas
import lib.make_variants
import lib.server

exporter = ArmoryExporter()

def compile_shader(raw_shaders_path, shader_name, defs):
    os.chdir(raw_shaders_path + './' + shader_name)
    fp = armutils.get_fp()

    # Open json file
    json_name = shader_name + '.shader.json'
    base_name = json_name.split('.', 1)[0]
    with open(json_name) as f:
        json_file = f.read()
    json_data = json.loads(json_file)
    
    lib.make_datas.make(base_name, json_data, fp, defs)
    lib.make_variants.make(base_name, json_data, fp, defs)

def export_data(fp, sdk_path, is_play=False, is_publish=False, in_viewport=False):
    global exporter

    raw_shaders_path = sdk_path + 'armory/Shaders/'
    assets_path = sdk_path + 'armory/Assets/'
    export_physics = bpy.data.worlds['Arm'].arm_physics != 'Disabled'
    assets.reset()

    # Build node trees
    # TODO: cache
    make_logic.build_node_trees()
    active_worlds = set()
    for scene in bpy.data.scenes:
        if scene.game_export and scene.world != None:
            active_worlds.add(scene.world)
    world_outputs = make_world.build_node_trees(active_worlds)
    make_renderpath.build_node_trees(assets_path)
    for wout in world_outputs:
        make_world.write_output(wout)

    # Export scene data
    assets.embedded_data = sorted(list(set(assets.embedded_data)))
    physics_found = False
    ArmoryExporter.compress_enabled = is_publish
    ArmoryExporter.in_viewport = in_viewport
    for scene in bpy.data.scenes:
        if scene.game_export:
            ext = '.zip' if (scene.data_compressed and is_publish) else '.arm'
            asset_path = 'build/compiled/Assets/' + armutils.safe_filename(scene.name) + ext
            exporter.execute(bpy.context, asset_path)
            if physics_found == False and ArmoryExporter.export_physics:
                physics_found = True
            assets.add(asset_path)
    
    if physics_found == False: # Disable physics anyway if no rigid body exported
        export_physics = False
    
    # Clean compiled variants if cache is disabled
    if bpy.data.worlds['Arm'].arm_cache_shaders == False:
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
                defs = make_utils.def_strings_to_array(strdefs)
            else:
                defs = []
            compile_shader(raw_shaders_path, shader_name, defs)

    # Reset path
    os.chdir(fp)

    # Copy std shaders
    if not os.path.isdir('build/compiled/Shaders/std'):
        shutil.copytree(raw_shaders_path + 'std', 'build/compiled/Shaders/std')

    # Write compiled.glsl
    write_data.write_compiledglsl()

    # Write khafile.js
    write_data.write_khafilejs(is_play, export_physics, dce_full=is_publish)

    # Write Main.hx - depends on write_khafilejs for writing number of assets
    write_data.write_main(is_play, in_viewport, is_publish)

    # Copy ammo.js if necessary
    #if target_name == 'html5':
    if export_physics and bpy.data.worlds['Arm'].arm_physics == 'Bullet':
        ammojs_path = sdk_path + '/lib/haxebullet/js/ammo/ammo.js'
        if not os.path.isfile('build/html5/ammo.js'):
            shutil.copy(ammojs_path, 'build/html5')
        if not os.path.isfile('build/debug-html5/ammo.js'):
            shutil.copy(ammojs_path, 'build/debug-html5')

def compile_project(target_name=None, is_publish=False, watch=False):
    sdk_path =  armutils.get_sdk_path()
    ffmpeg_path = armutils.get_ffmpeg_path()
    wrd = bpy.data.worlds['Arm']

    # Set build command
    if target_name == None:
        target_name = wrd.arm_project_target

    if armutils.get_os() == 'win':
        node_path = sdk_path + '/nodejs/node.exe'
        khamake_path = sdk_path + '/win32/resources/app/extensions/kha/Kha/make'
    elif armutils.get_os() == 'mac':
        node_path = sdk_path + '/nodejs/node-osx'
        khamake_path = sdk_path + '/Kode Studio.app/Contents/Resources/app/extensions/kha/Kha/make'
    else:
        node_path = sdk_path + '/nodejs/node-linux64'
        khamake_path = sdk_path + '/linux64/resources/app/extensions/kha/Kha/make'
    
    kha_target_name = make_utils.get_kha_target(target_name)
    cmd = [node_path, khamake_path, kha_target_name]

    if ffmpeg_path != '':
        cmd.append('--ffmpeg')
        cmd.append('"' + ffmpeg_path + '"')

    if armutils.get_os() == 'win': # OpenGL for now
        cmd.append('-g')
        cmd.append('opengl2')

    # User defined commands
    cmd_text = wrd.arm_command_line
    if cmd_text != '':
        for s in bpy.data.texts[cmd_text].as_string().split(' '):
            cmd.append(s)

    if state.krom_running:
        if state.compileproc == None: # Already compiling
            # Patch running game, stay silent, disable krafix and haxe
            # cmd.append('--silent')
            cmd.append('--noproject')
            cmd.append('--haxe')
            cmd.append('""')
            cmd.append('--krafix')
            cmd.append('""')
            # Khamake throws error when krafix is not found, hide for now
            state.compileproc = subprocess.Popen(cmd, stderr=subprocess.PIPE)
            threading.Timer(0.1, watch_patch).start()
            return state.compileproc
    elif watch == True:
        state.compileproc = subprocess.Popen(cmd)
        threading.Timer(0.1, watch_compile, ['build']).start()
        return state.compileproc
    else:
        return subprocess.Popen(cmd)

# For live patching
def patch_project():
    sdk_path = armutils.get_sdk_path()
    fp = armutils.get_fp()
    os.chdir(fp)
    export_data(fp, sdk_path, is_play=True)

def build_project(is_play=False, is_publish=False, in_viewport=False):
    # Clear flag
    state.in_viewport = False

    # Save blend
    bpy.ops.wm.save_mainfile()
    log.clear()

    # Set camera in active scene
    wrd = bpy.data.worlds['Arm']
    active_scene = bpy.context.screen.scene if wrd.arm_play_active_scene else bpy.data.scenes[wrd.arm_project_scene]
    if active_scene.camera == None:
        for o in active_scene.objects:
            if o.type == 'CAMERA':
                active_scene.camera = o
                break

    # Get paths
    sdk_path = armutils.get_sdk_path()
    raw_shaders_path = sdk_path + '/armory/Shaders/'
    
    # Set dir
    fp = armutils.get_fp()
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
        path_tracer.compile(raw_shaders_path + 'pt_trace_pass/pt_trace_pass.frag.glsl')

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
            with open('Sources/' + bpy.data.worlds['Arm'].arm_project_package + '/' + text.name, 'w') as f:
                f.write(text.as_string())

    # Save internal assets

    # Export data
    export_data(fp, sdk_path, is_play=is_play, is_publish=is_publish, in_viewport=in_viewport)

    if state.playproc == None:
        log.print_progress(50)

def stop_project():
    if state.playproc != None:
        state.playproc.terminate()
        state.playproc = None

def watch_play():
    if state.playproc == None:
        return
    line = b''
    while state.playproc != None and state.playproc.poll() == None:
        char = state.playproc.stderr.read(1) # Read immediately one by one 
        if char == b'\n':
            msg = str(line).split('"', 1) # Extract message
            if len(msg) > 1:
                trace = msg[1].rsplit('"', 1)[0]
                log.electron_trace(trace)
            line = b''
        else:
            line += char
    state.playproc = None
    state.playproc_finished = True
    log.clear()

def watch_compile(mode):
    state.compileproc.wait()
    log.print_progress(100)
    if state.compileproc == None: ##
        return
    result = state.compileproc.poll()
    state.compileproc = None
    state.compileproc_finished = True
    if result == 0:
        state.compileproc_success = True
        on_compiled(mode)
    else:
        state.compileproc_success = False
        log.print_info('Build failed, check console')

def watch_patch():
    state.compileproc.wait()
    # result = state.compileproc.poll()
    state.compileproc = None
    state.compileproc_finished = True

def play_project(self, in_viewport):
    if armutils.with_krom() and in_viewport and bpy.context.area.type == 'VIEW_3D':
        state.play_area = bpy.context.area

    # Build data
    build_project(is_play=True, in_viewport=in_viewport)
    state.in_viewport = in_viewport

    wrd = bpy.data.worlds['Arm']

    # Native
    if in_viewport == False and wrd.arm_play_runtime == 'Native':
        state.compileproc = compile_project(target_name='--run')
        mode = 'play'
        threading.Timer(0.1, watch_compile, [mode]).start()
    # Viewport
    elif armutils.with_krom() and in_viewport:
        state.compileproc = compile_project(target_name='krom')
        mode = 'play_viewport'
        threading.Timer(0.1, watch_compile, [mode]).start()
    # Electron, Browser
    else:
        x = 0
        y = 0
        w, h = armutils.get_render_resolution()
        winoff = 0
        write_data.write_electronjs(x, y, w, h, winoff, in_viewport)
        write_data.write_indexhtml(w, h, in_viewport)
        state.compileproc = compile_project(target_name='html5')
        mode = 'play'
        threading.Timer(0.1, watch_compile, [mode]).start()

def on_compiled(mode): # build, play, play_viewport, publish
    log.clear()
    sdk_path = armutils.get_sdk_path()

    # Print info
    if mode == 'publish':
        target_name = make_utils.get_kha_target(bpy.data.worlds['Arm'].arm_publish_target)
        print('Project published')
        files_path = armutils.get_fp() + '/build/' + target_name
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

    # Launch project in new window
    elif mode =='play':
        wrd = bpy.data.worlds['Arm']
        if wrd.arm_play_runtime == 'Electron':
            electron_app_path = './build/electron.js'

            if armutils.get_os() == 'win':
                electron_path = sdk_path + 'win32/Kode Studio.exe'
            elif armutils.get_os() == 'mac':
                electron_path = sdk_path + 'Kode Studio.app/Contents/MacOS/Electron'
            else:
                electron_path = sdk_path + 'linux64/kodestudio'

            state.playproc = subprocess.Popen([electron_path, '--chromedebug', '--remote-debugging-port=9222', '--enable-logging', electron_app_path], stderr=subprocess.PIPE)
            watch_play()
        elif wrd.arm_play_runtime == 'Browser':
            # Start server
            os.chdir(armutils.get_fp())
            t = threading.Thread(name='localserver', target=lib.server.run)
            t.daemon = True
            t.start()
            html5_app_path = 'http://localhost:8040/build/html5'
            webbrowser.open(html5_app_path)

def clean_cache():
    os.chdir(armutils.get_fp())
    wrd = bpy.data.worlds['Arm']

    # Preserve envmaps
    envmaps_path = 'build/compiled/Assets/envmaps'
    if os.path.isdir(envmaps_path):
        shutil.move(envmaps_path, '.')

    # Remove compiled data
    if os.path.isdir('build/compiled'):
        shutil.rmtree('build/compiled')

    # Move envmaps back
    if os.path.isdir('envmaps'):
        os.makedirs('build/compiled/Assets')
        shutil.move('envmaps', 'build/compiled/Assets')

def clean_project():
    os.chdir(armutils.get_fp())
    wrd = bpy.data.worlds['Arm']

    # Preserve envmaps
    # if wrd.arm_cache_envmaps:
        # envmaps_path = 'build/compiled/Assets/envmaps'
        # if os.path.isdir(envmaps_path):
            # shutil.move(envmaps_path, '.')

    # Remove build and compiled data
    if os.path.isdir('build'):
        shutil.rmtree('build')

    # Move envmaps back
    # if wrd.arm_cache_envmaps and os.path.isdir('envmaps'):
        # os.makedirs('build/compiled/Assets')
        # shutil.move('envmaps', 'build/compiled/Assets')

    # Remove compiled nodes
    nodes_path = 'Sources/' + wrd.arm_project_package.replace('.', '/') + '/node/'
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
    assets.invalidate_enabled = False
    minimize = bpy.data.worlds['Arm'].arm_minimize
    bpy.data.worlds['Arm'].arm_minimize = True
    clean_project()
    build_project(is_publish=True)
    state.compileproc = compile_project(target_name=bpy.data.worlds['Arm'].arm_publish_target, is_publish=True)
    threading.Timer(0.1, watch_compile, ['publish']).start()
    bpy.data.worlds['Arm'].arm_minimize = minimize
    assets.invalidate_enabled = True

def get_render_result():
    with open(armutils.get_fp() + '/build/html5/render.msg', 'w') as f:
        pass
