from arm.logicnode.arm_nodes import *

class PlayTilesheetNode(ArmLogicTreeNode):
    """Plays the given tilesheet action."""
    bl_idname = 'LNPlayTilesheetNode'
    bl_label = 'Play Tilesheet'
    arm_version = 1
    arm_section = 'tilesheet'

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmStringSocket', 'Name')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketAction', 'Done')
