from arm.logicnode.arm_nodes import *

class GetCameraAspectNode(ArmLogicTreeNode):
    """Returns the aspect of the given camera."""
    bl_idname = 'LNGetCameraAspectNode'
    bl_label = 'Get Camera Aspect'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Camera')

        self.add_output('ArmFloatSocket', 'Aspect')
