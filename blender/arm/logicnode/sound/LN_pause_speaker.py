from arm.logicnode.arm_nodes import *

class PauseSpeakerNode(ArmLogicTreeNode):
    """Pauses playback of a speaker object, the playback will be resumed
    at the paused position.

    @seeNode Play Speaker
    @seeNode Stop Speaker
    """
    bl_idname = 'LNPauseSoundNode'
    bl_label = 'Pause Speaker'
    arm_version = 1

    def init(self, context):
        super(PauseSpeakerNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Speaker')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(PauseSpeakerNode, category=PKG_AS_CATEGORY)
