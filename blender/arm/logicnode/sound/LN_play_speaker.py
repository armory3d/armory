from arm.logicnode.arm_nodes import *

class PlaySpeakerNode(ArmLogicTreeNode):
    """Use to play a speaker."""
    bl_idname = 'LNPlaySoundNode'
    bl_label = 'Play Speaker'
    arm_version = 1

    def init(self, context):
        super(PlaySpeakerNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Speaker')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(PlaySpeakerNode, category=PKG_AS_CATEGORY)
