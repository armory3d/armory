import os
import glob
import time
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
scripts_mtime = 0 # Monitor source changes

def compile_shader(raw_shaders_path, shader_name, defs):
    os.chdir(raw_shaders_path + './' + shader_name)
    fp = armutils.get_fp()

    # Open json file
    json_name = shader_name + '.json'
    base_name = json_name.split('.', 1)[0]
    with open(json_name) as f:
        json_file = f.read()
    json_data = json.loads(json_file)
    
    lib.make_datas.make(base_name, json_data, fp, defs)
    lib.make_variants.make(base_name, json_data, fp, defs)

def export_data(fp, sdk_path, is_play=False, is_publish=False, in_viewport=False):
    global exporter
    wrd = bpy.data.worlds['Arm']

    print('\nArmory v' + wrd.arm_version)

    # Clean compiled variants if cache is disabled
    if wrd.arm_cache_shaders == False:
        if os.path.isdir('build/html5-resources'):
            shutil.rmtree('build/html5-resources')
        if os.path.isdir('build/krom-resources'):
            shutil.rmtree('build/krom-resources')
        if os.path.isdir('build/window/krom-resources'):
            shutil.rmtree('build/window/krom-resources')
        if os.path.isdir('build/compiled/Shaders'):
            shutil.rmtree('build/compiled/Shaders')
        if os.path.isdir('build/compiled/ShaderDatas'):
            shutil.rmtree('build/compiled/ShaderDatas')
        if os.path.isdir('build/compiled/ShaderRaws'):
            shutil.rmtree('build/compiled/ShaderRaws')
    # Remove shader datas if shaders were deleted
    elif os.path.isdir('build/compiled/Shaders') == False and os.path.isdir('build/compiled/ShaderDatas') == True:
        shutil.rmtree('build/compiled/ShaderDatas')

    raw_shaders_path = sdk_path + 'armory/Shaders/'
    assets_path = sdk_path + 'armory/Assets/'
    export_physics = bpy.data.worlds['Arm'].arm_physics != 'Disabled'
    export_navigation = bpy.data.worlds['Arm'].arm_navigation != 'Disabled'
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
    navigation_found = False
    ArmoryExporter.compress_enabled = is_publish
    ArmoryExporter.in_viewport = in_viewport
    for scene in bpy.data.scenes:
        if scene.game_export:
            ext = '.zip' if (scene.data_compressed and is_publish) else '.arm'
            asset_path = 'build/compiled/Assets/' + armutils.safe_filename(scene.name) + ext
            exporter.execute(bpy.context, asset_path)
            if physics_found == False and ArmoryExporter.export_physics:
                physics_found = True
            if navigation_found == False and ArmoryExporter.export_navigation:
                navigation_found = True
            assets.add(asset_path)
    
    if physics_found == False: # Disable physics anyway if no rigid body exported
        export_physics = False

    if navigation_found == False:
        export_navigation = False

    # Write referenced shader variants
    for ref in assets.shader_datas:
        # Data does not exist yet
        if not os.path.isfile(fp + '/' + ref):
            shader_name = ref.split('/')[3] # Extract from 'build/compiled/...'
            defs = make_utils.def_strings_to_array(wrd.world_defs + wrd.rp_defs)
            if shader_name.startswith('compositor_pass'):
                defs += make_utils.def_strings_to_array(wrd.compo_defs)
            compile_shader(raw_shaders_path, shader_name, defs)

    # Reset path
    os.chdir(fp)

    # Copy std shaders
    if not os.path.isdir('build/compiled/Shaders/std'):
        shutil.copytree(raw_shaders_path + 'std', 'build/compiled/Shaders/std')

    # Write compiled.glsl
    write_data.write_compiledglsl()

    # Write khafile.js
    write_data.write_khafilejs(is_play, export_physics, export_navigation, dce_full=is_publish)

    # Write Main.hx - depends on write_khafilejs for writing number of assets
    write_data.write_main(is_play, in_viewport, is_publish)

