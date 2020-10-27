from arm.logicnode.arm_nodes import *

class OnTimerNode(ArmLogicTreeNode):
    """Activates the output when a given time elapsed (optionally repeating the timer).

    @input Duration: the time in seconds after which to activate the output
    @input Repeat: whether to repeat the timer"""
    bl_idname = 'LNOnTimerNode'
    bl_label = 'On Timer'
    arm_version = 1

    def init(self, context):
        super(OnTimerNode, self).init(context)
        self.add_input('NodeSocketFloat', 'Duration')
        self.add_input('NodeSocketBool', 'Repeat')
        self.add_output('ArmNodeSocketAction', 'Out')
