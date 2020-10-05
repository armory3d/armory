from arm.logicnode.arm_nodes import *

class SetCameraFovNode(ArmLogicTreeNode):
    """Sets the field of view (FOV) of the given camera.

    @seeNode Get Camera FOV"""
    bl_idname = 'LNSetCameraFovNode'
    bl_label = 'Set Camera FOV'
    arm_version = 1

    def init(self, context):
        super(SetCameraFovNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Camera')
        self.add_input('NodeSocketFloat', 'FOV', default_value=0.85)
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetCameraFovNode, category=PKG_AS_CATEGORY)
