from arm.logicnode.arm_nodes import *

class AlternateNode(ArmLogicTreeNode):
    """Activates the outputs alternating every time it is active."""
    bl_idname = 'LNAlternateNode'
    bl_label = 'Alternate Output'
    arm_section = 'flow'
    arm_version = 2

    def __init__(self, *args, **kwargs):
        super(AlternateNode, self).__init__(*args, **kwargs)
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

