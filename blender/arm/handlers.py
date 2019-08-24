import os
import sys
import bpy
import importlib
from bpy.app.handlers import persistent
import arm.utils
import arm.props as props
import arm.make as make
import arm.make_state as state
import arm.api

@persistent
def on_depsgraph_update_post(self):
    if state.proc_build != None:
        return

    # Recache
    depsgraph = bpy.context.evaluated_depsgraph_get()

    for update in depsgraph.updates:
        uid = update.id
        if hasattr(uid, 'arm_cached'):
            # uid.arm_cached = False # TODO: does not trigger update
            if isinstance(uid, bpy.types.Mesh) and uid.name in bpy.data.meshes:
                bpy.data.meshes[uid.name].arm_cached = False
            elif isinstance(uid, bpy.types.Curve) and uid.name in bpy.data.curves:
                bpy.data.curves[uid.name].arm_cached = False
            elif isinstance(uid, bpy.types.MetaBall) and uid.name in bpy.data.metaballs:
                bpy.data.metaballs[uid.name].arm_cached = False
            elif isinstance(uid, bpy.types.Armature) and uid.name in bpy.data.armatures:
                bpy.data.armatures[uid.name].arm_cached = False
            elif isinstance(uid, bpy.types.NodeTree) and uid.name in bpy.data.node_groups:
                bpy.data.node_groups[uid.name].arm_cached = False
            elif isinstance(uid, bpy.types.Material) and uid.name in bpy.data.materials:
                bpy.data.materials[uid.name].arm_cached = False

    # Send last operator to Krom
    wrd = bpy.data.worlds['Arm']
    if state.proc_play != None and \
       state.target == 'krom' and \
       wrd.arm_live_patch:
        ops = bpy.context.window_manager.operators
        if len(ops) > 0 and ops[-1] != None:
            send_operator(ops[-1])

def send_operator(op):
    if hasattr(bpy.context, 'object') and bpy.context.object != None:
        obj = bpy.context.object.name
        if op.name == 'Move':
            vec = bpy.context.object.location
            js = 'var o = iron.Scene.active.getChild("' + obj + '"); o.transform.loc.set(' + str(vec[0]) + ', ' + str(vec[1]) + ', ' + str(vec[2]) + '); o.transform.dirty = true;'
            make.write_patch(js)
        elif op.name == 'Resize':
            vec = bpy.context.object.scale
            js = 'var o = iron.Scene.active.getChild("' + obj + '"); o.transform.scale.set(' + str(vec[0]) + ', ' + str(vec[1]) + ', ' + str(vec[2]) + '); o.transform.dirty = true;'
            make.write_patch(js)
        elif op.name == 'Rotate':
            vec = bpy.context.object.rotation_euler.to_quaternion()
            js = 'var o = iron.Scene.active.getChild("' + obj + '"); o.transform.rot.set(' + str(vec[1]) + ', ' + str(vec[2]) + ', ' + str(vec[3]) + ' ,' + str(vec[0]) + '); o.transform.dirty = true;'
            make.write_patch(js)
        else: # Rebuild
            make.patch()

def always():
    # Force ui redraw
    if state.redraw_ui and context_screen != None:
        for area in context_screen.areas:
            if area.type == 'VIEW_3D' or area.type == 'PROPERTIES':
                area.tag_redraw()
        state.redraw_ui = False
    # TODO: depsgraph.updates only triggers material trees
    space = arm.utils.logic_editor_space(context_screen)
    if space != None:
        space.node_tree.arm_cached = False
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

    # Show trait users as collections
    arm.utils.update_trait_collections()

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
