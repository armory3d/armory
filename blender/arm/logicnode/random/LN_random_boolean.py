from arm.logicnode.arm_nodes import *


class RandomBooleanNode(ArmLogicTreeNode):
    """Generates a random boolean."""
    bl_idname = 'LNRandomBooleanNode'
    bl_label = 'Random Boolean'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmBoolSocket', 'Bool')