def compile_project(target_name=None, is_publish=False, watch=False, patch=False):
    sdk_path =  armutils.get_sdk_path()
    ffmpeg_path = armutils.get_ffmpeg_path()
    wrd = bpy.data.worlds['Arm']

    # Set build command
    if target_name == None:
        target_name = wrd.arm_project_target
    elif target_name == 'native':
        target_name = ''

    if armutils.get_os() == 'win':
        node_path = sdk_path + '/nodejs/node.exe'
        khamake_path = sdk_path + '/win32/Kha/make'
    elif armutils.get_os() == 'mac':
        node_path = sdk_path + '/nodejs/node-osx'
        khamake_path = sdk_path + '/Kode Studio.app/Contents/Kha/make'
    else:
        node_path = sdk_path + '/nodejs/node-linux64'
        khamake_path = sdk_path + '/linux64/Kha/make'
    
    kha_target_name = make_utils.get_kha_target(target_name)
    cmd = [node_path, khamake_path, kha_target_name]

    if ffmpeg_path != '':
        cmd.append('--ffmpeg')
        cmd.append('"' + ffmpeg_path + '"')

    if armutils.get_os() == 'win':
        cmd.append('-g')
        if (target_name == '' or target_name == '--run') and wrd.arm_gapi_win == 'direct3d9':
            cmd.append('direct3d9')
        else:
            cmd.append('opengl2')

    if kha_target_name == 'krom':
        if state.in_viewport:
            if armutils.glsl_version() >= 330:
                cmd.append('--shaderversion')
                cmd.append('330')
            else:
                cmd.append('--shaderversion')
                cmd.append('110')
        else:
            cmd.append('--to')
            cmd.append('build/window')

    # User defined commands
    cmd_text = wrd.arm_command_line
    if cmd_text != '':
        for s in bpy.data.texts[cmd_text].as_string().split(' '):
            cmd.append(s)

    if patch:
        if state.compileproc == None:
            # Quick build - disable krafix and haxe
            cmd.append('--nohaxe')
            cmd.append('--noshaders')
            cmd.append('--noproject')
            state.compileproc = subprocess.Popen(cmd, stderr=subprocess.PIPE)
            if state.playproc == None:
                if state.in_viewport:
                    mode = 'play_viewport'
                else:
                    mode = 'play'
            else:
                mode = 'build'
            threading.Timer(0.1, watch_patch, [mode]).start()
            return state.compileproc
    elif watch:
        state.compileproc = subprocess.Popen(cmd)
        threading.Timer(0.1, watch_compile, ['build']).start()
        return state.compileproc
    else:
        return subprocess.Popen(cmd)

def build_project(is_play=False, is_publish=False, in_viewport=False, target=None):
    wrd = bpy.data.worlds['Arm']

    # Set target
    if target == None:
        state.target = wrd.arm_project_target.lower()

    # Clear flag
    state.in_viewport = False

    # Save blend
    bpy.ops.wm.save_mainfile()
    log.clear()

    # Set camera in active scene
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
            if text.filepath != '' and text.is_dirty and os.path.isfile(text.filepath):
                area.spaces[0].text = text
                bpy.ops.text.save()
        area.type = old_type

    # Save internal Haxe scripts
    for text in bpy.data.texts:
        if text.filepath == '' and text.name[-3:] == '.hx':
            with open('Sources/' + bpy.data.worlds['Arm'].arm_project_package + '/' + text.name, 'w') as f:
                f.write(text.as_string())

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
        bpy.data.worlds['Arm'].arm_recompile = False
        state.compileproc_success = True
        on_compiled(mode)
    else:
        state.compileproc_success = False
        log.print_info('Build failed, check console')

def watch_patch(mode):
    state.compileproc.wait()
    log.print_progress(100)
    # result = state.compileproc.poll()
    state.compileproc = None
    state.compileproc_finished = True
    on_compiled(mode)

def runtime_to_target(in_viewport):
    wrd = bpy.data.worlds['Arm']
    if in_viewport or wrd.arm_play_runtime == 'Krom':
        return 'krom'
    elif wrd.arm_play_runtime == 'Native':
        return 'native'
    else:
        return 'html5'

def get_khajs_path(in_viewport, target):
    if in_viewport:
        return 'build/krom/krom.js'
    elif target == 'krom':
        return 'build/window/krom/krom.js'
    else: # browser, electron
        return 'build/html5/kha.js'

