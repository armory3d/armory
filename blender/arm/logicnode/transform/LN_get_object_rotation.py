from arm.logicnode.arm_nodes import *

class GetRotationNode(ArmLogicTreeNode):
    """Returns the current rotation of the given object."""
    bl_idname = 'LNGetRotationNode'
    bl_label = 'Get Object Rotation'
    arm_section = 'rotation'
    arm_version = 1

    def init(self, context):
        super(GetRotationNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('NodeSocketVector', 'Euler Angles')
        self.add_output('NodeSocketVector', 'Vector')
        self.add_output('NodeSocketFloat', 'Angle (Radians)')
        self.add_output('NodeSocketFloat', 'Angle (Degrees)')
        self.add_output('NodeSocketVector', 'Quaternion XYZ')
        self.add_output('NodeSocketFloat', 'Quaternion W')
