from collections import OrderedDict
import itertools
import textwrap
from typing import Any, final, Generator, List, Optional, Type, Union
from typing import OrderedDict as ODict  # Prevent naming conflicts

import bpy.types
from bpy.props import *
from nodeitems_utils import NodeItem
from arm.logicnode.arm_sockets import ArmCustomSocket

import arm  # we cannot import arm.livepatch here or we have a circular import
# Pass custom property types and NodeReplacement forward to individual
# node modules that import arm_nodes
from arm.logicnode.arm_props import *
from arm.logicnode.replacement import NodeReplacement
import arm.node_utils
import arm.utils

if arm.is_reload(__name__):
    arm.logicnode.arm_props = arm.reload_module(arm.logicnode.arm_props)
    from arm.logicnode.arm_props import *
    arm.logicnode.replacement = arm.reload_module(arm.logicnode.replacement)
    from arm.logicnode.replacement import NodeReplacement
    arm.node_utils = arm.reload_module(arm.node_utils)
    arm.utils = arm.reload_module(arm.utils)
    arm.logicnode.arm_sockets = arm.reload_module(arm.logicnode.arm_sockets)
    from arm.logicnode.arm_sockets import ArmCustomSocket
else:
    arm.enable_reload(__name__)

# When passed as a category to add_node(), this will use the capitalized
# name of the package of the node as the category to make renaming
# categories easier.
PKG_AS_CATEGORY = "__pkgcat__"

nodes = []
category_items: ODict[str, List['ArmNodeCategory']] = OrderedDict()

array_nodes: dict[str, 'ArmLogicTreeNode'] = dict()

# See ArmLogicTreeNode.update()
# format: [tree pointer => (num inputs, num input links, num outputs, num output links)]
last_node_state: dict[int, tuple[int, int, int, int]] = {}


