from arm.logicnode.arm_nodes import *

class ActiveCameraNode(ArmLogicTreeNode):
    """Get the active camera of the active scene."""
    bl_idname = 'LNActiveCameraNode'
    bl_label = 'Get Active Camera'

    def init(self, context):
        self.add_output('ArmNodeSocketObject', 'Object')

add_node(ActiveCameraNode, category=MODULE_AS_CATEGORY)
