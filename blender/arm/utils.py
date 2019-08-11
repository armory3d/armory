import bpy
import json
import os
import glob
import platform
import re
import subprocess
import webbrowser
import numpy as np
import arm.lib.armpack
import arm.make_state as state
import arm.log as log

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def write_arm(filepath, output):
    if filepath.endswith('.lz4'):
        pass
    else:
        if bpy.data.worlds['Arm'].arm_minimize:
            with open(filepath, 'wb') as f:
                f.write(arm.lib.armpack.packb(output))
        else:
            filepath_json = filepath.split('.arm')[0] + '.json'
            with open(filepath_json, 'w') as f:
                f.write(json.dumps(output, sort_keys=True, indent=4, cls=NumpyEncoder))

def unpack_image(image, path, file_format='JPEG'):
    print('Armory Info: Unpacking to ' + path)
    image.filepath_raw = path
    image.file_format = file_format
    image.save()

def convert_image(image, path, file_format='JPEG'):
    # Convert image to compatible format
    print('Armory Info: Converting to ' + path)
    ren = bpy.context.scene.render
    orig_quality = ren.image_settings.quality
    orig_file_format = ren.image_settings.file_format
    orig_color_mode = ren.image_settings.color_mode
    ren.image_settings.quality = 90
    ren.image_settings.file_format = file_format
    if file_format == 'PNG':
        ren.image_settings.color_mode = 'RGBA'
    image.save_render(path, scene=bpy.context.scene)
    ren.image_settings.quality = orig_quality
    ren.image_settings.file_format = orig_file_format
    ren.image_settings.color_mode = orig_color_mode

def blend_name():
    return bpy.path.basename(bpy.context.blend_data.filepath).rsplit('.')[0]

def build_dir():
    return 'build_' + safestr(blend_name())

def get_fp():
    wrd = bpy.data.worlds['Arm']
    if wrd.arm_project_root != '':
        return bpy.path.abspath(wrd.arm_project_root)
    else:
        s = bpy.data.filepath.split(os.path.sep)
        s.pop()
        return os.path.sep.join(s)

def get_fp_build():
    return get_fp() + '/' + build_dir()

def get_os():
    s = platform.system()
    if s == 'Windows':
        return 'win'
    elif s == 'Darwin':
        return 'mac'
    else:
        return 'linux'

def get_gapi():
    wrd = bpy.data.worlds['Arm']
    if state.is_export:
        item = wrd.arm_exporterlist[wrd.arm_exporterlist_index]
        return getattr(item, target_to_gapi(item.arm_project_target))
    if wrd.arm_runtime == 'Browser':
        return 'webgl'
    return 'direct3d11' if get_os() == 'win' else 'opengl'

def get_rp():
    wrd = bpy.data.worlds['Arm']
    return wrd.arm_rplist[wrd.arm_rplist_index]

def bundled_sdk_path():
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

# Passed by load_post handler when armsdk is found in project folder
use_local_sdk = False
def get_sdk_path():
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons["armory"].preferences
    p = bundled_sdk_path()
    if use_local_sdk:
        return get_fp() + '/armsdk/'
    elif os.path.exists(p) and addon_prefs.sdk_bundled:
        return p
    else:
        return addon_prefs.sdk_path

def get_ide_path():
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons["armory"].preferences
    return '' if not hasattr(addon_prefs, 'ide_path') else addon_prefs.ide_path

def get_ffmpeg_path():
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons['armory'].preferences
    return addon_prefs.ffmpeg_path

def get_renderdoc_path():
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons['armory'].preferences
    p = addon_prefs.renderdoc_path
    if p == '' and get_os() == 'win':
        pdefault = 'C:\\Program Files\\RenderDoc\\qrenderdoc.exe'
        if os.path.exists(pdefault):
            p = pdefault
    return p

def get_code_editor():
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons['armory'].preferences
    return 'kodestudio' if not hasattr(addon_prefs, 'code_editor') else addon_prefs.code_editor

def get_ui_scale():
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons['armory'].preferences
    return 1.0 if not hasattr(addon_prefs, 'ui_scale') else addon_prefs.ui_scale

def get_khamake_threads():
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons['armory'].preferences
    return 1 if not hasattr(addon_prefs, 'khamake_threads') else addon_prefs.khamake_threads

def get_compilation_server():
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons['armory'].preferences
    return False if not hasattr(addon_prefs, 'compilation_server') else addon_prefs.compilation_server

def get_save_on_build():
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons['armory'].preferences
    return False if not hasattr(addon_prefs, 'save_on_build') else addon_prefs.save_on_build

