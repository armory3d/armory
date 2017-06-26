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
import arm.utils
import arm.write_data as write_data
import arm.make_logic as make_logic
import arm.make_renderpath as make_renderpath
import arm.make_world as make_world
import arm.make_utils as make_utils
import arm.make_state as state
import arm.path_tracer as path_tracer
import arm.assets as assets
import arm.log as log
import arm.lib.make_datas
import arm.lib.make_variants
import arm.lib.server
from arm.exporter import ArmoryExporter

exporter = ArmoryExporter()
scripts_mtime = 0 # Monitor source changes

def compile_shader(raw_shaders_path, shader_name, defs):
    os.chdir(raw_shaders_path + './' + shader_name)

    # Open json file
    json_name = shader_name + '.json'
    base_name = json_name.split('.', 1)[0]
    with open(json_name) as f:
        json_file = f.read()
    json_data = json.loads(json_file)
    
    fp = arm.utils.get_fp_build()
    arm.lib.make_datas.make(base_name, json_data, fp, defs)
    arm.lib.make_variants.make(base_name, json_data, fp, defs)

def export_data(fp, sdk_path, is_play=False, is_publish=False, in_viewport=False):
    global exporter
    wrd = bpy.data.worlds['Arm']

    print('\nArmory v' + wrd.arm_version)
    print('OS: ' + arm.utils.get_os() + ', Target: ' + state.target + ', GAPI: ' + arm.utils.get_gapi())

    # Clean compiled variants if cache is disabled
    if wrd.arm_cache_shaders == False:
        build_dir = arm.utils.build_dir()
        if os.path.isdir(build_dir + '/build/html5-resources'):
            shutil.rmtree(build_dir + '/build/html5-resources')
        if os.path.isdir(build_dir + '/build/krom-resources'):
            shutil.rmtree(build_dir + '/build/krom-resources')
        if os.path.isdir(build_dir + '/window/krom-resources'):
            shutil.rmtree(build_dir + '/window/krom-resources')
        if os.path.isdir(build_dir + '/compiled/Shaders'):
            shutil.rmtree(build_dir + '/compiled/Shaders')
        if os.path.isdir(build_dir + '/compiled/ShaderRaws'):
            shutil.rmtree(build_dir + '/compiled/ShaderRaws')

    raw_shaders_path = sdk_path + 'armory/Shaders/'
    assets_path = sdk_path + 'armory/Assets/'
    export_physics = bpy.data.worlds['Arm'].arm_physics != 'Disabled'
    export_navigation = bpy.data.worlds['Arm'].arm_navigation != 'Disabled'
    export_ui = bpy.data.worlds['Arm'].arm_ui != 'Disabled'
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
    ui_found = False
    ArmoryExporter.compress_enabled = is_publish
    ArmoryExporter.in_viewport = in_viewport
    for scene in bpy.data.scenes:
        if scene.game_export:
            ext = '.zip' if (scene.data_compressed and is_publish) else '.arm'
            asset_path = arm.utils.build_dir() + '/compiled/Assets/' + arm.utils.safestr(scene.name) + ext
            exporter.execute(bpy.context, asset_path, scene=scene)
            if ArmoryExporter.export_physics:
                physics_found = True
            if ArmoryExporter.export_navigation:
                navigation_found = True
            if ArmoryExporter.export_ui:
                ui_found = True
            assets.add(asset_path)
    
    if physics_found == False: # Disable physics if no rigid body is exported
        export_physics = False

    if navigation_found == False:
        export_navigation = False

    if ui_found == False:
        export_ui = False

    if wrd.arm_ui == 'Enabled':
        export_ui = True

    # Write referenced shader variants
    for ref in assets.shader_datas:
        # Data does not exist yet
        if not os.path.isfile(fp + '/' + ref):
            shader_name = ref.split('/')[3] # Extract from 'build/compiled/...'
            defs = make_utils.def_strings_to_array(wrd.world_defs + wrd.rp_defs)
            if shader_name.startswith('compositor_pass'):
                defs += make_utils.def_strings_to_array(wrd.compo_defs)
            elif shader_name.startswith('grease_pencil'):
                defs = []
            compile_shader(raw_shaders_path, shader_name, defs)

    # Reset path
    os.chdir(fp)

    # Copy std shaders
    if not os.path.isdir(arm.utils.build_dir() + '/compiled/Shaders/std'):
        shutil.copytree(raw_shaders_path + 'std', arm.utils.build_dir() + '/compiled/Shaders/std')

    # Write compiled.glsl
    write_data.write_compiledglsl()

    # Write khafile.js
    enable_dce = is_publish and wrd.arm_dce
    write_data.write_khafilejs(is_play, export_physics, export_navigation, export_ui, is_publish, enable_dce)

    # Write Main.hx - depends on write_khafilejs for writing number of assets
    resx, resy = arm.utils.get_render_resolution(arm.utils.get_active_scene())
    write_data.write_main(resx, resy, is_play, in_viewport, is_publish)
    if resx != state.last_resx or resy != state.last_resy:
        wrd.arm_recompile = True
    state.last_resx = resx
    state.last_resy = resy

