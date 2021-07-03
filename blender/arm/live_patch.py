import os
import shutil
from typing import Any, Type

import bpy

import arm.assets
import arm.node_utils
from arm.exporter import ArmoryExporter
import arm.log as log
from arm.logicnode.arm_nodes import ArmLogicTreeNode
import arm.make as make
import arm.make_state as state
import arm.utils

# Current patch id
patch_id = 0

# Any object can act as a message bus owner
msgbus_owner = object()

# Whether live patch is currently active
__running = False


def start():
    """Start the live patch session."""
    log.debug("Live patch session started")

    listen(bpy.types.Object, "location", "obj_location")
    listen(bpy.types.Object, "rotation_euler", "obj_rotation")
    listen(bpy.types.Object, "scale", "obj_scale")

    # 'energy' is defined in sub classes only, also workaround for
    # https://developer.blender.org/T88408
    for light_type in (bpy.types.AreaLight, bpy.types.PointLight, bpy.types.SpotLight, bpy.types.SunLight):
        listen(light_type, "color", "light_color")
        listen(light_type, "energy", "light_energy")

    global __running
    __running = True


def stop():
    """Stop the live patch session."""
    global __running
    __running = False

    log.debug("Live patch session stopped")
    bpy.msgbus.clear_by_owner(msgbus_owner)


def patch_export():
    """Re-export the current scene and update the game accordingly."""
    if state.proc_build is not None:
        return

    arm.assets.invalidate_enabled = False

    with arm.utils.WorkingDir(arm.utils.get_fp()):
        asset_path = arm.utils.get_fp_build() + '/compiled/Assets/' + arm.utils.safestr(bpy.context.scene.name) + '.arm'
        ArmoryExporter.export_scene(bpy.context, asset_path, scene=bpy.context.scene)

        dir_std_shaders_dst = os.path.join(arm.utils.build_dir(), 'compiled', 'Shaders', 'std')
        if not os.path.isdir(dir_std_shaders_dst):
            dir_std_shaders_src = os.path.join(arm.utils.get_sdk_path(), 'armory', 'Shaders', 'std')
            shutil.copytree(dir_std_shaders_src, dir_std_shaders_dst)

        node_path = arm.utils.get_node_path()
        khamake_path = arm.utils.get_khamake_path()
        cmd = [
            node_path, khamake_path, 'krom',
            '--shaderversion', '330',
            '--parallelAssetConversion', '4',
            '--to', arm.utils.build_dir() + '/debug',
            '--nohaxe',
            '--noproject'
        ]

        arm.assets.invalidate_enabled = True
        state.proc_build = make.run_proc(cmd, patch_done)


def patch_done():
    """Signal Iron to reload the running scene after a re-export."""
    js = 'iron.Scene.patch();'
    write_patch(js)
    state.proc_build = None


def write_patch(js: str):
    """Write the given javascript code to 'krom.patch'."""
    global patch_id
    with open(arm.utils.get_fp_build() + '/debug/krom/krom.patch', 'w') as f:
        patch_id += 1
        f.write(str(patch_id) + '\n')
        f.write(js)


def listen(rna_type: Type[bpy.types.bpy_struct], prop: str, event_id: str):
    """Subscribe to '<rna_type>.<prop>'. The event_id can be choosen
    freely but must match with the id used in send_event().
    """
    bpy.msgbus.subscribe_rna(
        key=(rna_type, prop),
        owner=msgbus_owner,
        args=(event_id, ),
        notify=send_event
        # options={"PERSISTENT"}
    )


