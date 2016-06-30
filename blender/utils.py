import bpy
import json
import os

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

    
# Start server
# s = bpy.data.filepath.split(os.path.sep)
# s.pop()
# fp = os.path.sep.join(s)
# os.chdir(fp)
# blender_path = bpy.app.binary_path
# blend_path = bpy.data.filepath
# p = subprocess.Popen([blender_path, blend_path, '-b', '-P', scripts_path + 'lib/server.py', '&'])
# atexit.register(p.terminate)
