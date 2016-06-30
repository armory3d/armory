import os
import sys
import shutil
import bpy
import platform
import json
from bpy.props import *
import subprocess
from subprocess import call
import atexit
import webbrowser
import write_data
import nodes_logic
import nodes_pipeline
import nodes_world
import path_tracer
from exporter import ArmoryExporter
import lib.make_resources
import lib.make_variants
import utils

def init_armory_props():
    if not 'CGVersion' in bpy.data.worlds[0]:
        wrd = bpy.data.worlds[0]
        wrd.CGProjectScene = bpy.data.scenes[0].name
        # Switch to Cycles
        if bpy.data.scenes[0].render.engine == 'BLENDER_RENDER':
            for scene in bpy.data.scenes:
                scene.render.engine = 'CYCLES'

# Play button in 3D View panel
def draw_play_item(self, context):
    layout = self.layout
    layout.operator("arm.play")

# Menu in render region
class ArmoryProjectPanel(bpy.types.Panel):
    bl_label = "Armory Project"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    bpy.types.VIEW3D_HT_header.append(draw_play_item)
 
    def draw(self, context):
        layout = self.layout
        wrd = bpy.data.worlds[0]
        layout.prop_search(wrd, "CGProjectScene", bpy.data, "scenes", "Start Scene")
        layout.prop(wrd, 'CGProjectName')
        layout.prop(wrd, 'CGProjectPackage')
        row = layout.row()
        row.prop(wrd, 'CGProjectWidth')
        row.prop(wrd, 'CGProjectHeight')
        layout.prop(wrd, 'CGProjectSamplesPerPixel')
        layout.prop(wrd, 'CGPhysics')

class ArmoryBuildPanel(bpy.types.Panel):
    bl_label = "Armory Build"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
 
    def draw(self, context):
        layout = self.layout
        wrd = bpy.data.worlds[0]
        layout.prop(wrd, 'CGProjectTarget')
        layout.operator("arm.build")
        row = layout.row(align=True)
        row.alignment = 'EXPAND'
        row.operator("arm.folder")
        row.operator("arm.clean")
        layout.prop_search(wrd, "CGKhafileConfig", bpy.data, "texts", "Config")
        layout.prop(wrd, 'CGMinimize')
        layout.prop(wrd, 'CGCacheShaders')
        layout.label('Armory v' + wrd.CGVersion)

def get_export_scene_override(scene):
    # None for now
    override = {
        'window': None,
        'screen': None,
        'area': None,
        'region': None,
        'edit_object': None,
        'scene': scene}
    return override

def compile_shader(raw_path, shader_name, defs):
    os.chdir(raw_path + './' + shader_name)
    lib.make_resources.make(shader_name + '.shader.json', minimize=bpy.data.worlds[0].CGMinimize, defs=defs)
    lib.make_variants.make(shader_name + '.shader.json', defs)

def def_strings_to_array(strdefs):
    defs = strdefs.split('_')
    defs = defs[1:]
    defs = ['_' + d for d in defs] # Restore _
    return defs

def export_game_data(fp, raw_path):
    shader_references = []
    asset_references = []
    
    # Build node trees
    # TODO: cache
    nodes_logic.buildNodeTrees()
    nodes_world.buildNodeTrees(shader_references, asset_references) # TODO: Have to build nodes everytime to collect env map resources
    nodes_pipeline.buildNodeTrees(shader_references, asset_references) 

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
        if scene.game_export:
            bpy.ops.export_scene.armory(
                get_export_scene_override(scene),
                filepath='Assets/generated/' + scene.name + '.json')
            shader_references += ArmoryExporter.shader_references
            asset_references += ArmoryExporter.asset_references

    # Move armatures back
    for a in armatures:
        a.armature.location.x = a.x
        a.armature.location.y = a.y
        a.armature.location.z = a.z
    
    # Write khafile.js
    write_data.write_khafilejs(shader_references, asset_references)

    # Write Main.hx
    write_data.write_main()
    
    # Clean compiled variants if cache is disabled
    if bpy.data.worlds[0].CGCacheShaders == False:
        if os.path.isdir("compiled"):
            shutil.rmtree('compiled')
    
    # Write referenced shader variants
    # Assume asset_references contains shader resources only for now
    for ref in asset_references:
        # Resource does not exist yet
        os.chdir(fp)
        if not os.path.exists(ref):
            shader_name = ref.split('/')[2]
            strdefs = ref[:-5] # Remove .json extnsion
            defs = strdefs.split(shader_name) # 'name/name_def_def'
            if len(defs) > 2:
                strdefs = defs[2] # Apended defs
                defs = def_strings_to_array(strdefs)
            else:
                defs = []
            compile_shader(raw_path, shader_name, defs)

