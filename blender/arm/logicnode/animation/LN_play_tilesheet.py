from arm.logicnode.arm_nodes import *

class PlayTilesheetNode(ArmLogicTreeNode):
    """Play tilesheet node"""
    bl_idname = 'LNPlayTilesheetNode'
    bl_label = 'Play Tilesheet'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketString', 'Action')
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketAction', 'Done')

add_node(PlayTilesheetNode, category=MODULE_AS_CATEGORY, section='tilesheet')
