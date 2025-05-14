from arm.logicnode.arm_nodes import *

class PulseNode(ArmLogicTreeNode):
    """Sends a signal repeatedly between the given time interval until you stop it.

    @input Start: Starts to send the signals
    @input Stop: Stops to send the signals
    @input Interval: The interval between the signals
    """
    bl_idname = 'LNPulseNode'
    bl_label = 'Pulse'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'Start')
        self.add_input('ArmNodeSocketAction', 'Stop')
        self.add_input('ArmFloatSocket', 'Interval', default_value=0.1)

        self.add_output('ArmNodeSocketAction', 'Out')