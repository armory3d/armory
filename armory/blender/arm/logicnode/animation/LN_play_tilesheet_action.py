from arm.logicnode.arm_nodes import *

class PlayTilesheetActionNode(ArmLogicTreeNode):
    """Plays the given tilesheet action."""
    bl_idname = 'LNPlayTilesheetActionNode'
    bl_label = 'Play Tilesheet Action'
    arm_version = 1
    arm_section = 'tilesheet'

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmStringSocket', 'Action')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketAction', 'Done')
