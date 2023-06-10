from arm.logicnode.arm_nodes import *


class CombineColorNode(ArmLogicTreeNode):
    """Combines the given HSVA() components to a color value.
    If any input is `null`, the respective channel of the output color is set to `0.0`.
    formula from // https://stackoverflow.com/a/17243070
    """
    bl_idname = 'LNCombineColorHSVNode'
    bl_label = 'Combine HSVA'
    arm_section = 'color'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmFloatSocket', 'H', default_value=0.0)
        self.add_input('ArmFloatSocket', 'S', default_value=0.0)
        self.add_input('ArmFloatSocket', 'V', default_value=0.0)
        self.add_input('ArmFloatSocket', 'A', default_value=1.0)

        self.add_output('ArmColorSocket', 'Color', default_value=[1.0, 1.0, 1.0, 1.0])