def send_event(event_id: str, opt_data: Any = None):
    """Send the result of the given event to Krom."""
    if not __running:
        return

    if hasattr(bpy.context, 'object') and bpy.context.object is not None:
        obj = bpy.context.object.name

        if bpy.context.object.mode == "OBJECT":
            if event_id == "obj_location":
                vec = bpy.context.object.location
                js = f'var o = iron.Scene.active.getChild("{obj}"); o.transform.loc.set({vec[0]}, {vec[1]}, {vec[2]}); o.transform.dirty = true;'
                write_patch(js)

            elif event_id == 'obj_scale':
                vec = bpy.context.object.scale
                js = f'var o = iron.Scene.active.getChild("{obj}"); o.transform.scale.set({vec[0]}, {vec[1]}, {vec[2]}); o.transform.dirty = true;'
                write_patch(js)

            elif event_id == 'obj_rotation':
                vec = bpy.context.object.rotation_euler.to_quaternion()
                js = f'var o = iron.Scene.active.getChild("{obj}"); o.transform.rot.set({vec[1]}, {vec[2]}, {vec[3]}, {vec[0]}); o.transform.dirty = true;'
                write_patch(js)

            elif event_id == 'light_color':
                light: bpy.types.Light = bpy.context.object.data
                vec = light.color
                js = f'var lRaw = iron.Scene.active.getLight("{light.name}").data.raw; lRaw.color[0]={vec[0]}; lRaw.color[1]={vec[1]}; lRaw.color[2]={vec[2]};'
                write_patch(js)

            elif event_id == 'light_energy':
                light: bpy.types.Light = bpy.context.object.data

                # Align strength to Armory, see exporter.export_light()
                # TODO: Use exporter.export_light() and simply reload all raw light data in Iron?
                strength_fac = 1.0
                if light.type == 'SUN':
                    strength_fac = 0.325
                elif light.type in ('POINT', 'SPOT', 'AREA'):
                    strength_fac = 0.01

                js = f'var lRaw = iron.Scene.active.getLight("{light.name}").data.raw; lRaw.strength={light.energy * strength_fac};'
                write_patch(js)

        else:
            patch_export()

    if event_id == 'ln_insert_link':
        node: ArmLogicTreeNode
        link: bpy.types.NodeLink
        node, link = opt_data

        # This event is called twice for a connection but we only need
        # send it once
        if node == link.from_node:
            tree_name = arm.node_utils.get_export_tree_name(node.get_tree())

            # [1:] is used here because make_logic already uses that for
            # node names if arm_debug is used
            from_node_name = arm.node_utils.get_export_node_name(node)[1:]
            to_node_name = arm.node_utils.get_export_node_name(link.to_node)[1:]

            from_index = arm.node_utils.get_socket_index(node.outputs, link.from_socket)
            to_index = arm.node_utils.get_socket_index(link.to_node.inputs, link.to_socket)

            js = f'LivePatch.patchCreateNodeLink("{tree_name}", "{from_node_name}", "{to_node_name}", "{from_index}", "{to_index}");'
            write_patch(js)

    if event_id == 'ln_update_prop':
        node: ArmLogicTreeNode
        prop_name: str
        node, prop_name = opt_data

        tree_name = arm.node_utils.get_export_tree_name(node.get_tree())
        node_name = arm.node_utils.get_export_node_name(node)[1:]

        value = arm.node_utils.haxe_format_prop(node, prop_name)

        js = f'LivePatch.patchUpdateNodeProp("{tree_name}", "{node_name}", "{prop_name}", {value});'
        write_patch(js)


def on_operator(operator_id: str):
    """As long as bpy.msgbus doesn't listen to changes made by
    operators (*), additionally notify the callback manually.

    (*) https://developer.blender.org/T72109
    """
    if not __running:
        return
    # Don't re-export the scene for the following operators
    if operator_id in ("VIEW3D_OT_select", "OUTLINER_OT_item_activate", "OBJECT_OT_editmode_toggle", "NODE_OT_select", "NODE_OT_translate_attach_remove_on_cancel"):
        return

    if operator_id == "TRANSFORM_OT_translate":
        send_event("obj_location")
    elif operator_id in ("TRANSFORM_OT_rotate", "TRANSFORM_OT_trackball"):
        send_event("obj_rotation")
    elif operator_id == "TRANSFORM_OT_resize":
        send_event("obj_scale")

    # Rebuild
    else:
        patch_export()