def compile_project(target_name=None, is_publish=False, watch=False, patch=False):
    wrd = bpy.data.worlds['Arm']

    fp = arm.utils.get_fp()
    os.chdir(fp)

    # Set build command
    if target_name == None:
        target_name = wrd.arm_project_target
    elif target_name == 'native':
        target_name = ''

    node_path = arm.utils.get_node_path()
    khamake_path = arm.utils.get_khamake_path()
    
    kha_target_name = make_utils.get_kha_target(target_name)
    cmd = [node_path, khamake_path, kha_target_name]

    ffmpeg_path = arm.utils.get_ffmpeg_path() # Path to binary
    if ffmpeg_path != '':
        cmd.append('--ffmpeg')
        cmd.append(ffmpeg_path) # '"' + ffmpeg_path + '"'

    if target_name == '' or target_name == '--run':
        cmd.append('-g')
        cmd.append(arm.utils.get_gapi())

    if kha_target_name == 'krom':
        cmd.append('-g')
        cmd.append('opengl')
        if state.in_viewport:
            if arm.utils.glsl_version() >= 330:
                cmd.append('--shaderversion')
                cmd.append('330')
            else:
                cmd.append('--shaderversion')
                cmd.append('110')
    
    cmd.append('--to')
    if kha_target_name == 'krom' and not state.in_viewport:
        cmd.append(arm.utils.build_dir() + '/window')
    else:
        cmd.append(arm.utils.build_dir())

    # User defined commands
    if wrd.arm_khamake != '':
        for s in bpy.data.texts[wrd.arm_khamake].as_string().split(' '):
            cmd.append(s)

    if patch:
        if state.compileproc == None:
            cmd.append('--nohaxe')
            cmd.append('--noproject')
            # cmd.append('--noshaders')
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

def build_project(is_play=False, is_publish=False, is_render=False, in_viewport=False, target=None):
    wrd = bpy.data.worlds['Arm']

    state.is_render = is_render

    # Set target
    if target == None:
        state.target = wrd.arm_project_target.lower()

    # Clear flag
    state.in_viewport = False

    # Save blend
    if arm.utils.get_save_on_build():
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
    sdk_path = arm.utils.get_sdk_path()
    raw_shaders_path = sdk_path + '/armory/Shaders/'
    
    # Set dir
    fp = arm.utils.get_fp()
    os.chdir(fp)

    # Create directories
    sources_path = 'Sources/' + arm.utils.safestr(wrd.arm_project_package)
    if not os.path.exists(sources_path):
        os.makedirs(sources_path)

    # Compile path tracer shaders
    # if len(bpy.data.cameras) > 0 and bpy.data.cameras[0].renderpath_path == 'pathtrace_path':
        # path_tracer.compile(raw_shaders_path + 'pt_trace_pass/pt_trace_pass.frag.glsl')

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
            with open('Sources/' + arm.utils.safestr(wrd.arm_project_package) + '/' + text.name, 'w') as f:
                f.write(text.as_string())

    # Export data
    export_data(fp, sdk_path, is_play=is_play, is_publish=is_publish, in_viewport=in_viewport)

    if state.target == 'html5':
        w, h = arm.utils.get_render_resolution(arm.utils.get_active_scene())
        write_data.write_indexhtml(w, h)
        # Bundle files from include dir
        if os.path.isdir('include'):
            for fn in glob.iglob(os.path.join('include', '**'), recursive=False):
                shutil.copy(fn, arm.utils.build_dir() + '/html5/' + os.path.basename(fn))

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
        return arm.utils.build_dir() + '/krom/krom.js'
    elif target == 'krom':
        return arm.utils.build_dir() + '/window/krom/krom.js'
    else: # Browser
        return arm.utils.build_dir() + '/html5/kha.js'

