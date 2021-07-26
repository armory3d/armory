from arm.logicnode.arm_nodes import *

class GetTilesheetStateNode(ArmLogicTreeNode):
    """Returns the information about the current tilesheet of the given object."""
    bl_idname = 'LNGetTilesheetStateNode'
    bl_label = 'Get Tilesheet State'
    arm_version = 1
    arm_section = 'tilesheet'

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')

        self.add_output('ArmStringSocket', 'Name')
        self.add_output('ArmIntSocket', 'Frame')
        self.add_output('ArmBoolSocket', 'Is Paused')
