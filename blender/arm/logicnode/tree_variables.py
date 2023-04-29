import bpy
from bpy.props import *

import arm.log
import arm.make_state
import arm.node_utils
import arm.props_traits_props
import arm.utils
import arm.logicnode.arm_nodes

if arm.is_reload(__name__):
    arm.log = arm.reload_module(arm.log)
    arm.make_state = arm.reload_module(arm.make_state)
    arm.node_utils = arm.reload_module(arm.node_utils)
    arm.props_traits_props = arm.reload_module(arm.props_traits_props)
    arm.utils = arm.reload_module(arm.utils)
    arm.logicnode.arm_nodes = arm.reload_module(arm.logicnode.arm_nodes)
else:
    arm.enable_reload(__name__)


class ARM_PT_Variables(bpy.types.Panel):
    bl_label = 'Tree Variables'
    bl_idname = 'ARM_PT_Variables'
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Armory'

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ArmLogicTreeType' and context.space_data.edit_tree

    def draw(self, context):
        layout = self.layout

        tree: bpy.types.NodeTree = context.space_data.path[-1].node_tree
        node = context.active_node
        if node is None or node.arm_logic_id == '':
            layout.operator('arm.variable_promote_node', icon='PLUS')
        else:
            layout.operator('arm.variable_node_make_local', icon='TRIA_DOWN_BAR')

        row = layout.row(align=True)
        col = row.column(align=True)

        num_prop_rows = max(len(tree.arm_treevariableslist), 6)
        col.template_list('ARM_UL_TreeVarList', '', tree, 'arm_treevariableslist', tree, 'arm_treevariableslist_index', rows=num_prop_rows)

        col.operator('arm.variable_assign_to_node', icon='NODE')

        if len(tree.arm_treevariableslist) > 0:
            selected_item = tree.arm_treevariableslist[tree.arm_treevariableslist_index]

            col.separator()
            sub_row = col.row(align=True)
            sub_row.alignment = 'EXPAND'
            op = sub_row.operator('arm.add_var_node')
            op.node_id = selected_item.name
            op.node_type = selected_item.node_type
            op = sub_row.operator('arm.add_setvar_node')
            op.node_id = selected_item.name
            op.node_type = selected_item.node_type

        col = row.column(align=True)
        col.enabled = len(tree.arm_treevariableslist) > 1
        col.operator('arm_treevariableslist.move_item', icon='TRIA_UP', text='').direction = 'UP'
        col.operator('arm_treevariableslist.move_item', icon='TRIA_DOWN', text='').direction = 'DOWN'

        if len(tree.arm_treevariableslist) > 0:
            selected_item = tree.arm_treevariableslist[tree.arm_treevariableslist_index]

            box = layout.box()
            box.label(text='Selected Variable:')
            master_node = arm.logicnode.arm_nodes.ArmLogicVariableNodeMixin.get_master_node(tree, selected_item.name)
            master_node.draw_content(context, box)
            for inp in master_node.inputs:
                if hasattr(inp, 'draw'):
                    inp.draw(context, box, master_node, inp.label if inp.label is not None else inp.name)


class ARM_OT_TreeVariablePromoteNode(bpy.types.Operator):
    bl_idname = 'arm.variable_promote_node'
    bl_label = 'New Var From Node'
    bl_description = 'Create a tree variable from the active node and promote it to a tree variable node'

    var_name: StringProperty(
        name='Name',
        description='Name of the new tree variable',
        default='Untitled'
    )

    @classmethod
    def poll(cls, context):
        if not arm.logicnode.arm_nodes.is_logic_node_edit_context(context):
            return False
        tree: bpy.types.NodeTree = context.space_data.path[-1].node_tree
        if tree is None:
            return False

        node = context.active_node
        if node is None or not node.bl_idname.startswith('LN'):
            return False

        if not isinstance(node, arm.logicnode.arm_nodes.ArmLogicVariableNodeMixin):
            return False

        return node.arm_logic_id == ''

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def execute(self, context):
        node: arm.logicnode.arm_nodes.ArmLogicVariableNodeMixin = context.active_node
        tree: bpy.types.NodeTree = context.space_data.path[-1].node_tree

        var_type = node.bl_idname
        var_item = ARM_PG_TreeVarListItem.create_new(tree, self.var_name, var_type)

        node.is_master_node = True
        node.arm_logic_id = var_item.name
        node.use_custom_color = True
        node.color = var_item.color

        arm.make_state.redraw_ui = True

        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.scale_y = 1.3
        row.activate_init = True
        row.prop(self, 'var_name')


