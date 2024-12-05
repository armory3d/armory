from arm.logicnode.arm_nodes import *

class SetWorldStrengthNode(ArmLogicTreeNode):
    """Sets the strength of the given World."""
    bl_idname = 'LNSetWorldStrengthNode'
    bl_label = 'Set World Strength'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmFloatSocket', 'Strength')

        self.add_output('ArmNodeSocketAction', 'Out')
