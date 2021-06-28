from typing import Type, Union

import bpy
from bpy.types import NodeSocket, NodeInputs, NodeOutputs
from nodeitems_utils import NodeItem

import arm.log
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


def nodetype_to_nodeitem(node_type: Type[bpy.types.Node]) -> NodeItem:
    """Create a NodeItem from a given node class."""
    # Internal node types seem to have no bl_idname attribute
    if issubclass(node_type, bpy.types.NodeInternal):
        return NodeItem(node_type.__name__)

    return NodeItem(node_type.bl_idname)
