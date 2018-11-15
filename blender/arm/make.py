import os
from pathlib import Path
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
import arm.lib.server
from arm.exporter import ArmoryExporter

exporter = ArmoryExporter()
scripts_mtime = 0 # Monitor source changes
profile_time = 0

def run_proc(cmd, done):
    def fn(p, done):
        p.wait()
        if done != None:
            done()
    p = subprocess.Popen(cmd)
    threading.Thread(target=fn, args=(p, done)).start()
    return p

def compile_shader_pass(res, raw_shaders_path, shader_name, defs):
    os.chdir(raw_shaders_path + '/' + shader_name)

    # Open json file
    json_name = shader_name + '.json'
    with open(json_name) as f:
        json_file = f.read()
    json_data = json.loads(json_file)

    fp = arm.utils.get_fp_build()
    arm.lib.make_datas.make(res, shader_name, json_data, fp, defs)

    path = fp + '/compiled/Shaders'
    c = json_data['contexts'][0]
    for s in ['vertex_shader', 'fragment_shader', 'geometry_shader', 'tesscontrol_shader', 'tesseval_shader']:
        if s in c:
            shutil.copy(c[s], path + '/' + c[s].split('/')[-1])

def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def export_data(fp, sdk_path):
    global exporter
    wrd = bpy.data.worlds['Arm']

    print('\nArmory v{0} ({1})'.format(wrd.arm_version, wrd.arm_commit))
    print('OS: ' + arm.utils.get_os() + ', Target: ' + state.target + ', GAPI: ' + arm.utils.get_gapi() + ', Blender: ' + bpy.app.version_string)

    # Clean compiled variants if cache is disabled
    build_dir = arm.utils.get_fp_build()
    if wrd.arm_cache_build == False:
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

    raw_shaders_path = sdk_path + '/armory/Shaders/'
    assets_path = sdk_path + '/armory/Assets/'
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
    ArmoryExporter.compress_enabled = state.is_publish and wrd.arm_asset_compression
    ArmoryExporter.optimize_enabled = state.is_publish and wrd.arm_optimize_data
    for scene in bpy.data.scenes:
        if scene.arm_export:
            ext = '.zip' if ArmoryExporter.compress_enabled else '.arm'
            asset_path = build_dir + '/compiled/Assets/' + arm.utils.safestr(scene.name) + ext
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

    modules = []
    if wrd.arm_audio == 'Enabled':
        modules.append('audio')
    if export_physics:
        modules.append('physics')
    if export_navigation:
        modules.append('navigation')
    if export_ui:
        modules.append('ui')
    if wrd.arm_hscript == 'Enabled':
        modules.append('hscript')
    if wrd.arm_formatlib == 'Enabled':
        modules.append('format')
    print('Exported modules: ' + str(modules))

    defs = arm.utils.def_strings_to_array(wrd.world_defs)
    cdefs = arm.utils.def_strings_to_array(wrd.compo_defs)
    print('Shader flags: ' + str(defs))
    if wrd.arm_debug_console:
        print('Khafile flags: ' + str(assets.khafile_defs))

    # Write compiled.inc
    shaders_path = build_dir + '/compiled/Shaders'
    if not os.path.exists(shaders_path):
        os.makedirs(shaders_path)
    write_data.write_compiledglsl(defs + cdefs)

    # Write referenced shader passes
    if wrd.arm_modding_mode != "Mod":
        if not os.path.isfile(build_dir + '/compiled/Shaders/shader_datas.arm') or state.last_world_defs != wrd.world_defs:
            res = {}
            res['shader_datas'] = []
            for ref in assets.shader_passes:
                # Ensure shader pass source exists
                if not os.path.exists(raw_shaders_path + '/' + ref):
                    continue
                assets.shader_passes_assets[ref] = []
                if ref.startswith('compositor_pass'):
                    compile_shader_pass(res, raw_shaders_path, ref, defs + cdefs)
                # elif ref.startswith('grease_pencil'):
                    # compile_shader_pass(res, raw_shaders_path, ref, [])
                else:
                    compile_shader_pass(res, raw_shaders_path, ref, defs)
            arm.utils.write_arm(shaders_path + '/shader_datas.arm', res)
        for ref in assets.shader_passes:
            for s in assets.shader_passes_assets[ref]:
                assets.add_shader(shaders_path + '/' + s + '.glsl')
        for file in assets.shaders_external:
            name = file.split('/')[-1].split('\\')[-1]
            target = build_dir + '/compiled/Shaders/' + name
            if not os.path.exists(target):
                shutil.copy(file, target)
    state.last_world_defs = wrd.world_defs

    # Reset path
    os.chdir(fp)

    # Copy std shaders
    if not os.path.isdir(build_dir + '/compiled/Shaders/std'):
        shutil.copytree(raw_shaders_path + 'std', build_dir + '/compiled/Shaders/std')

    # Write config.arm
    resx, resy = arm.utils.get_render_resolution(arm.utils.get_active_scene())
    if wrd.arm_write_config:
        write_data.write_config(resx, resy)

    # Write khafile.js
    enable_dce = state.is_publish and wrd.arm_dce
    import_logic = not state.is_publish and arm.utils.logic_editor_space() != None
    write_data.write_khafilejs(state.is_play, export_physics, export_navigation, export_ui, state.is_publish, enable_dce, state.is_viewport, ArmoryExporter.import_traits, import_logic)

    # Write Main.hx - depends on write_khafilejs for writing number of assets
    scene_name = arm.utils.get_project_scene_name()
    write_data.write_mainhx(scene_name, resx, resy, state.is_play, state.is_viewport, state.is_publish)
    if scene_name != state.last_scene or resx != state.last_resx or resy != state.last_resy:
        wrd.arm_recompile = True
        state.last_resx = resx
        state.last_resy = resy
        state.last_scene = scene_name

