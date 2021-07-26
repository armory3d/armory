from arm.logicnode.arm_nodes import *

class QuaternionNode(ArmLogicTreeNode):
    """TO DO."""
    bl_idname = 'LNQuaternionNode'
    bl_label = 'Quaternion'
    arm_section = 'quaternions'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmFloatSocket', 'X')
        self.add_input('ArmFloatSocket', 'Y')
        self.add_input('ArmFloatSocket', 'Z')
        self.add_input('ArmFloatSocket', 'W', default_value=1.0)

        self.add_output('ArmVectorSocket', 'Quaternion')
        self.add_output('ArmVectorSocket', 'XYZ')
        self.add_output('ArmFloatSocket', 'W')
