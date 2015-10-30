import shutil
import bpy
import os
import platform
import json
from bpy.props import *
import subprocess
import atexit
import webbrowser

def defaultSettings():
    wrd = bpy.data.worlds[0]
    wrd['TargetZblendVersion'] = "0.1.0"
    wrd['TargetEnum'] = 3
    wrd['TargetRenderer'] = 0
    wrd['TargetProjectName'] = "my_project"
    wrd['TargetProjectPackage'] = "my_project"
    wrd['TargetProjectWidth'] = 1136
    wrd['TargetProjectHeight'] = 640
    wrd['TargetProjectScale'] = 1.0
    wrd['TargetProjectOrient'] = 0
    wrd['TargetScene'] = bpy.data.scenes[0].name
    wrd['TargetGravity'] = bpy.data.scenes[0].name
    wrd['TargetClear'] = bpy.data.worlds[0].name
    wrd['TargetFog'] = (False)
    wrd['TargetFogColor'] = (0.5, 0.5, 0.7, 1.0)
    wrd['TargetFogDensity'] = (0.04)
    wrd['TargetShadowMapping'] = (False)
    wrd['TargetShadowMapSize'] = 1024
    wrd['TargetShading'] = 0
    wrd['TargetShader'] = 0
    wrd['TargetAA'] = 1
    wrd['TargetPhysics'] = 1
    wrd['TargetSSAO'] = (False)
    wrd['TargetAutoBuildNodes'] = (True)
    wrd['TargetMinimize'] = (True)
    # Make sure we are using cycles
    if bpy.data.scenes[0].render.engine == 'BLENDER_RENDER':
        for scene in bpy.data.scenes:
            scene.render.engine = 'CYCLES'

# Store properties in the world object
def initWorldProperties():
    bpy.types.World.TargetZblendVersion = StringProperty(name = "ZblendVersion")
    bpy.types.World.TargetEnum = EnumProperty(
        items = [('OSX', 'OSX', 'OSX'), 
                 ('Windows', 'Windows', 'Windows'), 
                 ('Linux', 'Linux', 'Linux'), 
                 ('HTML5', 'HTML5', 'HTML5'),
                 ('iOS', 'iOS', 'iOS'),
                 ('Android', 'Android', 'Android')],
        name = "Target")
    bpy.types.World.TargetRenderer = EnumProperty(
        items = [('OGL', 'OGL', 'OGL'), 
                 ('D3D9', 'D3D9', 'D3D9'), 
                 ('D3D11', 'D3D11', 'D3D11')],
        name = "Renderer")
    bpy.types.World.TargetProjectName = StringProperty(name = "Name")
    bpy.types.World.TargetProjectPackage = StringProperty(name = "Package")
    bpy.types.World.TargetProjectWidth = IntProperty(name = "Width")
    bpy.types.World.TargetProjectHeight = IntProperty(name = "Height")
    bpy.types.World.TargetProjectScale = FloatProperty(name = "Scale", default=1.0)
    bpy.types.World.TargetProjectOrient = EnumProperty(
        items = [('Portrait', 'Portrait', 'Portrait'), 
                 ('Landscape', 'Landscape', 'Landscape')],
        name = "Orient")
    bpy.types.World.TargetScene = StringProperty(name = "Scene")
    bpy.types.World.TargetGravity = StringProperty(name = "Gravity")
    bpy.types.World.TargetClear = StringProperty(name = "Clear")
    bpy.types.World.TargetFog = BoolProperty(name = "Fog")
    bpy.types.World.TargetFogColor = FloatVectorProperty(name = "Fog Color", default=[0.5,0.5,0.7,1], size=4, subtype="COLOR", min=0, max=1)
    bpy.types.World.TargetFogDensity = FloatProperty(name = "Fog Density", min=0, max=1)
    bpy.types.World.TargetShadowMapping = BoolProperty(name = "Shadow mapping")
    bpy.types.World.TargetShadowMapSize = IntProperty(name = "Shadow map size")
    bpy.types.World.TargetShading = EnumProperty(
        items = [('Forward', 'Forward', 'Forward'), 
                 ('Deferred', 'Deferred', 'Deferred')],
        name = "Shading")
    bpy.types.World.TargetShader = EnumProperty(
        items = [('Physically based', 'Physically based', 'Physically based'),
                 ('Flat', 'Flat', 'Flat'),
                 ('Unlit', 'Unlit', 'Unlit')],
        name = "Shader")
    bpy.types.World.TargetAA = EnumProperty(
        items = [('Disabled', 'Disabled', 'Disabled'), 
                 ('2X', '2X', '2X')],
        name = "Anti-aliasing")
    bpy.types.World.TargetPhysics = EnumProperty(
        items = [('Disabled', 'Disabled', 'Disabled'), 
                 ('Bullet', 'Bullet', 'Bullet')],
        name = "Physics")
    bpy.types.World.TargetSSAO = BoolProperty(name = "SSAO")
    bpy.types.World.TargetAutoBuildNodes = BoolProperty(name = "Auto-build nodes")
    bpy.types.World.TargetMinimize = BoolProperty(name = "Minimize")

    # Default settings
    # todo: check version
    if not 'TargetZblendVersion' in bpy.data.worlds[0]:
        defaultSettings()

    # Make sure we are using nodes for every material
    # Use material nodes
    for mat in bpy.data.materials:
        bpy.ops.cycles.use_shading_nodes({"material":mat})
    # Use world nodes
    for wrd in bpy.data.worlds:
        bpy.ops.cycles.use_shading_nodes({"world":wrd})
    
    return

