from arm.logicnode.arm_nodes import *

class ColorMixNode(ArmLogicTreeNode):
    """Mix 2 colors:

    @input Color: Fist color to mix.
    @input Color: Second color to mix.
    @input Mix: Mix factor from 0 to 1.

    @output Color: Mixed color.

    @see https://github.com/rvanwijnen/spectral.js 2023 Ronald van Wijnen.
    """

    bl_idname = 'LNColorMixNode'
    bl_label = 'Color Mix'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmColorSocket', 'Color In', default_value=[1.0, 1.0, 1.0, 1.0])
        self.add_input('ArmColorSocket', 'Color In', default_value=[1.0, 1.0, 1.0, 1.0])
        self.add_input('ArmFloatSocket', 'Mix', default_value= 0.5)

        self.add_output('ArmColorSocket', 'Color Out', is_var=True)