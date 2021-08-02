import importlib
import os
import queue
import sys

import bpy
from bpy.app.handlers import persistent

import arm.api
import arm.live_patch as live_patch
import arm.logicnode.arm_nodes as arm_nodes
import arm.nodes_logic
import arm.make as make
import arm.make_state as state
import arm.props as props
import arm.utils


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
    if state.proc_play is not None and state.target == 'krom' and wrd.arm_live_patch:
        ops = bpy.context.window_manager.operators
        if len(ops) > 0 and ops[-1] is not None:
            live_patch.on_operator(ops[-1].bl_idname)

    # Hacky solution to update armory props after operator executions
    last_operator = bpy.context.active_operator
    if last_operator is not None:
        on_operator_post(last_operator.bl_idname)


def on_operator_post(operator_id: str) -> None:
    """Called after operator execution. Does not work for operators
    executed in another context. Warning: this function is also called
    when the operator execution raised an exception!"""
    # 3D View > Object > Rigid Body > Copy from Active
    if operator_id == "RIGIDBODY_OT_object_settings_copy":
        # Copy armory rigid body settings
        source_obj = bpy.context.active_object
        for target_obj in bpy.context.selected_objects:
            target_obj.arm_rb_linear_factor = source_obj.arm_rb_linear_factor
            target_obj.arm_rb_angular_factor = source_obj.arm_rb_angular_factor
            target_obj.arm_rb_trigger = source_obj.arm_rb_trigger
            target_obj.arm_rb_force_deactivation = source_obj.arm_rb_force_deactivation
            target_obj.arm_rb_deactivation_time = source_obj.arm_rb_deactivation_time
            target_obj.arm_rb_ccd = source_obj.arm_rb_ccd
            target_obj.arm_rb_collision_filter_mask = source_obj.arm_rb_collision_filter_mask


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


def always() -> float:
    # Force ui redraw
    if state.redraw_ui and context_screen is not None:
        for area in context_screen.areas:
            if area.type == 'VIEW_3D' or area.type == 'PROPERTIES':
                area.tag_redraw()
        state.redraw_ui = False
    # TODO: depsgraph.updates only triggers material trees
    space = arm.utils.logic_editor_space(context_screen)
    if space is not None:
        space.node_tree.arm_cached = False
    return 0.5


def poll_threads() -> float:
    """Polls the thread callback queue and if a thread has finished, it
    is joined with the main thread and the corresponding callback is
    executed in the main thread.
    """
    try:
        thread, callback = make.thread_callback_queue.get(block=False)
    except queue.Empty:
        return 0.25

    thread.join()

    try:
        callback()
    except Exception as e:
        # If there is an exception, we can no longer return the time to
        # the next call to this polling function, so to keep it running
        # we re-register it and then raise the original exception.
        bpy.app.timers.unregister(poll_threads)
        bpy.app.timers.register(poll_threads, first_interval=0.01, persistent=True)
        raise e

    # Quickly check if another thread has finished
    return 0.01


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

    load_libraries()

    # Show trait users as collections
    arm.utils.update_trait_collections()
    props.update_armory_world()


def load_libraries():
    lib_path = os.path.join(arm.utils.get_fp(), 'Libraries')
    if os.path.exists(lib_path):
        # Don't register nodes twice when calling register_nodes()
        arm_nodes.reset_globals()

        # Make sure that Armory's categories are registered first (on top of the menu)
        arm.logicnode.init_categories()

        libs = os.listdir(lib_path)
        for lib in libs:
            fp = os.path.join(lib_path, lib)
            if os.path.isdir(fp):
                if fp not in appended_py_paths and os.path.exists(os.path.join(fp, 'blender.py')):
                    appended_py_paths.append(fp)
                    sys.path.append(fp)
                    import blender
                    importlib.reload(blender)
                    blender.register()
                    sys.path.remove(fp)

        # Register newly added nodes and node categories
        arm.nodes_logic.register_nodes()


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
    global appended_py_paths

    bpy.app.handlers.load_post.append(on_load_post)
    bpy.app.handlers.depsgraph_update_post.append(on_depsgraph_update_post)
    # bpy.app.handlers.undo_post.append(on_undo_post)

    bpy.app.timers.register(always, persistent=True)
    bpy.app.timers.register(poll_threads, persistent=True)

    if arm.utils.get_fp() != '':
        appended_py_paths = []

        # TODO: On windows, on_load_post is not called when opening .blend file from explorer
        if arm.utils.get_os() == 'win':
            on_load_post(None)
        else:
            # load_libraries() is called by on_load_post(). This call makes sure that libraries are also loaded
            # when a file is already opened during add-on registration
            load_libraries()

    reload_blend_data()


def unregister():
    bpy.app.timers.unregister(poll_threads)
    bpy.app.timers.unregister(always)

    bpy.app.handlers.load_post.remove(on_load_post)
    bpy.app.handlers.depsgraph_update_post.remove(on_depsgraph_update_post)
    # bpy.app.handlers.undo_post.remove(on_undo_post)