def compile(assets_only=False):
    wrd = bpy.data.worlds['Arm']
    fp = arm.utils.get_fp()
    os.chdir(fp)

    # Set build command
    target_name = state.target

    node_path = arm.utils.get_node_path()
    khamake_path = arm.utils.get_khamake_path()
    cmd = [node_path, khamake_path]

    kha_target_name = arm.utils.get_kha_target(target_name)
    if kha_target_name != '':
        cmd.append(kha_target_name)

    # Custom exporter
    if state.is_export:
        item = wrd.arm_exporterlist[wrd.arm_exporterlist_index]
        if item.arm_project_target == 'custom' and item.arm_project_khamake != '':
            for s in item.arm_project_khamake.split(' '):
                cmd.append(s)

    ffmpeg_path = arm.utils.get_ffmpeg_path() # Path to binary
    if ffmpeg_path != '':
        cmd.append('--ffmpeg')
        cmd.append(ffmpeg_path) # '"' + ffmpeg_path + '"'

    state.export_gapi = arm.utils.get_gapi()
    cmd.append('-g')
    cmd.append(state.export_gapi)

    if arm.utils.get_legacy_shaders() and not state.is_viewport:
        cmd.append('--shaderversion')
        cmd.append('110')
    elif 'android' in state.target or 'ios' in state.target or 'html5' in state.target:
        cmd.append('--shaderversion')
        cmd.append('300')
    else:
        cmd.append('--shaderversion')
        cmd.append('330')

    if '_VR' in wrd.world_defs:
        cmd.append('--vr')
        cmd.append('webvr')

    if arm.utils.get_rp().rp_renderer == 'Raytracer':
        cmd.append('--raytrace')
        cmd.append('dxr')
        dxc_path = fp + '/HlslShaders/fxc.exe'
        subprocess.Popen([dxc_path, '-Zpr', '-Fo', fp + '/Bundled/pt_raygeneration.o', '-T', 'lib_6_1', fp + '/HlslShaders/pt_raygeneration.hlsl'])
        subprocess.Popen([dxc_path, '-Zpr', '-Fo', fp + '/Bundled/pt_closesthit.o', '-T', 'lib_6_1', fp + '/HlslShaders/pt_closesthit.hlsl'])
        subprocess.Popen([dxc_path, '-Zpr', '-Fo', fp + '/Bundled/pt_miss.o', '-T', 'lib_6_1', fp + '/HlslShaders/pt_miss.hlsl'])

    if arm.utils.get_khamake_threads() > 1:
        cmd.append('--parallelAssetConversion')
        cmd.append(str(arm.utils.get_khamake_threads()))

    cmd.append('--to')
    if (kha_target_name == 'krom' and not state.is_viewport and not state.is_publish) or (kha_target_name == 'html5' and not state.is_publish):
        cmd.append(arm.utils.build_dir() + '/debug')
    else:
        cmd.append(arm.utils.build_dir())

    if assets_only:
        cmd.append('--nohaxe')
        cmd.append('--noproject')

    print("Running: ", cmd)
    print("Using project from " + arm.utils.get_fp())
    state.proc_build = run_proc(cmd, build_done)

def build_viewport():
    if state.proc_build != None:
        return

    if not arm.utils.check_saved(None):
        return

    if not arm.utils.check_sdkpath(None):
        return

    arm.utils.check_default_props()

    assets.invalidate_enabled = False
    play(is_viewport=True)
    assets.invalidate_enabled = True

