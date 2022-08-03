import bpy

import arm.utils
from arm.logicnode.arm_nodes import *
import arm.logicnode.miscellaneous.LN_call_group as LN_call_group


class GroupInputsNode(ArmLogicTreeNode):
    """Input for a node group."""
    bl_idname = 'LNGroupInputsNode'
    bl_label = 'Group Input Node'
    arm_section = 'group'
    arm_version = 1

    def __init__(self):
        array_nodes[str(id(self))] = self

    def init(self, context):
        tree = bpy.context.space_data.edit_tree
        node_count = 0
        for node in tree.nodes:
            if node.bl_idname == 'LNGroupInputsNode':
                node_count += 1
        if node_count > 1:
            arm.log.warn("Only one group input node per node tree is allowed")
            tree.nodes.remove(self)
        else:
            super().init(context)

    def copy(self, node):
        tree = bpy.context.space_data.edit_tree
        node_count = 0
        for node in tree.nodes:
            if node.bl_idname == 'LNGroupInputsNode':
                node_count += 1
        if node_count > 1:
            arm.log.warn("Only one group input node per node tree is allowed")
            tree.nodes.remove(self)

    def update(self):
        super().update()
        LN_call_group.CallGroupNode.update_all()

    def arm_init(self, context):
        self.add_output('ArmAnySocket', '')

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)

        op = row.operator('arm.node_add_output', text='New', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        op.socket_type = 'ArmAnySocket'
        if len(self.outputs) > 1:
            op2 = row.operator('arm.node_remove_output', text='', icon='X', emboss=True)
            op2.node_index = str(id(self))
