from arm.logicnode.arm_nodes import *

class TimerNode(ArmLogicTreeNode):
    """Creates a timer."""
    bl_idname = 'LNTimerNode'
    bl_label = 'Timer'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'Start')
        self.add_input('ArmNodeSocketAction', 'Pause')
        self.add_input('ArmNodeSocketAction', 'Stop')
        self.add_input('ArmFloatSocket', 'Duration', default_value=1.0)
        self.add_input('ArmIntSocket', 'Repeat')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketAction', 'Done')
        self.add_output('ArmBoolSocket', 'Running')
        self.add_output('ArmIntSocket', 'Time Passed')
        self.add_output('ArmIntSocket', 'Time Left')
        self.add_output('ArmFloatSocket', 'Progress')
        self.add_output('ArmFloatSocket', 'Repetitions')

    def draw_label(self) -> str:
        inp_duration = self.inputs['Duration']
        inp_repeat = self.inputs['Repeat']
        if inp_duration.is_linked or inp_repeat.is_linked:
            return self.bl_label

        return f'{self.bl_label}: {round(inp_duration.default_value, 3)}s ({inp_repeat.default_value} R.)'
