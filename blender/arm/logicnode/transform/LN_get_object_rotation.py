from arm.logicnode.arm_nodes import *

class GetRotationNode(ArmLogicTreeNode):
    """Returns the current rotation of the given object."""
    bl_idname = 'LNGetRotationNode'
    bl_label = 'Get Object Rotation'
    arm_section = 'rotation'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')

        self.add_output('ArmVectorSocket', 'Euler Angles')
        self.add_output('ArmVectorSocket', 'Vector')
        self.add_output('ArmFloatSocket', 'Angle (Radians)')
        self.add_output('ArmFloatSocket', 'Angle (Degrees)')
        self.add_output('ArmVectorSocket', 'Quaternion XYZ')
        self.add_output('ArmFloatSocket', 'Quaternion W')