class ARM_OT_TreeVariableMakeLocalNode(bpy.types.Operator):
    bl_idname = 'arm.variable_node_make_local'
    bl_label = 'Make Node Local'
    bl_description = (
        'Remove the reference to the tree variable from the active node. '
        'If the active node is the only node that links to the selected '
        'tree variable, the tree variable is removed'
    )

    @classmethod
    def poll(cls, context):
        if not arm.logicnode.arm_nodes.is_logic_node_edit_context(context):
            return False
        tree: bpy.types.NodeTree = context.space_data.path[-1].node_tree
        if tree is None:
            return False

        node = context.active_node
        if node is None or not node.bl_idname.startswith('LN'):
            return False

        if not isinstance(node, arm.logicnode.arm_nodes.ArmLogicVariableNodeMixin):
            return False

        return node.arm_logic_id != ''

    def execute(self, context):
        node: arm.logicnode.arm_nodes.ArmLogicVariableNodeMixin = context.active_node
        node.make_local()
        node.color = [0.608, 0.608, 0.608]  # default color
        node.use_custom_color = False

        return {'FINISHED'}


class ARM_OT_TreeVariableVariableAssignToNode(bpy.types.Operator):
    bl_idname = 'arm.variable_assign_to_node'
    bl_label = 'Assign To Node'
    bl_description = (
            'Assign the selected tree variable to the active variable node. '
            'The variable node must have the same type as the variable'
    )

    @classmethod
    def poll(cls, context):
        if not arm.logicnode.arm_nodes.is_logic_node_edit_context(context):
            return False
        tree: bpy.types.NodeTree = context.space_data.path[-1].node_tree
        if tree is None or len(tree.arm_treevariableslist) == 0:
            return False

        node = context.active_node
        if node is None or not node.bl_idname.startswith('LN'):
            return False

        if not isinstance(node, arm.logicnode.arm_nodes.ArmLogicVariableNodeMixin):
            return False

        # Only assign variables to nodes of the correct type
        if node.bl_idname != tree.arm_treevariableslist[tree.arm_treevariableslist_index].node_type:
            return False

        return True

    def execute(self, context):
        node: arm.logicnode.arm_nodes.ArmLogicVariableNodeMixin = context.active_node
        tree: bpy.types.NodeTree = context.space_data.path[-1].node_tree

        var_item = tree.arm_treevariableslist[tree.arm_treevariableslist_index]

        # Make node local first to ensure the old tree variable (if
        # linked) is notified that the node is no longer linked
        if node.arm_logic_id != var_item.name:
            node.make_local()

        node.arm_logic_id = var_item.name
        node.use_custom_color = True
        node.color = var_item.color
        arm.logicnode.arm_nodes.ArmLogicVariableNodeMixin.synchronize(tree, node.arm_logic_id)

        return {'FINISHED'}


class ARM_OT_TreeVariableListMoveItem(bpy.types.Operator):
    bl_idname = 'arm_treevariableslist.move_item'
    bl_label = 'Move'
    bl_description = 'Move an item in the list'
    bl_options = {'UNDO', 'INTERNAL'}

    direction: EnumProperty(
        items=(
            ('UP', 'Up', ''),
            ('DOWN', 'Down', '')
        )
    )

    def execute(self, context):
        tree: bpy.types.NodeTree = context.space_data.path[-1].node_tree
        index = tree.arm_treevariableslist_index

        max_index = len(tree.arm_treevariableslist) - 1
        new_index = 0

        if self.direction == 'UP':
            new_index = index - 1
        elif self.direction == 'DOWN':
            new_index = index + 1
        new_index = max(0, min(new_index, max_index))

        tree.arm_treevariableslist.move(index, new_index)
        tree.arm_treevariableslist_index = new_index

        return{'FINISHED'}


class ARM_OT_AddVarGetterNode(bpy.types.Operator):
    """Add a node to get the value of the selected tree variable"""
    bl_idname = 'arm.add_var_node'
    bl_label = 'Add Getter'
    bl_options = {'GRAB_CURSOR', 'BLOCKING'}

    node_id: StringProperty()
    node_type: StringProperty()
    getter_node_ref = None

    @classmethod
    def poll(cls, context):
        if not arm.logicnode.arm_nodes.is_logic_node_edit_context(context):
            return False
        tree: bpy.types.NodeTree = context.space_data.path[-1].node_tree
        return tree is not None and len(tree.arm_treevariableslist) > 0

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        self.execute(context)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            self.getter_node_ref.location = context.space_data.cursor_location
        elif event.type == 'LEFTMOUSE':  # Confirm
            return {'FINISHED'}
        return {'RUNNING_MODAL'}

    def execute(self, context):
        self.getter_node_ref = self.create_getter_node(context, self.node_type, self.node_id)
        return {'FINISHED'}

    @staticmethod
    def create_getter_node(context, node_type: str, node_id: str) -> arm.logicnode.arm_nodes.ArmLogicTreeNode:
        tree: bpy.types.NodeTree = context.space_data.path[-1].node_tree
        nodes = context.space_data.path[-1].node_tree.nodes

        node = nodes.new(node_type)
        node.location = context.space_data.cursor_location
        node.arm_logic_id = node_id
        node.use_custom_color = True
        node.color = tree.arm_treevariableslist[tree.arm_treevariableslist_index].color

        arm.logicnode.arm_nodes.ArmLogicVariableNodeMixin.synchronize(tree, node.arm_logic_id)

        return node


