from arm.logicnode.arm_nodes import *

class SetGravityEnabledNode(ArmLogicTreeNode):
    """Sets whether the gravity is enabled for the given rigid body."""
    bl_idname = 'LNSetGravityEnabledNode'
    bl_label = 'Set RB Gravity Enabled'
    arm_version = 1

    def init(self, context):
        super(SetGravityEnabledNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'RB')
        self.add_input('NodeSocketBool', 'Enabled')
        self.add_output('ArmNodeSocketAction', 'Out')
