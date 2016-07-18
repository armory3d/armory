import project
import nodes_logic
import nodes_pipeline
import nodes_world
import exporter
import traits_animation
import traits_params
import traits
import props
import lib.drop_to_ground

import bpy
import utils
import subprocess
import atexit
import os

def register():
    props.register()
    project.register()
    nodes_logic.register()
    nodes_pipeline.register()
    nodes_world.register()
    exporter.register()
    traits_animation.register()
    traits_params.register()
    traits.register()
    lib.drop_to_ground.register()

    # Start server
    user_preferences = bpy.context.user_preferences
    addon_prefs = user_preferences.addons['armory'].preferences
    scripts_path = addon_prefs.sdk_path + '/armory/blender/'
    os.chdir(utils.get_fp())
    blender_path = bpy.app.binary_path
    blend_path = bpy.data.filepath
    register.p = subprocess.Popen([blender_path, blend_path, '-b', '-P', scripts_path + 'lib/server.py', '&'])
    atexit.register(register.p.terminate)

def unregister():
    project.unregister()
    nodes_logic.unregister()
    nodes_pipeline.unregister()
    nodes_world.unregister()
    exporter.unregister()
    traits_animation.unregister()
    traits_params.unregister()
    traits.unregister()
    props.unregister()
    lib.drop_to_ground.unregister()

    # Stop server
    register.p.terminate()
