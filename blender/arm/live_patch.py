import os
import shutil
from typing import Any, Type

import bpy

import arm.assets
from arm import log, make
from arm.exporter import ArmoryExporter
from arm.logicnode.arm_nodes import ArmLogicTreeNode
import arm.make_state as state
import arm.node_utils
import arm.utils

if arm.is_reload(__name__):
    arm.assets = arm.reload_module(arm.assets)
    arm.exporter = arm.reload_module(arm.exporter)
    from arm.exporter import ArmoryExporter
    log = arm.reload_module(log)
    arm.logicnode.arm_nodes = arm.reload_module(arm.logicnode.arm_nodes)
    from arm.logicnode.arm_nodes import ArmLogicTreeNode
    make = arm.reload_module(make)
    state = arm.reload_module(state)
    arm.node_utils = arm.reload_module(arm.node_utils)
    arm.utils = arm.reload_module(arm.utils)
else:
    arm.enable_reload(__name__)

    patch_id = 0
    """Current patch id"""

    __running = False
    """Whether live patch is currently active"""

# Any object can act as a message bus owner
msgbus_owner = object()


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
    global __running, patch_id
    if __running:
        __running = False
        patch_id = 0

        log.debug("Live patch session stopped")
        bpy.msgbus.clear_by_owner(msgbus_owner)


def patch_export():
    """Re-export the current scene and update the game accordingly."""
    if not __running or state.proc_build is not None:
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
    with open(arm.utils.get_fp_build() + '/debug/krom/krom.patch', 'w', encoding='utf-8') as f:
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

    elif event_id == 'ln_update_prop':
        node: ArmLogicTreeNode
        prop_name: str
        node, prop_name = opt_data

        tree_name = arm.node_utils.get_export_tree_name(node.get_tree())
        node_name = arm.node_utils.get_export_node_name(node)[1:]

        value = arm.node_utils.haxe_format_prop_value(node, prop_name)

        if prop_name.endswith('_get'):
            # Hack because some nodes use a different Python property
            # name than they use in Haxe
            prop_name = prop_name[:-4]

        js = f'LivePatch.patchUpdateNodeProp("{tree_name}", "{node_name}", "{prop_name}", {value});'
        write_patch(js)

    elif event_id == 'ln_socket_val':
        node: ArmLogicTreeNode
        socket: bpy.types.NodeSocket
        node, socket = opt_data

        socket_index = arm.node_utils.get_socket_index(node.inputs, socket)

        if socket_index != -1:
            tree_name = arm.node_utils.get_export_tree_name(node.get_tree())
            node_name = arm.node_utils.get_export_node_name(node)[1:]

            value = socket.get_default_value()
            inp_type = socket.arm_socket_type

            if inp_type in ('VECTOR', 'RGB'):
                value = f'new iron.Vec4({arm.node_utils.haxe_format_socket_val(value, array_outer_brackets=False)}, 1.0)'
            elif inp_type == 'RGBA':
                value = f'new iron.Vec4({arm.node_utils.haxe_format_socket_val(value, array_outer_brackets=False)})'
            elif inp_type == 'ROTATION':
                value = f'new iron.Quat({arm.node_utils.haxe_format_socket_val(value, array_outer_brackets=False)})'
            elif inp_type == 'OBJECT':
                value = f'iron.Scene.active.getChild("{value}")' if value != '' else 'null'
            else:
                value = arm.node_utils.haxe_format_socket_val(value)

            js = f'LivePatch.patchUpdateNodeInputVal("{tree_name}", "{node_name}", {socket_index}, {value});'
            write_patch(js)

    elif event_id == 'ln_create':
        node: ArmLogicTreeNode = opt_data

        tree_name = arm.node_utils.get_export_tree_name(node.get_tree())
        node_name = arm.node_utils.get_export_node_name(node)[1:]
        node_type = 'armory.logicnode.' + node.bl_idname[2:]

        prop_names = list(arm.node_utils.get_haxe_property_names(node))
        prop_py_names, prop_hx_names = zip(*prop_names) if len(prop_names) > 0 else ([], [])
        prop_values = (getattr(node, prop_name) for prop_name in prop_py_names)
        prop_datas = arm.node_utils.haxe_format_socket_val(list(zip(prop_hx_names, prop_values)))

        inp_data = [(inp.arm_socket_type, inp.get_default_value()) for inp in node.inputs]
        inp_data = arm.node_utils.haxe_format_socket_val(inp_data)
        out_data = [(out.arm_socket_type, out.get_default_value()) for out in node.outputs]
        out_data = arm.node_utils.haxe_format_socket_val(out_data)

        js = f'LivePatch.patchNodeCreate("{tree_name}", "{node_name}", "{node_type}", {prop_datas}, {inp_data}, {out_data});'
        write_patch(js)

    elif event_id == 'ln_delete':
        node: ArmLogicTreeNode = opt_data

        tree_name = arm.node_utils.get_export_tree_name(node.get_tree())
        node_name = arm.node_utils.get_export_node_name(node)[1:]

        js = f'LivePatch.patchNodeDelete("{tree_name}", "{node_name}");'
        write_patch(js)

    elif event_id == 'ln_copy':
        newnode: ArmLogicTreeNode
        node: ArmLogicTreeNode
        newnode, node = opt_data

        # Use newnode to get the tree, node has no id_data at this moment
        tree_name = arm.node_utils.get_export_tree_name(newnode.get_tree())

        newnode_name = arm.node_utils.get_export_node_name(newnode)[1:]
        node_name = arm.node_utils.get_export_node_name(node)[1:]

        props_list = '[' + ','.join(f'"{p}"' for _, p in arm.node_utils.get_haxe_property_names(node)) + ']'

        inp_data = [(inp.arm_socket_type, inp.get_default_value()) for inp in newnode.inputs]
        inp_data = arm.node_utils.haxe_format_socket_val(inp_data)
        out_data = [(out.arm_socket_type, out.get_default_value()) for out in newnode.outputs]
        out_data = arm.node_utils.haxe_format_socket_val(out_data)

        js = f'LivePatch.patchNodeCopy("{tree_name}", "{node_name}", "{newnode_name}", {props_list}, {inp_data}, {out_data});'
        write_patch(js)

    elif event_id == 'ln_update_sockets':
        node: ArmLogicTreeNode = opt_data

        tree_name = arm.node_utils.get_export_tree_name(node.get_tree())
        node_name = arm.node_utils.get_export_node_name(node)[1:]

        inp_data = '['
        for idx, inp in enumerate(node.inputs):
            inp_data += '{'
            # is_linked can be true even if there are no links if the
            # user starts dragging a connection away before releasing
            # the mouse
            if inp.is_linked and len(inp.links) > 0:
                inp_data += 'isLinked: true,'
                inp_data += f'fromNode: "{arm.node_utils.get_export_node_name(inp.links[0].from_node)[1:]}",'
                inp_data += f'fromIndex: {arm.node_utils.get_socket_index(inp.links[0].from_node.outputs, inp.links[0].from_socket)},'
            else:
                inp_data += 'isLinked: false,'
                inp_data += f'socketType: "{inp.arm_socket_type}",'
                inp_data += f'socketValue: {arm.node_utils.haxe_format_socket_val(inp.get_default_value())},'

            inp_data += f'toIndex: {idx}'
            inp_data += '},'
        inp_data += ']'

        out_data = '['
        for idx, out in enumerate(node.outputs):
            out_data += '['
            for link in out.links:
                out_data += '{'
                if out.is_linked:
                    out_data += 'isLinked: true,'
                    out_data += f'toNode: "{arm.node_utils.get_export_node_name(link.to_node)[1:]}",'
                    out_data += f'toIndex: {arm.node_utils.get_socket_index(link.to_node.inputs, link.to_socket)},'
                else:
                    out_data += 'isLinked: false,'
                    out_data += f'socketType: "{out.arm_socket_type}",'
                    out_data += f'socketValue: {arm.node_utils.haxe_format_socket_val(out.get_default_value())},'

                out_data += f'fromIndex: {idx}'
                out_data += '},'
            out_data += '],'
        out_data += ']'

        js = f'LivePatch.patchSetNodeLinks("{tree_name}", "{node_name}", {inp_data}, {out_data});'
        write_patch(js)


