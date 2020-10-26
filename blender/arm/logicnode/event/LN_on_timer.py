from arm.logicnode.arm_nodes import *

class OnTimerNode(ArmLogicTreeNode):
    """Activates the output when the given time has elapsed (optionally repeating the timer).

    @input Duration: the time interval before the output activation
    @input Repeat: while `true` will repeat after done
    @output Progress: the progress of the time from 0.0 to 1.0"""
    bl_idname = 'LNOnTimerNode'
    bl_label = 'On Timer'
    arm_version = 1

    def init(self, context):
        super(OnTimerNode, self).init(context)
        self.add_input('NodeSocketFloat', 'Duration')
        self.add_input('NodeSocketBool', 'Repeat')
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('NodeSocketFloat', 'Progress')

add_node(OnTimerNode, category=PKG_AS_CATEGORY)
