from arm.logicnode.arm_nodes import *

class SharpenGetNode(ArmLogicTreeNode):
    """Returns the sharpen post-processing settings."""
    bl_idname = 'LNSharpenGetNode'
    bl_label = 'Get Sharpen Settings'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmColorSocket', 'Color')
        self.add_output('ArmFloatSocket', 'Size')
        self.add_output('ArmFloatSocket', 'Strength')
