import collections.abc
from typing import Any, Generator, Optional, Type, Union

import bpy
import mathutils
from bpy.types import NodeSocket, NodeInputs, NodeOutputs
from nodeitems_utils import NodeItem

import arm.log
import arm.logicnode.arm_sockets
import arm.utils

if arm.is_reload(__name__):
    arm.log = arm.reload_module(arm.log)
    arm.logicnode.arm_sockets = arm.reload_module(arm.logicnode.arm_sockets)
    arm.utils = arm.reload_module(arm.utils)
else:
    arm.enable_reload(__name__)


def find_node_by_link(node_group, to_node, inp):
    for link in node_group.links:
        if link.to_node == to_node and link.to_socket == inp:
            if link.from_node.bl_idname == 'NodeReroute': # Step through reroutes
                return find_node_by_link(node_group, link.from_node, link.from_node.inputs[0])
            return link.from_node


def find_node_by_link_from(node_group, from_node, outp):
    for link in node_group.links:
        if link.from_node == from_node and link.from_socket == outp:
            return link.to_node

def find_link(node_group, to_node, inp):
    for link in node_group.links:
        if link.to_node == to_node and link.to_socket == inp:
            return link


def get_node_by_type(node_group: bpy.types.NodeTree, ntype: str) -> bpy.types.Node:
    for node in node_group.nodes:
        if node.type == ntype:
            return node


def iter_nodes_by_type(node_group: bpy.types.NodeTree, ntype: str) -> Generator[bpy.types.Node, None, None]:
    for node in node_group.nodes:
        if node.type == ntype:
            yield node


def input_get_connected_node(input_socket: bpy.types.NodeSocket) -> tuple[Optional[bpy.types.Node], Optional[bpy.types.NodeSocket]]:
    """Get the node and the output socket of that node that is connected
    to the given input, while following reroutes. If the input has
    multiple incoming connections, the first one is followed. If the
    connection route ends without a connected node, `(None, None)` is
    returned.
    """
    # If this method is called while a socket is being unconnected, it
    # can happen that is_linked is true but there are no links
    if not input_socket.is_linked or len(input_socket.links) == 0:
        return None, None

    link: bpy.types.NodeLink = input_socket.links[0]
    from_node = link.from_node

    if from_node.type == 'REROUTE':
        return input_get_connected_node(from_node.inputs[0])

    return from_node, link.from_socket


def output_get_connected_node(output_socket: bpy.types.NodeSocket) -> tuple[Optional[bpy.types.Node], Optional[bpy.types.NodeSocket]]:
    """Get the node and the input socket of that node that is connected
    to the given output, while following reroutes. If the output has
    multiple outgoing connections, the first one is followed. If the
    connection route ends without a connected node, `(None, None)` is
    returned.
    """
    if not output_socket.is_linked or len(output_socket.links) == 0:
        return None, None

    link: bpy.types.NodeLink = output_socket.links[0]
    to_node = link.to_node

    if to_node.type == 'REROUTE':
        return output_get_connected_node(to_node.outputs[0])

    return to_node, link.to_socket


def get_socket_index(sockets: Union[NodeInputs, NodeOutputs], socket: NodeSocket) -> int:
    """Find the socket index in the given node input or output
    collection, return -1 if not found.
    """
    for i in range(0, len(sockets)):
        if sockets[i] == socket:
            return i
    return -1


def get_socket_type(socket: NodeSocket) -> str:
    if isinstance(socket, arm.logicnode.arm_sockets.ArmCustomSocket):
        return socket.arm_socket_type
    else:
        return socket.type


def get_socket_default(socket: NodeSocket) -> Any:
    """Get the socket's default value, or `None` if it doesn't exist."""
    if isinstance(socket, arm.logicnode.arm_sockets.ArmCustomSocket):
        if socket.arm_socket_type != 'NONE':
            return socket.default_value_raw

    # Shader-type sockets don't have a default value
    elif socket.type != 'SHADER':
        return socket.default_value

    return None


def set_socket_default(socket: NodeSocket, value: Any):
    """Set the socket's default value if it exists."""
    if isinstance(socket, arm.logicnode.arm_sockets.ArmCustomSocket):
        if socket.arm_socket_type != 'NONE':
            socket.default_value_raw = value

    # Shader-type sockets don't have a default value
    elif socket.type != 'SHADER':
        socket.default_value = value


