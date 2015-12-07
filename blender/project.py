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

def defaultSettings():
    wrd = bpy.data.worlds[0]
    wrd['CGVersion'] = "15.12.0"
    wrd['CGProjectTarget'] = 0
    wrd['CGProjectName'] = "cycles_game"
    wrd['CGProjectPackage'] = "game"
    wrd['CGProjectWidth'] = 1136
    wrd['CGProjectHeight'] = 640
    wrd['CGTargetScene'] = bpy.data.scenes[0].name
    wrd['CGAA'] = 1
    wrd['CGPhysics'] = 1
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
    bpy.types.World.CGTargetScene = StringProperty(name = "Scene")
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

# Menu in tools region
class ToolsPanel(bpy.types.Panel):
    bl_label = "Cycles Game"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    # Info panel play
    bpy.types.INFO_HT_header.prepend(draw_play_item)
 
    def draw(self, context):
        layout = self.layout
        wrd = bpy.data.worlds[0]
        layout.prop(wrd, 'CGProjectName')
        layout.prop(wrd, 'CGProjectPackage')
        row = layout.row()
        row.prop(wrd, 'CGProjectWidth')
        row.prop(wrd, 'CGProjectHeight')
        layout.prop_search(wrd, "CGTargetScene", bpy.data, "scenes", "Scene")
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
    for scene in bpy.data.scenes:
        if scene.name[0] != '.': # Skip hidden scenes
            bpy.ops.export_scene.lue({"scene":scene}, filepath='Assets/' + scene.name + '.json')

    # Move armatures back
    for a in armatures:
        a.armature.location.x = a.x
        a.armature.location.y = a.y
        a.armature.location.z = a.z
    
    # Write khafile.js
    write_data.write_khafilejs()

    # Write Main.hx
    write_data.write_main()

def buildProject(self, build_type=0):
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
    buildNodeTrees()
    
    # Set dir
    s = bpy.data.filepath.split(os.path.sep)
    name = s.pop()
    name = name.split(".")
    name = name[0]
    fp = os.path.sep.join(s)
    os.chdir(fp)

    # Save blend
    bpy.ops.wm.save_mainfile()

    # Export
    exportGameData()
    
    # Set build command
    if (bpy.data.worlds[0]['CGProjectTarget'] == 0):
        bashCommand = "-t osx"
    elif (bpy.data.worlds[0]['CGProjectTarget'] == 1):
        bashCommand = "-t windows"
    elif (bpy.data.worlds[0]['CGProjectTarget'] == 2):
        bashCommand = "-t linux"
    elif (bpy.data.worlds[0]['CGProjectTarget'] == 3):
        bashCommand = "-t html5"
    elif (bpy.data.worlds[0]['CGProjectTarget'] == 4):
        bashCommand = "-t ios"
    elif (bpy.data.worlds[0]['CGProjectTarget'] == 5):
        bashCommand = "-t android_native"
    
    # Build
    haxelib_path = "haxelib"
    if platform.system() == 'Darwin':
        haxelib_path = "/usr/local/bin/haxelib"

    prefix = haxelib_path + " run kha "

    output = subprocess.check_output([haxelib_path + " path cyclesgame"], shell=True)
    output = str(output).split("\\n")[0].split("'")[1]
    scripts_path = output + "blender/"

    blender_path = bpy.app.binary_path
    blend_path = bpy.data.filepath
    p = subprocess.Popen([blender_path, blend_path, '-b', '-P', scripts_path + 'lib/build.py', '--', prefix + bashCommand, str(build_type), str(bpy.data.worlds[0]['CGProjectTarget'])])
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
    
    # Remove build dir
    if os.path.isdir("build"):
        shutil.rmtree('build')

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



def buildNodeTrees():
    s = bpy.data.filepath.split(os.path.sep)
    s.pop()
    fp = os.path.sep.join(s)
    os.chdir(fp)

    # Make sure package dir exists
    if not os.path.exists('Sources/' + bpy.data.worlds[0].CGProjectPackage.replace(".", "/")):
        os.makedirs('Sources/' + bpy.data.worlds[0].CGProjectPackage.replace(".", "/"))
    
    # Export node scripts
    for node_group in bpy.data.node_groups:
        buildNodeTree(node_group)

def buildNodeTree(node_group):
    rn = getRootNode(node_group)

    path = 'Sources/' + bpy.data.worlds[0].CGProjectPackage.replace(".", "/") + "/"

    node_group_name = node_group.name.replace('.', '_')

    with open(path + node_group_name + '.hx', 'w') as f:
        f.write('package ' + bpy.data.worlds[0].CGProjectPackage + ';\n\n')
        f.write('import cycles.node.*;\n\n')
        f.write('class ' + node_group_name + ' extends cycles.trait.NodeExecutor {\n\n')
        f.write('\tpublic function new() { super(); requestAdd(add); }\n\n')
        f.write('\tfunction add() {\n')
        # Make sure root node exists
        if rn != None:
            name = '_' + rn.name.replace(".", "_").replace("@", "")
            buildNode(node_group, rn, f, [])
            f.write('\n\t\tstart(' + name + ');\n')
        f.write('\t}\n')
        f.write('}\n')

def buildNode(node_group, node, f, created_nodes):
    # Get node name
    name = '_' + node.name.replace(".", "_").replace("@", "")

    # Check if node already exists
    for n in created_nodes:
        if n == name:
            return name

    # Create node
    type = node.name.split(".")[0].replace("@", "") + "Node"
    f.write('\t\tvar ' + name + ' = new ' + type + '();\n')
    created_nodes.append(name)
    
    # Variables
    if type == "TransformNode":
        f.write('\t\t' + name + '.transform = node.transform;\n')
    
    # Create inputs
    for inp in node.inputs:
        # Is linked - find node
        inpname = ''
        if inp.is_linked:
            n = findNodeByLink(node_group, node, inp)
            inpname = buildNode(node_group, n, f, created_nodes)
        # Not linked - create node with default values
        else:
            inpname = buildDefaultNode(inp)
        
        # Add input
        f.write('\t\t' + name + '.inputs.push(' + inpname + ');\n')
        
    return name
            
def findNodeByLink(node_group, to_node, inp):
    for link in node_group.links:
        if link.to_node == to_node and link.to_socket == inp:
            return link.from_node
    
def getRootNode(node_group):
    for n in node_group.nodes:
        if n.outputs[0].is_linked == False:
            return n

def buildDefaultNode(inp):
    inpname = ''
    if inp.type == "VECTOR":
        inpname = 'VectorNode.create(' + str(inp.default_value[0]) + ', ' + str(inp.default_value[1]) + ", " + str(inp.default_value[2]) + ')'
    elif inp.type == "VALUE":
        inpname = 'FloatNode.create(' + str(inp.default_value) + ')'
    elif inp.type == 'BOOLEAN':
        inpname = 'BoolNode.create(' + str(inp.default_value).lower() + ')'
        
    return inpname

# Registration
def register():
    bpy.utils.register_module(__name__)
    # Store properties in world
    initWorldProperties()

def unregister():
    bpy.utils.unregister_module(__name__)
