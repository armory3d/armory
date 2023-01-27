from arm.logicnode.arm_nodes import *


class SeparateColorHSVNode(ArmLogicTreeNode):
    """Splits the given color into its HSVA components (hue, saturation, value, and alpha).
    If the input color is `null`, the outputs are each set to `0.0`.
    formula from: https://axonflux.com/handy-rgb-to-hsl-and-rgb-to-hsv-color-model-c
    """
    bl_idname = 'LNSeparateColorHSVNode'
    bl_label = 'Separate HSVA'
    arm_section = 'color'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmColorSocket', 'Color', default_value=[1.0, 1.0, 1.0, 1.0])

        self.add_output('ArmFloatSocket', 'H')
        self.add_output('ArmFloatSocket', 'S')
        self.add_output('ArmFloatSocket', 'V')
        self.add_output('ArmFloatSocket', 'A')