def get_export_tree_name(tree: bpy.types.NodeTree, do_warn=False) -> str:
    """Return the name of the given node tree that's used in the
    exported Haxe code.

    If `do_warn` is true, a warning is displayed if the export name
    differs from the actual tree name.
    """
    export_name = arm.utils.safesrc(tree.name[0].upper() + tree.name[1:])

    if export_name != tree.name:
        arm.log.warn('Logic node tree and generated trait names differ! Node'
                     f' tree: "{tree.name}", trait: "{export_name}"')

    return export_name


def get_export_node_name(node: bpy.types.Node) -> str:
    """Return the name of the given node that's used in the exported
    Haxe code.
    """
    return '_' + arm.utils.safesrc(node.name)


def get_haxe_property_names(node: bpy.types.Node) -> Generator[tuple[str, str], None, None]:
    """Generator that yields the names of all node properties that have
    a counterpart in the node's Haxe class.
    """
    for i in range(0, 10):
        prop_name = f'property{i}_get'
        prop_found = hasattr(node, prop_name)
        if not prop_found:
            prop_name = f'property{i}'
            prop_found = hasattr(node, prop_name)
        if prop_found:
            # Haxe properties are called property0 - property9 even if
            # their Python equivalent can end with '_get', so yield
            # both names
            yield prop_name, f'property{i}'


def haxe_format_socket_val(socket_val: Any, array_outer_brackets=True) -> str:
    """Formats a socket value to be valid Haxe syntax.

    If `array_outer_brackets` is false, no square brackets are put
    around array values.

    Make sure that elements of sequence types are not yet in Haxe
    syntax, otherwise they are strings and get additional quotes!
    """
    if isinstance(socket_val, bool):
        socket_val = str(socket_val).lower()

    elif isinstance(socket_val, str):
        socket_val = '"{:s}"'.format(socket_val.replace('"', '\\"'))

    elif isinstance(socket_val, (collections.abc.Sequence, bpy.types.bpy_prop_array, mathutils.Color, mathutils.Euler, mathutils.Vector)):
        socket_val = ','.join(haxe_format_socket_val(v, array_outer_brackets=True) for v in socket_val)
        if array_outer_brackets:
            socket_val = f'[{socket_val}]'

    elif socket_val is None:
        # Don't write 'None' into the Haxe code
        socket_val = 'null'

    return str(socket_val)


def haxe_format_val(prop) -> str:
    """Formats a basic value to be valid Haxe syntax."""
    if isinstance(prop, str):
        res = '"' + str(prop) + '"'
    elif isinstance(prop, bool):
        res = str(prop).lower()
    else:
        if prop is None:
            res = 'null'
        else:
            res = str(prop)

    return str(res)


def haxe_format_prop_value(node: bpy.types.Node, prop_name: str) -> str:
    """Formats a property value to be valid Haxe syntax."""
    prop_value = getattr(node, prop_name)
    if isinstance(prop_value, str):
        prop_value = '"' + str(prop_value) + '"'
    elif isinstance(prop_value, bool):
        prop_value = str(prop_value).lower()
    elif hasattr(prop_value, 'name'):  # PointerProperty
        prop_value = '"' + str(prop_value.name) + '"'
    elif isinstance(prop_value, bpy.types.bpy_prop_array):
        prop_value = '[' + ','.join(haxe_format_val(prop) for prop in prop_value) + ']'
    else:
        if prop_value is None:
            prop_value = 'null'
        else:
            prop_value = str(prop_value)

    return prop_value


def nodetype_to_nodeitem(node_type: Type[bpy.types.Node]) -> NodeItem:
    """Create a NodeItem from a given node class."""
    # Internal node types seem to have no bl_idname attribute
    if issubclass(node_type, bpy.types.NodeInternal):
        return NodeItem(node_type.__name__)

    return NodeItem(node_type.bl_idname)


def copy_basic_node_props(from_node: bpy.types.Node, to_node: bpy.types.Node):
    """Copy non-node-specific properties to a different node."""
    to_node.parent = from_node.parent
    to_node.location = from_node.location
    to_node.select = from_node.select

    to_node.arm_logic_id = from_node.arm_logic_id
    to_node.arm_watch = from_node.arm_watch
