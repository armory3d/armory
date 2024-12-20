from arm.logicnode.arm_nodes import *

class RotationFromTransformNode(ArmLogicTreeNode):
    """Returns rotation matrix from the given transform."""
    bl_idname = 'LNRotationFromTransformNode'
    bl_label = 'Transform to Rotation Matrix'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmDynamicSocket', 'Transform')

        self.add_output('ArmVectorSocket', 'Vector x')
        self.add_output('ArmVectorSocket', 'Vector y')
        self.add_output('ArmVectorSocket', 'Vector z')