# Store properties in world for now
initWorldProperties()

# Info panel play
def draw_play_item(self, context):
    layout = self.layout
    layout.operator("zblend.play")

# Menu in tools region
class ToolsPanel(bpy.types.Panel):
    bl_label = "zblend_project"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    # Info panel play
    bpy.types.INFO_HT_header.prepend(draw_play_item)
 
    def draw(self, context):
        layout = self.layout
        wrd = bpy.data.worlds[0]
        layout.prop(wrd, 'TargetProjectName')
        layout.prop(wrd, 'TargetProjectPackage')
        layout.prop(wrd, 'TargetProjectWidth')
        layout.prop(wrd, 'TargetProjectHeight')
        row = layout.row()
        row.active = False
        row.prop(wrd, 'TargetProjectScale')
        layout.prop_search(wrd, "TargetScene", bpy.data, "scenes", "Scene")
        layout.prop(wrd, 'TargetEnum')
        if wrd['TargetEnum'] == 4 or wrd['TargetEnum'] == 5:
            layout.prop(wrd, 'TargetProjectOrient')
        row = layout.row()
        row.active = False
        row.prop(wrd, 'TargetRenderer')
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("zblend.play")
        row.operator("zblend.build")
        row.operator("zblend.project")
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("zblend.folder")
        row.operator("zblend.clean")
        layout.prop_search(wrd, "TargetGravity", bpy.data, "scenes", "Gravity")
        layout.prop_search(wrd, "TargetClear", bpy.data, "worlds", "Clear Color")
        layout.prop(wrd, 'TargetFog')
        if wrd['TargetFog'] == True:
            layout.prop(wrd, 'TargetFogColor')
            layout.prop(wrd, 'TargetFogDensity')
        layout.prop(wrd, 'TargetShadowMapping')
        if wrd['TargetShadowMapping'] == True:
            layout.prop(wrd, 'TargetShadowMapSize')
        layout.prop(wrd, 'TargetShading')
        layout.prop(wrd, 'TargetShader')
        layout.prop(wrd, 'TargetAA')
        layout.prop(wrd, 'TargetPhysics')
        layout.prop(wrd, 'TargetSSAO')
        row = layout.row()
        row.prop(wrd, 'TargetAutoBuildNodes')
        if wrd['TargetAutoBuildNodes'] == False:
            row.operator("zblend.buildnodes")
        layout.prop(wrd, 'TargetMinimize')
        layout.operator("zblend.defaultsettings")

# Used to output json
class Object:
    def to_JSON(self):
        if bpy.data.worlds[0]['TargetMinimize'] == True:
            return json.dumps(self, default=lambda o: o.__dict__, separators=(',',':'))
        else:
            return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