class ARM_OT_AddVarSetterNode(bpy.types.Operator):
    """Add a node to set the value of the selected tree variable"""
    bl_idname = 'arm.add_setvar_node'
    bl_label = 'Add Setter'
    bl_options = {'GRAB_CURSOR', 'BLOCKING'}

    node_id: StringProperty()
    node_type: StringProperty()
    getter_node_ref = None
    setter_node_ref = None

    @classmethod
    def poll(cls, context):
        if not arm.logicnode.arm_nodes.is_logic_node_edit_context(context):
            return False
        tree: bpy.types.NodeTree = context.space_data.path[-1].node_tree
        return tree is not None and len(tree.arm_treevariableslist) > 0

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        self.execute(context)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            self.setter_node_ref.location = context.space_data.cursor_location
            self.getter_node_ref.location[0] = context.space_data.cursor_location[0]
            self.getter_node_ref.location[1] = context.space_data.cursor_location[1] - self.setter_node_ref.height - 17
        elif event.type == 'LEFTMOUSE':  # Confirm
            return {'FINISHED'}
        return {'RUNNING_MODAL'}

    def execute(self, context):
        nodes = context.space_data.path[-1].node_tree.nodes

        node = ARM_OT_AddVarGetterNode.create_getter_node(context, self.node_type, self.node_id)

        setter_node = nodes.new('LNSetVariableNode')
        setter_node.location = context.space_data.cursor_location

        links = context.space_data.path[-1].node_tree.links
        links.new(node.outputs[0], setter_node.inputs[1])

        self.getter_node_ref = node
        self.setter_node_ref = setter_node
        return {'FINISHED'}


class ARM_PG_TreeVarListItem(bpy.types.PropertyGroup):
    def _set_name(self, value: str):
        old_name = self._get_name()

        tree = bpy.context.space_data.path[-1].node_tree
        lst = tree.arm_treevariableslist

        if value == '':
            # Don't allow empty variable names
            new_name = old_name
        else:
            new_name = arm.utils.unique_name_in_lists(item_lists=[lst], name_attr='name', wanted_name=value, ignore_item=self)

        self['_name'] = new_name

        for node in tree.nodes:
            if node.arm_logic_id == old_name:
                node.arm_logic_id = new_name

    def _get_name(self) -> str:
        return self.get('_name', 'Untitled')

    def _update_color(self, context):
        space = context.space_data

        # Can be None if color is set before tree is initialized (upon
        # updating old files to newer SDK for example)
        if space is not None:
            for node in space.path[-1].node_tree.nodes:
                if node.arm_logic_id == self.name:
                    node.use_custom_color = True
                    node.color = self.color

    name: StringProperty(
        name='Name',
        description='The name of this variable',
        default='Untitled',
        get=_get_name,
        set=_set_name
    )

    node_type: StringProperty(
        name='Type',
        description='The type of this variable/the bl_idname of the node\'s that may use this variable',
        default='LNIntegerNode'
    )

    color: FloatVectorProperty(
        name='Color',
        description='The color of the nodes that link to this tree variable',
        subtype='COLOR',
        default=[1.0, 1.0, 1.0],
        update=_update_color,
        size=3,
        min=0,
        max=1
    )

    @classmethod
    def create_new(cls, tree: bpy.types.NodeTree, item_name: str, item_type: str) -> 'ARM_PG_TreeVarListItem':
        lst = tree.arm_treevariableslist

        var_item: ARM_PG_TreeVarListItem = lst.add()
        var_item['_name'] = arm.utils.unique_name_in_lists(
            item_lists=[lst], name_attr='name', wanted_name=item_name, ignore_item=var_item
        )
        var_item.node_type = item_type
        var_item.color = arm.utils.get_random_color_rgb()

        tree.arm_treevariableslist_index = len(lst) - 1
        arm.make_state.redraw_ui = True

        return var_item


class ARM_UL_TreeVarList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item: ARM_PG_TreeVarListItem, icon, active_data, active_propname, index):
        node_type = arm.utils.type_name_to_type(item.node_type).bl_label

        row = layout.row(align=True)
        _row = row.row()
        _row.ui_units_x = 1.0
        _row.prop(item, 'color', text='')
        row.prop(item, 'name', text='', emboss=False)
        row.label(text=node_type)


