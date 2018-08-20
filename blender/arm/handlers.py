import os
import sys
import bpy
from bpy.app.handlers import persistent
import arm.utils
import arm.props as props
import arm.make as make
import arm.make_state as state
import arm.api

last_operator = None
first_update = True
v8_started = False

@persistent
def on_scene_update_pre(context):
    # TODO: get rid of this function as soon as there is a proper way to detect object data updates
    global last_operator
    global first_update
    global v8_started

    if first_update == True: # Skip first one, object reports is_update_data
        first_update = False
        return

    # Viewport player
    with_armory = bpy.context.scene.render.engine == 'ARMORY'
    if with_armory:
        play_area = None
        if bpy.context.screen != None:
            for area in bpy.context.screen.areas:
                if area.type == 'VIEW_3D':
                    play_area = area
                    break
        if play_area != None and play_area.spaces[0].shading.type == 'MATERIAL':
            if not v8_started:
                v8_started = True
                make.build_viewport()
        else:
            v8_started = False

    if state.redraw_ui and bpy.context.screen != None:
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D' or area.type == 'PROPERTIES':
                area.tag_redraw()
        state.redraw_ui = False

    # Recache edited data
    ops = bpy.context.window_manager.operators
    operators_changed = False
    if len(ops) > 0 and last_operator != ops[-1]:
        last_operator = ops[-1]
        operators_changed = True

    if hasattr(bpy.context, 'active_object'):
        obj = bpy.context.active_object
        if obj != None:
            if obj.data != None and obj.data.is_updated:
                recache(obj)
            if len(ops) > 0 and ops[-1].bl_idname == 'OBJECT_OT_transform_apply':
                recache(obj)
            # New children
            if obj.type == 'ARMATURE':
                for c in obj.children:
                    if c.data != None and c.data.is_updated:
                        recache(c)
    if hasattr(bpy.context, 'sculpt_object') and bpy.context.sculpt_object != None:
        recache(bpy.context.sculpt_object)
    if hasattr(bpy.context, 'active_pose_bone') and bpy.context.active_pose_bone != None:
        recache(bpy.context.active_object)

    if hasattr(bpy.context, 'object'):
        obj = bpy.context.object
        if obj != None:
            if operators_changed:
                op_changed(ops[-1], obj)
            if obj.active_material != None and obj.active_material.is_updated:
                if obj.active_material.lock_cache == True: # is_cached was set to true, resulting in a is_updated call
                    obj.active_material.lock_cache = False
                else:
                    obj.active_material.is_cached = False

    # Invalidate logic node tree cache if it is being edited..
    space = arm.utils.logic_editor_space()
    if space != None:
        space.node_tree.is_cached = False

def recache(obj):
    # Moving keyframes triggers is_updated_data..
    if state.proc_build != None:
        return
    if obj.data == None:
        return
    if hasattr(obj.data, 'arm_cached'):
        obj.data.arm_cached = False

def op_changed(op, obj):
    # Recache mesh data
    if op.bl_idname == 'OBJECT_OT_modifier_add' or \
       op.bl_idname == 'OBJECT_OT_modifier_remove' or \
       op.bl_idname == 'OBJECT_OT_transform_apply' or \
       op.bl_idname == 'APPLY_OT_transformlocrotscale' or \
       op.bl_idname == 'OBJECT_OT_shade_smooth' or \
       op.bl_idname == 'OBJECT_OT_shade_flat':
        # Note: Blender reverts object data when manipulating
        # OBJECT_OT_transform_apply operator.. recaching object flag instead
        obj.arm_cached = False
    if op.bl_idname.startswith('MARKER_OT_'):
        # Marker changed, recache action
        obj.data.arm_cached = False

appended_py_paths = []
@persistent
def on_load_post(context):
    global appended_py_paths
    global first_update

    first_update = True

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
                    sys.path.append(fp)
                    appended_py_paths.append(fp)
                    import blender
                    blender.register()

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
    if hasattr(bpy.app.handlers, 'scene_update_pre'):
        bpy.app.handlers.scene_update_pre.append(on_scene_update_pre)
    bpy.app.handlers.load_post.append(on_load_post)
    # TODO: On windows, on_load_post is not called when opening .blend file from explorer
    if arm.utils.get_os() == 'win' and arm.utils.get_fp() != '':
        on_load_post(None)
    reload_blend_data()

def unregister():
    if hasattr(bpy.app.handlers, 'scene_update_pre'):
        bpy.app.handlers.scene_update_pre.remove(on_scene_update_pre)
    bpy.app.handlers.load_post.remove(on_load_post)
