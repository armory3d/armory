from arm.logicnode.arm_nodes import *


class SetGlobalCanvasScaleNode(ArmLogicTreeNode):
    """Sets the scale of the entire UI Canvas."""
    bl_idname = 'LNSetGlobalCanvasScaleNode'
    bl_label = 'Set Global Canvas Scale'
    arm_section = 'global'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmFloatSocket', 'Scale', default_value=1.0)

        self.add_output('ArmNodeSocketAction', 'Out')
