from arm.logicnode.arm_nodes import *

class IsRigidBodyActiveNode(ArmLogicTreeNode):
    """Returns whether the given rigid body is active or sleeping."""
    bl_idname = 'LNIsRigidBodyActiveNode'
    bl_label = 'RB Is Active'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'RB')
        self.add_output('ArmBoolSocket', 'Is Active')
