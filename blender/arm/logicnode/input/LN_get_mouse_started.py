from arm.logicnode.arm_nodes import *

class GetMouseStartedNode(ArmLogicTreeNode):
    """."""
    bl_idname = 'LNGetMouseStartedNode'
    bl_label = 'Get Mouse Started'
    arm_version = 1

    def init(self, context):
        super(GetMouseStartedNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('NodeSocketString', 'Button')
