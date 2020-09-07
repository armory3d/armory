from typing import Callable
import webbrowser

import bpy
from bpy.types import NodeTree
import nodeitems_utils

from arm.logicnode import *
from arm.logicnode import arm_nodes
from arm.logicnode.arm_nodes import ArmNodeCategory
from arm.logicnode import arm_sockets

registered_nodes = []
registered_categories = []


class ArmLogicTree(NodeTree):
    """Logic nodes"""
    bl_idname = 'ArmLogicTreeType'
    bl_label = 'Logic Node Editor'
    bl_icon = 'DECORATE'


class ARM_MT_NodeAddOverride(bpy.types.Menu):
    """
    Overrides the `Add node` menu. If called from the logic node
    editor, the custom menu is drawn, otherwise the default one is drawn.

    Todo: Find a better solution to custom menus, this will conflict
    with other add-ons overriding this menu.
    """
    bl_idname = "NODE_MT_add"
    bl_label = "Add"
    bl_translation_context = bpy.app.translations.contexts.operator_default

    overridden_draw: Callable = None

    def draw(self, context):
        if context.space_data.tree_type == 'ArmLogicTreeType':
            layout = self.layout

            # Invoke the search
            layout.operator_context = "INVOKE_DEFAULT"
            layout.operator('arm.node_search', icon="VIEWZOOM")

            for category_section in arm_nodes.category_items.values():
                layout.separator()

                for category in category_section:
                    layout.menu(f'ARM_MT_{category.name.lower()}_menu', text=category.name, icon=category.icon)

        else:
            ARM_MT_NodeAddOverride.overridden_draw(self, context)


def get_category_draw_func(category: ArmNodeCategory):
    def draw_category_menu(self, context):
        layout = self.layout

        for index, node_section in enumerate(category.node_sections.values()):
            if index != 0:
                layout.separator()

            for node_item in node_section:
                op = layout.operator("node.add_node", text=node_item.label)
                op.type = node_item.nodetype
                op.use_transform = True

    return draw_category_menu


def register_nodes():
    global registered_nodes

    # Re-register all nodes for now..
    if len(registered_nodes) > 0:
        unregister_nodes()

    for n in arm_nodes.nodes:
        registered_nodes.append(n)
        bpy.utils.register_class(n)

    # Also add Blender's layout nodes
    arm_nodes.add_node(bpy.types.NodeReroute, 'Layout')
    arm_nodes.add_node(bpy.types.NodeFrame, 'Layout')

    # Generate and register category menus
    for category_section in arm_nodes.category_items.values():
        for category in category_section:
            category.sort_nodes()
            menu_class = type(f'ARM_MT_{category.name}Menu', (bpy.types.Menu, ), {
                'bl_space_type': 'NODE_EDITOR',
                'bl_idname': f'ARM_MT_{category.name.lower()}_menu',
                'bl_label': category.name,
                'bl_description': category.description,
                'draw': get_category_draw_func(category)
            })
            registered_categories.append(menu_class)

            bpy.utils.register_class(menu_class)


def unregister_nodes():
    global registered_nodes, registered_categories

    for n in registered_nodes:
        bpy.utils.unregister_class(n)
    for c in registered_categories:
        bpy.utils.unregister_class(c)

    registered_nodes = []
    registered_categories = []


class ARM_PT_LogicNodePanel(bpy.types.Panel):
    bl_label = 'Armory Logic Node'
    bl_idname = 'ARM_PT_LogicNodePanel'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Node'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        if context.active_node != None and context.active_node.bl_idname.startswith('LN'):
            layout.prop(context.active_node, 'arm_logic_id')
            layout.prop(context.active_node, 'arm_watch')
            layout.operator('arm.open_node_source')

class ArmOpenNodeSource(bpy.types.Operator):
    """Expose Haxe source"""
    bl_idname = 'arm.open_node_source'
    bl_label = 'Open Node Source'

    def execute(self, context):
        if context.active_node is not None and context.active_node.bl_idname.startswith('LN'):
            name = context.active_node.bl_idname[2:]
            webbrowser.open('https://github.com/armory3d/armory/tree/master/Sources/armory/logicnode/' + name + '.hx')
        return{'FINISHED'}

