from arm.logicnode.arm_nodes import *


class RandomOutputNode(ArmLogicTreeNode):
    """Activate a random output when the input is activated."""
    bl_idname = 'LNRandomOutputNode'
    bl_label = 'Random Output'
    arm_section = 'logic'
    arm_version = 1

    def __init__(self):
        array_nodes[str(id(self))] = self

    def arm_init(self, context):

        self.add_input('ArmNodeSocketAction', 'In')

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)

        op = row.operator('arm.node_add_output', text='New', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        op.socket_type = 'ArmNodeSocketAction'
        op2 = row.operator('arm.node_remove_output', text='', icon='X', emboss=True)
        op2.node_index = str(id(self))
