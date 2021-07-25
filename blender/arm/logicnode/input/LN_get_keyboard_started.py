from arm.logicnode.arm_nodes import *

class GetKeyboardStartedNode(ArmLogicTreeNode):
    """."""
    bl_idname = 'LNGetKeyboardStartedNode'
    bl_label = 'Get Keyboard Started'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmStringSocket', 'Key')