#Node Variables Panel
class ARM_PT_Variables(bpy.types.Panel):
    bl_label = 'Armory Node Variables'
    bl_idname = 'ARM_PT_Variables'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Node'

    def draw(self, context):
        layout = self.layout

        nodes = list(filter(lambda node: node.arm_logic_id != "", list(context.space_data.node_tree.nodes)))

        IDs = []
        for n in nodes:
             if not n.arm_logic_id in IDs:
                IDs.append(n.arm_logic_id)

        for ID in IDs:
            row = layout.row(align=True)
            row.alignment = 'EXPAND'
            row.label(text = ID)
            getN = row.operator(operator = 'arm.add_var_node')
            getN.ntype = ID
            setN = row.operator('arm.add_setvar_node')
            setN.ntype = ID

class ARMAddVarNode(bpy.types.Operator):
    '''Add a linked node of that Variable'''
    bl_idname = 'arm.add_var_node'
    bl_label = 'Add Get'
    bl_options = {'GRAB_CURSOR', 'BLOCKING'}

    ntype: bpy.props.StringProperty()
    nodeRef = None

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        self.execute(context)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            self.nodeRef.location = context.space_data.cursor_location
        elif event.type == 'LEFTMOUSE':  # Confirm
            return {'FINISHED'}
        return {'RUNNING_MODAL'}

    def execute(self, context):
        nodes = context.space_data.node_tree.nodes
        node = nodes.new("LNDynamicNode")
        print(context.space_data.backdrop_offset[0])
        node.location = context.space_data.cursor_location
        node.arm_logic_id = self.ntype
        node.label = "GET " + self.ntype
        node.use_custom_color = True
        node.color = (0.22, 0.89, 0.5)
        #node.width = 5
        global nodeRef
        self.nodeRef = node
        return({'FINISHED'})

class ARMAddSetVarNode(bpy.types.Operator):
    '''Add a node to set this Variable'''
    bl_idname = 'arm.add_setvar_node'
    bl_label = 'Add Set'
    bl_options = {'GRAB_CURSOR', 'BLOCKING'}

    ntype: bpy.props.StringProperty()
    nodeRef = None
    setNodeRef = None

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        self.execute(context)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            self.setNodeRef.location = context.space_data.cursor_location
            self.nodeRef.location[0] = context.space_data.cursor_location[0]+10
            self.nodeRef.location[1] = context.space_data.cursor_location[1]-10
        elif event.type == 'LEFTMOUSE':  # Confirm
            return {'FINISHED'}
        return {'RUNNING_MODAL'}

    def execute(self, context):
        nodes = context.space_data.node_tree.nodes
        node = nodes.new("LNDynamicNode")
        print(context.space_data.backdrop_offset[0])
        node.location = context.space_data.cursor_location
        node.arm_logic_id = self.ntype
        node.label = "GET " + self.ntype
        node.use_custom_color = True
        node.color = (0.32, 0.65, 0.89)
        node.bl_width_min = 3
        node.width = 5
        node.bl_width_min = 100
        setNode = nodes.new("LNSetVariableNode")
        setNode.label = "SET " + self.ntype
        setNode.location = context.space_data.cursor_location
        setNode.use_custom_color = True
        setNode.color = (0.49, 0.2, 1.0)
        links = context.space_data.node_tree.links
        links.new(node.outputs[0], setNode.inputs[1])
        global nodeRef
        self.nodeRef = node
        global setNodeRef
        self.setNodeRef = setNode
        return({'FINISHED'})

# node replacement code
replacements = {}

def add_replacement(item):
    replacements[item.from_node] = item

def get_replaced_nodes():
    return replacements.keys()

def get_replacement_for_node(node):
    return replacements[node.bl_idname]

class Replacement:
    # represents a single replacement rule, this can replace exactly one node with another
    #
    # from_node: the node type to be removed
    # to_node: the node type which takes from_node's place
    # *SocketMapping: a map which defines how the sockets of the old node shall be connected to the new node
    # {1: 2} means that anything connected to the socket with index 1 on the original node will be connected to the socket with index 2 on the new node
    def __init__(self, from_node, to_node, in_socket_mapping, out_socket_mapping, property_mapping):
        self.from_node = from_node
        self.to_node = to_node
        self.in_socket_mapping = in_socket_mapping
        self.out_socket_mapping = out_socket_mapping
        self.property_mapping = property_mapping

