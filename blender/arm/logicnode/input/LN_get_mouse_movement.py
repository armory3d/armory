from arm.logicnode.arm_nodes import *


class GetMouseMovementNode(ArmLogicTreeNode):
    """Get the movement coordinates of the mouse and the mouse wheel delta.
    The multiplied output variants default to -1 to invert the values."""
    bl_idname = 'LNGetMouseMovementNode'
    bl_label = 'Get Mouse Movement'
    arm_section = 'mouse'
    arm_version = 1

    def init(self, context):
        super(GetMouseMovementNode, self).init(context)

        self.add_input('NodeSocketFloat', 'X Multiplier', default_value=-1.0)
        self.add_input('NodeSocketFloat', 'Y Multiplier', default_value=-1.0)
        self.add_input('NodeSocketFloat', 'Wheel Delta Multiplier', default_value=-1.0)

        self.add_output('NodeSocketFloat', 'X')
        self.add_output('NodeSocketFloat', 'Y')
        self.add_output('NodeSocketFloat', 'Multiplied X')
        self.add_output('NodeSocketFloat', 'Multiplied Y')
        self.add_output('NodeSocketInt', 'Wheel Delta')
        self.add_output('NodeSocketFloat', 'Multiplied Wheel Delta')