class ArmLogicTreeNode(bpy.types.Node):
    arm_category = PKG_AS_CATEGORY
    arm_section = 'default'
    arm_is_obsolete = False

    @final
    def init(self, context):
        # make sure a given node knows the version of the NodeClass from when it was created
        if isinstance(type(self).arm_version, int):
            self.arm_version = type(self).arm_version
        else:
            self.arm_version = 1

        if not hasattr(self, 'arm_init'):
            # Show warning for older node packages
            arm.log.warn(f'Node {self.bl_idname} has no arm_init function and might not work correctly!')
        else:
            self.arm_init(context)

        self.clear_tree_cache()
        arm.live_patch.send_event('ln_create', self)

    def register_id(self):
        """Registers a node ID so that the ID can be used by operators
        to target this node (nodes can't be stored in pointer properties).
        """
        array_nodes[self.get_id_str()] = self

    def get_id_str(self) -> str:
        return str(self.as_pointer())

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ArmLogicTreeType' or 'ArmGroupTree'

    @classmethod
    def on_register(cls):
        """Don't call this method register() as it will be triggered before Blender registers the class, resulting in
        a double registration."""
        add_node(cls, cls.arm_category, cls.arm_section, cls.arm_is_obsolete)

    @classmethod
    def on_unregister(cls):
        pass

    @classmethod
    def absolute_location(cls, node):
        """Gets the absolute location of the node including frames and parent nodes."""
        locx, locy = node.location[:]
        if node.parent:
            locx += node.parent.location.x
            locy += node.parent.location.y
            return cls.absolute_location(node.parent)
        else:
            return locx, locy

    def get_tree(self) -> bpy.types.NodeTree:
        return self.id_data

    def clear_tree_cache(self):
        self.get_tree().arm_cached = False

    def update(self):
        """Called if the node was updated in some way, for example
        if socket connections change. This callback is not called if
        socket values were changed.
        """
        def num_connected(sockets):
            return sum([socket.is_linked for socket in sockets])

        # If a link between sockets is removed, there is currently no
        # _reliable_ way in the Blender API to check which connection
        # was removed (*).
        #
        # So instead we just check _if_ the number of links or sockets
        # has changed (the update function is called before and after
        # each link removal). Because we listen for those updates in
        # general, we automatically also listen to link creation events,
        # which is more stable than using the dedicated callback for
        # that (`insert_link()`), because adding links can remove other
        # links and we would need to react to that as well.
        #
        # (*) https://devtalk.blender.org/t/how-to-detect-which-link-was-deleted-by-user-in-node-editor

        self_id = self.as_pointer()

        current_state = (len(self.inputs), num_connected(self.inputs), len(self.outputs), num_connected(self.outputs))
        if self_id not in last_node_state:
            # Lazily initialize the last_node_state dict to also store
            # state for nodes that already exist in the tree
            last_node_state[self_id] = current_state

        if last_node_state[self_id] != current_state:
            self.on_socket_state_change()
            last_node_state[self_id] = current_state

        # Notify sockets
        for socket in itertools.chain(self.inputs, self.outputs):
            if isinstance(socket, ArmCustomSocket):
                socket.on_node_update()

        self.clear_tree_cache()

    def free(self):
        """Called before the node is deleted."""
        self.clear_tree_cache()
        arm.live_patch.send_event('ln_delete', self)

    def copy(self, src_node):
        """Called upon node duplication or upon pasting a copied node.
        `self` holds the copied node and `src_node` a temporal copy of
        the original node at the time of copying).
        """
        self.clear_tree_cache()
        arm.live_patch.send_event('ln_copy', (self, src_node))

    def on_prop_update(self, context: bpy.types.Context, prop_name: str):
        """Called if a property created with a function from the
        arm_props module is changed. If the property has a custom update
        function, it is called before `on_prop_update()`.
        """
        self.clear_tree_cache()
        arm.live_patch.send_event('ln_update_prop', (self, prop_name))

    def on_socket_val_update(self, context: bpy.types.Context, socket: bpy.types.NodeSocket):
        self.clear_tree_cache()
        arm.live_patch.send_event('ln_socket_val', (self, socket))

    def on_socket_state_change(self):
        """Called if the state (amount, connection state) of the node's
        socket changes (see ArmLogicTreeNode.update())
        """
        arm.live_patch.send_event('ln_update_sockets', self)

    def on_logic_id_change(self):
        """Called if the node's arm_logic_id value changes."""
        self.clear_tree_cache()
        arm.live_patch.patch_export()

    def insert_link(self, link: bpy.types.NodeLink):
        """Called on *both* nodes when a link between two nodes is created."""
        # arm.live_patch.send_event('ln_insert_link', (self, link))
        pass

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        # needs to be overridden by individual node classes with arm_version>1
        """(only called if the node's version is inferior to the node class's version)
        Help with the node replacement process, by explaining how a node (`self`) should be replaced.
        This method can either return a NodeReplacement object (see `nodes_logic.py`), or a brand new node.

        If a new node is returned, then the following needs to be already set:
        - the node's links to the other nodes
        - the node's properties
        - the node inputs's default values

        If more than one node need to be created (for example, if an input needs a type conversion after update),
        please return all the nodes in a list.

        please raise a LookupError specifically when the node's version isn't handled by the function.

        note that the lowest 'defined' version should be 1. if the node's version is 0, it means that it has been saved before versioning was a thing.
        NODES OF VERSION 1 AND VERSION 0 SHOULD HAVE THE SAME CONTENTS
        """
        if self.arm_version == 0 and type(self).arm_version == 1:
            # In case someone doesn't implement this function, but the node has version 0
            return NodeReplacement.Identity(self)
        else:
            raise LookupError(f"the current node class {repr(type(self)):s} does not implement get_replacement_node() even though it has updated")

    def add_input(self, socket_type: str, socket_name: str, default_value: Any = None, is_var: bool = False) -> bpy.types.NodeSocket:
        """Adds a new input socket to the node.

        If `is_var` is true, a dot is placed inside the socket to denote
        that this socket can be used for variable access (see
        SetVariable node).
        """
        socket = self.inputs.new(socket_type, socket_name)

        if default_value is not None:
            if isinstance(socket, ArmCustomSocket):
                if socket.arm_socket_type != 'NONE':
                    socket.default_value_raw = default_value
                else:
                    raise ValueError('specified a default value for an input node that doesn\'t accept one')
            else:  # should not happen anymore?
                socket.default_value = default_value

        if is_var and not socket.display_shape.endswith('_DOT'):
            socket.display_shape += '_DOT'

        return socket

    def add_output(self, socket_type: str, socket_name: str, default_value: Any = None, is_var: bool = False) -> bpy.types.NodeSocket:
        """Adds a new output socket to the node.

        If `is_var` is true, a dot is placed inside the socket to denote
        that this socket can be used for variable access (see
        SetVariable node).
        """
        socket = self.outputs.new(socket_type, socket_name)

        # FIXME: …a default_value on an output socket? Why is that a thing?
        if default_value is not None:
            if socket.arm_socket_type != 'NONE':
                socket.default_value_raw = default_value
            else:
                raise ValueError('specified a default value for an input node that doesn\'t accept one')

        if is_var and not socket.display_shape.endswith('_DOT'):
            socket.display_shape += '_DOT'

        return socket

    def get_socket_index(self, socket:bpy.types.NodeSocket) -> int:
        """Gets the scket index of a socket in this node."""

        index = 0
        if socket.is_output:
            for output in self.outputs:
                if output == socket:
                    return index
                index = index + 1
        else:
            for input in self.inputs:
                if input == socket:
                    return index
                index = index + 1
        return -1

    def insert_input(self, socket_type: str, socket_index: int, socket_name: str, default_value: Any = None, is_var: bool = False) -> bpy.types.NodeSocket:
        """Insert a new input socket to the node at a particular index.

        If `is_var` is true, a dot is placed inside the socket to denote
        that this socket can be used for variable access (see
        SetVariable node).
        """

        socket = self.add_input(socket_type, socket_name, default_value, is_var)
        self.inputs.move(len(self.inputs) - 1, socket_index)
        return socket

    def insert_output(self, socket_type: str, socket_index: int, socket_name: str, default_value: Any = None, is_var: bool = False) -> bpy.types.NodeSocket:
        """Insert a new output socket to the node at a particular index.

        If `is_var` is true, a dot is placed inside the socket to denote
        that this socket can be used for variable access (see
        SetVariable node).
        """

        socket = self.add_output(socket_type, socket_name, default_value, is_var)
        self.outputs.move(len(self.outputs) - 1, socket_index)
        return socket

    def change_input_socket(self, socket_type: str, socket_index: int, socket_name: str, default_value: Any = None, is_var: bool = False) -> bpy.types.NodeSocket:
        """Change an input socket type retaining the previous socket links
        
        If `is_var` is true, a dot is placed inside the socket to denote
        that this socket can be used for variable access (see
        SetVariable node).
        """

        old_socket = self.inputs[socket_index]
        links = old_socket.links
        from_sockets = []
        for link in links:
            from_sockets.append(link.from_socket)
        current_socket = self.insert_input(socket_type, socket_index, socket_name, default_value, is_var)
        if default_value is None:
            old_socket.copy_defaults(current_socket)
        self.inputs.remove(old_socket)
        tree = self.get_tree()
        for from_socket in from_sockets:
            tree.links.new(from_socket, current_socket)
        return current_socket

    def change_output_socket(self, socket_type: str, socket_index: int, socket_name: str, default_value: Any = None, is_var: bool = False) -> bpy.types.NodeSocket:
        """Change an output socket type retaining the previous socket links
        
        If `is_var` is true, a dot is placed inside the socket to denote
        that this socket can be used for variable access (see
        SetVariable node).
        """

        links = self.outputs[socket_index].links
        to_sockets = []
        for link in links:
            to_sockets.append(link.to_socket)
        self.outputs.remove(self.outputs[socket_index])
        current_socket = self.insert_output(socket_type, socket_index, socket_name, default_value, is_var)
        tree = self.get_tree()
        for to_socket in to_sockets:
            tree.links.new(current_socket, to_socket)
        return current_socket

