from arm.logicnode.arm_nodes import *

class PlayTilesheetNode(ArmLogicTreeNode):
    """Plays the given tilesheet action."""
    bl_idname = 'LNPlayTilesheetNode'
    bl_label = 'Play Tilesheet'
    arm_version = 1

    def init(self, context):
        super(PlayTilesheetNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketString', 'Action')
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketAction', 'Done')

add_node(PlayTilesheetNode, category=PKG_AS_CATEGORY, section='tilesheet')
