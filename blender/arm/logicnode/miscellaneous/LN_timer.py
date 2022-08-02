from arm.logicnode.arm_nodes import *


class TimerNode(ArmLogicTreeNode):
    """Runs a timer with a specified amount of repetitions.

    @input Start: Start the timer or continue if paused. In both cases,
        the values of `Duration` and `Repeat` are (re-)evaluated.
    @input Pause: Pause the timer.
    @input Stop: Stop and reset the timer. This does not activate any outputs.
    @input Duration: The time in seconds that the timer runs.
    @input Repeat: The number of times the timer will repeat, or 0 for infinite repetition.

    @output Out: Activated after each repetition.
    @output Done: Activated after the last repetition (never activated if `Repeat` is 0).
    @output Running: Whether the timer is currently running.
    @output Time Passed: The time in seconds that has passed since the
        current repetition started, excluding pauses.
    @output Time Left: The time left in seconds until the timer is done
        or the next repetition starts.
    @output Progress: Percentage of the timer's progress of the current
        repetition (`Time Passed/Duration`).
    @output Repetitions: The index of the current repetition, starting at 0.
    """
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

        return f'{self.bl_label}: {round(inp_duration.default_value_raw, 3)}s ({inp_repeat.default_value_raw} R.)'
