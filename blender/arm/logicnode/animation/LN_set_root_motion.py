from arm.logicnode.arm_nodes import *

class SetRootMotionNode(ArmLogicTreeNode):
    """Sets the root motion bone in an armature object."""
    bl_idname = 'LNSetRootMotionNode'
    bl_label = 'Set Root Motion'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmStringSocket', 'Bone')

        self.add_output('ArmNodeSocketAction', 'Out')