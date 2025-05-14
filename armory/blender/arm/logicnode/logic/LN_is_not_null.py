from arm.logicnode.arm_nodes import *

class IsNotNoneNode(ArmLogicTreeNode):
    """Passes through its activation only if the plugged-in value is
    not `null`.

    @seeNode Is Null"""
    bl_idname = 'LNIsNotNoneNode'
    bl_label = 'Is Not Null'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmDynamicSocket', 'Value')

        self.add_output('ArmNodeSocketAction', 'Out')
