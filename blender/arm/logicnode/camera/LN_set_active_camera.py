from arm.logicnode.arm_nodes import *

class SetCameraNode(ArmLogicTreeNode):
    """Set the active camera of the active scene."""
    bl_idname = 'LNSetCameraNode'
    bl_label = 'Set Active Camera'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')

        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetCameraNode, category=PKG_AS_CATEGORY)
