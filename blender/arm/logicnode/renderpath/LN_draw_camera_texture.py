from arm.logicnode.arm_nodes import *

class DrawCameraTextureNode(ArmLogicTreeNode):
    """to do"""
    bl_idname = 'LNDrawCameraTextureNode'
    bl_label = 'Draw Camera to Texture'
    arm_section = 'draw'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmBoolSocket', 'Activated/Deactivated', default_value = True)
        self.add_input('ArmNodeSocketObject', 'Camera')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmIntSocket', 'Material Slot')   

        self.add_output('ArmNodeSocketAction', 'Out')