from arm.logicnode.arm_nodes import *


class SeparateQuaternionNode(ArmLogicTreeNode):
    """TO DO."""
    bl_idname = 'LNSeparateQuaternionNode'
    bl_label = "Separate Quaternion"
    arm_section = 'quaternions'
    arm_version = 1

    def init(self, context):
        super(SeparateQuaternionNode, self).init(context)
        self.add_input('NodeSocketVector', 'Quaternion')
        self.add_output('NodeSocketFloat', 'X')
        self.add_output('NodeSocketFloat', 'Y')
        self.add_output('NodeSocketFloat', 'Z')
        self.add_output('NodeSocketFloat', 'W')
