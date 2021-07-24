from typing import Callable
import webbrowser

import bpy
from bpy.props import BoolProperty, StringProperty

import arm.logicnode.arm_nodes as arm_nodes
import arm.logicnode.replacement
import arm.logicnode
import arm.props_traits
import arm.ui_icons as ui_icons
import arm.utils

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

    TODO: Find a better solution to custom menus, this will conflict
     with other add-ons overriding this menu.
    """
    bl_idname = "NODE_MT_add"
    bl_label = "Add"
    bl_translation_context = bpy.app.translations.contexts.operator_default

    overridden_menu: bpy.types.Menu = None
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
    bl_options = {'INTERNAL'}

    type: StringProperty(name="NodeItem type")
    use_transform: BoolProperty(name="Use Transform")

    def invoke(self, context, event):
        bpy.ops.node.add_node('INVOKE_DEFAULT', type=self.type, use_transform=self.use_transform)
        return {'FINISHED'}

    @classmethod
    def description(cls, context, properties):
        """Show the node's bl_description attribute as a tooltip or, if
        it doesn't exist, its docstring."""
        nodetype = arm.utils.type_name_to_type(properties.type)

        if hasattr(nodetype, 'bl_description'):
            return nodetype.bl_description.split('.')[0]

        if nodetype.__doc__ is None:
            return ""

        return nodetype.__doc__.split('.')[0]

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ArmLogicTreeType' and context.space_data.edit_tree


def get_category_draw_func(category: arm_nodes.ArmNodeCategory):
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

    arm.logicnode.init_nodes()

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
        if issubclass(n, arm_nodes.ArmLogicTreeNode):
            n.on_unregister()
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
    bl_category = 'Armory'

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ArmLogicTreeType' and context.space_data.edit_tree

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        if context.active_node is not None and context.active_node.bl_idname.startswith('LN'):
            layout.prop(context.active_node, 'arm_logic_id')
            layout.prop(context.active_node, 'arm_watch')

            layout.separator()
            layout.operator('arm.open_node_documentation', icon='HELP')
            column = layout.column(align=True)
            column.operator('arm.open_node_python_source', icon='FILE_SCRIPT')
            column.operator('arm.open_node_haxe_source', icon_value=ui_icons.get_id("haxe"))


class ArmOpenNodeHaxeSource(bpy.types.Operator):
    """Expose Haxe source"""
    bl_idname = 'arm.open_node_haxe_source'
    bl_label = 'Open Node Haxe Source'

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
    """Open the node's documentation in the wiki"""
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


class ARM_PT_Variables(bpy.types.Panel):
    bl_label = 'Armory Node Variables'
    bl_idname = 'ARM_PT_Variables'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Armory'

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ArmLogicTreeType' and context.space_data.edit_tree

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
    """Add a linked node of that Variable"""
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
    """Add a node to set this Variable"""
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


class ReplaceNodesOperator(bpy.types.Operator):
    """Automatically replaces deprecated nodes."""
    bl_idname = "node.replace"
    bl_label = "Replace Nodes"
    bl_description = "Replace deprecated nodes"

    def execute(self, context):
        arm.logicnode.replacement.replace_all()
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return context.space_data is not None and context.space_data.type == 'NODE_EDITOR'


def register():
    arm.logicnode.arm_sockets.register()

    bpy.utils.register_class(ArmLogicTree)
    bpy.utils.register_class(ARM_PT_LogicNodePanel)
    bpy.utils.register_class(ArmOpenNodeHaxeSource)
    bpy.utils.register_class(ArmOpenNodePythonSource)
    bpy.utils.register_class(ArmOpenNodeWikiEntry)
    bpy.utils.register_class(ReplaceNodesOperator)
    bpy.utils.register_class(ARM_PT_Variables)
    bpy.utils.register_class(ARMAddVarNode)
    bpy.utils.register_class(ARMAddSetVarNode)
    ARM_MT_NodeAddOverride.overridden_menu = bpy.types.NODE_MT_add
    ARM_MT_NodeAddOverride.overridden_draw = bpy.types.NODE_MT_add.draw
    bpy.utils.register_class(ARM_MT_NodeAddOverride)
    bpy.utils.register_class(ARM_OT_AddNodeOverride)

    arm.logicnode.init_categories()
    register_nodes()


def unregister():
    unregister_nodes()

    # Ensure that globals are reset if the addon is enabled again in the same Blender session
    arm_nodes.reset_globals()

    bpy.utils.unregister_class(ReplaceNodesOperator)
    bpy.utils.unregister_class(ArmLogicTree)
    bpy.utils.unregister_class(ARM_PT_LogicNodePanel)
    bpy.utils.unregister_class(ArmOpenNodeHaxeSource)
    bpy.utils.unregister_class(ArmOpenNodePythonSource)
    bpy.utils.unregister_class(ArmOpenNodeWikiEntry)
    bpy.utils.unregister_class(ARM_PT_Variables)
    bpy.utils.unregister_class(ARMAddVarNode)
    bpy.utils.unregister_class(ARMAddSetVarNode)
    bpy.utils.unregister_class(ARM_OT_AddNodeOverride)
    bpy.utils.unregister_class(ARM_MT_NodeAddOverride)
    bpy.utils.register_class(ARM_MT_NodeAddOverride.overridden_menu)

    arm.logicnode.arm_sockets.unregister()