def build(target, is_play=False, is_publish=False, is_viewport=False, is_export=False):
    global profile_time
    profile_time = time.time()

    state.target = target
    state.is_play = is_play
    state.is_publish = is_publish
    state.is_viewport = is_viewport
    state.is_export = is_export

    # Save blend
    if arm.utils.get_save_on_build():
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
    wrd = bpy.data.worlds['Arm']
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
    export_data(fp, sdk_path)

    if state.target == 'html5':
        w, h = arm.utils.get_render_resolution(arm.utils.get_active_scene())
        write_data.write_indexhtml(w, h, is_publish)
        # Bundle files from include dir
        if os.path.isdir('include'):
            dest  = '/html5/' if is_publish else '/debug/html5/'
            for fn in glob.iglob(os.path.join('include', '**'), recursive=False):
                shutil.copy(fn, arm.utils.build_dir() + dest + os.path.basename(fn))

def play_done():
    state.proc_play = None
    state.redraw_ui = True
    log.clear()

def build_done():
    print('Finished in ' + str(time.time() - profile_time))
    if state.proc_build == None:
        return
    result = state.proc_build.poll()
    state.proc_build = None
    state.redraw_ui = True
    if result == 0:
        bpy.data.worlds['Arm'].arm_recompile = False
        build_success()
    else:
        log.print_info('Build failed, check console')

def runtime_to_target(is_viewport):
    wrd = bpy.data.worlds['Arm']
    if is_viewport or wrd.arm_runtime == 'Krom':
        return 'krom'
    else:
        return 'html5'

def get_khajs_path(is_viewport, target):
    if is_viewport:
        return arm.utils.build_dir() + '/krom/krom.js'
    elif target == 'krom':
        return arm.utils.build_dir() + '/debug/krom/krom.js'
    else: # Browser
        return arm.utils.build_dir() + '/debug/html5/kha.js'

def play(is_viewport):
    global scripts_mtime
    global code_parsed
    wrd = bpy.data.worlds['Arm']

    log.clear()

    build(target=runtime_to_target(is_viewport), is_play=True, is_viewport=is_viewport)

    khajs_path = get_khajs_path(is_viewport, state.target)
    if not wrd.arm_cache_build or \
       not os.path.isfile(khajs_path) or \
       assets.khafile_defs_last != assets.khafile_defs or \
       state.last_target != state.target or \
       state.last_is_viewport != state.is_viewport:
        wrd.arm_recompile = True

    state.last_target = state.target
    state.last_is_viewport = state.is_viewport

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

    compile(assets_only=(not wrd.arm_recompile))