def get_viewport_controls():
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons['armory'].preferences
    return 'qwerty' if not hasattr(addon_prefs, 'viewport_controls') else addon_prefs.viewport_controls

def get_legacy_shaders():
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons['armory'].preferences
    return False if not hasattr(addon_prefs, 'legacy_shaders') else addon_prefs.legacy_shaders

def get_relative_paths():
    # Convert absolute paths to relative
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons['armory'].preferences
    return False if not hasattr(addon_prefs, 'relative_paths') else addon_prefs.relative_paths

def get_node_path():
    if get_os() == 'win':
        return get_sdk_path() + '/nodejs/node.exe'
    elif get_os() == 'mac':
        return get_sdk_path() + '/nodejs/node-osx'
    else:
        return get_sdk_path() + '/nodejs/node-linux64'

def get_kha_path():
    if os.path.exists('Kha'):
        return 'Kha'
    return get_sdk_path() + '/Kha'

def get_haxe_path():
    if get_os() == 'win':
        return get_kha_path() + '/Tools/haxe/haxe.exe'
    elif get_os() == 'mac':
        return get_kha_path() + '/Tools/haxe/haxe-osx'
    else:
        return get_kha_path() + '/Tools/haxe/haxe-linux64'

def get_khamake_path():
    return get_kha_path() + '/make'

def krom_paths():
    sdk_path = get_sdk_path()
    if arm.utils.get_os() == 'win':
        krom_location = sdk_path + '/Krom'
        krom_path = krom_location + '/Krom.exe'
    elif arm.utils.get_os() == 'mac':
        krom_location = sdk_path + '/Krom/Krom.app/Contents/MacOS'
        krom_path = krom_location + '/Krom'
    else:
        krom_location = sdk_path + '/Krom'
        krom_path = krom_location + '/Krom'
    return krom_location, krom_path

def fetch_bundled_script_names():
    wrd = bpy.data.worlds['Arm']
    wrd.arm_bundled_scripts_list.clear()
    os.chdir(get_sdk_path() + '/armory/Sources/armory/trait')
    for file in glob.glob('*.hx'):
        wrd.arm_bundled_scripts_list.add().name = file.rsplit('.')[0]

script_props = {}
script_props_defaults = {}
def fetch_script_props(file):
    with open(file) as f:
        name = file.rsplit('.')[0]
        if 'Sources' in name:
            name = name[name.index('Sources')+8:]
        if '/' in name:
            name = name.replace('/','.')
        if '\\' in file:
            name = name.replace('\\','.')
        script_props[name] = []
        script_props_defaults[name] = []
        lines = f.read().splitlines()
        read_prop = False
        for l in lines:
            if not read_prop:
                read_prop = l.lstrip().startswith('@prop')
            if read_prop and 'var ' in l:
                p = l.split('var ')[1]

                valid_prop = False
                # Has type
                if ':' in p:
                    # Fetch default value
                    if '=' in p:
                        s = p.split('=')
                        ps = s[0].split(':')
                        prop = (ps[0].strip(), ps[1].split(';')[0].strip())
                        prop_value = s[1].split(';')[0].replace('\'', '').replace('"', '').strip()
                        valid_prop = True
                    else:
                        ps = p.split(':')
                        prop = (ps[0].strip(), ps[1].split(';')[0].strip())
                        prop_value = ''
                        valid_prop = True
                # Fetch default value
                elif '=' in p:
                    s = p.split('=')
                    prop = (s[0].strip(), None)
                    prop_value = s[1].split(';')[0].replace('\'', '').replace('"', '').strip()
                    valid_prop = True
                # Register prop
                if valid_prop:
                    script_props[name].append(prop)
                    script_props_defaults[name].append(prop_value)

                read_prop = False

def fetch_script_names():
    if bpy.data.filepath == "":
        return
    wrd = bpy.data.worlds['Arm']
    # Sources
    wrd.arm_scripts_list.clear()
    sources_path = get_fp() + '/Sources/' + safestr(wrd.arm_project_package)
    if os.path.isdir(sources_path):
        os.chdir(sources_path)
        # Glob supports recursive search since python 3.5 so it should cover both blender 2.79 and 2.8 integrated python
        for file in glob.glob('**/*.hx', recursive=True):
            name = file.rsplit('.')[0]
            # Replace the path syntax for package syntax so that it can be searchable in blender traits "Class" dropdown
            wrd.arm_scripts_list.add().name = name.replace(os.sep, '.')
            fetch_script_props(file)

    # Canvas
    wrd.arm_canvas_list.clear()
    canvas_path = get_fp() + '/Bundled/canvas'
    if os.path.isdir(canvas_path):
        os.chdir(canvas_path)
        for file in glob.glob('*.json'):
            wrd.arm_canvas_list.add().name = file.rsplit('.')[0]
    os.chdir(get_fp())

