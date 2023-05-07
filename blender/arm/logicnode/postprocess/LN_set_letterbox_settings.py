from arm.logicnode.arm_nodes import *

class LetterboxSetNode(ArmLogicTreeNode):
    """Set the letterbox post-processing settings."""
    bl_idname = 'LNLetterboxSetNode'
    bl_label = 'Set Letterbox Settings'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmColorSocket', 'Color', default_value=[0.0, 0.0, 0.0, 0.0])
        self.add_input('ArmFloatSocket', 'Size', default_value=0.1)

        self.add_output('ArmNodeSocketAction', 'Out')
