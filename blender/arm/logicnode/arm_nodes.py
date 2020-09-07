from collections import OrderedDict
import itertools
from typing import Generator, List, Optional, Type
from typing import OrderedDict as ODict  # Prevent naming conflicts

import bpy.types
from bpy.props import *
from nodeitems_utils import NodeItem

# When passed as a category to add_node(), this will use the capitalized
# name of the parent package of the node as the category to make
# renaming categories easier.
MODULE_AS_CATEGORY = "__modcat__"

nodes = []
category_items: ODict[str, List['ArmNodeCategory']] = OrderedDict()

array_nodes = dict()


class ArmLogicTreeNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ArmLogicTreeType'


class ArmNodeAddInputButton(bpy.types.Operator):
    """Add new input"""
    bl_idname = 'arm.node_add_input'
    bl_label = 'Add Input'
    node_index: StringProperty(name='Node Index', default='')
    socket_type: StringProperty(name='Socket Type', default='NodeSocketShader')
    name_format: StringProperty(name='Name Format', default='Input {0}')
    index_name_offset: IntProperty(name='Index Name Offset', default=0)

    def execute(self, context):
        global array_nodes
        inps = array_nodes[self.node_index].inputs
        inps.new(self.socket_type, self.name_format.format(str(len(inps) + self.index_name_offset)))
        return{'FINISHED'}

class ArmNodeAddInputValueButton(bpy.types.Operator):
    """Add new input"""
    bl_idname = 'arm.node_add_input_value'
    bl_label = 'Add Input'
    node_index: StringProperty(name='Node Index', default='')
    socket_type: StringProperty(name='Socket Type', default='NodeSocketShader')

    def execute(self, context):
        global array_nodes
        inps = array_nodes[self.node_index].inputs
        inps.new(self.socket_type, 'Value')
        return{'FINISHED'}

class ArmNodeRemoveInputButton(bpy.types.Operator):
    """Remove last input"""
    bl_idname = 'arm.node_remove_input'
    bl_label = 'Remove Input'
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
    """Add new output"""
    bl_idname = 'arm.node_add_output'
    bl_label = 'Add Output'
    node_index: StringProperty(name='Node Index', default='')
    socket_type: StringProperty(name='Socket Type', default='NodeSocketShader')
    name_format: StringProperty(name='Name Format', default='Output {0}')
    index_name_offset: IntProperty(name='Index Name Offset', default=0)

    def execute(self, context):
        global array_nodes
        outs = array_nodes[self.node_index].outputs
        outs.new(self.socket_type, self.name_format.format(str(len(outs) + self.index_name_offset)))
        return{'FINISHED'}

class ArmNodeRemoveOutputButton(bpy.types.Operator):
    """Remove last output"""
    bl_idname = 'arm.node_remove_output'
    bl_label = 'Remove Output'
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
    node_index: StringProperty(name='Node Index', default='')
    in_socket_type: StringProperty(name='In Socket Type', default='NodeSocketShader')
    out_socket_type: StringProperty(name='Out Socket Type', default='NodeSocketShader')
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
        return{'FINISHED'}

class ArmNodeRemoveInputOutputButton(bpy.types.Operator):
    """Remove last input and output"""
    bl_idname = 'arm.node_remove_input_output'
    bl_label = 'Remove Input Output'
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


class ArmNodeSearch(bpy.types.Operator):
    bl_idname = "arm.node_search"
    bl_label = "Search..."
    bl_options = {"REGISTER"}
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

    def register_node(self, node_type: Type[bpy.types.Node], node_section: str) -> None:
        """Registers a node to this category so that it will be
        displayed int the `Add node` menu."""
        self.add_node_section(node_section)

        # Internal node types seem to have no bl_idname attribute
        if issubclass(node_type, bpy.types.NodeInternal):
            item = NodeItem(node_type.__name__)
        else:
            item = NodeItem(node_type.bl_idname)

        self.node_sections[node_section].append(item)

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


def add_node(node_type: Type[bpy.types.Node], category: str, section: str = 'default') -> None:
    """
    Registers a node to the given category. If no section is given, the
    node is put into the default section that does always exist.
    """
    global nodes

    if category == MODULE_AS_CATEGORY:
        category = node_type.__module__.rsplit('.', 2)[1].capitalize()

    nodes.append(node_type)
    node_category = get_category(category)

    if node_category is None:
        node_category = add_category(category)

    node_category.register_node(node_type, section)
    node_type.bl_icon = node_category.icon


bpy.utils.register_class(ArmNodeSearch)
bpy.utils.register_class(ArmNodeAddInputButton)
bpy.utils.register_class(ArmNodeAddInputValueButton)
bpy.utils.register_class(ArmNodeRemoveInputButton)
bpy.utils.register_class(ArmNodeRemoveInputValueButton)
bpy.utils.register_class(ArmNodeAddOutputButton)
bpy.utils.register_class(ArmNodeRemoveOutputButton)
bpy.utils.register_class(ArmNodeAddInputOutputButton)
bpy.utils.register_class(ArmNodeRemoveInputOutputButton)