class ArmLogicVariableNodeMixin(ArmLogicTreeNode):
    """A mixin class for variable nodes. This class adds functionality
    that allows variable nodes to
        1) be identified as such and
        2) to be promoted to nodes that are linked to a tree variable.

    If a variable node is promoted to a tree variable node and the
    tree variable does not exist yet, it is created. Each tree variable
    only exists as long as there are variable nodes that are linked to
    it. A variable node's links to a tree variables can be removed by
    calling `make_local()`. If a tree variable node is copied to a
    different tree where the variable doesn't exist, it is created.

    Tree variable nodes come in two states: master and replica nodes.
    In order to not having to find memory-intensive and complicated ways
    for storing every possible variable node data in the tree variable
    UI list entries themselves (Blender doesn't support dynamically
    typed properties), we store the data in one of the variable nodes,
    called the master node. The other nodes are synchronized with the
    master node and must implement a routine to copy the data from the
    master node.

    The user doesn't need to know about the master/replica concept, the
    master node gets chosen automatically and it is made sure that there
    can be only one master node, even after copying.
    """
    is_master_node: BoolProperty(default=False)

    _text_wrapper = textwrap.TextWrapper()

    def synchronize_from_master(self, master_node: 'ArmLogicVariableNodeMixin'):
        """Called if the node should synchronize its data from the passed
        master_node. Override this in variable nodes to react to updates
        made to the master node.
        """
        pass

    def _synchronize_to_replicas(self, master_node: 'ArmLogicVariableNodeMixin'):
        for replica_node in self.get_replica_nodes(self.get_tree(), self.arm_logic_id):
            replica_node.synchronize_from_master(master_node)
        self.clear_tree_cache()

    def make_local(self):
        """Demotes this node to a local variable node that is not linked
        to any tree variable.
        """
        has_replicas = True
        if self.is_master_node:
            self._synchronize_to_replicas(self)
            has_replicas = self.choose_new_master_node(self.get_tree(), self.arm_logic_id)
            self.is_master_node = False

        # Remove the tree variable if there are no more nodes that link
        # to it
        if not has_replicas:
            tree = self.get_tree()
            for idx, item in enumerate(tree.arm_treevariableslist):
                if item.name == self.arm_logic_id:
                    tree.arm_treevariableslist.remove(idx)
                    break

            max_index = len(tree.arm_treevariableslist) - 1
            if tree.arm_treevariableslist_index > max_index:
                tree.arm_treevariableslist_index = max_index

        self.arm_logic_id = ''
        self.clear_tree_cache()

    def free(self):
        self.make_local()
        super().free()

    def copy(self, src_node: 'ArmLogicVariableNodeMixin'):
        # Because the `copy()` callback is actually called upon pasting
        # the node, `src_node` is a temporal copy of the copied node
        # that retains the state of the node upon copying. This however
        # means that we can't reliably use the master state of the
        # pasted node because it might have changed in between, also
        # `src_node.get_tree()` will return `None`. So if the pasted
        # node is linked to a tree var, we simply check if the tree of
        # the pasted node has the tree variable and depending on that we
        # set `is_master_node`.

        if self.arm_logic_id != '':
            target_tree = self.get_tree()
            lst = target_tree.arm_treevariableslist

            self.is_master_node = False  # Ignore this node in get_master_node below
            if self.__class__.get_master_node(target_tree, self.arm_logic_id) is None:
                var_item = lst.add()
                var_item['_name'] = arm.utils.unique_str_for_list(
                    items=lst, name_attr='name', wanted_name=self.arm_logic_id, ignore_item=var_item
                )
                var_item.node_type = self.bl_idname
                var_item.color = arm.utils.get_random_color_rgb()

                target_tree.arm_treevariableslist_index = len(lst) - 1
                arm.make_state.redraw_ui = True

                self.is_master_node = True
            else:
                for item in lst:
                    if item.name == self.arm_logic_id:
                        self.color = item.color
                        break

        super().copy(src_node)

    def on_socket_state_change(self):
        if self.is_master_node:
            self._synchronize_to_replicas(self)
        super().on_socket_state_change()

    def on_logic_id_change(self):
        tree = self.get_tree()
        is_linked = self.arm_logic_id != ''
        for inp in self.inputs:
            if is_linked:
                for link in inp.links:
                    tree.links.remove(link)

            inp.hide = is_linked
            inp.enabled = not is_linked  # Hide in sidebar, see Blender's space_node.py
        super().on_logic_id_change()

    def on_prop_update(self, context: bpy.types.Context, prop_name: str):
        if self.is_master_node:
            self._synchronize_to_replicas(self)
        super().on_prop_update(context, prop_name)

    def on_socket_val_update(self, context: bpy.types.Context, socket: bpy.types.NodeSocket):
        if self.is_master_node:
            self._synchronize_to_replicas(self)
        super().on_socket_val_update(context, socket)

    def draw_content(self, context, layout):
        """Override in variable nodes as replacement for draw_buttons()"""
        pass

    @final
    def draw_buttons(self, context, layout):
        if self.arm_logic_id == '':
            self.draw_content(context, layout)
        else:
            txt_wrapper = self.__class__._text_wrapper
            # Roughly estimate how much text fits in the node's width
            txt_wrapper.width = self.width / 6

            msg = f'Value linked to tree variable "{self.arm_logic_id}"'
            lines = txt_wrapper.wrap(msg)

            for line in lines:
                row = layout.row(align=True)
                row.alignment = 'EXPAND'
                row.label(text=line)
                row.scale_y = 0.4

    def draw_label(self) -> str:
        if self.arm_logic_id == '':
            return self.bl_label
        else:
            return f'TV: {self.arm_logic_id}'

    @classmethod
    def synchronize(cls, tree: bpy.types.NodeTree, logic_id: str):
        """Synchronizes the value of the master node of the given
        `logic_id` to all replica nodes.
        """
        master_node = cls.get_master_node(tree, logic_id)
        master_node._synchronize_to_replicas(master_node)

    @staticmethod
    def choose_new_master_node(tree: bpy.types.NodeTree, logic_id: str) -> bool:
        """Choose a new master node from the remaining replica nodes.

        Return `True` if a new master node was found, otherwise return
        `False`.
        """
        try:
            node = next(ArmLogicVariableNodeMixin.get_replica_nodes(tree, logic_id))
        except StopIteration:
            return False  # No replica node found

        node.is_master_node = True
        return True

    @staticmethod
    def get_master_node(tree: bpy.types.NodeTree, logic_id: str) -> Optional['ArmLogicVariableNodeMixin']:
        for node in tree.nodes:
            if node.arm_logic_id == logic_id and isinstance(node, ArmLogicVariableNodeMixin):
                if node.is_master_node:
                    return node
        return None

    @staticmethod
    def get_replica_nodes(tree: bpy.types.NodeTree, logic_id: str) -> Generator['ArmLogicVariableNodeMixin', None, None]:
        """A generator that iterates over all variable nodes for a given
        ID that are not the master node.
        """
        for node in tree.nodes:
            if node.arm_logic_id == logic_id and isinstance(node, ArmLogicVariableNodeMixin):
                if not node.is_master_node:
                    yield node


