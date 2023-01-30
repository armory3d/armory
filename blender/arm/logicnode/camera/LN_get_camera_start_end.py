from arm.logicnode.arm_nodes import *

class GetCameraStartEndNode(ArmLogicTreeNode):
    """Returns the Start & End of the given camera.

    @seeNode Set Camera Start & End"""
    bl_idname = 'LNGetCameraStartEndNode'
    bl_label = 'Get Camera Start End'
    arm_version = 1
    
    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Camera')

        self.add_output('ArmFloatSocket', 'Start')
        self.add_output('ArmFloatSocket', 'End')