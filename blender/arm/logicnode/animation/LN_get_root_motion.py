from arm.logicnode.arm_nodes import *

class GetRootMotionNode(ArmLogicTreeNode):
    """Gets root motion of an armature object"""
    bl_idname = 'LNGetRootMotionNode'
    bl_label = 'Get Root Motion'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('ArmStringSocket', 'Bone')
        self.add_output('ArmVectorSocket', 'Velocity')