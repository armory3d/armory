import bpy
import json
import os
import glob
import lib.umsgpack
import platform
import zipfile
import re

def write_arm(filepath, output):
    if filepath.endswith('.zip'):
        with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            if bpy.data.worlds['Arm'].arm_minimize:
                zip_file.writestr('data.arm', lib.umsgpack.dumps(output))
            else:
                zip_file.writestr('data.arm', json.dumps(output, sort_keys=True, indent=4))
    else:
        if bpy.data.worlds['Arm'].arm_minimize:
            with open(filepath, 'wb') as f:
                f.write(lib.umsgpack.dumps(output))
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

def get_fp():
    s = bpy.data.filepath.split(os.path.sep)
    s.pop()
    return os.path.sep.join(s)

def get_os():
    s = platform.system()
    if s == 'Windows':
        return 'win'
    elif s == 'Darwin':
        return 'mac'
    else:
        return 'linux'

def get_sdk_path():
    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons['armory'].preferences
    if with_krom() and addon_prefs.sdk_bundled:
        if get_os() == 'mac':
            # SDK on MacOS is located in .app folder due to security
            # blender.app/Contents/MacOS/blender
            return bpy.app.binary_path[:-22] + '/armsdk/'
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

def fetch_script_names():
    if bpy.data.filepath == "":
        return

    sdk_path = get_sdk_path()
    wrd = bpy.data.worlds['Arm']
    wrd.bundled_scripts_list.clear()
    os.chdir(sdk_path + '/armory/Sources/armory/trait')
    for file in glob.glob('*.hx'):
        wrd.bundled_scripts_list.add().name = file.rsplit('.')[0]
    wrd.scripts_list.clear()
    sources_path = get_fp() + '/Sources/' + wrd.arm_project_package
    if os.path.isdir(sources_path):
        os.chdir(sources_path)
        for file in glob.glob('*.hx'):
            wrd.scripts_list.add().name = file.rsplit('.')[0]
    os.chdir(get_fp())

def to_hex(val):
    return '#%02x%02x%02x%02x' % (int(val[3] * 255), int(val[0] * 255), int(val[1] * 255), int(val[2] * 255))

def color_to_int(val):
    return (int(val[3] * 255) << 24) + (int(val[0] * 255) << 16) + (int(val[1] * 255) << 8) + int(val[2] * 255)

def safe_filename(s):
    return s

def safefilename(s):
    for c in r'[]/\;,><&*:%=+@!#^()|?^':
        s = s.replace(c, '-')
    return s

def safe_source_name(s):
    s = safefilename(s).replace('.', '_').replace('-', '_').replace(' ', '')
    if s[0].isdigit():
        s = '_' + s
    return s

def safe_assetpath(s):
    return s[2:] if s[:2] == '//' else s # Remove leading '//'

def extract_filename(s):
    return os.path.basename(s)

def get_render_resolution(scene):
    render = scene.render
    scale = render.resolution_percentage / 100
    return int(render.resolution_x * scale), int(render.resolution_y * scale)

def get_project_scene_name():
    wrd = bpy.data.worlds['Arm']
    if wrd.arm_play_active_scene:
        return safe_filename(bpy.context.screen.scene.name)
    else:
        return safe_filename(wrd.arm_project_scene)

def get_active_scene():
    wrd = bpy.data.worlds['Arm']
    return bpy.context.screen.scene if wrd.arm_play_active_scene else bpy.data.scenes[wrd.arm_project_scene]

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

def check_camera(self):
    if len(bpy.data.cameras) == 0:
        self.report({"ERROR"}, "No camera found in scene")
        return False
    return True

def check_sdkpath(self):
    s = get_sdk_path()
    for c in r'[];><&*%=+@!#^()|?^':
        if c in s:
            self.report({"ERROR"}, "SDK path '{0}' contains special characters. Please move SDK to different path for now.".format(s))
            return False
    for c in s:
        if ord(c) > 127:
            self.report({"ERROR"}, "SDK path '{0}' contains special characters. Please move SDK to different path for now.".format(s))
            return False
    return True

def tess_enabled(target):
    return target == 'krom' or target == 'native'

def is_object_animation_enabled(bobject):
    # Checks if animation is present and enabled
    if bobject.object_animation_enabled == False or bobject.type == 'ARMATURE' or bobject.type == 'BONE':
        return False
    if bobject.animation_data and bobject.animation_data.action:
        return True
    return False

def is_bone_animation_enabled(bobject):
    # Checks if animation is present and enabled for parented armature
    if bobject.parent and bobject.parent.type == 'ARMATURE':
        if bobject.parent.bone_animation_enabled == False:
            return False
        if bobject.parent.animation_data and bobject.parent.animation_data.action:
            return True
    return False

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
