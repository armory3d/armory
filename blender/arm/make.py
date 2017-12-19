import os
import glob
import time
import shutil
import bpy
import json
import stat
from bpy.props import *
import subprocess
import threading
import webbrowser
import arm.utils
import arm.write_data as write_data
import arm.make_logic as make_logic
import arm.make_renderpath as make_renderpath
import arm.make_world as make_world
import arm.make_state as state
import arm.assets as assets
import arm.log as log
import arm.lib.make_datas
import arm.lib.make_variants
import arm.lib.server
from arm.exporter import ArmoryExporter
import time
try:
    import barmory
except ImportError:
    pass

exporter = ArmoryExporter()
scripts_mtime = 0 # Monitor source changes
code_parsed = False
profile_time = 0

def compile_shader_pass(res, raw_shaders_path, shader_name, defs):
    os.chdir(raw_shaders_path + '/' + shader_name)

    # Open json file
    json_name = shader_name + '.json'
    base_name = json_name.split('.', 1)[0]
    with open(json_name) as f:
        json_file = f.read()
    json_data = json.loads(json_file)

    fp = arm.utils.get_fp_build()
    arm.lib.make_datas.make(res, base_name, json_data, fp, defs)
    arm.lib.make_variants.make(base_name, json_data, fp, defs)

def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def export_data(fp, sdk_path, is_play=False, is_publish=False, in_viewport=False):
    global exporter
    wrd = bpy.data.worlds['Arm']

    print('\nArmory v{0} ({1})'.format(wrd.arm_version, wrd.arm_commit))
    print('OS: ' + arm.utils.get_os() + ', Target: ' + state.target + ', GAPI: ' + arm.utils.get_gapi())

    # Clean compiled variants if cache is disabled
    build_dir = arm.utils.get_fp_build()
    if wrd.arm_cache_shaders == False:
        if os.path.isdir(build_dir + '/debug/html5-resources'):
            shutil.rmtree(build_dir + '/debug/html5-resources', onerror=remove_readonly)
        if os.path.isdir(build_dir + '/krom-resources'):
            shutil.rmtree(build_dir + '/krom-resources', onerror=remove_readonly)
        if os.path.isdir(build_dir + '/debug/krom-resources'):
            shutil.rmtree(build_dir + '/debug/krom-resources', onerror=remove_readonly)
        if os.path.isdir(build_dir + '/windows-resources'):
            shutil.rmtree(build_dir + '/windows-resources', onerror=remove_readonly)
        if os.path.isdir(build_dir + '/linux-resources'):
            shutil.rmtree(build_dir + '/linux-resources', onerror=remove_readonly)
        if os.path.isdir(build_dir + '/osx-resources'):
            shutil.rmtree(build_dir + '/osx-resources', onerror=remove_readonly)
        if os.path.isdir(build_dir + '/compiled/Shaders'):
            shutil.rmtree(build_dir + '/compiled/Shaders', onerror=remove_readonly)
        if os.path.isdir(build_dir + '/compiled/ShaderRaws'):
            shutil.rmtree(build_dir + '/compiled/ShaderRaws', onerror=remove_readonly)

    # Detect camera plane changes
    if len(bpy.data.cameras) > 0:
        cam = bpy.data.cameras[0]
        if state.last_clip_start == 0:
            state.last_clip_start = cam.clip_start
            state.last_clip_end = cam.clip_end
        elif cam.clip_start != state.last_clip_start or cam.clip_end != state.last_clip_end:
            if os.path.isdir(build_dir + '/compiled/Shaders'):
                shutil.rmtree(build_dir + '/compiled/Shaders', onerror=remove_readonly)
            state.last_clip_start = cam.clip_start
            state.last_clip_end = cam.clip_end

    raw_shaders_path = sdk_path + 'armory/Shaders/'
    assets_path = sdk_path + 'armory/Assets/'
    export_physics = bpy.data.worlds['Arm'].arm_physics != 'Disabled'
    export_navigation = bpy.data.worlds['Arm'].arm_navigation != 'Disabled'
    export_ui = bpy.data.worlds['Arm'].arm_ui != 'Disabled'
    assets.reset()

    # Build node trees
    ArmoryExporter.import_traits = []
    make_logic.build()
    make_world.build()
    make_renderpath.build()

    # Export scene data
    assets.embedded_data = sorted(list(set(assets.embedded_data)))
    physics_found = False
    navigation_found = False
    ui_found = False
    ArmoryExporter.compress_enabled = is_publish and wrd.arm_asset_compression
    ArmoryExporter.in_viewport = in_viewport
    for scene in bpy.data.scenes:
        if scene.arm_export:
            ext = '.zip' if (scene.arm_compress and is_publish) else '.arm'
            asset_path = build_dir + '/compiled/Assets/' + arm.utils.safestr(scene.name) + ext
            exporter.execute(bpy.context, asset_path, scene=scene, write_capture_info=state.is_render_anim, play_area=state.play_area)
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

    modules = []
    if export_physics:
        modules.append('physics')
    if export_navigation:
        modules.append('navigation')
    if export_ui:
        modules.append('ui')
    print('Exported modules: ' + str(modules))

    defs = arm.utils.def_strings_to_array(wrd.world_defs)
    print('Shader flags: ' + str(defs))

    # Write referenced shader passes
    if not os.path.isfile(build_dir + '/compiled/Shaders/shader_datas.arm') or state.last_world_defs != wrd.world_defs:
        path = build_dir + '/compiled/Shaders'
        if not os.path.exists(path):
            os.makedirs(path)
        res = {}
        res['shader_datas'] = []
        for ref in assets.shader_passes:
            # Ensure shader pass source exists
            if not os.path.exists(raw_shaders_path + '/' + ref):
                continue
            if ref.startswith('compositor_pass'):
                cdefs = arm.utils.def_strings_to_array(wrd.compo_defs)
                compile_shader_pass(res, raw_shaders_path, ref, defs + cdefs)
            # elif ref.startswith('grease_pencil'):
                # compile_shader_pass(res, raw_shaders_path, ref, [])
            else:
                compile_shader_pass(res, raw_shaders_path, ref, defs)
        arm.utils.write_arm(path + '/shader_datas.arm', res)
    state.last_world_defs = wrd.world_defs

    # Reset path
    os.chdir(fp)

    # Copy std shaders
    if not os.path.isdir(build_dir + '/compiled/Shaders/std'):
        shutil.copytree(raw_shaders_path + 'std', build_dir + '/compiled/Shaders/std')

    # Write compiled.glsl
    write_data.write_compiledglsl()

    # Write khafile.js
    enable_dce = is_publish and wrd.arm_dce
    import_logic = not is_publish and arm.utils.logic_editor_space() != None
    write_data.write_khafilejs(is_play, export_physics, export_navigation, export_ui, is_publish, enable_dce, in_viewport, ArmoryExporter.import_traits, import_logic)

    # Write Main.hx - depends on write_khafilejs for writing number of assets
    scene_name = arm.utils.get_project_scene_name()
    resx, resy = arm.utils.get_render_resolution(arm.utils.get_active_scene())
    # Import all logic nodes for patching if logic is being edited
    write_data.write_main(scene_name, resx, resy, is_play, in_viewport, is_publish)
    if scene_name != state.last_scene or resx != state.last_resx or resy != state.last_resy:
        wrd.arm_recompile = True
        state.last_resx = resx
        state.last_resy = resy
        state.last_scene = scene_name

