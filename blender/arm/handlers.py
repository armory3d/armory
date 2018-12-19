import os
import sys
import bpy
import importlib
from bpy.app.handlers import persistent
import arm.utils
import arm.props as props
import arm.make_state as state
import arm.api

@persistent
def on_depsgraph_update_post(self):
    if state.proc_build != None:
        return

    depsgraph = bpy.context.depsgraph
    for update in depsgraph.updates:
        uid = update.id
        if hasattr(uid, 'arm_cached'):
            # uid.arm_cached = False # TODO: does not trigger update
            if isinstance(uid, bpy.types.Mesh):
                bpy.data.meshes[uid.name].arm_cached = False
            elif isinstance(uid, bpy.types.Curve):
                bpy.data.curves[uid.name].arm_cached = False
            elif isinstance(uid, bpy.types.MetaBall):
                bpy.data.metaballs[uid.name].arm_cached = False
            elif isinstance(uid, bpy.types.Armature):
                bpy.data.armatures[uid.name].arm_cached = False
            elif isinstance(uid, bpy.types.NodeTree):
                bpy.data.node_groups[uid.name].arm_cached = False
            elif isinstance(uid, bpy.types.Material):
                bpy.data.materials[uid.name].arm_cached = False

def always():
    if state.redraw_ui and context_screen != None:
        for area in context_screen.areas:
            if area.type == 'VIEW_3D' or area.type == 'PROPERTIES':
                area.tag_redraw()
        state.redraw_ui = False
    return 0.5

appended_py_paths = []
context_screen = None

@persistent
def on_load_post(context):
    global appended_py_paths

    global context_screen
    context_screen = bpy.context.screen

    props.init_properties_on_load()
    reload_blend_data()

    bpy.ops.arm.sync_proxy()

    wrd = bpy.data.worlds['Arm']
    wrd.arm_recompile = True
    arm.api.drivers = dict()

    # Load libraries
    if os.path.exists(arm.utils.get_fp() + '/Libraries'):
        libs = os.listdir(arm.utils.get_fp() + '/Libraries')
        for lib in libs:
            if os.path.isdir(arm.utils.get_fp() + '/Libraries/' + lib):
                fp = arm.utils.get_fp() + '/Libraries/' + lib
                if fp not in appended_py_paths and os.path.exists(fp + '/blender.py'):
                    appended_py_paths.append(fp)
                    sys.path.append(fp)
                    import blender
                    importlib.reload(blender)
                    blender.register()
                    sys.path.remove(fp)

    arm.utils.update_trait_groups()

def reload_blend_data():
    armory_pbr = bpy.data.node_groups.get('Armory PBR')
    if armory_pbr == None:
        load_library('Armory PBR')

def load_library(asset_name):
    if bpy.data.filepath.endswith('arm_data.blend'): # Prevent load in library itself
        return
    sdk_path = arm.utils.get_sdk_path()
    data_path = sdk_path + '/armory/blender/data/arm_data.blend'
    data_names = [asset_name]

    # Import
    data_refs = data_names.copy()
    with bpy.data.libraries.load(data_path, link=False) as (data_from, data_to):
        data_to.node_groups = data_refs

    for ref in data_refs:
        ref.use_fake_user = True

def register():
    bpy.app.handlers.load_post.append(on_load_post)
    bpy.app.handlers.depsgraph_update_post.append(on_depsgraph_update_post)
    # bpy.app.handlers.undo_post.append(on_undo_post)
    bpy.app.timers.register(always, persistent=True)

    # TODO: On windows, on_load_post is not called when opening .blend file from explorer
    if arm.utils.get_os() == 'win' and arm.utils.get_fp() != '':
        on_load_post(None)
    reload_blend_data()

def unregister():
    bpy.app.handlers.load_post.remove(on_load_post)
    bpy.app.handlers.depsgraph_update_post.remove(on_depsgraph_update_post)
    # bpy.app.handlers.undo_post.remove(on_undo_post)
