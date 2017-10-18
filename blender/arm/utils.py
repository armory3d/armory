import bpy
import json
import os
import glob
import platform
import zipfile
import re
import arm.lib.armpack
import arm.make_state as state
import arm.make_utils as make_utils

def write_arm(filepath, output):
    if filepath.endswith('.zip'):
        with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            if bpy.data.worlds['Arm'].arm_minimize:
                zip_file.writestr('data.arm', arm.lib.armpack.packb(output))
            else:
                zip_file.writestr('data.arm', json.dumps(output, sort_keys=True, indent=4))
    else:
        if bpy.data.worlds['Arm'].arm_minimize:
            with open(filepath, 'wb') as f:
                f.write(arm.lib.armpack.packb(output))
        else:
            with open(filepath, 'w') as f:
                f.write(json.dumps(output, sort_keys=True, indent=4))

def write_image(image, path, file_format='JPEG'):
    # Convert image to compatible format
    print('Armory Info: Writing ' + path)
    ren = bpy.context.scene.render
    orig_quality = ren.image_settings.quality
    orig_file_format = ren.image_settings.file_format
    
    ren.image_settings.quality = 90
    ren.image_settings.file_format = file_format
    
    image.save_render(path, bpy.context.scene)
    
    ren.image_settings.quality = orig_quality
    ren.image_settings.file_format = orig_file_format

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
        return getattr(item, make_utils.target_to_gapi(item.arm_project_target))
    else:
        if wrd.arm_play_runtime == 'Browser':
            return 'webgl'
        else:
            return 'opengl'

def get_rp():
    wrd = bpy.data.worlds['Arm']
    return wrd.arm_rplist[wrd.arm_rplist_index]

def get_sdk_path():
    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons['armory'].preferences
    if with_krom() and addon_prefs.sdk_bundled:
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

def get_ffmpeg_path():
    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons['armory'].preferences
    return addon_prefs.ffmpeg_path

def get_ease_viewport_camera():
    return True

def get_save_on_build():
    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons['armory'].preferences
    return True if not hasattr(addon_prefs, 'save_on_build') else addon_prefs.save_on_build

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

    if get_os() == 'win':
        return get_sdk_path() + '/win32/Kha' # Using symlink on Windows
    elif get_os() == 'mac':
        return get_sdk_path() + '/Kode Studio.app/Contents/Resources/app/extensions/kha/Kha'
    else:
        return get_sdk_path() + '/linux64/resources/app/extensions/kha/Kha'

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
        krom_location = sdk_path + '/win32/Krom/win32' # Using symlink on Windows
        krom_path = krom_location + '/Krom.exe'
    elif arm.utils.get_os() == 'mac':
        krom_location = sdk_path + '/Kode Studio.app/Contents/Resources/app/extensions/krom/Krom/macos/Krom.app/Contents/MacOS'
        krom_path = krom_location + '/Krom'
    else:
        krom_location = sdk_path + '/linux64/resources/app/extensions/krom/Krom/linux'
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
        if '/' in file:
            file = file.split('/')[-1]
        if '\\' in file:
            file = file.split('\\')[-1]
        name = file.rsplit('.')[0]
        script_props[name] = []
        script_props_defaults[name] = []
        lines = f.read().splitlines()
        readprop = False
        for l in lines:
            if not readprop:
                readprop = '@prop' in l
            if readprop and 'var ' in l:
                p = l.split('var ')[1]
                if ':' in p:
                    if '=' in p: # Fetch default value
                        s = p.split('=')
                        v = s[1].split(';')[0].strip()
                    else:
                        v = ''
                    p = p.split(':')[0].strip()
                    script_props[name].append(p)
                    script_props_defaults[name].append(v)
                elif '=' in p:
                    s = p.split('=')
                    p = s[0].strip()
                    v = s[1].split(';')[0].strip()
                    script_props[name].append(p)
                    script_props_defaults[name].append(v)
                readprop = False

