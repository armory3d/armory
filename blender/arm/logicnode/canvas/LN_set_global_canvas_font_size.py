from arm.logicnode.arm_nodes import *


class SetGlobalCanvasFontSizeNode(ArmLogicTreeNode):
    """Sets the font size of the entire UI Canvas."""
    bl_idname = 'LNSetGlobalCanvasFontSizeNode'
    bl_label = 'Set Global Canvas Font Size'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmFloatSocket', 'Size', default_value=10)

        self.add_output('ArmNodeSocketAction', 'Out')
