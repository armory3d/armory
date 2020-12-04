"""
This module contains the functionality to replace nodes by other nodes
in order to keep files from older Armory versions compatible with newer versions.

Nodes can define custom update procedures which describe how the replacement
should look like.
"""
import os.path
import time
import traceback
from typing import Dict, List, Optional, Tuple

import bpy.props

import arm.log as log
import arm.logicnode.arm_nodes as arm_nodes
import arm.logicnode.arm_sockets

# List of errors that occurred during the replacement
# Format: (error identifier, node.bl_idname (or None), tree name, exception traceback (optional))
replacement_errors: List[Tuple[str, Optional[str], str, Optional[str]]] = []


class NodeReplacement:
    """
    Represents a simple replacement rule, this can replace nodes of one type to nodes of a second type.
    However, it is fairly limited. For instance, it assumes there are no changes in the type of the inputs or outputs
    Second, it also assumes that node properties (especially EnumProperties) keep the same possible values.

    - from_node, from_node_version: the type of node to be removed, and its version number
    - to_node, to_node_version: the type of node which takes from_node's place, and its version number
    - *_socket_mapping: a map which defines how the sockets of the old node shall be connected to the new node
      {1: 2} means that anything connected to the socket with index 1 on the original node will be connected to the socket with index 2 on the new node
    - property_mapping: the mapping used to transfer the values of the old node's properties to the new node's properties.
      {"property0": "property1"} mean that the value of the new node's property1 should be the old node's property0's value.
    - input_defaults: a mapping used to give default values to the inputs which aren't overridden otherwise.
    - property_defaults: a mapping used to define the value of the new node's properties, when they aren't overridden otherwise.
    """

    def __init__(self, from_node: str, from_node_version: int, to_node: str, to_node_version: int,
                 in_socket_mapping: Dict[int, int], out_socket_mapping: Dict[int, int], property_mapping: Optional[Dict[str, str]] = None,
                 input_defaults: Optional[Dict[int, any]] = None, property_defaults: Optional[Dict[str, any]] = None):
        self.from_node = from_node
        self.to_node = to_node
        self.from_node_version = from_node_version
        self.to_node_version = to_node_version

        self.in_socket_mapping = in_socket_mapping
        self.out_socket_mapping = out_socket_mapping
        self.property_mapping = {} if property_mapping is None else property_mapping

        self.input_defaults = {} if input_defaults is None else input_defaults
        self.property_defaults = {} if property_defaults is None else property_defaults

    @classmethod
    def Identity(cls, node: 'ArmLogicTreeNode'):
        """Returns a NodeReplacement that does nothing, while operating on a given node.
        WARNING: it assumes that all node properties have names that start with "property"
        """
        in_socks = {i: i for i in range(len(node.inputs))}
        out_socks = {i: i for i in range(len(node.outputs))}
        props = {}
        i = 0

        # finding all the properties fo a node is not possible in a clean way for now.
        # so, I'll assume their names start with "property", and list all the node's attributes that fulfill that condition.
        # next, to check that those are indeed properties (in the blender sense), we need to check the class's type annotations.
        # those annotations are not even instances of bpy.types.Property, but tuples, with the first element being a function accessible at bpy.props.XXXProperty
        property_types = []
        for possible_prop_type in dir(bpy.props):
            if possible_prop_type.endswith('Property'):
                property_types.append(getattr(bpy.props, possible_prop_type))
        possible_properties = []
        for attrname in dir(node):
            if attrname.startswith('property'):
                possible_properties.append(attrname)
        for attrname in possible_properties:
            if attrname not in node.__annotations__:
                continue
            if not isinstance(node.__annotations__[attrname], tuple):
                continue
            if node.__annotations__[attrname][0] in property_types:
                props[attrname] = attrname

        return NodeReplacement(
            node.bl_idname, node.arm_version, node.bl_idname, type(node).arm_version,
            in_socket_mapping=in_socks, out_socket_mapping=out_socks,
            property_mapping=props
        )

    def chain_with(self, other):
        """Modify the current NodeReplacement by "adding" a second replacement after it"""
        if self.to_node != other.from_node or self.to_node_version != other.from_node_version:
            raise TypeError('the given NodeReplacement-s could not be chained')
        self.to_node = other.to_node
        self.to_node_version = other.to_node_version

        for i1, i2 in self.in_socket_mapping.items():
            i3 = other.in_socket_mapping[i2]
            self.in_socket_mapping[i1] = i3
        for i1, i2 in self.out_socket_mapping.items():
            i3 = other.out_socket_mapping[i2]
            self.out_socket_mapping[i1] = i3
        for p1, p2 in self.property_mapping.items():
            p3 = other.property_mapping[p2]
            self.property_mapping[p1] = p3

        old_input_defaults = self.input_defaults
        self.input_defaults = other.input_defaults.copy()
        for i, x in old_input_defaults.items():
            self.input_defaults[ other.in_socket_mapping[i] ] = x

        old_property_defaults = self.property_defaults
        self.property_defaults = other.property_defaults.copy()
        for p, x in old_property_defaults.items():
            self.property_defaults[ other.property_mapping[p] ] = x