def fetch_script_names():
    if bpy.data.filepath == "":
        return
    wrd = bpy.data.worlds['Arm']
    # Sources
    wrd.arm_scripts_list.clear()
    sources_path = get_fp() + '/Sources/' + safestr(wrd.arm_project_package)
    if os.path.isdir(sources_path):
        os.chdir(sources_path)
        for file in glob.glob('*.hx'):
            name = file.rsplit('.')[0]
            wrd.arm_scripts_list.add().name = name
            fetch_script_props(file)

    # Canvas
    wrd.arm_canvas_list.clear()
    canvas_path = get_fp() + '/Bundled/canvas'
    if os.path.isdir(canvas_path):
        os.chdir(canvas_path)
        for file in glob.glob('*.json'):
            wrd.arm_canvas_list.add().name = file.rsplit('.')[0]
    os.chdir(get_fp())

def fetch_trait_props():
    for o in bpy.data.objects:
        for item in o.arm_traitlist:
            if item.name not in script_props:
                continue
            props = script_props[item.name]
            defaults = script_props_defaults[item.name]
            # Remove old props
            for i in range(len(item.arm_traitpropslist) - 1, -1, -1):
                ip = item.arm_traitpropslist[i]
                if ip.name not in props:
                    item.arm_traitpropslist.remove(i)
            # Add new props
            for i in range(0, len(props)):
                p = props[i]
                found = False
                for ip in item.arm_traitpropslist:
                    if ip.name == p:
                        found = True
                        break
                if not found:
                    prop = item.arm_traitpropslist.add()
                    prop.name = p
                    prop.value = defaults[i]

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
    wrd = bpy.data.worlds['Arm']
    if wrd.arm_play_active_scene:
        if bpy.app.version >= (2, 80, 1): # 2.8
            return bpy.context.scene.name
        else:
            return bpy.context.screen.scene.name
    else:
        return wrd.arm_project_scene

def get_active_scene():
    wrd = bpy.data.worlds['Arm']
    if bpy.app.version >= (2, 80, 1): # 2.8
        context_scene = bpy.context.scene
    else:
        context_scene = bpy.context.screen.scene
    return context_scene if wrd.arm_play_active_scene else bpy.data.scenes[wrd.arm_project_scene]

def logic_editor_space():
    if hasattr(bpy.context, 'window') and bpy.context.window != None:
        areas = bpy.context.window.screen.areas
        for area in areas:
            if area.type == 'NODE_EDITOR':
                for space in area.spaces:
                    if space.type == 'NODE_EDITOR':
                        if space.node_tree != None and space.node_tree.bl_idname == 'ArmLogicTreeType': # and space.node_tree.is_updated:
                            return space
    return None

krom_found = False
def with_krom():
    global krom_found
    return krom_found

glslver = 110
def glsl_version():
    global glslver
    return glslver

def check_saved(self):
    if bpy.data.filepath == "":
        self.report({"ERROR"}, "Save blend file first")
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
        self.report({"ERROR"}, "SDK path '{0}' contains special characters. Please move SDK to different path for now.".format(s))
        return False
    else:
        return True

def check_projectpath(self):
    s = get_fp()
    if check_path(s) == False:
        self.report({"WARNING"}, "Project path '{0}' contains special characters, build process may fail.".format(s))
        return False
    else:
        return True

def check_engine(self):
    if bpy.context == None or bpy.context.scene == None:
        return
    engine = bpy.context.scene.render.engine
    if engine != 'CYCLES' and engine != 'BLENDER_EEVEE':
        self.report({"ERROR"}, "Switch to Cycles or Eevee engine first")
        return False
    return True

def tess_enabled(target):
    rpdat = get_rp()
    return (target == 'krom' or target == 'native') and rpdat.arm_tessellation

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
        if bobject.parent.animation_data and bobject.parent.animation_data.action:
            return True
    return False

def export_bone_data(bobject):
    return bobject.find_armature() and is_bone_animation_enabled(bobject) and bpy.data.worlds['Arm'].arm_skin.startswith('GPU')

def register():
    global krom_found
    global glslver
    import importlib.util
    if importlib.util.find_spec('barmory') != None:
        krom_found = True
        import bgl
        glslver = int(bgl.glGetString(bgl.GL_SHADING_LANGUAGE_VERSION).split(' ', 1)[0].replace('.', ''))

def unregister():
    pass
