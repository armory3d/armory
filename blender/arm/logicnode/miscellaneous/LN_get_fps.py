from arm.logicnode.arm_nodes import *

class GetFPSNode(ArmLogicTreeNode):
    """Get the frames per second count."""
    bl_idname = 'LNGetFPSNode'
    bl_label = 'Get Frames Per Second'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmIntSocket', 'Count')
