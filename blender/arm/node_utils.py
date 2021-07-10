from typing import Any, Generator, Type, Union

import bpy
from bpy.types import NodeSocket, NodeInputs, NodeOutputs
from nodeitems_utils import NodeItem

import arm.log
import arm.logicnode.arm_sockets
import arm.utils


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

def get_node_by_type(node_group, ntype):
    for node in node_group.nodes:
        if node.type == ntype:
            return node

def get_node_armorypbr(node_group):
    for node in node_group.nodes:
        if node.type == 'GROUP' and node.node_tree.name.startswith('Armory PBR'):
            return node

def get_input_node(node_group, to_node, input_index):
    for link in node_group.links:
        if link.to_node == to_node and link.to_socket == to_node.inputs[input_index]:
            if link.from_node.bl_idname == 'NodeReroute': # Step through reroutes
                return find_node_by_link(node_group, link.from_node, link.from_node.inputs[0])
            return link.from_node

def get_output_node(node_group, from_node, output_index):
    for link in node_group.links:
        if link.from_node == from_node and link.from_socket == from_node.outputs[output_index]:
            if link.to_node.bl_idname == 'NodeReroute': # Step through reroutes
                return find_node_by_link_from(node_group, link.to_node, link.to_node.inputs[0])
            return link.to_node


def get_socket_index(sockets: Union[NodeInputs, NodeOutputs], socket: NodeSocket) -> int:
    """Find the socket index in the given node input or output
    collection, return -1 if not found.
    """
    for i in range(0, len(sockets)):
        if sockets[i] == socket:
            return i
    return -1


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


def get_haxe_property_names(node: bpy.types.Node) -> Generator[str, None, None]:
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
            yield prop_name


def haxe_format_socket_val(socket_val: Any) -> str:
    """Formats a socket value to be valid Haxe syntax."""
    if isinstance(socket_val, str):
        socket_val = '"{:s}"'.format(socket_val.replace('"', '\\"'))

    elif socket_val is None:
        # Don't write 'None' into the Haxe code
        socket_val = 'null'

    return socket_val


def haxe_format_prop(node: bpy.types.Node, prop_name: str) -> str:
    """Formats a property value to be valid Haxe syntax."""
    prop_value = getattr(node, prop_name)
    if isinstance(prop_value, str):
        prop_value = '"' + str(prop_value) + '"'
    elif isinstance(prop_value, bool):
        prop_value = str(prop_value).lower()
    elif hasattr(prop_value, 'name'):  # PointerProperty
        prop_value = '"' + str(prop_value.name) + '"'
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
