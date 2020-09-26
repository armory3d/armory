from typing import Callable
import os.path
import time
import webbrowser

import bpy
from bpy.props import BoolProperty, StringProperty
#from bpy.types import NodeTree, Node
import nodeitems_utils

from arm.logicnode import arm_nodes
from arm.logicnode.arm_nodes import ArmNodeCategory
from arm.logicnode import arm_sockets
# Do not remove this line as it runs all node modules for registering!
from arm.logicnode import *
import arm.utils
from pathlib import Path

registered_nodes = []
registered_categories = []


class ArmLogicTree(bpy.types.NodeTree):
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


class ARM_OT_AddNodeOverride(bpy.types.Operator):
    bl_idname = "arm.add_node_override"
    bl_label = "Add Node"
    bl_property = "type"

    type: StringProperty(name="NodeItem type")
    use_transform: BoolProperty(name="Use Transform")

    def invoke(self, context, event):
        bpy.ops.node.add_node('INVOKE_DEFAULT', type=self.type, use_transform=self.use_transform)
        return {"FINISHED"}

    @classmethod
    def description(cls, context, properties):
        """Show the node's bl_description attribute as a tooltip or, if
        it doesn't exist, its docstring."""
        # Type name to type
        nodetype = bpy.types.bpy_struct.bl_rna_get_subclass_py(properties.type)

        if hasattr(nodetype, 'bl_description'):
            return nodetype.bl_description.split('.')[0]

        return nodetype.__doc__.split('.')[0]

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ArmLogicTreeType' and context.space_data.edit_tree


def get_category_draw_func(category: ArmNodeCategory):
    def draw_category_menu(self, context):
        layout = self.layout

        for index, node_section in enumerate(category.node_sections.values()):
            if index != 0:
                layout.separator()

            for node_item in node_section:
                op = layout.operator("arm.add_node_override", text=node_item.label)
                op.type = node_item.nodetype
                op.use_transform = True

    return draw_category_menu


def register_nodes():
    global registered_nodes

    # Re-register all nodes for now..
    if len(registered_nodes) > 0 or len(registered_categories) > 0:
        unregister_nodes()

    for node_type in arm_nodes.nodes:
        # Don't register internal nodes, they are already registered
        if not issubclass(node_type, bpy.types.NodeInternal):
            registered_nodes.append(node_type)
            bpy.utils.register_class(node_type)

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
        if context.selected_nodes is not None:
            if len(context.selected_nodes) == 1:
                if context.selected_nodes[0].bl_idname.startswith('LN'):
                    name = context.selected_nodes[0].bl_idname[2:]
                    version = arm.utils.get_last_commit()
                    if version == '':
                        version = 'master'
                    webbrowser.open(f'https://github.com/armory3d/armory/tree/{version}/Sources/armory/logicnode/{name}.hx')
        return{'FINISHED'}

class ArmOpenNodePythonSource(bpy.types.Operator):
    """Expose Python source"""
    bl_idname = 'arm.open_node_python_source'
    bl_label = 'Open Node Python Source'

    def execute(self, context):
        if context.selected_nodes is not None:
            if len(context.selected_nodes) == 1:
                node = context.selected_nodes[0]
                if node.bl_idname.startswith('LN') and node.arm_version is not None:
                    version = arm.utils.get_last_commit()
                    if version == '':
                        version = 'master'
                    rel_path = node.__module__.replace('.', '/')
                    webbrowser.open(f'https://github.com/armory3d/armory/tree/{version}/blender/{rel_path}.py')
        return{'FINISHED'}

class ArmOpenNodeWikiEntry(bpy.types.Operator):
    """Expose Python source"""
    bl_idname = 'arm.open_node_documentation'
    bl_label = 'Open Node Documentation'

    def to_wiki_id(self, node_name):
        """convert from the conventional node name to its wiki counterpart's anchor or id
            expected node_name format: LN_[a-z_]+
        """
        return node_name.replace('_','-')[3:]

    def execute(self, context):
        if context.selected_nodes is not None:
            if len(context.selected_nodes) == 1:
                node = context.selected_nodes[0]
                if node.bl_idname.startswith('LN') and node.arm_version is not None:
                    wiki_id = self.to_wiki_id(node.__module__.rsplit('.', 2).pop())
                    webbrowser.open(f'https://github.com/armory3d/armory/wiki/reference#{wiki_id}')
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


def replace(tree: bpy.types.NodeTree, node: bpy.types.Node):
    """Replaces the given node with its replacement."""

    # the node can either return a NodeReplacement object (for simple replacements)
    # or a brand new node, for more complex stuff.
    response = node.get_replacement_node(tree)

    if isinstance(response, bpy.types.Node):
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
    elif isinstance(response, arm_nodes.NodeReplacement):
        replacement = response
        # if the returned object is a NodeReplacement, check that it corresponds to the node (also, create the new node)
        if node.bl_idname != replacement.from_node or node.arm_version != replacement.from_node_version:
            raise LookupError("the provided NodeReplacement doesn't seem to correspond to the node needing replacement")
        newnode = tree.nodes.new(response.to_node)
        if newnode.arm_version != replacement.to_node_version:
            raise LookupError("the provided NodeReplacement doesn't seem to correspond to the node needing replacement")

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
            if isinstance(input_socket, arm_sockets.ArmCustomSocket):
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
                if isinstance(dest_socket, arm_sockets.ArmCustomSocket):
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


