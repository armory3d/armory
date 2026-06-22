from arm.logicnode.arm_nodes import *

class SetTilesheetFrame(ArmLogicTreeNode):
    """Set the frame of the current tilesheet action.
    @input Frame: Frame offset to set with 0 as the first frame of the active action.
    """
    bl_idname = 'LNSetTilesheetFrameNode'
    bl_label = 'Set Tilesheet Frame'
    arm_version = 1
    arm_section = 'tilesheet'

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmIntSocket', 'Frame')

        self.add_output('ArmNodeSocketAction', 'Out')