# Creates asset node in project.kha
def createAsset(filename, type, splitExt=None):
    if (splitExt == None):
        splitExt = True
        
    str = filename.split(".")
    l = len(str)
    name = str[0]
    for i in range(1, l - 1):
        name += "." + str[i]
    
    if (splitExt == False):
        name = filename
    
    x = Object()
    x.type = type
    x.file = filename
    x.name = name
    return x

# Creates room node in project.kha
def createRoom(name, assets):
    x = Object()
    x.name = name
    x.parent = None
    x.neighbours = []
    x.assets = []
    for a in assets:
        if a.type == 'font':
            x.assets.append(a.name + str(a.size) + '.kravur')
        else:
            x.assets.append(a.name)
    return x

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
            bpy.ops.export_scene.zblend({"scene":scene}, filepath='Assets/' + scene.name + '.json')

    # Move armatures back
    for a in armatures:
        a.armature.location.x = a.x
        a.armature.location.y = a.y
        a.armature.location.z = a.z

    # Export project file
    x = Object()
    x.format = 2
    x.game = Object()
    x.game.name = bpy.data.worlds[0]['TargetProjectName']
    x.game.width = bpy.data.worlds[0]['TargetProjectWidth']
    x.game.height = bpy.data.worlds[0]['TargetProjectHeight']
    if bpy.data.worlds[0]['TargetAA'] == 1:
        x.game.antiAliasingSamples = 2
    x.libraries = ["zblend", "haxebullet", "dependencies"]
    # Defined libraries
    for o in bpy.data.worlds[0].my_liblist:
        if o.enabled_prop:
            x.libraries.append(o.name)
    # Assets
    x.assets = []
    x.rooms = []
    # - Data
    x.assets.append(createAsset("data.json", "blob"))
    # - Scenes
    for s in bpy.data.scenes:
        x.assets.append(createAsset(s.name + ".json", "blob"))
    # - Defined assets
    for o in bpy.data.worlds[0].my_list:
        if o.enabled_prop:
            if (o.type_prop == 'Atlas'):
                x.assets.append(createAsset(o.name + "_metadata.json", "blob"))
                x.assets.append(createAsset(o.name + "_atlas.png", "image"))
            elif (o.type_prop == 'Font'):
                asset = createAsset(o.name, "font")
                asset.size = o.size_prop
                x.assets.append(asset)
            else:
                typeName = o.type_prop.lower()
                x.assets.append(createAsset(o.name, typeName))
    # - Rooms
    x.rooms.append(createRoom("room1", x.assets))
    # Write project file
    with open('project.kha', 'w') as f:
        f.write(x.to_JSON())
        

    # Export scene properties
    data = Object()
    
    # Objects
    objs = [] 
    for o in bpy.data.objects:
        x = Object()
        x.name = o.name
        x.traits = []
        for t in o.my_traitlist:
            # Disabled trait
            if t.enabled_prop == False:
                continue
            
            y = Object()
            y.type = t.type_prop

            # Script
            if y.type == 'Script':
                y.class_name = t.class_name_prop
            # Custom traits
            elif y.type == 'Mesh Renderer':
                y.class_name = 'MeshRenderer'
                if t.default_material_prop: # Use object material
                    y.material = ""
                else:
                    y.material = t.material_prop
                y.lighting = t.lighting_prop
                y.cast_shadow = t.cast_shadow_prop
                y.receive_shadow = t.receive_shadow_prop
            elif y.type == 'Custom Renderer':
                y.class_name = t.class_name_prop
                
                if t.default_material_prop: # Use object material
                    y.material = ""
                else:
                    y.material = t.material_prop
                
                y.shader = t.shader_prop
                y.data = t.data_prop
            elif y.type == 'Billboard Renderer':
                y.type = 'Custom Renderer'
                y.class_name = 'BillboardRenderer'
                if t.default_material_prop: # Use object material
                    y.material = ""
                else:
                    y.material = t.material_prop
                y.shader = 'billboardshader'
            elif y.type == 'Particles Renderer':
                y.type = 'Custom Renderer'
                y.class_name = 'ParticlesRenderer'
                if t.default_material_prop: # Use object material
                    y.material = ""
                else:
                    y.material = t.material_prop
                y.shader = 'particlesshader'
                y.data = t.data_prop
            # Convert to scripts
            elif y.type == 'Nodes':
                y.type = 'Script'
                y.class_name = t.nodes_name_prop.replace('.', '_')
            elif y.type == 'Scene Instance':
                y.type = 'Script'
                y.class_name = "SceneInstance:'" + t.scene_prop + "'"
            elif y.type == 'Animation':
                y.type = 'Script'
                y.class_name = "Animation:'" + t.start_track_name_prop + "':"
                # Names
                anim_names = []
                anim_starts = []
                anim_ends = []
                for animt in o.my_animationtraitlist:
                    if animt.enabled_prop == False:
                        continue
                    anim_names.append(animt.name)
                    anim_starts.append(animt.start_prop)
                    anim_ends.append(animt.end_prop)
                y.class_name += str(anim_names) + ":"
                y.class_name += str(anim_starts) + ":"
                y.class_name += str(anim_ends)
                # Armature offset
                for a in armatures:
                    if o.parent == a.armature:
                        y.class_name += ":" + str(a.x) + ":" + str(a.y) + ":" + str(a.z)
                        break

            elif y.type == 'Camera':
                y.type = 'Script'
                cam = bpy.data.cameras[t.camera_link_prop]
                if cam.type == 'PERSP':
                    y.class_name = 'PerspectiveCamera'
                elif cam.type == 'ORTHO':
                    y.class_name = 'OrthoCamera'
            elif y.type == 'Light':
                y.type = 'Script'
                y.class_name = 'Light'
            elif y.type == 'Rigid Body':
                if bpy.data.worlds[0]['TargetPhysics'] == 0:
                    continue
                y.type = 'Script'
                # Get rigid body
                if t.default_body_prop == True:
                    rb = o.rigid_body
                else:
                    rb = bpy.data.objects[t.body_link_prop].rigid_body
                shape = '0' # BOX
                if t.custom_shape_prop == True:
                    if t.custom_shape_type_prop == 'Terrain':
                        shape = '7'
                    elif t.custom_shape_type_prop == 'Static Mesh':
                        shape = '8'
                elif rb.collision_shape == 'SPHERE':
                    shape = '1'
                elif rb.collision_shape == 'CONVEX_HULL':
                    shape = '2'
                elif rb.collision_shape == 'MESH':
                    shape = '3'
                elif rb.collision_shape == 'CONE':
                    shape = '4'
                elif rb.collision_shape == 'CYLINDER':
                    shape = '5'
                elif rb.collision_shape == 'CAPSULE':
                    shape = '6'
                body_mass = 0
                if rb.enabled:
                    body_mass = rb.mass
                y.class_name = 'RigidBody:' + str(body_mass) + \
                                ':' + shape + \
                                ":" + str(rb.friction) + \
                                ":" + str(t.shape_size_scale_prop[0]) + \
                                ":" + str(t.shape_size_scale_prop[1]) + \
                                ":" + str(t.shape_size_scale_prop[2])

            # Append trait
            x.traits.append(y)

        # Material slots
        x.materials = []
        if o.material_slots:
            for ms in o.material_slots:
                x.materials.append(ms.name)
        objs.append(x)

    # Materials
    mats = []
    for m in bpy.data.materials:
        # Make sure material is using nodes
        if m.node_tree == None:
            continue
        x = Object()
        x.name = m.name
        nodes = m.node_tree.nodes
        # Diffuse
        if 'Diffuse BSDF' in nodes:
            x.diffuse = True
            dnode = nodes['Diffuse BSDF']
            dcol = dnode.inputs[0].default_value
            x.diffuse_color = [dcol[0], dcol[1], dcol[2], dcol[3]]
        else:
            x.diffuse = False
        # Glossy
        if 'Glossy BSDF' in nodes:
            x.glossy = True
            gnode = nodes['Glossy BSDF']
            gcol = gnode.inputs[0].default_value
            x.glossy_color = [gcol[0], gcol[1], gcol[2], gcol[3]]
            x.roughness = gnode.inputs[1].default_value
        else:
            x.glossy = False
        # Texture
        if 'Image Texture' in nodes:
            x.texture = nodes['Image Texture'].image.name.split(".")[0]
        else:
            x.texture = ''
        mats.append(x)

    # Output data json
    data.objects = objs
    data.materials = mats
    data.orient = bpy.data.worlds[0]['TargetProjectOrient']
    data.scene = bpy.data.worlds[0]['TargetScene']
    data.packageName = bpy.data.worlds[0]['TargetProjectPackage']
    gravityscn = bpy.data.scenes[bpy.data.worlds[0]['TargetGravity']]
    if gravityscn.use_gravity:
        data.gravity = [gravityscn.gravity[0], gravityscn.gravity[1], gravityscn.gravity[2]]
    else:
        data.gravity = [0.0, 0.0, 0.0]
    clearwrd = bpy.data.worlds[bpy.data.worlds[0]['TargetClear']]
    # Only 'Background' surface for now
    clearcol = clearwrd.node_tree.nodes['Background'].inputs[0].default_value
    data.clear = [clearcol[0], clearcol[1], clearcol[2], clearcol[3]]
    data.fog = bpy.data.worlds[0]['TargetFog']
    data.fogColor = [bpy.data.worlds[0]['TargetFogColor'][0], bpy.data.worlds[0]['TargetFogColor'][1], bpy.data.worlds[0]['TargetFogColor'][2], bpy.data.worlds[0]['TargetFogColor'][3]]
    data.fogDensity = bpy.data.worlds[0]['TargetFogDensity']
    data.shadowMapping = bpy.data.worlds[0]['TargetShadowMapping']
    data.shadowMapSize = bpy.data.worlds[0]['TargetShadowMapSize']
    data.physics = bpy.data.worlds[0]['TargetPhysics']
    data.ssao = bpy.data.worlds[0]['TargetSSAO']
    with open('Assets/data.json', 'w') as f:
        f.write(data.to_JSON())
        
    # Write Main.hx
    # TODO: move to separate file
    #if not os.path.isfile('Sources/Main.hx'):
    with open('Sources/Main.hx', 'w') as f:
        f.write(
"""// Auto-generated
package ;
class Main {
    public static function main() {
        CompileTime.importPackage('zblend.trait');
        CompileTime.importPackage('""" + bpy.data.worlds[0]['TargetProjectPackage'] + """');
        #if js
        untyped __js__("
            function loadScript(url, callback) {
                var head = document.getElementsByTagName('head')[0];
                var script = document.createElement('script');
                script.type = 'text/javascript';
                script.src = url;
                script.onreadystatechange = callback;
                script.onload = callback;
                head.appendChild(script);
            }
        ");
        untyped loadScript('ammo.js', start);
        #else
        start();
        #end
    }
    static function start() {
        var starter = new kha.Starter();
        starter.start(new zblend.Root("ZBlend", "room1", Game));
    }
}
class Game {
    public function new() {
        zblend.Root.setScene(zblend.Root.gameData.scene);
    }
}
""")

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

    # Auto-build nodes
    if (bpy.data.worlds[0]['TargetAutoBuildNodes'] == True):
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
    #self.report({'INFO'}, "Exporting game data...")
    exportGameData()
    
    # Set build command
    if (bpy.data.worlds[0]['TargetEnum'] == 0):
        bashCommand = "Kha/make.js -t osx"
    elif (bpy.data.worlds[0]['TargetEnum'] == 1):
        bashCommand = "Kha/make.js -t windows"
    elif (bpy.data.worlds[0]['TargetEnum'] == 2):
        bashCommand = "Kha/make.js -t linux"
    elif (bpy.data.worlds[0]['TargetEnum'] == 3):
        bashCommand = "Kha/make.js -t html5"
    elif (bpy.data.worlds[0]['TargetEnum'] == 4):
        bashCommand = "Kha/make.js -t ios"
    elif (bpy.data.worlds[0]['TargetEnum'] == 5):
        bashCommand = "Kha/make.js -t android"
    
    # Build
    prefix = "node "
    if (platform.system() == "Darwin"):
        prefix = "/usr/local/bin/node "
    elif (platform.system() == "Linux"):
        prefix = "nodejs "
    
    #p = Process(target=build_process, args=(prefix + bashCommand, open, run, fp, bpy.data.worlds[0]['TargetEnum'], name,))
    #p.start()
    #atexit.register(p.terminate)

    blender_path = bpy.app.binary_path
    blend_path = bpy.data.filepath
    p = subprocess.Popen([blender_path, blend_path, '-b', '-P', fp + '/Libraries/zblend/blender/zblend_build.py', '--', prefix + bashCommand, str(build_type), str(bpy.data.worlds[0]['TargetEnum'])])
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
    if (bpy.data.worlds[0]['TargetAutoBuildNodes'] == True):
        path = 'Sources/' + bpy.data.worlds[0].TargetProjectPackage.replace(".", "/") + "/"
        for node_group in bpy.data.node_groups:
            node_group_name = node_group.name.replace('.', '_')
            os.remove(path + node_group_name + '.hx')

    self.report({'INFO'}, "Clean done")

