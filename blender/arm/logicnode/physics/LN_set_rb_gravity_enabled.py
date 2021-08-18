from arm.logicnode.arm_nodes import *

class SetGravityEnabledNode(ArmLogicTreeNode):
    """Sets whether the gravity is enabled for the given rigid body."""
    bl_idname = 'LNSetGravityEnabledNode'
    bl_label = 'Set RB Gravity Enabled'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'RB')
        self.add_input('ArmBoolSocket', 'Enabled')

        self.add_output('ArmNodeSocketAction', 'Out')