def play_project(in_viewport, is_render=False):
    global scripts_mtime
    wrd = bpy.data.worlds['Arm']

    log.clear()

    # Store area
    if arm.utils.with_krom() and in_viewport and bpy.context.area != None and bpy.context.area.type == 'VIEW_3D':
        state.play_area = bpy.context.area

    state.target = runtime_to_target(in_viewport)

    # Build data
    build_project(is_play=True, is_render=is_render, in_viewport=in_viewport, target=state.target)
    state.in_viewport = in_viewport

    khajs_path = get_khajs_path(in_viewport, state.target)
    if not wrd.arm_cache_compiler or \
       not os.path.isfile(khajs_path) or \
       assets.khafile_defs_last != assets.khafile_defs or \
       state.last_target != state.target or \
       state.last_in_viewport != state.in_viewport or \
       state.target == 'native':
        wrd.arm_recompile = True

    state.last_target = state.target
    state.last_in_viewport = state.in_viewport

    # Trait sources modified
    script_path = arm.utils.get_fp() + '/Sources/' + arm.utils.safestr(wrd.arm_project_package)
    if os.path.isdir(script_path):
        for fn in glob.iglob(os.path.join(script_path, '**', '*.hx'), recursive=True):
            mtime = os.path.getmtime(fn)
            if scripts_mtime < mtime:
                scripts_mtime = mtime
                wrd.arm_recompile = True

    # New compile requred - traits changed
    if wrd.arm_recompile:
        # Unable to live-patch, stop player
        if state.krom_running:
            bpy.ops.arm.space_stop('EXEC_DEFAULT')
            return

        mode = 'play'
        if state.target == 'native':
            state.compileproc = compile_project(target_name='--run')
        elif state.target == 'krom':
            if in_viewport:
                mode = 'play_viewport'
            state.compileproc = compile_project(target_name='krom')
        else: # Browser
            state.compileproc = compile_project(target_name='html5')
        threading.Timer(0.1, watch_compile, [mode]).start()
    else: # kha.js up to date
        compile_project(target_name=state.target, patch=True)

def on_compiled(mode): # build, play, play_viewport, publish
    log.clear()
    sdk_path = arm.utils.get_sdk_path()
    wrd = bpy.data.worlds['Arm']

    # Print info
    if mode == 'publish':
        target_name = make_utils.get_kha_target(wrd.arm_project_target)
        print('Project published')
        files_path = arm.utils.get_fp_build() + '/' + target_name
        if target_name == 'html5':
            print('HTML5 files are located in ' + files_path)
        elif target_name == 'ios' or target_name == 'osx': # TODO: to macos
            print('XCode project files are located in ' + files_path + '-build')
        elif target_name == 'windows':
            print('VisualStudio 2017 project files are located in ' + files_path + '-build')
        elif target_name == 'windowsapp':
            print('VisualStudio 2017 project files are located in ' + files_path + '-build')
        elif target_name == 'android-native':
            print('Android Studio project files are located in ' + files_path + '-build/' + arm.utils.safestr(wrd.arm_project_name))
        else:
            print('Makefiles are located in ' + files_path + '-build')
        return

    # Launch project in new window
    elif mode =='play':
        if wrd.arm_play_runtime == 'Browser':
            # Start server
            os.chdir(arm.utils.get_fp())
            t = threading.Thread(name='localserver', target=arm.lib.server.run)
            t.daemon = True
            t.start()
            html5_app_path = 'http://localhost:8040/' + arm.utils.build_dir() + '/html5'
            webbrowser.open(html5_app_path)
        elif wrd.arm_play_runtime == 'Krom':
            krom_location, krom_path = arm.utils.krom_paths()
            # os.chdir(krom_location)
            os.chdir(arm.utils.get_fp_build())
            args = [krom_path, arm.utils.get_fp_build() + '/window/krom', arm.utils.get_fp_build() + '/window/krom-resources', '--nosound']
            # if state.is_render:
                # args.append('--nowindow')
            state.playproc = subprocess.Popen(args, stderr=subprocess.PIPE)
            watch_play()

def clean_cache():
    os.chdir(arm.utils.get_fp())
    wrd = bpy.data.worlds['Arm']

    # Preserve envmaps
    envmaps_path = arm.utils.build_dir() + '/compiled/Assets/envmaps'
    if os.path.isdir(envmaps_path):
        shutil.move(envmaps_path, '.')

    # Remove compiled data
    if os.path.isdir(arm.utils.build_dir() + '/compiled'):
        shutil.rmtree(arm.utils.build_dir() + '/compiled')

    # Move envmaps back
    if os.path.isdir('envmaps'):
        os.makedirs(arm.utils.build_dir() + '/compiled/Assets')
        shutil.move('envmaps', arm.utils.build_dir() + '/compiled/Assets')

    # Temp: To recache signatures for batched materials
    for mat in bpy.data.materials:
        mat.signature = ''

def clean_project():
    os.chdir(arm.utils.get_fp())
    wrd = bpy.data.worlds['Arm']

    # Remove build and compiled data
    if os.path.isdir(arm.utils.build_dir()):
        shutil.rmtree(arm.utils.build_dir())

    # Remove compiled nodes
    nodes_path = 'Sources/' + arm.utils.safestr(wrd.arm_project_package).replace('.', '/') + '/node/'
    if os.path.isdir(nodes_path):
        shutil.rmtree(nodes_path)

    # Remove khafile/korefile/Main.hx
    if os.path.isfile('khafile.js'):
        os.remove('khafile.js')
    if os.path.isfile('korefile.js'):
        os.remove('korefile.js')
    if os.path.isfile('Sources/Main.hx'):
        os.remove('Sources/Main.hx')

    # Temp: To recache signatures for batched materials
    for mat in bpy.data.materials:
        mat.signature = ''

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
    play_project(False, is_render=True)
