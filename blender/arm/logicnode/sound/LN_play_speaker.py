from arm.logicnode.arm_nodes import *

class PlaySpeakerNode(ArmLogicTreeNode):
    """Starts the playback of a speaker object. If the playback was
    paused it is resumed from the paused position.

    @seeNode Pause Speaker
    @seeNode Play Speaker
    """
    bl_idname = 'LNPlaySoundNode'
    bl_label = 'Play Speaker'
    arm_version = 1

    def init(self, context):
        super(PlaySpeakerNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Speaker')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(PlaySpeakerNode, category=PKG_AS_CATEGORY)
