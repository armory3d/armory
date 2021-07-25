from arm.logicnode.arm_nodes import *

class GetBoneTransformNode(ArmLogicTreeNode):
    """Returns bone transform in world space."""
    bl_idname = 'LNGetBoneTransformNode'
    bl_label = 'Get Bone Transform'
    arm_version = 1
    arm_section = 'armature'

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmStringSocket', 'Bone')
        self.add_output('ArmDynamicSocket', 'Transform')
