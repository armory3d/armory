import importlib
import os
import queue
import sys
import types

import bpy
from bpy.app.handlers import persistent

import arm
import arm.api
import arm.nodes_logic
import arm.make_state as state
import arm.utils
import arm.utils_vs
from arm import live_patch, log, make, props
from arm.logicnode import arm_nodes

if arm.is_reload(__name__):
    arm.api = arm.reload_module(arm.api)
    live_patch = arm.reload_module(live_patch)
    log = arm.reload_module(log)
    arm_nodes = arm.reload_module(arm_nodes)
    arm.nodes_logic = arm.reload_module(arm.nodes_logic)
    make = arm.reload_module(make)
    state = arm.reload_module(state)
    props = arm.reload_module(props)
    arm.utils = arm.reload_module(arm.utils)
    arm.utils_vs = arm.reload_module(arm.utils_vs)
else:
    arm.enable_reload(__name__)


@persistent
def on_depsgraph_update_post(self):
    if state.proc_build is not None:
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

    # Hacky solution to update armory props after operator executions.
    # bpy.context.active_operator doesn't always exist, in some cases
    # like marking assets for example, this code is also executed before
    # the operator actually finishes and sets the variable
    last_operator = getattr(bpy.context, 'active_operator', None)
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
            target_obj.arm_rb_angular_friction = source_obj.arm_rb_angular_friction
            target_obj.arm_rb_trigger = source_obj.arm_rb_trigger
            target_obj.arm_rb_deactivation_time = source_obj.arm_rb_deactivation_time
            target_obj.arm_rb_ccd = source_obj.arm_rb_ccd
            target_obj.arm_rb_collision_filter_mask = source_obj.arm_rb_collision_filter_mask

    elif operator_id == "NODE_OT_new_node_tree":
        if bpy.context.space_data.tree_type == arm.nodes_logic.ArmLogicTree.bl_idname:
            # In Blender 3.5+, new node trees are no longer called "NodeTree"
            # but follow the bl_label attribute by default. New logic trees
            # are thus called "Armory Logic Editor" which conflicts with Haxe's
            # class naming convention. To avoid this, we listen for the
            # creation of a node tree and then rename it.
            # Unfortunately, manually naming the tree has the unfortunate
            # side effect of not basing the new name on the name of the
            # previously opened node tree, as it is the case for Blender trees...
            bpy.context.space_data.edit_tree.name = "LogicTree"


def send_operator(op):
    if hasattr(bpy.context, 'object') and bpy.context.object is not None:
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
    if state.redraw_ui:
        for area in bpy.context.screen.areas:
            if area.type in ('NODE_EDITOR', 'PROPERTIES', 'VIEW_3D'):
                area.tag_redraw()
        state.redraw_ui = False

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


loaded_py_libraries: dict[str, types.ModuleType] = {}
context_screen = None


@persistent
def on_save_pre(context):
    # Ensure that files are saved with the correct version number
    # (e.g. startup files with an "Arm" world may have old version numbers)
    wrd = bpy.data.worlds['Arm']
    wrd.arm_version = props.arm_version
    wrd.arm_commit = props.arm_commit


@persistent
def on_load_pre(context):
    unload_py_libraries()


@persistent
def on_load_post(context):
    global context_screen
    context_screen = bpy.context.screen

    props.init_properties_on_load()
    reload_blend_data()
    arm.utils.fetch_bundled_script_names()

    wrd = bpy.data.worlds['Arm']
    wrd.arm_recompile = True
    arm.api.remove_drivers()

    load_py_libraries()

    # Show trait users as collections
    arm.utils.update_trait_collections()
    props.update_armory_world()


def load_py_libraries():
    if bpy.data.filepath == '':
        # When a blend file is opened from the file explorer, Blender
        # first opens the default file and then the actual blend file,
        # so this function is called twice. Because the cwd is already
        # that of the folder containing the blend file, libraries would
        # be loaded/unloaded once for the default file which is not needed.
        return

    lib_path = os.path.join(arm.utils.get_fp(), 'Libraries')
    if os.path.exists(lib_path):
        # Don't register nodes twice when calling register_nodes()
        arm_nodes.reset_globals()

        # Make sure that Armory's categories are registered first (on top of the menu)
        arm.logicnode.init_categories()

        libs = os.listdir(lib_path)
        for lib_name in libs:
            fp = os.path.join(lib_path, lib_name)
            if os.path.isdir(fp):
                if os.path.exists(os.path.join(fp, 'blender.py')):
                    sys.path.append(fp)

                    lib_module = importlib.import_module('blender')
                    importlib.reload(lib_module)
                    if hasattr(lib_module, 'register'):
                        lib_module.register()

                    log.debug(f'Armory: Loaded Python library {lib_name}')
                    loaded_py_libraries[lib_name] = lib_module

                    sys.path.remove(fp)

        # Register newly added nodes and node categories
        arm.nodes_logic.register_nodes()


def unload_py_libraries():
    for lib_name, lib_module in loaded_py_libraries.items():
        if hasattr(lib_module, 'unregister'):
            lib_module.unregister()
        arm.log.debug(f'Armory: Unloaded Python library {lib_name}')

    loaded_py_libraries.clear()


def reload_blend_data():
    armory_pbr = bpy.data.node_groups.get('Armory PBR')
    if armory_pbr is None:
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


def post_register():
    """Called in start.py after all Armory modules have been registered.
    It is also called in case of add-on reloads. Put code here that
    needs to be run once at the beginning of each session.
    """
    if arm.utils.get_os_is_windows():
        arm.utils_vs.fetch_installed_vs(silent=True)


def register():
    bpy.app.handlers.save_pre.append(on_save_pre)
    bpy.app.handlers.load_pre.append(on_load_pre)
    bpy.app.handlers.load_post.append(on_load_post)
    bpy.app.handlers.depsgraph_update_post.append(on_depsgraph_update_post)
    # bpy.app.handlers.undo_post.append(on_undo_post)

    bpy.app.timers.register(always, persistent=True)
    bpy.app.timers.register(poll_threads, persistent=True)

    if arm.utils.get_fp() != '':
        # TODO: On windows, on_load_post is not called when opening .blend file from explorer
        if arm.utils.get_os() == 'win':
            on_load_post(None)
        else:
            # load_py_libraries() is called by on_load_post(). This call makes sure that libraries are also loaded
            # when a file is already opened during add-on registration
            load_py_libraries()

    reload_blend_data()


def unregister():
    unload_py_libraries()

    bpy.app.timers.unregister(poll_threads)
    bpy.app.timers.unregister(always)

    bpy.app.handlers.load_post.remove(on_load_post)
    bpy.app.handlers.load_pre.remove(on_load_pre)
    bpy.app.handlers.save_pre.remove(on_save_pre)
    bpy.app.handlers.depsgraph_update_post.remove(on_depsgraph_update_post)
    # bpy.app.handlers.undo_post.remove(on_undo_post)
