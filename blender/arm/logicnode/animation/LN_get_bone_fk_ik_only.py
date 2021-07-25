from arm.logicnode.arm_nodes import *

class GetBoneFkIkOnlyNode(ArmLogicTreeNode):
    """Get if a particular bone is animated by Forward kinematics or Inverse kinematics only."""
    bl_idname = 'LNGetBoneFkIkOnlyNode'
    bl_label = 'Get Bone FK IK Only'
    arm_version = 1
    arm_section = 'armature'

    def init(self, context):
        super(GetBoneFkIkOnlyNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketString', 'Bone')
        self.add_output('NodeSocketBool', 'FK or IK only')