def fetch_wasm_names():
    if bpy.data.filepath == "":
        return
    wrd = bpy.data.worlds['Arm']
    # WASM modules
    wrd.arm_wasm_list.clear()
    sources_path = get_fp() + '/Bundled'
    if os.path.isdir(sources_path):
        os.chdir(sources_path)
        for file in glob.glob('*.wasm'):
            name = file.rsplit('.')[0]
            wrd.arm_wasm_list.add().name = name
    os.chdir(get_fp())

def fetch_trait_props():
    for o in bpy.data.objects:
        fetch_prop(o)
    for s in bpy.data.scenes:
        fetch_prop(s)

def fetch_prop(o):
    for item in o.arm_traitlist:
        name = ''
        if item.type_prop == 'Bundled Script':
            name = 'armory.trait.' + item.name
        else:
            name = item.name
        if name not in script_props:
            continue
        props = script_props[name]
        defaults = script_props_defaults[name]
        # Remove old props
        for i in range(len(item.arm_traitpropslist) - 1, -1, -1):
            ip = item.arm_traitpropslist[i]
            # if ip.name not in props:
            if ip.name.split('(')[0] not in [p[0] for p in props]:
                item.arm_traitpropslist.remove(i)
        # Add new props
        for i in range(0, len(props)):
            p = props[i]
            found = False
            for ip in item.arm_traitpropslist:
                if ip.name.replace(')', '').split('(')[0] == p[0]:
                    found = ip
                    break
            # Not in list
            if not found:
                prop = item.arm_traitpropslist.add()
                prop.name = p[0] + ('(' + p[1] + ')' if p[1] else '')
                prop.value = defaults[i]

            if found:
                prop = item.arm_traitpropslist[found.name]
                f = found.name.replace(')', '').split('(')

                # Default value added and current value is blank (no override)
                if (not found.value and defaults[i]):
                    prop.value = defaults[i]
                # Type has changed, update displayed name
                if (len(f) == 1 or (len(f) > 1 and f[1] != p[1])):
                    prop.name = p[0] + ('(' + p[1] + ')' if p[1] else '')

def fetch_bundled_trait_props():
    # Bundled script props
    for o in bpy.data.objects:
        for t in o.arm_traitlist:
            if t.type_prop == 'Bundled Script':
                file_path = get_sdk_path() + '/armory/Sources/armory/trait/' + t.name + '.hx'
                if os.path.exists(file_path):
                    fetch_script_props(file_path)
                    fetch_prop(o)

def update_trait_collections():
    for col in bpy.data.collections:
        if col.name.startswith('Trait|'):
            bpy.data.collections.remove(col)
    for o in bpy.data.objects:
        for t in o.arm_traitlist:
            if 'Trait|' + t.name not in bpy.data.collections:
                col = bpy.data.collections.new('Trait|' + t.name)
            else:
                col = bpy.data.collections['Trait|' + t.name]
            col.objects.link(o)

def to_hex(val):
    return '#%02x%02x%02x%02x' % (int(val[3] * 255), int(val[0] * 255), int(val[1] * 255), int(val[2] * 255))

def color_to_int(val):
    return (int(val[3] * 255) << 24) + (int(val[0] * 255) << 16) + (int(val[1] * 255) << 8) + int(val[2] * 255)

def safesrc(s):
    s = safestr(s).replace('.', '_').replace('-', '_').replace(' ', '')
    if s[0].isdigit():
        s = '_' + s
    return s

def safestr(s):
    for c in r'[]/\;,><&*:%=+@!#^()|?^':
        s = s.replace(c, '_')
    return ''.join([i if ord(i) < 128 else '_' for i in s])

def asset_name(bdata):
    s = bdata.name
    # Append library name if linked
    if bdata.library != None:
        s += '_' + bdata.library.name
    return s

def asset_path(s):
    return s[2:] if s[:2] == '//' else s # Remove leading '//'

def extract_filename(s):
    return os.path.basename(asset_path(s))

def get_render_resolution(scene):
    render = scene.render
    scale = render.resolution_percentage / 100
    return int(render.resolution_x * scale), int(render.resolution_y * scale)

def get_project_scene_name():
    return get_active_scene().name

def get_active_scene():
    if not state.is_export:
        return bpy.context.scene
    else:
        wrd = bpy.data.worlds['Arm']
        item = wrd.arm_exporterlist[wrd.arm_exporterlist_index]
        return item.arm_project_scene

