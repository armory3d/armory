from arm.logicnode.arm_nodes import *


class GetGlobalCanvasFontSizeNode(ArmLogicTreeNode):
    """Returns the font size of the entire UI Canvas."""
    bl_idname = 'LNGetGlobalCanvasFontSizeNode'
    bl_label = 'Get Global Canvas Font Size'
    arm_section = 'global'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmFloatSocket', 'Size')