def replace(tree: bpy.types.NodeTree, node: 'ArmLogicTreeNode'):
    """Replaces the given node with its replacement."""

    # the node can either return a NodeReplacement object (for simple replacements)
    # or a brand new node, for more complex stuff.
    response = node.get_replacement_node(tree)

    if isinstance(response, arm_nodes.ArmLogicTreeNode):
        newnode = response
        # some misc. properties
        newnode.parent = node.parent
        newnode.location = node.location
        newnode.select = node.select

    elif isinstance(response, list):  # a list of nodes:
        for newnode in response:
            newnode.parent = node.parent
            newnode.location = node.location
            newnode.select = node.select

    elif isinstance(response, NodeReplacement):
        replacement = response
        # if the returned object is a NodeReplacement, check that it corresponds to the node (also, create the new node)
        if node.bl_idname != replacement.from_node or node.arm_version != replacement.from_node_version:
            raise LookupError("The provided NodeReplacement doesn't seem to correspond to the node needing replacement")

        # Create the replacement node
        newnode = tree.nodes.new(response.to_node)
        if newnode.arm_version != replacement.to_node_version:
            tree.nodes.remove(newnode)
            raise LookupError("The provided NodeReplacement doesn't seem to correspond to the node needing replacement")

        # some misc. properties
        newnode.parent = node.parent
        newnode.location = node.location
        newnode.select = node.select

        # now, use the `replacement` to hook up the new node correctly
        # start by applying defaults
        for prop_name, prop_value in replacement.property_defaults.items():
            setattr(newnode, prop_name, prop_value)
        for input_id, input_value in replacement.input_defaults.items():
            input_socket = newnode.inputs[input_id]
            if isinstance(input_socket, arm.logicnode.arm_sockets.ArmCustomSocket):
                if input_socket.arm_socket_type != 'NONE':
                    input_socket.default_value_raw = input_value
            elif input_socket.type != 'SHADER':
                # note: shader-type sockets don't have a default value...
                input_socket.default_value = input_value

        # map properties
        for src_prop_name, dest_prop_name in replacement.property_mapping.items():
            setattr(newnode, dest_prop_name, getattr(node, src_prop_name))

        # map inputs
        for src_socket_id, dest_socket_id in replacement.in_socket_mapping.items():
            src_socket = node.inputs[src_socket_id]
            dest_socket = newnode.inputs[dest_socket_id]
            if src_socket.is_linked:
                # an input socket only has one link
                datasource_socket = src_socket.links[0].from_socket
                tree.links.new(datasource_socket, dest_socket)
            else:
                if isinstance(dest_socket, arm.logicnode.arm_sockets.ArmCustomSocket):
                    if dest_socket.arm_socket_type != 'NONE':
                        dest_socket.default_value_raw = src_socket.default_value_raw
                elif dest_socket.type != 'SHADER':
                    # note: shader-type sockets don't have a default value...
                    dest_socket.default_value = src_socket.default_value

        # map outputs
        for src_socket_id, dest_socket_id in replacement.out_socket_mapping.items():
            dest_socket = newnode.outputs[dest_socket_id]
            for link in node.outputs[src_socket_id].links:
                tree.links.new(dest_socket, link.to_socket)
    else:
        print(response)

    tree.nodes.remove(node)


