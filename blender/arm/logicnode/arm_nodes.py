import itertools
from collections import OrderedDict
from typing import Any, Generator, List, Optional, Type
from typing import OrderedDict as ODict  # Prevent naming conflicts

import bpy.types
from bpy.props import *
from nodeitems_utils import NodeItem

import arm  # we cannot import arm.livepatch here or we have a circular import
# Pass custom property types and NodeReplacement forward to individual
# node modules that import arm_nodes
from arm.logicnode.arm_props import *
from arm.logicnode.replacement import NodeReplacement
import arm.node_utils

# When passed as a category to add_node(), this will use the capitalized
# name of the package of the node as the category to make renaming
# categories easier.
PKG_AS_CATEGORY = "__pkgcat__"

nodes = []
category_items: ODict[str, List['ArmNodeCategory']] = OrderedDict()

array_nodes = dict()

# See ArmLogicTreeNode.update()
# format: [tree pointer => (num inputs, num input links, num outputs, num output links)]
last_node_state: dict[int, tuple[int, int, int, int]] = {}


class ArmLogicTreeNode(bpy.types.Node):
    arm_category = PKG_AS_CATEGORY
    arm_section = 'default'
    arm_is_obsolete = False

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

        arm.live_patch.send_event('ln_create', self)

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ArmLogicTreeType'

    @classmethod
    def on_register(cls):
        """Don't call this method register() as it will be triggered before Blender registers the class, resulting in
        a double registration."""
        add_node(cls, cls.arm_category, cls.arm_section, cls.arm_is_obsolete)

    @classmethod
    def on_unregister(cls):
        pass

    def get_tree(self):
        return self.id_data

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
            arm.live_patch.send_event('ln_update_sockets', self)
            last_node_state[self_id] = current_state

    def free(self):
        """Called before the node is deleted."""
        arm.live_patch.send_event('ln_delete', self)

    def copy(self, node):
        """Called if the node was copied. `self` holds the copied node,
        `node` the original one.
        """
        arm.live_patch.send_event('ln_copy', (self, node))

    def on_prop_update(self, context: bpy.types.Context, prop_name: str):
        """Called if a property created with a function from the
        arm_props module is changed. If the property has a custom update
        function, it is called before `on_prop_update()`.
        """
        arm.live_patch.send_event('ln_update_prop', (self, prop_name))

    def on_socket_val_update(self, context: bpy.types.Context, socket: bpy.types.NodeSocket):
        arm.live_patch.send_event('ln_socket_val', (self, socket))

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

        if default_value is not None:
            socket.default_value = default_value

        if is_var and not socket.display_shape.endswith('_DOT'):
            socket.display_shape += '_DOT'

        return socket


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
        inps = array_nodes[self.node_index].inputs
        inps.new(self.socket_type, self.name_format.format(str(len(inps) + self.index_name_offset)))

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

    def execute(self, context):
        global array_nodes
        node = array_nodes[self.node_index]
        inps = node.inputs
        min_inps = 0 if not hasattr(node, 'min_inputs') else node.min_inputs
        if len(inps) > min_inps:
            inps.remove(inps.values()[-1])
        return{'FINISHED'}

class ArmNodeRemoveInputValueButton(bpy.types.Operator):
    """Remove last input"""
    bl_idname = 'arm.node_remove_input_value'
    bl_label = 'Remove Input'
    bl_options = {'UNDO', 'INTERNAL'}
    node_index: StringProperty(name='Node Index', default='')

    def execute(self, context):
        global array_nodes
        node = array_nodes[self.node_index]
        inps = node.inputs
        min_inps = 0 if not hasattr(node, 'min_inputs') else node.min_inputs
        if len(inps) > min_inps and inps[-1].name == 'Value':
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
        outs.new(self.socket_type, self.name_format.format(str(len(outs) + self.index_name_offset)))

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

    def execute(self, context):
        global array_nodes
        node = array_nodes[self.node_index]
        outs = node.outputs
        min_outs = 0 if not hasattr(node, 'min_outputs') else node.min_outputs
        if len(outs) > min_outs:
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
    in_index_name_offset: IntProperty(name='Index Name Offset', default=0)

    def execute(self, context):
        global array_nodes
        node = array_nodes[self.node_index]
        inps = node.inputs
        outs = node.outputs
        inps.new(self.in_socket_type, self.in_name_format.format(str(len(inps) + self.in_index_name_offset)))
        outs.new(self.out_socket_type, self.out_name_format.format(str(len(outs))))

        # Reset to default again for subsequent calls of this operator
        self.node_index = ''
        self.in_socket_type = 'ArmDynamicSocket'
        self.out_socket_type = 'ArmDynamicSocket'
        self.in_name_format = 'Input {0}'
        self.out_name_format = 'Output {0}'
        self.in_index_name_offset = 0

        return{'FINISHED'}

class ArmNodeRemoveInputOutputButton(bpy.types.Operator):
    """Remove last input and output"""
    bl_idname = 'arm.node_remove_input_output'
    bl_label = 'Remove Input Output'
    bl_options = {'UNDO', 'INTERNAL'}
    node_index: StringProperty(name='Node Index', default='')

    def execute(self, context):
        global array_nodes
        node = array_nodes[self.node_index]
        inps = node.inputs
        outs = node.outputs
        min_inps = 0 if not hasattr(node, 'min_inputs') else node.min_inputs
        min_outs = 0 if not hasattr(node, 'min_outputs') else node.min_outputs
        if len(inps) > min_inps:
            inps.remove(inps.values()[-1])
        if len(outs) > min_outs:
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
    def __init__(self, name: str, icon: str, description: str):
        self.name = name
        self.icon = icon
        self.description = description
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
        node_category = ArmNodeCategory(category, icon, description)
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

    if category == PKG_AS_CATEGORY:
        category = node_type.__module__.rsplit('.', 2)[-2].capitalize()

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


def deprecated(*alternatives: str, message=""):
    """Class decorator to deprecate logic node classes. You can pass multiple string
    arguments with the names of the available alternatives as well as a message
    (keyword-param only) with further information about the deprecation."""

    def wrapper(cls: ArmLogicTreeNode) -> ArmLogicTreeNode:
        cls.bl_label += ' (Deprecated)'
        cls.bl_description = f'Deprecated. {cls.bl_description}'
        cls.bl_icon = 'ERROR'
        cls.arm_is_obsolete = True

        if cls.__doc__ is None:
            cls.__doc__ = ''

        if len(alternatives) > 0:
            cls.__doc__ += '\n' + f'@deprecated {",".join(alternatives)}: {message}'
        else:
            cls.__doc__ += '\n' + f'@deprecated : {message}'

        return cls

    return wrapper


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
