import bpy
from bpy.types import NodeTree
from bpy.props import *
import nodeitems_utils
from nodeitems_utils import NodeCategory
from arm.logicnode import *
import webbrowser

registered_nodes = []

class ArmLogicTree(NodeTree):
    '''Logic nodes'''
    bl_idname = 'ArmLogicTreeType'
    bl_label = 'Logic Node Editor'
    bl_icon = 'DECORATE'

class LogicNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ArmLogicTreeType'

def register_nodes():
    global registered_nodes

    # Re-register all nodes for now..
    if len(registered_nodes) > 0:
        unregister_nodes()

    for n in arm_nodes.nodes:
        registered_nodes.append(n)
        bpy.utils.register_class(n)

    node_categories = []

    for category in sorted(arm_nodes.category_items):
        sorted_items=sorted(arm_nodes.category_items[category], key=lambda item: item.nodetype)
        node_categories.append(
            LogicNodeCategory('Logic' + category + 'Nodes', category, items=sorted_items)
        )

    nodeitems_utils.register_node_categories('ArmLogicNodes', node_categories)

def unregister_nodes():
    global registered_nodes
    for n in registered_nodes:
        bpy.utils.unregister_class(n)
    registered_nodes = []
    nodeitems_utils.unregister_node_categories('ArmLogicNodes')

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
    '''Expose Haxe source'''
    bl_idname = 'arm.open_node_source'
    bl_label = 'Open Node Source'
 
    def execute(self, context):
        if context.active_node != None and context.active_node.bl_idname.startswith('LN'):
            name = context.active_node.bl_idname[2:]
            webbrowser.open('https://github.com/armory3d/armory/tree/master/Sources/armory/logicnode/' + name + '.hx')
        return{'FINISHED'}

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
add_replacement(Replacement("LNOnGamepadNode", "LNMergedGamepadNode", {0: 0}, {0: 0}, {"property0": "property0", "property1": "property1"}))
add_replacement(Replacement("LNGamepadNode", "LNMergedGamepadNode", {0: 0}, {0: 1}, {"property0": "property0", "property1": "property1"}))

add_replacement(Replacement("LNOnMouseNode", "LNMergedMouseNode", {}, {0: 0}, {"property0": "property0", "property1": "property1"}))
add_replacement(Replacement("LNMouseNode", "LNMergedMouseNode", {}, {0: 1}, {"property0": "property0", "property1": "property1"}))

add_replacement(Replacement("LNOnSurfaceNode", "LNMergedSurfaceNode", {}, {0: 0}, {"property0": "property0"}))
add_replacement(Replacement("LNSurfaceNode", "LNMergedSurfaceNode", {}, {0: 1}, {"property0": "property0"}))

add_replacement(Replacement("LNOnKeyboardNode", "LNMergedKeyboardNode", {}, {0: 0}, {"property0": "property0", "property1": "property1"}))
add_replacement(Replacement("LNKeyboardNode", "LNMergedKeyboardNode", {}, {0: 1}, {"property0": "property0", "property1": "property1"}))

add_replacement(Replacement("LNOnVirtualButtonNode", "LNMergedVirtualButtonNode", {}, {0: 0}, {"property0": "property0", "property1": "property1"}))
add_replacement(Replacement("LNVirtualButtonNode", "LNMergedVirtualButtonNode", {}, {0: 1}, {"property0": "property0", "property1": "property1"}))

def register():
    bpy.utils.register_class(ArmLogicTree)
    bpy.utils.register_class(ARM_PT_LogicNodePanel)
    bpy.utils.register_class(ArmOpenNodeSource)
    bpy.utils.register_class(ReplaceNodesOperator)
    register_nodes()

def unregister():
    bpy.utils.unregister_class(ReplaceNodesOperator)
    unregister_nodes()
    bpy.utils.unregister_class(ArmLogicTree)
    bpy.utils.unregister_class(ARM_PT_LogicNodePanel)
    bpy.utils.unregister_class(ArmOpenNodeSource)
