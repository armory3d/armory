from arm.logicnode.arm_nodes import *

class ActiveSceneNode(ArmLogicTreeNode):
    """Returns the active scene."""
    bl_idname = 'LNActiveSceneNode'
    bl_label = 'Get Scene Active'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmDynamicSocket', 'Scene')
