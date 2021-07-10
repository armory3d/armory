from arm.logicnode.arm_nodes import *

class BoneIKNode(ArmLogicTreeNode):
    """Applies inverse kinematics in the given object bone."""
    bl_idname = 'LNBoneIKNode'
    bl_label = 'Bone IK'
    arm_version = 1
    arm_section = 'armature'

    def init(self, context):
        super(BoneIKNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmStringSocket', 'Bone')
        self.add_input('ArmVectorSocket', 'Goal')

        self.add_output('ArmNodeSocketAction', 'Out')
