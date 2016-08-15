import bpy
import json
import os
import glob
import lib.umsgpack
import platform

def write_arm(filepath, output):
    if bpy.data.worlds[0].ArmMinimize:
        with open(filepath, 'wb') as f:
            f.write(lib.umsgpack.dumps(output))
    else:
        with open(filepath, 'w') as f:
            # f.write(json.dumps(output, separators=(',',':')))
            f.write(json.dumps(output, sort_keys=True, indent=4))

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

def fetch_script_names():
    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons['armory'].preferences
    sdk_path = addon_prefs.sdk_path
    wrd = bpy.data.worlds[0]
    wrd.bundled_scripts_list.clear()
    os.chdir(sdk_path + '/armory/Sources/armory/trait')
    for file in glob.glob('*.hx'):
        wrd.bundled_scripts_list.add().name = file.rsplit('.')[0]
    wrd.scripts_list.clear()
    sources_path = get_fp() + '/Sources/' + wrd.ArmProjectPackage
    if os.path.isdir(sources_path):
        os.chdir(sources_path)
        for file in glob.glob('*.hx'):
            wrd.scripts_list.add().name = file.rsplit('.')[0]
    os.chdir(get_fp())

def to_hex(val):
    return '#%02x%02x%02x%02x' % (int(val[3] * 255), int(val[0] * 255), int(val[1] * 255), int(val[2] * 255))

def safe_filename(s):
    return s.replace('.', '_').replace('-', '_').replace(' ', '_')

def get_render_resolution(scene_index=0):
    render = bpy.data.scenes[scene_index].render
    scale = render.resolution_percentage / 100
    return int(render.resolution_x * scale), int(render.resolution_y * scale)