def build_success():
    log.clear()
    wrd = bpy.data.worlds['Arm']

    if wrd.arm_modding_mode != 'None':
        # Copy built shaders to the Krom dir
        src_dir = os.path.join(arm.utils.get_fp_build(), 'debug/krom-resources')
        target_dir = os.path.join(arm.utils.get_fp_build(), 'debug/krom/shaders')
        shutil.rmtree(target_dir, ignore_errors=True)
        os.rename(src_dir, target_dir)

        if wrd.arm_modding_mode == "Mod" and not state.is_publish and wrd.arm_runtime == 'Krom':
            # Copy the mod dir to parent game mod dir
            src_dir = os.path.join(arm.utils.get_fp_build(), 'debug/krom')
            game_blend_path = Path(wrd.arm_modding_game_blend.replace('//', ''))
            game_build_dir = 'build_' + arm.utils.safestr(game_blend_path.stem)
            mod_dir = os.path.join(str(game_blend_path.parent), game_build_dir, 'debug/krom/', wrd.arm_modding_folder)
            os.makedirs(mod_dir, exist_ok=True)
            target_dir = os.path.join(mod_dir, wrd.arm_project_package)
            shutil.rmtree(target_dir, ignore_errors=True)
            shutil.copytree(src_dir, target_dir)
            print('Mod was built and installed at: "', target_dir, '"')
            return

    if state.is_play:
        if wrd.arm_runtime == 'Browser':
            # Start server
            os.chdir(arm.utils.get_fp())
            t = threading.Thread(name='localserver', target=arm.lib.server.run)
            t.daemon = True
            t.start()
            html5_app_path = 'http://localhost:8040/' + arm.utils.build_dir() + '/debug/html5'
            webbrowser.open(html5_app_path)
        elif wrd.arm_runtime == 'Krom':
            if arm.utils.get_os() == 'win':
                bin_ext = '' if state.export_gapi == 'direct3d11' else '_' + state.export_gapi
            else:
                bin_ext = '' if state.export_gapi == 'opengl' else '_' + state.export_gapi
            krom_location, krom_path = arm.utils.krom_paths(bin_ext=bin_ext)
            os.chdir(krom_location)
            cmd = [krom_path, arm.utils.get_fp_build() + '/debug/krom', arm.utils.get_fp_build() + '/debug/krom-resources']
            if arm.utils.get_os() == 'win':
                cmd.append('--consolepid')
                cmd.append(str(os.getpid()))
                cmd.append('--sound')
            elif arm.utils.get_os() == 'mac' or arm.utils.get_os() == 'linux': # TODO: Wait for new Krom audio
                pass
            state.proc_play = run_proc(cmd, play_done)

    elif state.is_publish:
        sdk_path = arm.utils.get_sdk_path()
        target_name = arm.utils.get_kha_target(state.target)
        files_path = arm.utils.get_fp_build() + '/' + target_name

        if (target_name == 'html5' or target_name == 'krom') and wrd.arm_minify_js:
            # Minify JS
            minifier_path = sdk_path + '/lib/armory_tools/uglifyjs/bin/uglifyjs'
            if target_name == 'html5':
                jsfile = files_path + '/kha.js'
            else:
                jsfile = files_path + '/krom.js'
            args = [arm.utils.get_node_path(), minifier_path, jsfile, '-o', jsfile]
            proc = subprocess.Popen(args)
            proc.wait()

        if target_name == 'krom':
            # Clean up
            mapfile = files_path + '/krom.js.temp.map'
            if os.path.exists(mapfile):
                os.remove(mapfile)
            # Copy Krom binaries
            if state.target == 'krom-windows':
                gapi = state.export_gapi
                ext = '' if gapi == 'direct3d11' else '_' + gapi
                krom_location = sdk_path + '/Krom/Krom' + ext + '.exe'
                shutil.copy(krom_location, files_path + '/Krom.exe')
                os.rename(files_path + '/Krom.exe', files_path + '/' + arm.utils.safestr(wrd.arm_project_name) + '.exe')
            elif state.target == 'krom-linux':
                krom_location = sdk_path + '/Krom/Krom'
                shutil.copy(krom_location, files_path)
                os.rename(files_path + '/Krom', files_path + '/' + arm.utils.safestr(wrd.arm_project_name))
            else:
                krom_location = sdk_path + '/Krom/Krom.app'
                shutil.copytree(krom_location, files_path + '/Krom.app')
                game_files = os.listdir(files_path)
                for f in game_files:
                    f = files_path + '/' + f
                    if os.path.isfile(f):
                        shutil.move(f, files_path + '/Krom.app/Contents/MacOS')
                os.rename(files_path + '/Krom.app', files_path + '/' + arm.utils.safestr(wrd.arm_project_name) + '.app')
            # Rename
            ext = state.target.split('-')[-1] # krom-windows
            new_files_path = files_path + '-' + ext
            os.rename(files_path, new_files_path)
            files_path = new_files_path
        
        if target_name == 'html5':
            print('Exported HTML5 package to ' + files_path)
        elif target_name.startswith('ios') or target_name.startswith('osx'): # TODO: to macos
            print('Exported XCode project to ' + files_path + '-build')
        elif target_name.startswith('windows'):
            print('Exported Visual Studio 2017 project to ' + files_path + '-build')
        elif target_name.startswith('android-native'):
            print('Exported Android Studio project to ' + files_path + '-build/' + arm.utils.safestr(wrd.arm_project_name))
        elif target_name.startswith('krom'):
            print('Exported Krom package to ' + files_path)
        else:
            print('Exported makefiles to ' + files_path + '-build')

def clean():
    os.chdir(arm.utils.get_fp())
    wrd = bpy.data.worlds['Arm']

    # Remove build and compiled data
    try:
        if os.path.isdir(arm.utils.build_dir()):
            shutil.rmtree(arm.utils.build_dir(), onerror=remove_readonly)
        if os.path.isdir(arm.utils.get_fp() + '/build'): # Kode Studio build dir
            shutil.rmtree(arm.utils.get_fp() + '/build', onerror=remove_readonly)
    except:
        print('Armory Warning: Some files in the build folder are locked')

    # Remove compiled nodes
    pkg_dir = arm.utils.safestr(wrd.arm_project_package).replace('.', '/')
    nodes_path = 'Sources/' + pkg_dir + '/node/'
    if os.path.isdir(nodes_path):
        shutil.rmtree(nodes_path, onerror=remove_readonly)

    # Remove khafile/korefile/Main.hx
    if os.path.isfile('khafile.js'):
        os.remove('khafile.js')
    if os.path.isfile('korefile.js'):
        os.remove('korefile.js')
    if os.path.isfile('Sources/Main.hx'):
        os.remove('Sources/Main.hx')

    # Remove Sources/ dir if empty
    if os.path.exists('Sources/' + pkg_dir) and os.listdir('Sources/' + pkg_dir) == []:
        shutil.rmtree('Sources/' + pkg_dir, onerror=remove_readonly)
        if os.path.exists('Sources') and os.listdir('Sources') == []:
            shutil.rmtree('Sources/', onerror=remove_readonly)

    # To recache signatures for batched materials
    for mat in bpy.data.materials:
        mat.signature = ''
        mat.arm_cached = False

    print('Project cleaned')
