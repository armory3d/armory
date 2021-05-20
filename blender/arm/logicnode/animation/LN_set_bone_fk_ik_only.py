from arm.logicnode.arm_nodes import *

class SetBoneFkIkOnlyNode(ArmLogicTreeNode):
    """Set particular bone to be animated by Forward kinematics or Inverse kinematics only. All other animations will be ignored"""
    bl_idname = 'LNSetBoneFkIkOnlyNode'
    bl_label = 'Set Bone FK IK Only'
    arm_version = 1
    arm_section = 'armature'

    def init(self, context):
        super(SetBoneFkIkOnlyNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketString', 'Bone')
        self.add_input('NodeSocketBool', 'FK or IK only')

        self.add_output('ArmNodeSocketAction', 'Out')