def replace_all():
    """Iterate through all logic node trees in the file and check for node updates/replacements to execute."""
    global replacement_errors

    replacement_errors.clear()

    for tree in bpy.data.node_groups:
        if tree.bl_idname == "ArmLogicTreeType":
            # Use list() to make a "static" copy. It's possible to iterate over it because nodes which get removed
            # from the tree leave python objects in the list
            for node in list(tree.nodes):
                # Blender nodes (layout)
                if not isinstance(node, arm_nodes.ArmLogicTreeNode):
                    continue

                # That node has been removed from the tree without replace() being called on it somehow
                elif node.type == '':
                    continue

                # Node type deleted. That's unusual. Or it has been replaced for a looong time
                elif not node.is_registered_node_type():
                    replacement_errors.append(('unregistered', None, tree.name, None))

                # Invalid version number
                elif not isinstance(type(node).arm_version, int):
                    replacement_errors.append(('bad version', node.bl_idname, tree.name, None))

                # Actual replacement
                elif node.arm_version < type(node).arm_version:
                    try:
                        replace(tree, node)
                    except LookupError as err:
                        replacement_errors.append(('update failed', node.bl_idname, tree.name, traceback.format_exc()))
                    except Exception as err:
                        replacement_errors.append(('misc.', node.bl_idname, tree.name, traceback.format_exc()))

                # Node version is newer than supported by the class
                elif node.arm_version > type(node).arm_version:
                    replacement_errors.append(('future version', node.bl_idname, tree.name, None))

    # If possible, make a popup about the errors and write an error report into the .blend file's folder
    if len(replacement_errors) > 0:
        basedir = os.path.dirname(bpy.data.filepath)
        reportfile = os.path.join(
            basedir, 'node_update_failure.{:s}.txt'.format(
                time.strftime("%Y-%m-%dT%H-%M-%S%z")
            )
        )

        log.error(f'There were errors in the node update procedure, a detailed report has been written to {reportfile}')

        with open(reportfile, 'w') as reportf:
            for error_type, node_class, tree_name, tb in replacement_errors:
                if error_type == 'unregistered':
                    print(f"A node whose class doesn't exist was found in node tree \"{tree_name}\"", file=reportf)
                elif error_type == 'update failed':
                    print(f"A node of type {node_class} in tree \"{tree_name}\" failed to be updated, "
                          f"because there is no (longer?) an update routine for this version of the node.", file=reportf)
                elif error_type == 'future version':
                    print(f"A node of type {node_class} in tree \"{tree_name}\" seemingly comes from a future version of armory. "
                          f"Please check whether your version of armory is up to date", file=reportf)
                elif error_type == 'bad version':
                    print(f"A node of type {node_class} in tree \"{tree_name}\" doesn't have version information attached to it. "
                          f"If so, please check that the nodes in the file are compatible with the in-code node classes. "
                          f"If this nodes comes from an add-on, please check that it is compatible with this version of armory.", file=reportf)
                elif error_type == 'misc.':
                    print(f"A node of type {node_class} in tree \"{tree_name}\" failed to be updated, "
                          f"because the node's update procedure itself failed. Original exception:"
                          "\n" + tb + "\n", file=reportf)
                else:
                    print(f"Whoops, we don't know what this error type (\"{error_type}\") means. You might want to report a bug here. "
                          f"All we know is that it comes form a node of class {node_class} in the node tree called \"{tree_name}\".", file=reportf)

        bpy.ops.arm.show_node_update_errors()
