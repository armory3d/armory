from arm.logicnode.arm_nodes import *

class SetCameraNode(ArmLogicTreeNode):
    """Sets the active camera.

    @seeNode Get Active Camera"""
    bl_idname = 'LNSetCameraNode'
    bl_label = 'Set Camera Active'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Camera')

        self.add_output('ArmNodeSocketAction', 'Out')
