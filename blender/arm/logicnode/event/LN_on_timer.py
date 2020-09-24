from arm.logicnode.arm_nodes import *

class OnTimerNode(ArmLogicTreeNode):
    """Runs the output when the time is reached."""
    bl_idname = 'LNOnTimerNode'
    bl_label = 'On Timer'
    arm_version = 1

    def init(self, context):
        super(OnTimerNode, self).init(context)
        self.add_input('NodeSocketFloat', 'Duration')
        self.add_input('NodeSocketBool', 'Repeat')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(OnTimerNode, category=PKG_AS_CATEGORY)