# Play
class OBJECT_OT_PLAYButton(bpy.types.Operator):
    bl_idname = "zblend.play"
    bl_label = "Play"
 
    def execute(self, context):
        buildProject(self, 1)
        return{'FINISHED'}

# Build
class OBJECT_OT_BUILDButton(bpy.types.Operator):
    bl_idname = "zblend.build"
    bl_label = "Build"
 
    def execute(self, context):
        buildProject(self, 0)
        return{'FINISHED'}

# Open project
class OBJECT_OT_PROJECTButton(bpy.types.Operator):
    bl_idname = "zblend.project"
    bl_label = "Project"
 
    def execute(self, context):
        buildProject(self, 2)
        return{'FINISHED'}

# Open project folder
class OBJECT_OT_FOLDERButton(bpy.types.Operator):
    bl_idname = "zblend.folder"
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
    bl_idname = "zblend.clean"
    bl_label = "Clean"
 
    def execute(self, context):
        cleanProject(self)
        return{'FINISHED'}
    
# Build nodes
class OBJECT_OT_BUILDNODESButton(bpy.types.Operator):
    bl_idname = "zblend.buildnodes"
    bl_label = "Build Nodes"
 
    def execute(self, context):
        
        buildNodeTrees();
            
        self.report({'INFO'}, "Nodes built")
        return{'FINISHED'}
    
