from arm.logicnode.arm_nodes import *


class GetMouseMovementNode(ArmLogicTreeNode):
    """Get the movement coordinates of the mouse and the mouse wheel delta.
    The multiplied output variants default to -1 to invert the values."""
    bl_idname = 'LNGetMouseMovementNode'
    bl_label = 'Get Mouse Movement'
    arm_section = 'mouse'
    arm_version = 1

    def arm_init(self, context):

        self.add_input('ArmFloatSocket', 'X Multiplier', default_value=-1.0)
        self.add_input('ArmFloatSocket', 'Y Multiplier', default_value=-1.0)
        self.add_input('ArmFloatSocket', 'Wheel Delta Multiplier', default_value=-1.0)

        self.add_output('ArmFloatSocket', 'X')
        self.add_output('ArmFloatSocket', 'Y')
        self.add_output('ArmFloatSocket', 'Multiplied X')
        self.add_output('ArmFloatSocket', 'Multiplied Y')
        self.add_output('ArmIntSocket', 'Wheel Delta')
        self.add_output('ArmFloatSocket', 'Multiplied Wheel Delta')
