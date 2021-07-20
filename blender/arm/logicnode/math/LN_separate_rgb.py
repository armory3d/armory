from arm.logicnode.arm_nodes import *

class SeparateColorNode(ArmLogicTreeNode):
    """Splits the given color into RGB (red, green and blue)."""
    bl_idname = 'LNSeparateColorNode'
    bl_label = 'Separate RGB'
    arm_section = 'color'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmColorSocket', 'Color', default_value=[1.0, 1.0, 1.0, 1.0])

        self.add_output('ArmFloatSocket', 'R')
        self.add_output('ArmFloatSocket', 'G')
        self.add_output('ArmFloatSocket', 'B')