def build_project(self):
    # Save blend
    bpy.ops.wm.save_mainfile()
    
    # Get paths
    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons['armory'].preferences
    sdk_path = addon_prefs.sdk_path
    scripts_path = sdk_path + '/armory/blender/'
    raw_path = sdk_path + '/armory/raw/'
    
    # Set dir
    s = bpy.data.filepath.split(os.path.sep)
    name = s.pop()
    name = name.split(".")
    name = name[0]
    fp = os.path.sep.join(s)
    os.chdir(fp)

    # Create directories
    if not os.path.exists('Sources'):
        os.makedirs('Sources')
    if not os.path.exists('Assets'):
        os.makedirs('Assets')
    
    # Compile path tracer shaders
    if len(bpy.data.cameras) > 0 and bpy.data.cameras[0].pipeline_path == 'pathtrace_pipeline':
        path_tracer.compile(raw_path + 'pt_trace_pass/pt_trace_pass.frag.glsl')

    # Export data
    export_game_data(fp, raw_path)
    
    # Set build command
    target_index = bpy.data.worlds[0]['CGProjectTarget']
    targets = ['html5', 'windows', 'osx', 'linux', 'ios', 'android-native']

    # Copy ammo.js if necessary
    # if target_index == '0':
        # if not os.path.isfile('build/html5/ammo.js'):
            # ammojs_path = utils.get_fp() + '/../haxebullet/js/ammo/ammo.js'
            # shutil.copy(ammojs_path, 'build/html5')

    node_path = sdk_path + '/nodejs/node-osx'
    khamake_path = sdk_path + '/KodeStudio.app/Contents/Resources/app/extensions/kha/Kha/make'
    os.system(node_path + ' ' + khamake_path + ' ' + targets[target_index] + ' &')
    
    self.report({'INFO'}, "Building, see console...")

def play_project(self):
    pass

def clean_project(self):
    os.chdir(utils.get_fp())
    
    # Remove build data
    if os.path.isdir("build"):
        shutil.rmtree('build')

    # Remove generated data
    if os.path.isdir("Assets/generated"):
        shutil.rmtree('Assets/generated')

    # Remove generated shader variants
    if os.path.isdir("compiled"):
        shutil.rmtree('compiled')

    # Remove compiled nodes
    nodes_path = "Sources/" + bpy.data.worlds[0].CGProjectPackage.replace(".", "/") + "/node/"
    if os.path.isdir(nodes_path):
        shutil.rmtree(nodes_path)

    self.report({'INFO'}, "Done")

class ArmoryPlayButton(bpy.types.Operator):
    bl_idname = "arm.play"
    bl_label = "Play"
 
    def execute(self, context):
        play_project(self)
        return{'FINISHED'}

class ArmoryBuildButton(bpy.types.Operator):
    bl_idname = "arm.build"
    bl_label = "Build"
 
    def execute(self, context):
        build_project(self)
        return{'FINISHED'}

class ArmoryFolderButton(bpy.types.Operator):
    bl_idname = "arm.folder"
    bl_label = "Project Folder"
 
    def execute(self, context):
        webbrowser.open('file://' + utils.get_fp())
        return{'FINISHED'}
    
class ArmoryCleanButton(bpy.types.Operator):
    bl_idname = "arm.clean"
    bl_label = "Clean Project"
 
    def execute(self, context):
        clean_project(self)
        return{'FINISHED'}

# Registration
def register():
    bpy.utils.register_module(__name__)
    init_armory_props()

def unregister():
    bpy.utils.unregister_module(__name__)
