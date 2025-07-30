from arm.logicnode.arm_nodes import *

class ResolutionGetNode(ArmLogicTreeNode):
    """Returns the resolution parameters.
    """
    bl_idname = 'LNResolutionGetNode'
    bl_label = 'Get Resolution Settings'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmIntSocket', 'Size')
        self.add_output('ArmIntSocket', 'Filter')
