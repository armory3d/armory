from arm.logicnode.arm_nodes import *

class SeparateQuaternionNode(ArmLogicTreeNode):
    """Splits the given quaternion into X, Y, Z and W."""
    bl_idname = 'LNSeparateQuaternionNode'
    bl_label = "Separate Quaternion"
    arm_section = 'quaternions'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmVectorSocket', 'Quaternion')

        self.add_output('ArmFloatSocket', 'X')
        self.add_output('ArmFloatSocket', 'Y')
        self.add_output('ArmFloatSocket', 'Z')
        self.add_output('ArmFloatSocket', 'W')
