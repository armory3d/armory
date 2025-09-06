from arm.logicnode.arm_nodes import *

class WaitForNode(ArmLogicTreeNode):
    """
    Activate the output when all inputs have been activated at least once since the node's initialization.
    Use This node for parallel flows. Inputs don't need to be active at the same point in time.

    @input Input[0-n]: list of inputs to be activated
    @output Output: output triggered when all inputs are activated
    """
    bl_idname = 'LNWaitForNode'
    bl_label = 'Wait for All Inputs'
    arm_section = 'flow'
    arm_version = 1

    def __init__(self, *args, **kwargs):
        super(WaitForNode, self).__init__(*args, **kwargs)
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

