from arm.logicnode.arm_nodes import *

class WaitForNode(ArmLogicTreeNode):
    """
    Activates the output when all inputs are received disregaring its order. The idea
    is to wait for all inputs to be received to trigger the output.

    @input list of inputs to wait for triggering the output
    @output is triggered when all inputs are received
    """
    bl_idname = 'LNWaitForNode'
    bl_label = 'Wait for Input'
    arm_section = 'flow'
    arm_version = 1
    
    def __init__(self):
        super(WaitForNode, self).__init__()
        array_nodes[str(id(self))] = self

    def arm_init(self, context):
        self.add_output('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)

        op = row.operator('arm.node_add_input', text='New', icon='PLUS', emboss=True)
        op.node_index = str(id(self))
        op.socket_type = 'ArmNodeSocketAction'
        op2 = row.operator('arm.node_remove_input', text='', icon='X', emboss=True)
        op2.node_index = str(id(self))

