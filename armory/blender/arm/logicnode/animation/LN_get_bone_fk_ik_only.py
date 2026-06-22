from arm.logicnode.arm_nodes import *

class GetBoneFkIkOnlyNode(ArmLogicTreeNode):
    """Get if a particular bone is animated by Forward kinematics or Inverse kinematics only."""
    bl_idname = 'LNGetBoneFkIkOnlyNode'
    bl_label = 'Get Bone FK IK Only'
    arm_version = 1
    arm_section = 'armature'

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmStringSocket', 'Bone')
        self.add_output('ArmBoolSocket', 'FK or IK only')