def compile_project(target_name=None, watch=False, patch=False, no_project_file=False):
    """
    :param no_project_file: Pass '--noproject' to kha make. In the future assets will be copied.
    """
    wrd = bpy.data.worlds['Arm']

    fp = arm.utils.get_fp()
    os.chdir(fp)

    # Set build command
    if target_name == None:
        target_name = state.target
    if target_name == 'native':
        target_name = ''

    node_path = arm.utils.get_node_path()
    khamake_path = arm.utils.get_khamake_path()

    kha_target_name = arm.utils.get_kha_target(target_name)
    cmd = [node_path, khamake_path, kha_target_name]

    ffmpeg_path = arm.utils.get_ffmpeg_path() # Path to binary
    if ffmpeg_path != '':
        cmd.append('--ffmpeg')
        cmd.append(ffmpeg_path) # '"' + ffmpeg_path + '"'

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
    else:
        cmd.append('-g')
        cmd.append(arm.utils.get_gapi())

    # Kha defaults to 110
    if arm.utils.get_os() == 'linux' and (kha_target_name == 'krom' or kha_target_name == '') and state.in_viewport == False:
        cmd.append('--shaderversion')
        cmd.append('330')

    cmd.append('--to')
    if (kha_target_name == 'krom' and not state.in_viewport) or (kha_target_name == 'html5' and not state.is_publish):
        cmd.append(arm.utils.build_dir() + '/debug')
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
        if no_project_file:
            cmd.append('--noproject')
        print("Running: ", cmd)
        return subprocess.Popen(cmd)

def build_project(is_play=False, is_publish=False, is_render=False, is_render_anim=False, in_viewport=False):
    global profile_time
    profile_time = time.time()

    wrd = bpy.data.worlds['Arm']

    state.is_render = is_render
    state.is_render_anim = is_render_anim
    state.is_publish = is_publish
    state.in_viewport = in_viewport

    # Save blend
    if arm.utils.get_save_on_build() and not state.krom_running:
        bpy.ops.wm.save_mainfile()

    log.clear()

    # Set camera in active scene
    active_scene = arm.utils.get_active_scene()
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
        write_data.write_indexhtml(w, h, is_publish)
        # Bundle files from include dir
        if os.path.isdir('include'):
            dest  = '/html5/' if is_publish else '/debug/html5/'
            for fn in glob.iglob(os.path.join('include', '**'), recursive=False):
                shutil.copy(fn, arm.utils.build_dir() + dest + os.path.basename(fn))

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
                log.krom_trace(trace)
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
        print('Project built in ' + str(time.time() - profile_time))
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
        return arm.utils.build_dir() + '/debug/krom/krom.js'
    else: # Browser
        return arm.utils.build_dir() + '/debug/html5/kha.js'

