from arm.logicnode.arm_nodes import *

class LetterboxGetNode(ArmLogicTreeNode):
    """Returns the letterbox post-processing settings."""
    bl_idname = 'LNLetterboxGetNode'
    bl_label = 'Get Letterbox Settings'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmColorSocket', 'Color')
        self.add_output('ArmFloatSocket', 'Size')
