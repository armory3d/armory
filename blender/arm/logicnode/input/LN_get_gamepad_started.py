from arm.logicnode.arm_nodes import *

class GetGamepadStartedNode(ArmLogicTreeNode):
    """."""
    bl_idname = 'LNGetGamepadStartedNode'
    bl_label = 'Get Gamepad Started'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmIntSocket', 'Index')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmStringSocket', 'Button')