def logic_editor_space(context_screen=None):
    if context_screen == None:
        context_screen = bpy.context.screen
    if context_screen != None:
        areas = context_screen.areas
        for area in areas:
            for space in area.spaces:
                if space.type == 'NODE_EDITOR':
                    if space.node_tree != None and space.node_tree.bl_idname == 'ArmLogicTreeType':
                        return space
    return None

def voxel_support():
    # macos does not support opengl 4.5, needs metal
    return state.target != 'html5' and get_os() != 'mac'

def get_cascade_size(rpdat):
    cascade_size = int(rpdat.rp_shadowmap_cascade)
    # Clamp to 4096 per cascade
    if int(rpdat.rp_shadowmap_cascades) > 1 and cascade_size > 4096:
        cascade_size = 4096
    return cascade_size

def check_saved(self):
    if bpy.data.filepath == "":
        msg = "Save blend file first"
        self.report({"ERROR"}, msg) if self != None else log.print_info(msg)
        return False
    return True

def check_path(s):
    for c in r'[];><&*%=+@!#^()|?^':
        if c in s:
            return False
    for c in s:
        if ord(c) > 127:
            return False
    return True

def check_sdkpath(self):
    s = get_sdk_path()
    if check_path(s) == False:
        msg = "SDK path '{0}' contains special characters. Please move SDK to different path for now.".format(s)
        self.report({"ERROR"}, msg) if self != None else log.print_info(msg)
        return False
    else:
        return True

def check_projectpath(self):
    s = get_fp()
    if check_path(s) == False:
        msg = "Project path '{0}' contains special characters, build process may fail.".format(s)
        self.report({"ERROR"}, msg) if self != None else log.print_info(msg)
        return False
    else:
        return True

def disp_enabled(target):
    rpdat = get_rp()
    if rpdat.arm_rp_displacement == 'Tessellation':
        return target == 'krom' or target == 'native'
    return rpdat.arm_rp_displacement != 'Off'

def is_object_animation_enabled(bobject):
    # Checks if animation is present and enabled
    if bobject.arm_animation_enabled == False or bobject.type == 'BONE' or bobject.type == 'ARMATURE':
        return False
    if bobject.animation_data and bobject.animation_data.action:
        return True
    return False

def is_bone_animation_enabled(bobject):
    # Checks if animation is present and enabled for parented armature
    if bobject.parent and bobject.parent.type == 'ARMATURE':
        if bobject.parent.arm_animation_enabled == False:
            return False
        # Check for present actions
        adata = bobject.parent.animation_data
        has_actions = adata != None and adata.action != None
        if not has_actions and adata != None:
            if hasattr(adata, 'nla_tracks') and adata.nla_tracks != None:
                for track in adata.nla_tracks:
                    if track.strips == None:
                        continue
                    for strip in track.strips:
                        if strip.action == None:
                            continue
                        has_actions = True
                        break
                    if has_actions:
                        break
        if adata != None and has_actions:
            return True
    return False

def export_bone_data(bobject):
    return bobject.find_armature() and is_bone_animation_enabled(bobject) and get_rp().arm_skin == 'On'

def kode_studio_mklink_win(sdk_path, ide_path):
    # Fight long-path issues on Windows
    if not os.path.exists(ide_path + '/resources/app/kodeExtensions/kha/Kha'):
        source = ide_path + '/resources/app/kodeExtensions/kha/Kha'
        target = sdk_path + '/Kha'
        subprocess.check_call('mklink /J "%s" "%s"' % (source, target), shell=True)
    if not os.path.exists(ide_path + '/resources/app/kodeExtensions/krom/Krom'):
        source = ide_path + '/resources/app/kodeExtensions/krom/Krom'
        target = sdk_path + '/Krom'
        subprocess.check_call('mklink /J "%s" "%s"' % (source, target), shell=True)

def kode_studio_mklink_linux(sdk_path, ide_path):
    if not os.path.exists(ide_path + '/resources/app/kodeExtensions/kha/Kha'):
        source = ide_path + '/resources/app/kodeExtensions/kha/Kha'
        target = sdk_path + '/Kha'
        subprocess.check_call('ln -s "%s" "%s"' % (target, source), shell=True)
    if not os.path.exists(ide_path + '/resources/app/kodeExtensions/krom/Krom'):
        source = ide_path + '/resources/app/kodeExtensions/krom/Krom'
        target = sdk_path + '/Krom'
        subprocess.check_call('ln -s "%s" "%s"' % (target, source), shell=True)

