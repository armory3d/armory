from arm.logicnode.arm_nodes import *

class GetCameraFovNode(ArmLogicTreeNode):
    """Returns the field of view (FOV) of the given camera.

    @seeNode Set Camera FOV"""
    bl_idname = 'LNGetCameraFovNode'
    bl_label = 'Get Camera FOV'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')

        self.add_output('ArmFloatSocket', 'FOV')