def on_update_node_logic_id(node: arm.logicnode.arm_nodes.ArmLogicTreeNode, context):
    node.on_logic_id_change()


def node_compat_sdk2203():
    """Replace old arm_logic_id system with tree variable system."""
    for tree in bpy.data.node_groups:
        if tree.bl_idname == 'ArmLogicTreeType':
            # All tree variable nodes
            tv_nodes: dict[str, list[arm.logicnode.arm_nodes.ArmLogicVariableNodeMixin]] = {}

            # The type of the tree variable. If two types are found for
            # a logic ID and one is dynamic, assume it's a getter node.
            # Otherwise show a warning upon conflict, it was undefined
            # behaviour before anyway.
            tv_types: dict[str, str] = {}

            # First pass: find all tree variable nodes and decide the
            # variable type in case of conflicts
            node: arm.logicnode.arm_nodes.ArmLogicTreeNode
            for node in list(tree.nodes):
                if node.arm_logic_id != '':
                    if not isinstance(node, arm.logicnode.arm_nodes.ArmLogicVariableNodeMixin):
                        arm.log.warn(
                            'While updating the file to the current SDK'
                            f' version, the node {node.name} in tree'
                            f' {tree.name} is no variable node but had'
                            ' a logic ID. The logic ID was reset to'
                            ' prevent undefined behaviour.'
                        )
                        node.arm_logic_id = ''
                        continue

                    if node.arm_logic_id in tv_nodes:
                        tv_nodes[node.arm_logic_id].append(node)

                        # Check for getter nodes and type conflicts
                        cur_type = tv_types[node.arm_logic_id]
                        if cur_type == 'LNDynamicNode':
                            tv_types[node.arm_logic_id] = node.bl_idname
                        elif cur_type != node.bl_idname and node.bl_idname != 'LNDynamicNode':
                            arm.log.warn(
                                'Found nodes of different types with the'
                                ' same logic ID while updating the file'
                                ' to the current SDK version (undefined'
                                ' behaviour).\n'
                                f'\tConflicting types: {cur_type}, {node.bl_idname}\n'
                                f'\tLogic ID: {node.arm_logic_id}\n'
                                f'\tNew type for both nodes: {cur_type}'
                            )
                    else:
                        tv_nodes[node.arm_logic_id] = [node]
                        tv_types[node.arm_logic_id] = node.bl_idname

            # Second pass: add the tree variable and convert all found
            # tree var nodes to the correct type
            for logic_id in tv_nodes.keys():
                var_type = tv_types[logic_id]

                var_item = ARM_PG_TreeVarListItem.create_new(tree, logic_id, var_type)

                for node in tv_nodes[logic_id]:
                    if node.bl_idname != var_type:
                        newnode = tree.nodes.new(var_type)
                        arm.node_utils.copy_basic_node_props(from_node=node, to_node=newnode)

                        # Connect outputs as good as possible
                        for i in range(min(len(node.outputs), len(newnode.outputs))):
                            for out in node.outputs:
                                for link in out.links:
                                    tree.links.new(newnode.outputs[i], link.to_socket)

                        tree.nodes.remove(node)
                        node = newnode

                    # Hide sockets
                    node.on_logic_id_change()

                    node.use_custom_color = True
                    node.color = var_item.color

                arm.logicnode.arm_nodes.ArmLogicVariableNodeMixin.choose_new_master_node(tree, logic_id)


def node_compat_sdk2209():
    # See https://github.com/armory3d/armory/pull/2538
    for tree in bpy.data.node_groups:
        if tree.bl_idname == "ArmLogicTreeType":
            for item in tree.arm_treevariableslist:
                arm.logicnode.arm_nodes.ArmLogicVariableNodeMixin.synchronize(tree, item.name)


REG_CLASSES = (
    ARM_PT_Variables,
    ARM_OT_TreeVariableListMoveItem,
    ARM_OT_TreeVariableMakeLocalNode,
    ARM_OT_TreeVariableVariableAssignToNode,
    ARM_OT_TreeVariablePromoteNode,
    ARM_OT_AddVarGetterNode,
    ARM_OT_AddVarSetterNode,
    ARM_UL_TreeVarList,
    ARM_PG_TreeVarListItem,
)
register_classes, unregister_classes = bpy.utils.register_classes_factory(REG_CLASSES)


def register():
    register_classes()

    bpy.types.Node.arm_logic_id = StringProperty(
        name='ID',
        description='Nodes with equal identifier share data',
        default='',
        update=on_update_node_logic_id
    )

    bpy.types.NodeTree.arm_treevariableslist = CollectionProperty(type=ARM_PG_TreeVarListItem)
    bpy.types.NodeTree.arm_treevariableslist_index = IntProperty(name='Index for arm_variableslist', default=0)


def unregister():
    unregister_classes()
