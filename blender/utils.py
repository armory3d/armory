import bpy
import json
import os
import glob

class Object:
    def to_JSON(self):
        if bpy.data.worlds[0]['CGMinimize'] == True:
            return json.dumps(self, default=lambda o: o.__dict__, separators=(',',':'))
        else:
            return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

def get_fp():
    s = bpy.data.filepath.split(os.path.sep)
    s.pop()
    return os.path.sep.join(s)

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
    sources_path = get_fp() + '/Sources/' + wrd.CGProjectPackage
    if os.path.isdir(sources_path):
        os.chdir(sources_path)
        for file in glob.glob('*.hx'):
            wrd.scripts_list.add().name = file.rsplit('.')[0]
    os.chdir(get_fp())
