from arm.logicnode.arm_nodes import *


class InverseNode(ArmLogicTreeNode):
    """Activates the output if the input is not active."""
    bl_idname = 'LNInverseNode'
    bl_label = 'Invert Output'
    arm_section = 'flow'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')

        self.add_output('ArmNodeSocketAction', 'Out')
