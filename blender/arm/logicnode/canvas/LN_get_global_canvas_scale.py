from arm.logicnode.arm_nodes import *


class GetGlobalCanvasScaleNode(ArmLogicTreeNode):
    """Returns the scale of the entire UI Canvas."""
    bl_idname = 'LNGetGlobalCanvasScaleNode'
    bl_label = 'Get Global Canvas Scale'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmFloatSocket', 'Scale')