class ArmNodeAddInputButton(bpy.types.Operator):
    """Add a new input socket to the node set by node_index."""
    bl_idname = 'arm.node_add_input'
    bl_label = 'Add Input'
    bl_options = {'UNDO', 'INTERNAL'}

    node_index: StringProperty(name='Node Index', default='')
    socket_type: StringProperty(name='Socket Type', default='ArmDynamicSocket')
    name_format: StringProperty(name='Name Format', default='Input {0}')
    index_name_offset: IntProperty(name='Index Name Offset', default=0)

    def execute(self, context):
        global array_nodes
        node = array_nodes[self.node_index]
        inps = node.inputs

        socket_types = self.socket_type.split(';')
        name_formats = self.name_format.split(';')
        assert len(socket_types) == len(name_formats)

        format_index = (len(inps) + self.index_name_offset) // len(socket_types)
        for socket_type, name_format in zip(socket_types, name_formats):
            inp = inps.new(socket_type, name_format.format(str(format_index)))
            # Make sure inputs don't show up if the node links to a tree variable
            inp.hide = node.arm_logic_id != ''
            inp.enabled = node.arm_logic_id == ''

        # Reset to default again for subsequent calls of this operator
        self.node_index = ''
        self.socket_type = 'ArmDynamicSocket'
        self.name_format = 'Input {0}'
        self.index_name_offset = 0

        return{'FINISHED'}

