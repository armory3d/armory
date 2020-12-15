from arm.logicnode.arm_nodes import *

class TimerNode(ArmLogicTreeNode):
    """Creates a timer."""
    bl_idname = 'LNTimerNode'
    bl_label = 'Timer'
    arm_version = 1

    def init(self, context):
        super(TimerNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'Start')
        self.add_input('ArmNodeSocketAction', 'Pause')
        self.add_input('ArmNodeSocketAction', 'Stop')
        self.add_input('NodeSocketFloat', 'Duration', default_value=1.0)
        self.add_input('NodeSocketInt', 'Repeat')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketAction', 'Done')
        self.add_output('NodeSocketBool', 'Running')
        self.add_output('NodeSocketInt', 'Time Passed')
        self.add_output('NodeSocketInt', 'Time Left')
        self.add_output('NodeSocketFloat', 'Progress')
        self.add_output('NodeSocketFloat', 'Repetitions')

    def draw_label(self) -> str:
        inp_duration = self.inputs['Duration']
        inp_repeat = self.inputs['Repeat']
        if inp_duration.is_linked or inp_repeat.is_linked:
            return self.bl_label

        return f'{self.bl_label}: {round(inp_duration.default_value, 3)}s ({inp_repeat.default_value} R.)'
