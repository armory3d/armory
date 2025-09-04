from arm.logicnode.arm_nodes import *

class AutoExposureSetNode(ArmLogicTreeNode):
    """Set the sharpen post-processing settings."""
    bl_idname = 'LNAutoExposureSetNode'
    bl_label = 'Set Auto Exposure Settings'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmFloatSocket', 'Strength', default_value=1)
        self.add_input('ArmFloatSocket', 'Speed', default_value=1)

        self.add_output('ArmNodeSocketAction', 'Out')