# Default settings
class OBJECT_OT_DEFAULTSETTINGSButton(bpy.types.Operator):
    bl_idname = "zblend.defaultsettings"
    bl_label = "Default Settings"
 
    def execute(self, context):
        defaultSettings()
        self.report({'INFO'}, "Defaults set")
        return{'FINISHED'}




def buildNodeTrees():
    # Set dir
    s = bpy.data.filepath.split(os.path.sep)
    s.pop()
    fp = os.path.sep.join(s)
    os.chdir(fp)

    # Make sure package dir exists
    if not os.path.exists('Sources/' + bpy.data.worlds[0].TargetProjectPackage.replace(".", "/")):
        os.makedirs('Sources/' + bpy.data.worlds[0].TargetProjectPackage.replace(".", "/"))
    
    # Export node scripts
    for node_group in bpy.data.node_groups:
        buildNodeTree(node_group)

def buildNodeTree(node_group):
    rn = getRootNode(node_group)

    path = 'Sources/' + bpy.data.worlds[0].TargetProjectPackage.replace(".", "/") + "/"

    node_group_name = node_group.name.replace('.', '_')

    with open(path + node_group_name + '.hx', 'w') as f:
        f.write('package ' + bpy.data.worlds[0].TargetProjectPackage + ';\n\n')
        f.write('import zblend.node.*;\n\n')
        f.write('class ' + node_group_name + ' extends zblend.trait.NodeExecutor {\n\n')
        f.write('\tpublic function new() { super(); }\n\n')
        f.write('\toverride function onItemAdd() {\n')
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
        f.write('\t\t' + name + '.transform = owner.transform;\n')
    
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
bpy.utils.register_module(__name__)
