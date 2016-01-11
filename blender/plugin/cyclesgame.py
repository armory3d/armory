# Cycles Game Engine
# https://github.com/luboslenco/cyclesgame
bl_info = {
    "name": "Cycles Game",
    "category": "Game Engine",
    "description": "3D Game Engine built for Cycles",
    "author": "Lubos Lenco",
    "version": (16, 1, 0, 0),
    "wiki_url": "http://cyclesgame.org/"
}

import sys
import bpy
import os
import atexit
import platform
import subprocess
import webbrowser
from bpy.props import *

class StartPanel(bpy.types.Panel):
    bl_label = "Cycles Game Start"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    running = False
 
    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        if StartPanel.running == False:
            row.operator('cg.start')
        else:
            row.operator('cg.stop')
        row.operator('cg.update')
        row.operator('cg.help')

class OBJECT_OT_STARTButton(bpy.types.Operator):
    bl_idname = "cg.start"
    bl_label = "Start"
 
    def execute(self, context):
        # Check if fetch was done
        s = bpy.data.filepath.split(os.path.sep)
        s.pop()
        fp = os.path.sep.join(s)
        if not os.path.exists(fp + '/Sources'):
            update(self)
        start_plugin()
        StartPanel.running = True
        return {'FINISHED'}

class OBJECT_OT_STOPButton(bpy.types.Operator):
    bl_idname = "cg.stop"
    bl_label = "Stop"
 
    def execute(self, context):
        import start
        start.unregister()
        StartPanel.running = False
        return {'FINISHED'}

class OBJECT_OT_UPDATEButton(bpy.types.Operator):
    bl_idname = "cg.update"
    bl_label = "Update"
 
    def execute(self, context):
        # Fetch
        update(self)
        return{'FINISHED'}

class OBJECT_OT_HELPButton(bpy.types.Operator):
    bl_idname = "cg.help"
    bl_label = "Help"
 
    def execute(self, context):
        webbrowser.open('http://cyclesgame.org/docs/')
        return{'FINISHED'}

def start_plugin():
    haxelib_path = "haxelib"
    if platform.system() == 'Darwin':
        haxelib_path = "/usr/local/bin/haxelib"

    output = subprocess.check_output([haxelib_path + " path cyclesgame"], shell=True)
    output = str(output).split("\\n")[0].split("'")[1]
    scripts_path = output[:-8] + "blender/" # Remove 'Sources/' from haxelib path
    
    sys.path.append(scripts_path)
    import start
    start.register()
    
    # Start server
    s = bpy.data.filepath.split(os.path.sep)
    s.pop()
    fp = os.path.sep.join(s)
    os.chdir(fp)
    
    blender_path = bpy.app.binary_path
    blend_path = bpy.data.filepath
    p = subprocess.Popen([blender_path, blend_path, '-b', '-P', scripts_path + 'lib/server.py', '&'])
    atexit.register(p.terminate)

def update(self):
    haxelib_path = "haxelib"
    if platform.system() == 'Darwin':
        haxelib_path = "/usr/local/bin/haxelib"

    s = bpy.data.filepath.split(os.path.sep)
    s.pop()
    fp = os.path.sep.join(s)
    os.chdir(fp)

    # Create directories
    if not os.path.exists('Sources'):
        os.makedirs('Sources')
    if not os.path.exists('Assets'):
        os.makedirs('Assets')

    p = subprocess.Popen([haxelib_path + ' install cyclesgame &'], shell=True)
    
    self.report({'INFO'}, "Fetching, see console...")

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
