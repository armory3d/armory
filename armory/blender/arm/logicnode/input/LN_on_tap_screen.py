from arm.logicnode.arm_nodes import *


class OnTapScreen(ArmLogicTreeNode):
    """Activates the output on tap screen event.

    @input Duration: touching time
    @input Interval: interval between taps
    @input Repeat: repetitions amount to validate

    @output Done: the sequence success
    @output Fail: the the sequence failure
    @output Tap Number: number of the last tap
    @output Coords: the coordinates of the last tap
    """
    bl_idname = 'LNOnTapScreen'
    bl_label = 'On Tap Screen'
    arm_section = 'Input'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmFloatSocket', 'Duration', default_value=0.3)
        self.add_input('ArmFloatSocket', 'Interval', default_value=0.0)
        self.add_input('ArmIntSocket', 'Repeat', default_value=2)

        self.add_output('ArmNodeSocketAction', 'Done')
        self.add_output('ArmNodeSocketAction', 'Fail')
        self.add_output('ArmNodeSocketAction', 'Tap')
        self.add_output('ArmIntSocket', 'Tap Number')
        self.add_output('ArmVectorSocket', 'Coords')
