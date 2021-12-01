import bpy

import arm.utils
from arm.logicnode.arm_nodes import *


class GroupInputNode(ArmLogicTreeNode):
    """Input for a given a node tree."""
    bl_idname = 'LNGroupInputNode'
    bl_label = 'Group Input Node'
    arm_section = 'group'
    arm_version = 1

    def __init__(self):
        array_nodes[str(id(self))] = self

    def arm_init(self, context):
        self.add_output('ArmAnySocket', '')
    
    def draw_buttons(self, context, layout):
        row = layout.row(align=True)

        op = row.operator('arm.node_add_output', text='New', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        op.socket_type = 'ArmAnySocket'
        if(len(self.outputs) > 1):
            op2 = row.operator('arm.node_remove_output', text='', icon='X', emboss=True)
            op2.node_index = str(id(self))
