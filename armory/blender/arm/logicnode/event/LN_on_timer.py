from arm.logicnode.arm_nodes import *

class OnTimerNode(ArmLogicTreeNode):
    """Activates the output when a given time elapsed (optionally repeating the timer).

    @input Duration: the time in seconds after which to activate the output
    @input Repeat: whether to repeat the timer"""
    bl_idname = 'LNOnTimerNode'
    bl_label = 'On Timer'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmFloatSocket', 'Duration')
        self.add_input('ArmBoolSocket', 'Repeat')

        self.add_output('ArmNodeSocketAction', 'Out')
