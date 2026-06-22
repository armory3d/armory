from arm.logicnode.arm_nodes import *


class CombineColorNode(ArmLogicTreeNode):
    """Combines the given RGBA (red, green, blue, and alpha) components to a color value.
    If any input is `null`, the respective channel of the output color is set to `0.0`.
    """
    bl_idname = 'LNCombineColorNode'
    bl_label = 'Combine RGBA'
    arm_section = 'color'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmFloatSocket', 'R', default_value=0.0)
        self.add_input('ArmFloatSocket', 'G', default_value=0.0)
        self.add_input('ArmFloatSocket', 'B', default_value=0.0)
        self.add_input('ArmFloatSocket', 'A', default_value=1.0)

        self.add_output('ArmColorSocket', 'Color', default_value=[1.0, 1.0, 1.0, 1.0])
