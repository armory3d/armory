from arm.logicnode.arm_nodes import *

class SeparateVectorNode(ArmLogicTreeNode):
    """Splits the given vector into X, Y and Z."""
    bl_idname = 'LNSeparateVectorNode'
    bl_label = 'Separate XYZ'
    arm_section = 'vector'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmVectorSocket', 'Vector')

        self.add_output('ArmFloatSocket', 'X')
        self.add_output('ArmFloatSocket', 'Y')
        self.add_output('ArmFloatSocket', 'Z')
