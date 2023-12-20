from arm.logicnode.arm_nodes import *

class GetWorldStrengthNode(ArmLogicTreeNode):
    """Gets the strength of the given World."""
    bl_idname = 'LNGetWorldStrengthNode'
    bl_label = 'Get World Strength'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmFloatSocket', 'Strength')