def kode_studio_mklink_mac(sdk_path, ide_path):
    if not os.path.exists(ide_path + '/Contents/Resources/app/kodeExtensions/kha/Kha'):
        source = ide_path + '/Contents/Resources/app/kodeExtensions/kha/Kha'
        target = sdk_path + '/Kha'
        subprocess.check_call('ln -fs "%s" "%s"' % (target, source), shell=True)
    if not os.path.exists(ide_path + '/Contents/Resources/app/kodeExtensions/krom/Krom'):
        source = ide_path + '/Contents/Resources/app/kodeExtensions/krom/Krom'
        target = sdk_path + '/Krom'
        subprocess.check_call('ln -fs "%s" "%s"' % (target, source), shell=True)

def get_kode_path():
    p = get_ide_path()
    if p == '':
        if get_os() == 'win':
            p = get_sdk_path() + '/win32'
        elif get_os() == 'mac':
            p = get_sdk_path() + '/KodeStudio.app'
        else:
            p = get_sdk_path() + '/linux64'
    return p

def get_kode_bin():
    p = get_kode_path()
    if get_os() == 'win':
        return p + '/Kode Studio.exe'
    elif get_os() == 'mac':
        return p + '/Contents/MacOS/Electron'
    else:
        return p + '/kodestudio'

def get_vscode_bin():
    p = get_kode_path()
    if get_os() == 'win':
        return p + '/Code.exe'
    elif get_os() == 'mac':
        return p + '/Contents/MacOS/Electron'
    else:
        return p + '/code'

def kode_studio(hx_path=None):
    project_path = arm.utils.get_fp()
    kode_bin = get_kode_bin()
    if not os.path.exists(kode_bin):
        kode_bin = get_vscode_bin()
    if os.path.exists(kode_bin) and get_code_editor() == 'kodestudio':
        if arm.utils.get_os() == 'win':
            # kode_studio_mklink_win(get_sdk_path(), get_kode_path())
            args = [kode_bin, arm.utils.get_fp()]
            if hx_path != None:
                args.append(hx_path)
            subprocess.Popen(args)
        elif arm.utils.get_os() == 'mac':
            # kode_studio_mklink_mac(get_sdk_path(), get_kode_path())
            args = ['"' + kode_bin + '"' + ' "' + arm.utils.get_fp() + '"']
            if hx_path != None:
                args[0] += ' "' + hx_path + '"'
            subprocess.Popen(args, shell=True)
        else:
            # kode_studio_mklink_linux(get_sdk_path(), get_kode_path())
            args = [kode_bin, arm.utils.get_fp()]
            if hx_path != None:
                args.append(hx_path)
            subprocess.Popen(args)
    else:
        fp = hx_path if hx_path != None else arm.utils.get_fp()
        webbrowser.open('file://' + fp)

def def_strings_to_array(strdefs):
    defs = strdefs.split('_')
    defs = defs[1:]
    defs = ['_' + d for d in defs] # Restore _
    return defs

def get_kha_target(target_name): # TODO: remove
    if target_name == 'macos-hl':
        return 'osx-hl'
    elif target_name.startswith('krom'): # krom-windows
        return 'krom'
    elif target_name == 'custom':
        return ''
    return target_name

def target_to_gapi(arm_project_target):
    # TODO: align target names
    if arm_project_target == 'krom':
        return 'arm_gapi_' + arm.utils.get_os()
    elif arm_project_target == 'krom-windows':
        return 'arm_gapi_win'
    elif arm_project_target == 'windows-hl':
        return 'arm_gapi_win'
    elif arm_project_target == 'krom-linux':
        return 'arm_gapi_linux'
    elif arm_project_target == 'linux-hl':
        return 'arm_gapi_linux'
    elif arm_project_target == 'krom-macos':
        return 'arm_gapi_mac'
    elif arm_project_target == 'macos-hl':
        return 'arm_gapi_mac'
    elif arm_project_target == 'android-native-hl':
        return 'arm_gapi_android'
    elif arm_project_target == 'ios-hl':
        return 'arm_gapi_ios'
    elif arm_project_target == 'node':
        return 'arm_gapi_html5'
    else: # html5, custom
        return 'arm_gapi_' + arm_project_target

def check_default_props():
    wrd = bpy.data.worlds['Arm']
    if len(wrd.arm_rplist) == 0:
        wrd.arm_rplist.add()
        wrd.arm_rplist_index = 0

    if wrd.arm_project_name == '':
        # Take blend file name
        wrd.arm_project_name = arm.utils.blend_name()

def register(local_sdk=False):
    global use_local_sdk
    use_local_sdk = local_sdk

def unregister():
    pass