# actual replacement code
def replace(tree, node):
    replacement = get_replacement_for_node(node)
    newnode = tree.nodes.new(replacement.to_node)
    newnode.location = node.location
    newnode.parent = node.parent

    parent = node.parent
    while parent is not None:
        newnode.location[0] += parent.location[0]
        newnode.location[1] += parent.location[1]
        parent = parent.parent
    
    
    # map properties
    for prop in replacement.property_mapping.keys():
        setattr(newnode, replacement.property_mapping.get(prop), getattr(node, prop))

    # map unconnected inputs
    for in_socket in replacement.in_socket_mapping.keys():
        if not node.inputs[in_socket].is_linked:
            newnode.inputs[replacement.in_socket_mapping.get(in_socket)].default_value = node.inputs[in_socket].default_value

    # map connected inputs
    for link in tree.links:
        if link.from_node == node:
            # this is an output link
            for i in range(0, len(node.outputs)):
                # check the outputs
                # i represents the socket index
                # do we want to remap it & is it the one referenced in the current link
                if i in replacement.out_socket_mapping.keys() and node.outputs[i] == link.from_socket:
                    tree.links.new(newnode.outputs[replacement.out_socket_mapping.get(i)], link.to_socket)
        
        if link.to_node == node:
            # this is an input link
            for i in range(0, len(node.inputs)):
                # check the inputs
                # i represents the socket index
                # do we want to remap it & is it the one referenced socket in the current link
                if i in replacement.in_socket_mapping.keys() and node.inputs[i] == link.to_socket:
                    tree.links.new(newnode.inputs[replacement.in_socket_mapping.get(i)], link.from_socket)
    tree.nodes.remove(node)

def replaceAll():
    for tree in bpy.data.node_groups:
        if tree.bl_idname == "ArmLogicTreeType":
            for node in tree.nodes:
                if node.bl_idname in get_replaced_nodes():
                    print("Replacing "+ node.bl_idname+ " in Tree "+tree.name)
                    replace(tree, node)
        
    
class ReplaceNodesOperator(bpy.types.Operator):
    '''Automatically replaces deprecated nodes.'''
    bl_idname = "node.replace"
    bl_label = "Replace Nodes"

    def execute(self, context):
        replaceAll()
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return context.space_data != None and context.space_data.type == 'NODE_EDITOR'

# TODO: deprecated
# Input Replacement Rules
# add_replacement(Replacement("LNOnGamepadNode", "LNMergedGamepadNode", {0: 0}, {0: 0}, {"property0": "property0", "property1": "property1"}))

def register():
    arm_sockets.register()

    bpy.utils.register_class(ArmLogicTree)
    bpy.utils.register_class(ARM_PT_LogicNodePanel)
    bpy.utils.register_class(ArmOpenNodeSource)
    bpy.utils.register_class(ReplaceNodesOperator)
    bpy.utils.register_class(ARM_PT_Variables)
    bpy.utils.register_class(ARMAddVarNode)
    bpy.utils.register_class(ARMAddSetVarNode)
    ARM_MT_NodeAddOverride.overridden_draw = bpy.types.NODE_MT_add.draw
    bpy.utils.register_class(ARM_MT_NodeAddOverride)

    register_nodes()


def unregister():
    unregister_nodes()

    bpy.utils.unregister_class(ReplaceNodesOperator)
    bpy.utils.unregister_class(ArmLogicTree)
    bpy.utils.unregister_class(ARM_PT_LogicNodePanel)
    bpy.utils.unregister_class(ArmOpenNodeSource)
    bpy.utils.unregister_class(ARM_PT_Variables)
    bpy.utils.unregister_class(ARMAddVarNode)
    bpy.utils.unregister_class(ARMAddSetVarNode)
    bpy.utils.unregister_class(ARM_MT_NodeAddOverride)

    arm_sockets.unregister()
