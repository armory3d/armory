import os
import sys
import shutil
import bpy
import platform
import json
from bpy.props import *
import subprocess
import atexit
import webbrowser
import write_data
import nodes
import nodes_pipeline
from armory import ArmoryExporter

def defaultSettings():
    wrd = bpy.data.worlds[0]
    wrd['CGVersion'] = "16.1.0"
    wrd['CGProjectTarget'] = 0
    wrd['CGProjectName'] = "cycles_game"
    wrd['CGProjectPackage'] = "game"
    wrd['CGProjectWidth'] = 1136
    wrd['CGProjectHeight'] = 640
    wrd['CGProjectScene'] = bpy.data.scenes[0].name
    wrd['CGAA'] = 1
    wrd['CGPhysics'] = 0
    wrd['CGMinimize'] = (True)
    # Make sure we are using cycles
    if bpy.data.scenes[0].render.engine == 'BLENDER_RENDER':
        for scene in bpy.data.scenes:
            scene.render.engine = 'CYCLES'

# Store properties in the world object
def initWorldProperties():
    bpy.types.World.CGVersion = StringProperty(name = "CGVersion")
    bpy.types.World.CGProjectTarget = EnumProperty(
        items = [('HTML5', 'HTML5', 'HTML5'), 
                 ('Windows', 'Windows', 'Windows'), 
                 ('OSX', 'OSX', 'OSX'),
                 ('Linux', 'Linux', 'Linux'), 
                 ('iOS', 'iOS', 'iOS'),
                 ('Android', 'Android', 'Android')],
        name = "Target")
    bpy.types.World.CGProjectName = StringProperty(name = "Name")
    bpy.types.World.CGProjectPackage = StringProperty(name = "Package")
    bpy.types.World.CGProjectWidth = IntProperty(name = "Width")
    bpy.types.World.CGProjectHeight = IntProperty(name = "Height")
    bpy.types.World.CGProjectScene = StringProperty(name = "Scene")
    bpy.types.World.CGAA = EnumProperty(
        items = [('Disabled', 'Disabled', 'Disabled'), 
                 ('16X', '16X', '16X')],
        name = "Anti-aliasing")
    bpy.types.World.CGPhysics = EnumProperty(
        items = [('Disabled', 'Disabled', 'Disabled'), 
                 ('Bullet', 'Bullet', 'Bullet')],
        name = "Physics")
    bpy.types.World.CGMinimize = BoolProperty(name = "Minimize")

    # Default settings
    if not 'CGVersion' in bpy.data.worlds[0]:
        defaultSettings()

    # Use material nodes
    for mat in bpy.data.materials:
        bpy.ops.cycles.use_shading_nodes({"material":mat})
    # Use world nodes
    for wrd in bpy.data.worlds:
        bpy.ops.cycles.use_shading_nodes({"world":wrd})
    
    return

# Info panel play
def draw_play_item(self, context):
    layout = self.layout
    layout.operator("cg.play")

# Menu in render region
class ToolsPanel(bpy.types.Panel):
    bl_label = "Cycles Game"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    # Info panel play
    #bpy.types.INFO_HT_header.prepend(draw_play_item)
    bpy.types.VIEW3D_HT_header.append(draw_play_item)
 
    def draw(self, context):
        layout = self.layout
        wrd = bpy.data.worlds[0]
        layout.prop(wrd, 'CGProjectName')
        layout.prop(wrd, 'CGProjectPackage')
        row = layout.row()
        row.prop(wrd, 'CGProjectWidth')
        row.prop(wrd, 'CGProjectHeight')
        layout.prop_search(wrd, "CGProjectScene", bpy.data, "scenes", "Scene")
        layout.prop(wrd, 'CGProjectTarget')
        layout.operator("cg.build")
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("cg.folder")
        row.operator("cg.clean")
        layout.prop(wrd, 'CGAA')
        layout.prop(wrd, 'CGPhysics')
        layout.prop(wrd, 'CGMinimize')

class Object:
    def to_JSON(self):
        if bpy.data.worlds[0]['CGMinimize'] == True:
            return json.dumps(self, default=lambda o: o.__dict__, separators=(',',':'))
        else:
            return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

# Convert Blender data into game data
def exportGameData():
    # TODO: Set armatures to center of world so skin transform is zero
    armatures = []
    for o in bpy.data.objects:
        if o.type == 'ARMATURE':
            a = Object()
            a.armature = o
            a.x = o.location.x
            a.y = o.location.y
            a.z = o.location.z
            armatures.append(a)
            o.location.x = 0
            o.location.y = 0
            o.location.z = 0

    # Export scene data
    shader_references = []
    for scene in bpy.data.scenes:
        if scene.name[0] != '.': # Skip hidden scenes
            bpy.ops.export_scene.armory({"scene":scene}, filepath='Assets/generated/' + scene.name + '.json')
            shader_references += ArmoryExporter.shader_references

    # Move armatures back
    for a in armatures:
        a.armature.location.x = a.x
        a.armature.location.y = a.y
        a.armature.location.z = a.z
    
    # Write khafile.js
    write_data.write_khafilejs(shader_references)

    # Write Main.hx
    write_data.write_main()

