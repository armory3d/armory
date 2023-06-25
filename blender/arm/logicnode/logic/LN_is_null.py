from arm.logicnode.arm_nodes import *


class IsNoneNode(ArmLogicTreeNode):
    """Passes through its activation only if the plugged-in value is
    `null` (no value).

    @seeNode Is Not Null"""
    bl_idname = 'LNIsNoneNode'
    bl_label = 'Is Null'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmDynamicSocket', 'Value')

        self.add_output('ArmNodeSocketAction', 'Out')