def replaceAll():
    global replacement_errors
    list_of_errors = set()
    for tree in bpy.data.node_groups:
        if tree.bl_idname == "ArmLogicTreeType":
            for node in list(tree.nodes):
            # add the list() to make a "static" copy
            # (note: one can iterate it, because and nodes which get removed from the tree leave python objects in the list)
                if isinstance(node, (bpy.types.NodeFrame, bpy.types.NodeReroute) ):
                    pass
                elif node.type=='':
                    pass  # that node has been removed from the tree without replace() being called on it somehow.
                elif not node.is_registered_node_type():
                    # node type deleted. That's unusual. Or it has been replaced for a looong time.
                    list_of_errors.add( ('unregistered', None, tree.name) )
                elif not isinstance(type(node).arm_version, int):
                    list_of_errors.add( ('bad version', node.bl_idname, tree.name) )
                elif node.arm_version < type(node).arm_version:
                    try:
                        replace(tree, node)
                    except LookupError as err:
                        list_of_errors.add( ('update failed', node.bl_idname, tree.name) )
                    except Exception as err:
                        list_of_errors.add( ('misc.', node.bl_idname, tree.name) )
                elif node.arm_version > type(node).arm_version:
                    list_of_errors.add(  ('future version', node.bl_idname, tree.name) )

    # if possible, make a popup about the errors.
    # also write an error report.
    if len(list_of_errors) > 0:
        print('there were errors in node replacement')
        basedir = os.path.dirname(bpy.data.filepath)
        reportfile = os.path.join(
            basedir, 'node_update_failure.{:s}.txt'.format(
                time.strftime("%Y-%m-%dT%H-%M-%S%z")
            )
        )
        reportf = open(reportfile, 'w')
        for error_type, node_class, tree_name in list_of_errors:
            if error_type == 'unregistered':
                print(f"A node whose class doesn't exist was found in node tree \"{tree_name}\"", file=reportf)
            elif error_type == 'update failed':
                print(f"A node of type {node_class} in tree \"{tree_name}\" failed to be updated, "
                      f"because update isn't implemented (anymore?) for this version of the node", file=reportf)
            elif error_type == 'future version':
                print(f"A node of type {node_class} in tree \"{tree_name}\" seemingly comes from a future version of armory. "
                      f"Please check whether your version of armory is up to date", file=reportf)
            elif error_type == 'bad version':
                print(f"A node of type {node_class} in tree \"{tree_name}\" Doesn't have version information attached to it. "
                      f"If so, please check that the nodes in the file are compatible with the in-code node classes. "
                      f"If this nodes comes from an add-on, please check that it is compatible with this version of armory.", file=reportf)
            elif error_type == 'misc.':
                print(f"A node of type {node_class} in tree \"{tree_name}\" failed to be updated, "
                      f"because the node's update procedure itself failed.", file=reportf)
            else:
                print(f"Whoops, we don't know what this error type (\"{error_type}\") means. You might want to report a bug here. "
                      f"All we know is that it comes form a node of class {node_class} in the node tree called \"{tree_name}\".", file=reportf)
        reportf.close()

        replacement_errors = list_of_errors
        bpy.ops.arm.show_node_update_errors()
        replacement_errors = None


class ReplaceNodesOperator(bpy.types.Operator):
    """Automatically replaces deprecated nodes."""
    bl_idname = "node.replace"
    bl_label = "Replace Nodes"
    bl_description = "Replace deprecated nodes"

    def execute(self, context):
        replaceAll()
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return context.space_data is not None and context.space_data.type == 'NODE_EDITOR'



# https://blender.stackexchange.com/questions/150101/python-how-to-add-items-in-context-menu-in-2-8
def draw_custom_logicnode_menu(self, context):
    if context.space_data.tree_type == 'ArmLogicTreeType' \
        and context.selected_nodes is not None:
        if len(context.selected_nodes) == 1:
            if context.selected_nodes[0].bl_idname.startswith('LN'):
                layout = self.layout
                layout.separator()
                layout.operator("arm.open_node_documentation", text="Show documentation for this node")
                layout.operator("arm.open_node_source", text="Open .hx source in the browser")
                layout.operator("arm.open_node_python_source", text="Open .py source in the browser")

def register():
    arm_sockets.register()

    bpy.utils.register_class(ArmLogicTree)
    bpy.utils.register_class(ARM_PT_LogicNodePanel)
    bpy.utils.register_class(ArmOpenNodeSource)
    bpy.utils.register_class(ArmOpenNodePythonSource)
    bpy.utils.register_class(ArmOpenNodeWikiEntry)
    bpy.utils.register_class(ReplaceNodesOperator)
    bpy.utils.register_class(ARM_PT_Variables)
    bpy.utils.register_class(ARMAddVarNode)
    bpy.utils.register_class(ARMAddSetVarNode)
    ARM_MT_NodeAddOverride.overridden_draw = bpy.types.NODE_MT_add.draw
    bpy.utils.register_class(ARM_MT_NodeAddOverride)
    bpy.utils.register_class(ARM_OT_AddNodeOverride)

    bpy.types.NODE_MT_context_menu.append(draw_custom_logicnode_menu)

    register_nodes()


def unregister():
    unregister_nodes()

    bpy.utils.unregister_class(ReplaceNodesOperator)
    bpy.utils.unregister_class(ArmLogicTree)
    bpy.utils.unregister_class(ARM_PT_LogicNodePanel)
    bpy.utils.unregister_class(ArmOpenNodeSource)
    bpy.utils.unregister_class(ArmOpenNodePythonSource)
    bpy.utils.unregister_class(ArmOpenNodeWikiEntry)
    bpy.utils.unregister_class(ARM_PT_Variables)
    bpy.utils.unregister_class(ARMAddVarNode)
    bpy.utils.unregister_class(ARMAddSetVarNode)
    bpy.utils.unregister_class(ARM_OT_AddNodeOverride)
    bpy.utils.unregister_class(ARM_MT_NodeAddOverride)

    bpy.types.NODE_MT_context_menu.remove(draw_custom_logicnode_menu)

    arm_sockets.unregister()
