from arm.logicnode.arm_nodes import *

class GetGamepadStartedNode(ArmLogicTreeNode):
    """."""
    bl_idname = 'LNGetGamepadStartedNode'
    bl_label = 'Get Gamepad Started'
    arm_version = 1

    def init(self, context):
        super(GetGamepadStartedNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketInt', 'Index')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('NodeSocketString', 'Button')
