from arm.logicnode.arm_nodes import *

class GetMouseStartedNode(ArmLogicTreeNode):
    """."""
    bl_idname = 'LNGetMouseStartedNode'
    bl_label = 'Get Mouse Started'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmStringSocket', 'Button')
