from arm.logicnode.arm_nodes import *

class SetGravityEnabledNode(ArmLogicTreeNode):
    """Use to set if the gravity is enabled in a rigid body."""
    bl_idname = 'LNSetGravityEnabledNode'
    bl_label = 'Set Gravity Enabled'
    arm_version = 1

    def init(self, context):
        super(SetGravityEnabledNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Rigid Body')
        self.add_input('NodeSocketBool', 'Enabled')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetGravityEnabledNode, category=PKG_AS_CATEGORY)
