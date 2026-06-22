from arm.logicnode.arm_nodes import *

class GetCameraScaleNode(ArmLogicTreeNode):
    """Returns the scale of the given camera."""
    bl_idname = 'LNGetCameraScaleNode'
    bl_label = 'Get Camera Ortho Scale'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Camera')

        self.add_output('ArmFloatSocket', 'Ortho Scale')
2