def play_project(in_viewport, is_render=False, is_render_anim=False):
    global scripts_mtime
    global code_parsed
    wrd = bpy.data.worlds['Arm']

    log.clear()

    # Store area
    if arm.utils.with_krom() and in_viewport and bpy.context.area != None and bpy.context.area.type == 'VIEW_3D':
        state.play_area = bpy.context.area

    state.target = runtime_to_target(in_viewport)

    # Build data
    build_project(is_play=True, is_render=is_render, is_render_anim=is_render_anim, in_viewport=in_viewport)

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

    if state.in_viewport:
        if arm.utils.get_rp().rp_gi != 'Off' and bpy.app.version < (2, 80, 1):
            log.warn('Use Blender 2.8 to run Voxel GI in viewport')

    # Trait sources modified
    state.mod_scripts = []
    script_path = arm.utils.get_fp() + '/Sources/' + arm.utils.safestr(wrd.arm_project_package)
    if os.path.isdir(script_path):
        new_mtime = scripts_mtime
        for fn in glob.iglob(os.path.join(script_path, '**', '*.hx'), recursive=True):
            mtime = os.path.getmtime(fn)
            if scripts_mtime < mtime:
                arm.utils.fetch_script_props(fn) # Trait props
                fn = fn.split('Sources/')[1]
                fn = fn[:-3] #.hx
                fn = fn.replace('/', '.')
                state.mod_scripts.append(fn)
                wrd.arm_recompile = True
                if new_mtime < mtime:
                    new_mtime = mtime
        scripts_mtime = new_mtime
        if len(state.mod_scripts) > 0: # Trait props
            arm.utils.fetch_trait_props()

    # New compile requred - traits changed
    if wrd.arm_recompile:
        state.recompiled = True
        if state.krom_running:
            # TODO: Unable to live-patch, stop player
            bpy.ops.arm.space_stop('EXEC_DEFAULT')
            return
            if not code_parsed:
                code_parsed = True
                barmory.parse_code()
        else:
            code_parsed = False

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
        state.recompiled = False
        compile_project(patch=True)

def on_compiled(mode): # build, play, play_viewport, publish
    log.clear()
    sdk_path = arm.utils.get_sdk_path()
    wrd = bpy.data.worlds['Arm']

    # Launch project in new window
    if mode =='play':
        if wrd.arm_play_runtime == 'Browser':
            # Start server
            os.chdir(arm.utils.get_fp())
            t = threading.Thread(name='localserver', target=arm.lib.server.run)
            t.daemon = True
            t.start()
            html5_app_path = 'http://localhost:8040/' + arm.utils.build_dir() + '/debug/html5'
            webbrowser.open(html5_app_path)
        elif wrd.arm_play_runtime == 'Krom':
            krom_location, krom_path = arm.utils.krom_paths()
            os.chdir(krom_location)
            args = [krom_path, arm.utils.get_fp_build() + '/debug/krom', arm.utils.get_fp_build() + '/debug/krom-resources']
            # TODO: Krom sound freezes on MacOS
            if arm.utils.get_os() == 'mac':
                args.append('--nosound')
            if state.is_render:
                args.append('--nowindow')
            state.playproc = subprocess.Popen(args, stderr=subprocess.PIPE)
            watch_play()

def clean_project():
    os.chdir(arm.utils.get_fp())
    wrd = bpy.data.worlds['Arm']

    # Remove build and compiled data
    if os.path.isdir(arm.utils.build_dir()):
        shutil.rmtree(arm.utils.build_dir(), onerror=remove_readonly)
    if os.path.isdir(arm.utils.get_fp() + '/build'): # Kode Studio build dir
        shutil.rmtree(arm.utils.get_fp() + '/build', onerror=remove_readonly)

    # Remove compiled nodes
    nodes_path = 'Sources/' + arm.utils.safestr(wrd.arm_project_package).replace('.', '/') + '/node/'
    if os.path.isdir(nodes_path):
        shutil.rmtree(nodes_path, onerror=remove_readonly)

    # Remove khafile/korefile/Main.hx
    if os.path.isfile('khafile.js'):
        os.remove('khafile.js')
    if os.path.isfile('korefile.js'):
        os.remove('korefile.js')
    if os.path.isfile('Sources/Main.hx'):
        os.remove('Sources/Main.hx')

    # To recache signatures for batched materials
    for mat in bpy.data.materials:
        mat.signature = ''
        mat.is_cached = False

    print('Project cleaned')

def get_render_result():
    play_project(False, is_render=True)

def get_render_anim_result():
    if bpy.context.scene != None:
        print('Capturing animation frames into ' + bpy.context.scene.render.filepath)
    play_project(False, is_render=True, is_render_anim=True)