def buildProject(self, build_type=0):
    # Save blend
    bpy.ops.wm.save_mainfile()

    # Save scripts
    #area = bpy.context.area
    #old_type = area.type
    #area.type = 'TEXT_EDITOR'
    #for text in bpy.data.texts:
        #area.spaces[0].text = text
        #bpy.ops.text.save()
    ##bpy.ops.text.save()
    #area.type = old_type

    # Auto-build nodes # TODO: only if needed
    nodes.buildNodeTrees()
    nodes_pipeline.buildNodeTrees()
    
    # Set dir
    s = bpy.data.filepath.split(os.path.sep)
    name = s.pop()
    name = name.split(".")
    name = name[0]
    fp = os.path.sep.join(s)
    os.chdir(fp)

    # Export
    exportGameData()
    
    # Set build command
    if (bpy.data.worlds[0]['CGProjectTarget'] == 0):
        bashCommand = "-t html5"
    elif (bpy.data.worlds[0]['CGProjectTarget'] == 1):
        bashCommand = "-t windows"
    elif (bpy.data.worlds[0]['CGProjectTarget'] == 2):
        bashCommand = "-t osx"
    elif (bpy.data.worlds[0]['CGProjectTarget'] == 3):
        bashCommand = "-t linux"
    elif (bpy.data.worlds[0]['CGProjectTarget'] == 4):
        bashCommand = "-t ios"
    elif (bpy.data.worlds[0]['CGProjectTarget'] == 5):
        bashCommand = "-t android-native"
    
    # Build
    haxelib_path = "haxelib"
    if platform.system() == 'Darwin':
        haxelib_path = "/usr/local/bin/haxelib"

    prefix =  haxelib_path + " run kha "

    output = subprocess.check_output([haxelib_path + " path cyclesgame"], shell=True)
    output = str(output).split("\\n")[0].split("'")[1]
    scripts_path = output[:-8] + "blender/"

    blender_path = bpy.app.binary_path
    blend_path = bpy.data.filepath
    p = subprocess.Popen([blender_path, blend_path, '-b', '-P', scripts_path + 'lib/build.py', '--', bashCommand, str(build_type), str(bpy.data.worlds[0]['CGProjectTarget'])])
    #p = subprocess.Popen([blender_path, blend_path, '-b', '-P', scripts_path + 'lib/build.py', '--', prefix + bashCommand, str(build_type), str(bpy.data.worlds[0]['CGProjectTarget'])])
    atexit.register(p.terminate)
    
    self.report({'INFO'}, "Building, see console...")

def cleanProject(self):
    # Set dir
    s = bpy.data.filepath.split(os.path.sep)
    name = s.pop()
    name = name.split(".")
    name = name[0]
    fp = os.path.sep.join(s)
    os.chdir(fp)
    
    # Remove build data
    if os.path.isdir("build"):
        shutil.rmtree('build')

    # Remove generated data
    if os.path.isdir("Assets/generated"):
        shutil.rmtree('Assets/generated')

    # Remove compiled nodes
    path = 'Sources/' + bpy.data.worlds[0].CGProjectPackage.replace(".", "/") + "/"
    for node_group in bpy.data.node_groups:
        node_group_name = node_group.name.replace('.', '_')
        os.remove(path + node_group_name + '.hx')

    self.report({'INFO'}, "Done")

# Play
class OBJECT_OT_PLAYButton(bpy.types.Operator):
    bl_idname = "cg.play"
    bl_label = "Play"
 
    def execute(self, context):
        buildProject(self, 1)
        return{'FINISHED'}

# Build
class OBJECT_OT_BUILDButton(bpy.types.Operator):
    bl_idname = "cg.build"
    bl_label = "Build"
 
    def execute(self, context):
        buildProject(self, 0)
        return{'FINISHED'}

# Open project folder
class OBJECT_OT_FOLDERButton(bpy.types.Operator):
    bl_idname = "cg.folder"
    bl_label = "Folder"
 
    def execute(self, context):
        s = bpy.data.filepath.split(os.path.sep)
        name = s.pop()
        name = name.split(".")
        name = name[0]
        fp = os.path.sep.join(s)
    
        webbrowser.open('file://' + fp)
        return{'FINISHED'}
    
# Clean project
class OBJECT_OT_CLEANButton(bpy.types.Operator):
    bl_idname = "cg.clean"
    bl_label = "Clean"
 
    def execute(self, context):
        cleanProject(self)
        return{'FINISHED'}

# Registration
def register():
    bpy.utils.register_module(__name__)
    # Store properties in world
    initWorldProperties()

def unregister():
    bpy.utils.unregister_module(__name__)
