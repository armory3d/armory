from arm.logicnode.arm_nodes import *

class ActiveCameraNode(ArmLogicTreeNode):
    """Get the the active camera.

    @seeNode Set Active Camera"""
    bl_idname = 'LNActiveCameraNode'
    bl_label = 'Get Active Camera'
    arm_version = 1

    def init(self, context):
        super(ActiveCameraNode, self).init(context)
        self.add_output('ArmNodeSocketObject', 'Camera')

add_node(ActiveCameraNode, category=PKG_AS_CATEGORY)
