from arm.logicnode.arm_nodes import *

class PlaySpeakerNode(ArmLogicTreeNode):
    """Play speaker node"""
    bl_idname = 'LNPlaySoundNode'
    bl_label = 'Play Speaker'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Speaker')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(PlaySpeakerNode, category=MODULE_AS_CATEGORY)