class ArmNodeAddInputValueButton(bpy.types.Operator):
    """Add new input"""
    bl_idname = 'arm.node_add_input_value'
    bl_label = 'Add Input'
    bl_options = {'UNDO', 'INTERNAL'}
    node_index: StringProperty(name='Node Index', default='')
    socket_type: StringProperty(name='Socket Type', default='ArmDynamicSocket')

    def execute(self, context):
        global array_nodes
        inps = array_nodes[self.node_index].inputs
        inps.new(self.socket_type, 'Value')
        return{'FINISHED'}

class ArmNodeRemoveInputButton(bpy.types.Operator):
    """Remove last input"""
    bl_idname = 'arm.node_remove_input'
    bl_label = 'Remove Input'
    bl_options = {'UNDO', 'INTERNAL'}
    node_index: StringProperty(name='Node Index', default='')
    count: IntProperty(name='Number of inputs to remove', default=1, min=1)
    min_inputs: IntProperty(name='Number of inputs to keep', default=0, min=0)

    def execute(self, context):
        global array_nodes
        node = array_nodes[self.node_index]
        inps = node.inputs
        min_inps = self.min_inputs if not hasattr(node, 'min_inputs') else node.min_inputs
        if len(inps) >= min_inps + self.count:
            for _ in range(self.count):
                inps.remove(inps.values()[-1])
        return{'FINISHED'}

class ArmNodeRemoveInputValueButton(bpy.types.Operator):
    """Remove last input"""
    bl_idname = 'arm.node_remove_input_value'
    bl_label = 'Remove Input'
    bl_options = {'UNDO', 'INTERNAL'}
    node_index: StringProperty(name='Node Index', default='')
    target_name: StringProperty(name='Name of socket to remove', default='Value')

    def execute(self, context):
        global array_nodes
        node = array_nodes[self.node_index]
        inps = node.inputs
        min_inps = 0 if not hasattr(node, 'min_inputs') else node.min_inputs
        if len(inps) > min_inps and inps[-1].name == self.target_name:
            inps.remove(inps.values()[-1])
        return{'FINISHED'}

