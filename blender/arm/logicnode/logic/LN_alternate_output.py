from arm.logicnode.arm_nodes import *


class AlternateNode(ArmLogicTreeNode):
    """Activates the outputs `0` and `1` alternating every time it is active."""
    bl_idname = 'LNAlternateNode'
    bl_label = 'Alternate Output'
    arm_section = 'flow'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')

        self.add_output('ArmNodeSocketAction', '0')
        self.add_output('ArmNodeSocketAction', '1')
