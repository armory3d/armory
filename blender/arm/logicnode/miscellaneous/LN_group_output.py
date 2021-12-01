import bpy

import arm.utils
from arm.logicnode.arm_nodes import *


class GroupOutputNode(ArmLogicTreeNode):
    """Output for a given a node tree."""
    bl_idname = 'LNGroupOutputNode'
    bl_label = 'Group Output Node'
    arm_section = 'group'
    arm_version = 2

    def __init__(self):
        array_nodes[str(id(self))] = self

    def arm_init(self, context):
        self.add_input('ArmAnySocket', '')
    
    def draw_buttons(self, context, layout):
        row = layout.row(align=True)

        op = row.operator('arm.node_add_input', text='New', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        op.socket_type = 'ArmAnySocket'
        if(len(self.inputs) > 1):
            op2 = row.operator('arm.node_remove_input', text='', icon='X', emboss=True)
            op2.node_index = str(id(self))
