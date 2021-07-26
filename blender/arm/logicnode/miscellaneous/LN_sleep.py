from arm.logicnode.arm_nodes import *

class SleepNode(ArmLogicTreeNode):
    """Waits a specified amount of seconds until passing
    through the incoming signal."""
    bl_idname = 'LNSleepNode'
    bl_label = 'Sleep'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmFloatSocket', 'Time')

        self.add_output('ArmNodeSocketAction', 'Out')
