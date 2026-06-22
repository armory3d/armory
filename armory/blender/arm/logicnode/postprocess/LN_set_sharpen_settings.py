from arm.logicnode.arm_nodes import *

class SharpenSetNode(ArmLogicTreeNode):
    """Set the sharpen post-processing settings."""
    bl_idname = 'LNSharpenSetNode'
    bl_label = 'Set Sharpen Settings'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmColorSocket', 'Color', default_value=[0.0, 0.0, 0.0, 1.0])
        self.add_input('ArmFloatSocket', 'Size', default_value=2.5)
        self.add_input('ArmFloatSocket', 'Strength', default_value=0.25)

        self.add_output('ArmNodeSocketAction', 'Out')