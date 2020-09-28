from arm.logicnode.arm_nodes import *

class GetCameraFovNode(ArmLogicTreeNode):
    """Get the field of view (FOV) of a camera.

    @seeNode Set Camera FOV"""
    bl_idname = 'LNGetCameraFovNode'
    bl_label = 'Get Camera FOV'
    arm_version = 1

    def init(self, context):
        super(GetCameraFovNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('NodeSocketFloat', 'FOV')

add_node(GetCameraFovNode, category=PKG_AS_CATEGORY)