class ArmNodeAddOutputButton(bpy.types.Operator):
    """Add a new output socket to the node set by node_index"""
    bl_idname = 'arm.node_add_output'
    bl_label = 'Add Output'
    bl_options = {'UNDO', 'INTERNAL'}

    node_index: StringProperty(name='Node Index', default='')
    socket_type: StringProperty(name='Socket Type', default='ArmDynamicSocket')
    name_format: StringProperty(name='Name Format', default='Output {0}')
    index_name_offset: IntProperty(name='Index Name Offset', default=0)

    def execute(self, context):
        global array_nodes
        outs = array_nodes[self.node_index].outputs

        socket_types = self.socket_type.split(';')
        name_formats = self.name_format.split(';')
        assert len(socket_types) == len(name_formats)

        format_index = (len(outs) + self.index_name_offset) // len(socket_types)
        for socket_type, name_format in zip(socket_types, name_formats):
            outs.new(socket_type, name_format.format(str(format_index)))

        # Reset to default again for subsequent calls of this operator
        self.node_index = ''
        self.socket_type = 'ArmDynamicSocket'
        self.name_format = 'Output {0}'
        self.index_name_offset = 0

        return{'FINISHED'}

class ArmNodeRemoveOutputButton(bpy.types.Operator):
    """Remove last output"""
    bl_idname = 'arm.node_remove_output'
    bl_label = 'Remove Output'
    bl_options = {'UNDO', 'INTERNAL'}
    node_index: StringProperty(name='Node Index', default='')
    count: IntProperty(name='Number of outputs to remove', default=1, min=1)

    def execute(self, context):
        global array_nodes
        node = array_nodes[self.node_index]
        outs = node.outputs
        min_outs = 0 if not hasattr(node, 'min_outputs') else node.min_outputs
        if len(outs) >= min_outs + self.count:
            for _ in range(self.count):
                outs.remove(outs.values()[-1])
        return{'FINISHED'}

class ArmNodeAddInputOutputButton(bpy.types.Operator):
    """Add new input and output"""
    bl_idname = 'arm.node_add_input_output'
    bl_label = 'Add Input Output'
    bl_options = {'UNDO', 'INTERNAL'}

    node_index: StringProperty(name='Node Index', default='')
    in_socket_type: StringProperty(name='In Socket Type', default='ArmDynamicSocket')
    out_socket_type: StringProperty(name='Out Socket Type', default='ArmDynamicSocket')
    in_name_format: StringProperty(name='In Name Format', default='Input {0}')
    out_name_format: StringProperty(name='Out Name Format', default='Output {0}')
    in_index_name_offset: IntProperty(name='In Name Offset', default=0)
    out_index_name_offset: IntProperty(name='Out Name Offset', default=0)

    def execute(self, context):
        global array_nodes
        node = array_nodes[self.node_index]
        inps = node.inputs
        outs = node.outputs

        in_socket_types = self.in_socket_type.split(';')
        in_name_formats = self.in_name_format.split(';')
        assert len(in_socket_types) == len(in_name_formats)

        out_socket_types = self.out_socket_type.split(';')
        out_name_formats = self.out_name_format.split(';')
        assert len(out_socket_types) == len(out_name_formats)

        in_format_index = (len(outs) + self.in_index_name_offset) // len(in_socket_types)
        out_format_index = (len(outs) + self.out_index_name_offset) // len(out_socket_types)
        for socket_type, name_format in zip(in_socket_types, in_name_formats):
            inps.new(socket_type, name_format.format(str(in_format_index)))
        for socket_type, name_format in zip(out_socket_types, out_name_formats):
            outs.new(socket_type, name_format.format(str(out_format_index)))

        # Reset to default again for subsequent calls of this operator
        self.node_index = ''
        self.in_socket_type = 'ArmDynamicSocket'
        self.out_socket_type = 'ArmDynamicSocket'
        self.in_name_format = 'Input {0}'
        self.out_name_format = 'Output {0}'
        self.in_index_name_offset = 0
        self.out_index_name_offset = 0

        return{'FINISHED'}

