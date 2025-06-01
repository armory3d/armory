from arm.logicnode.arm_nodes import *

class AutoExposureGetNode(ArmLogicTreeNode):
    """Returns the auto exposure post-processing settings."""
    bl_idname = 'LNAutoExposureGetNode'
    bl_label = 'Get Auto Exposure Settings'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmFloatSocket', 'Strength')
        self.add_output('ArmFloatSocket', 'Speed')
