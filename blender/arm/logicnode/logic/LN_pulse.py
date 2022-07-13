from arm.logicnode.arm_nodes import *

class PulseNode(ArmLogicTreeNode):
    """Limits the rate of the incoming signal."""
    bl_idname = 'LNPulseNode'
    bl_label = 'Pulse'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketAction', 'Reset Tick')
        self.add_input('ArmFloatSocket', 'Interval', default_value=0.1)

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketAction', 'Failed')
