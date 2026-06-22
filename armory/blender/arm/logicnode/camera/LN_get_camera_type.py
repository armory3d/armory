from arm.logicnode.arm_nodes import *

class GetCameraTypeNode(ArmLogicTreeNode):
    """Returns the camera Type:
        0 : Perspective
        1 : Ortographic
    ."""
    bl_idname = 'LNGetCameraTypeNode'
    bl_label = 'Get Camera Type'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Camera')
        
        self.add_output('ArmBoolSocket', 'Type')
