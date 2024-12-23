from arm.logicnode.arm_nodes import *

class GetTouchMovementNode(ArmLogicTreeNode):
    """Returns the movement values of the current touch event."""
    bl_idname = 'LNGetTouchMovementNode'
    bl_label = 'Get Touch Movement'
    arm_section = 'surface'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmFloatSocket', 'X Multiplier', default_value=-1.0)
        self.add_input('ArmFloatSocket', 'Y Multiplier', default_value=-1.0)

        self.add_output('ArmFloatSocket', 'X')
        self.add_output('ArmFloatSocket', 'Y')
        self.add_output('ArmFloatSocket', 'Multiplied X')
        self.add_output('ArmFloatSocket', 'Multiplied Y')