def play_project(in_viewport):
    global scripts_mtime
    wrd = bpy.data.worlds['Arm']

    # Store area
    if armutils.with_krom() and in_viewport and bpy.context.area != None and bpy.context.area.type == 'VIEW_3D':
        state.play_area = bpy.context.area

    state.target = runtime_to_target(in_viewport)

    # Build data
    build_project(is_play=True, in_viewport=in_viewport, target=state.target)
    state.in_viewport = in_viewport

    khajs_path = get_khajs_path(in_viewport, state.target)
    if wrd.arm_recompile or \
       wrd.arm_recompile_trigger or \
       not wrd.arm_cache_compiler or \
       not wrd.arm_cache_shaders or \
       not os.path.isfile(khajs_path) or \
       state.last_target != state.target or \
       state.last_in_viewport != state.in_viewport:
        wrd.arm_recompile = True

    wrd.arm_recompile_trigger = False
    state.last_target = state.target
    state.last_in_viewport = state.in_viewport

    # Trait sources modified
    script_path = armutils.get_fp() + '/Sources/' + wrd.arm_project_package
    if os.path.isdir(script_path):
        for fn in glob.iglob(os.path.join(script_path, '**', '*.hx'), recursive=True):
            mtime = os.path.getmtime(fn)
            if scripts_mtime < mtime:
                scripts_mtime = mtime
                wrd.arm_recompile = True

    # New compile requred - traits or materials changed
    if wrd.arm_recompile or state.target == 'native':

        # Unable to live-patch, stop player
        if state.krom_running:
            bpy.ops.arm.space_stop()
            # play_project(in_viewport=True) # Restart
            return

        mode = 'play'
        if state.target == 'native':
            state.compileproc = compile_project(target_name='--run')
        elif state.target == 'krom':
            if in_viewport:
                mode = 'play_viewport'
            state.compileproc = compile_project(target_name='krom')
        else: # Electron, Browser
            w, h = armutils.get_render_resolution(armutils.get_active_scene())
            write_data.write_electronjs(w, h)
            write_data.write_indexhtml(w, h)
            state.compileproc = compile_project(target_name='html5')
        threading.Timer(0.1, watch_compile, [mode]).start()
    else: # kha.js up to date
        compile_project(target_name=state.target, patch=True)

def on_compiled(mode): # build, play, play_viewport, publish
    log.clear()
    sdk_path = armutils.get_sdk_path()
    wrd = bpy.data.worlds['Arm']

    # Print info
    if mode == 'publish':
        target_name = make_utils.get_kha_target(wrd.arm_project_target)
        print('Project published')
        files_path = armutils.get_fp() + '/build/' + target_name
        if target_name == 'html5':
            print('HTML5 files are located in ' + files_path)
        elif target_name == 'ios' or target_name == 'osx': # TODO: to macos
            print('XCode project files are located in ' + files_path + '-build')
        elif target_name == 'windows':
            print('VisualStudio 2015 project files are located in ' + files_path + '-build')
        elif target_name == 'android-native':
            print('Android Studio project files are located in ' + files_path + '-build/' + wrd.arm_project_name)
        else:
            print('Makefiles are located in ' + files_path + '-build')
        return

    # Launch project in new window
    elif mode =='play':
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
        elif wrd.arm_play_runtime == 'Krom':
            if armutils.get_os() == 'win':
                krom_location = sdk_path + '/win32/Krom/win32'
                krom_path = krom_location + '/Krom.exe'
            elif armutils.get_os() == 'mac':
                krom_location = sdk_path + '/Kode Studio.app/Contents/Krom/macos/Krom.app/Contents/MacOS'
                krom_path = krom_location + '/Krom'
            else:
                krom_location = sdk_path + '/linux64/Krom/linux'
                krom_path = krom_location + '/Krom'
            os.chdir(krom_location)
            state.playproc = subprocess.Popen([krom_path, armutils.get_fp() + '/build/window/krom', armutils.get_fp() + '/build/window/krom-resources'], stderr=subprocess.PIPE)
            watch_play()

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

    # Remove build and compiled data
    if os.path.isdir('build'):
        shutil.rmtree('build')

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
    state.compileproc = compile_project(target_name=bpy.data.worlds['Arm'].arm_project_target, is_publish=True)
    threading.Timer(0.1, watch_compile, ['publish']).start()
    bpy.data.worlds['Arm'].arm_minimize = minimize
    assets.invalidate_enabled = True

def get_render_result():
    with open(armutils.get_fp() + '/build/html5/render.msg', 'w') as f:
        pass