class ArmNodeRemoveInputOutputButton(bpy.types.Operator):
    """Remove last input and output"""
    bl_idname = 'arm.node_remove_input_output'
    bl_label = 'Remove Input Output'
    bl_options = {'UNDO', 'INTERNAL'}
    node_index: StringProperty(name='Node Index', default='')
    in_count: IntProperty(name='Number of inputs to remove', default=1, min=1)
    out_count: IntProperty(name='Number of inputs to remove', default=1, min=1)

    def execute(self, context):
        global array_nodes
        node = array_nodes[self.node_index]
        inps = node.inputs
        outs = node.outputs
        min_inps = 0 if not hasattr(node, 'min_inputs') else node.min_inputs
        min_outs = 0 if not hasattr(node, 'min_outputs') else node.min_outputs
        if len(inps) >= min_inps + self.in_count:
            for _ in range(self.in_count):
                inps.remove(inps.values()[-1])
        if len(outs) >= min_outs + self.out_count:
            for _ in range(self.out_count):
                outs.remove(outs.values()[-1])
        return{'FINISHED'}


class ArmNodeCallFuncButton(bpy.types.Operator):
    """Operator that calls a function on a specified
    node (used for dynamic callbacks)."""
    bl_idname = 'arm.node_call_func'
    bl_label = 'Execute'
    bl_options = {'UNDO', 'INTERNAL'}

    node_index: StringProperty(name='Node Index', default='')
    callback_name: StringProperty(name='Callback Name', default='')

    def execute(self, context):
        node = array_nodes[self.node_index]
        if hasattr(node, self.callback_name):
            getattr(node, self.callback_name)()
        else:
            return {'CANCELLED'}

        # Reset to default again for subsequent calls of this operator
        self.node_index = ''
        self.callback_name = ''

        return {'FINISHED'}


class ArmNodeSearch(bpy.types.Operator):
    bl_idname = "arm.node_search"
    bl_label = "Search..."
    bl_options = {"REGISTER", "INTERNAL"}
    bl_property = "item"

    def get_search_items(self, context):
        items = []
        for node in get_all_nodes():
            items.append((node.nodetype, node.label, ""))
        return items

    item: EnumProperty(items=get_search_items)

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ArmLogicTreeType' and context.space_data.edit_tree

    @classmethod
    def description(cls, context, properties):
        if cls.poll(context):
            return "Search for a logic node"
        else:
            return "Search for a logic node. This operator is not available" \
                   " without an active node tree"

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {"CANCELLED"}

    def execute(self, context):
        """Called when a node is added."""
        bpy.ops.node.add_node('INVOKE_DEFAULT', type=self.item, use_transform=True)
        return {"FINISHED"}


class ArmNodeCategory:
    """Represents a category (=directory) of logic nodes."""
    def __init__(self, name: str, icon: str, description: str, category_section: str):
        self.name = name
        self.icon = icon
        self.description = description
        self.category_section = category_section
        self.node_sections: ODict[str, List[NodeItem]] = OrderedDict()
        self.deprecated_nodes: List[NodeItem] = []

    def register_node(self, node_type: Type[bpy.types.Node], node_section: str) -> None:
        """Registers a node to this category so that it will be
        displayed int the `Add node` menu."""
        self.add_node_section(node_section)
        self.node_sections[node_section].append(arm.node_utils.nodetype_to_nodeitem(node_type))

    def register_deprecated_node(self, node_type: Type[bpy.types.Node]) -> None:
        if hasattr(node_type, 'arm_is_obsolete') and node_type.arm_is_obsolete:
            self.deprecated_nodes.append(arm.node_utils.nodetype_to_nodeitem(node_type))

    def get_all_nodes(self) -> Generator[NodeItem, None, None]:
        """Returns all nodes that are registered into this category."""
        yield from itertools.chain(*self.node_sections.values())

    def add_node_section(self, name: str):
        """Adds a node section to this category."""
        if name not in self.node_sections:
            self.node_sections[name] = []

    def sort_nodes(self):
        for node_section in self.node_sections:
            self.node_sections[node_section] = sorted(self.node_sections[node_section], key=lambda item: item.label)


def category_exists(name: str) -> bool:
    for category_section in category_items:
        for c in category_items[category_section]:
            if c.name == name:
                return True

    return False


def get_category(name: str) -> Optional[ArmNodeCategory]:
    for category_section in category_items:
        for c in category_items[category_section]:
            if c.name == name:
                return c

    return None


def get_all_categories() -> Generator[ArmNodeCategory, None, None]:
    for section_categories in category_items.values():
        yield from itertools.chain(section_categories)


def get_all_nodes() -> Generator[NodeItem, None, None]:
    for category in get_all_categories():
        yield from itertools.chain(category.get_all_nodes())


