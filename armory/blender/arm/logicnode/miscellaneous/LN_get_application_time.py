from arm.logicnode.arm_nodes import *

class TimeNode(ArmLogicTreeNode):
    """Returns the application execution time and the delta time."""
    bl_idname = 'LNTimeNode'
    bl_label = 'Get Application Time'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmFloatSocket', 'Time')
        self.add_output('ArmFloatSocket', 'Delta')