def on_operator(operator_id: str):
    """As long as bpy.msgbus doesn't listen to changes made by
    operators (*), additionally notify the callback manually.

    (*) https://developer.blender.org/T72109
    """
    if not __running:
        return

    if operator_id in IGNORE_OPERATORS:
        return

    if operator_id == 'TRANSFORM_OT_translate':
        send_event('obj_location')
    elif operator_id in ('TRANSFORM_OT_rotate', 'TRANSFORM_OT_trackball'):
        send_event('obj_rotation')
    elif operator_id == 'TRANSFORM_OT_resize':
        send_event('obj_scale')

    # Rebuild
    else:
        patch_export()


# Don't re-export the scene for the following operators
IGNORE_OPERATORS = (
    'ARM_OT_node_add_input',
    'ARM_OT_node_add_input_output',
    'ARM_OT_node_add_input_value',
    'ARM_OT_node_add_output',
    'ARM_OT_node_call_func',
    'ARM_OT_node_remove_input',
    'ARM_OT_node_remove_input_output',
    'ARM_OT_node_remove_input_value',
    'ARM_OT_node_remove_output',
    'ARM_OT_node_search',

    'NODE_OT_delete',
    'NODE_OT_duplicate_move',
    'NODE_OT_hide_toggle',
    'NODE_OT_link',
    'NODE_OT_move_detach_links',
    'NODE_OT_select',
    'NODE_OT_translate_attach',
    'NODE_OT_translate_attach_remove_on_cancel',

    'OBJECT_OT_editmode_toggle',
    'OUTLINER_OT_item_activate',
    'UI_OT_button_string_clear',
    'UI_OT_eyedropper_id',
    'VIEW3D_OT_select',
    'VIEW3D_OT_select_box',
)