def add_category_section(name: str) -> None:
    """Adds a section of categories to the node menu to group multiple
    categories visually together. The given name only acts as an ID and
    is not displayed in the user inferface."""
    global category_items
    if name not in category_items:
        category_items[name] = []


def add_node_section(name: str, category: str) -> None:
    """Adds a section of nodes to the sub menu of the given category to
    group multiple nodes visually together. The given name only acts as
    an ID and is not displayed in the user inferface."""
    node_category = get_category(category)

    if node_category is not None:
        node_category.add_node_section(name)


def add_category(category: str, section: str = 'default', icon: str = 'BLANK1', description: str = '') -> Optional[ArmNodeCategory]:
    """Adds a category of nodes to the node menu."""
    global category_items

    add_category_section(section)
    if not category_exists(category):
        node_category = ArmNodeCategory(category, icon, description, section)
        category_items[section].append(node_category)
        return node_category

    return None


def add_node(node_type: Type[bpy.types.Node], category: str, section: str = 'default', is_obsolete: bool = False) -> None:
    """
    Registers a node to the given category. If no section is given, the
    node is put into the default section that does always exist.

    Warning: Make sure that this function is not called multiple times per node!
    """
    global nodes

    category = eval_node_category(node_type, category)

    nodes.append(node_type)
    node_category = get_category(category)

    if node_category is None:
        node_category = add_category(category)

    if is_obsolete:
        # We need the obsolete nodes to be registered in order to have them replaced,
        # but do not add them to the menu.
        if node_category is not None:
            # Make the deprecated nodes available for documentation purposes
            node_category.register_deprecated_node(node_type)
        return

    node_category.register_node(node_type, section)
    node_type.bl_icon = node_category.icon


def eval_node_category(node: Union[ArmLogicTreeNode, Type[ArmLogicTreeNode]], category='') -> str:
    """Return the effective category name, that is the category name of
    the given node with resolved `PKG_AS_CATEGORY`.
    """
    if category == '':
        category = node.arm_category

    if category == PKG_AS_CATEGORY:
        return node.__module__.rsplit('.', 2)[-2].capitalize()
    return category


def deprecated(*alternatives: str, message=""):
    """Class decorator to deprecate logic node classes. You can pass multiple string
    arguments with the names of the available alternatives as well as a message
    (keyword-param only) with further information about the deprecation."""

    def wrapper(cls: ArmLogicTreeNode) -> ArmLogicTreeNode:
        cls.bl_label += ' (Deprecated)'
        if hasattr(cls, 'bl_description'):
            cls.bl_description = f'Deprecated. {cls.bl_description}'
        else:
            cls.bl_description = 'Deprecated.'
        cls.bl_icon = 'ERROR'
        cls.arm_is_obsolete = True

        # Deprecated nodes must use a category other than PKG_AS_CATEGORY
        # in order to prevent an empty 'Deprecated' category showing up
        # in the add node menu and in the generated wiki pages. The
        # "old" category is still used to put the node into the correct
        # category in the wiki.
        assert cls.arm_category != PKG_AS_CATEGORY, f'Deprecated node {cls.__name__} is missing an explicit category definition!'

        if cls.__doc__ is None:
            cls.__doc__ = ''

        if len(alternatives) > 0:
            cls.__doc__ += '\n' + f'@deprecated {",".join(alternatives)}: {message}'
        else:
            cls.__doc__ += '\n' + f'@deprecated : {message}'

        return cls

    return wrapper


def is_logic_node_context(context: bpy.context) -> bool:
    """Return whether the given bpy context is inside a logic node editor."""
    return context.space_data.type == 'NODE_EDITOR' and context.space_data.tree_type == 'ArmLogicTreeType'

def is_logic_node_edit_context(context: bpy.context) -> bool:
    """Return whether the given bpy context is inside a logic node editor and tree is being edited."""
    if context.space_data.type == 'NODE_EDITOR' and context.space_data.tree_type == 'ArmLogicTreeType':
        return context.space_data.edit_tree
    return False


def reset_globals():
    global nodes
    global category_items
    nodes = []
    category_items = OrderedDict()


REG_CLASSES = (
    ArmNodeSearch,
    ArmNodeAddInputButton,
    ArmNodeAddInputValueButton,
    ArmNodeRemoveInputButton,
    ArmNodeRemoveInputValueButton,
    ArmNodeAddOutputButton,
    ArmNodeRemoveOutputButton,
    ArmNodeAddInputOutputButton,
    ArmNodeRemoveInputOutputButton,
    ArmNodeCallFuncButton
)
register, unregister = bpy.utils.register_classes_factory(REG_CLASSES)
