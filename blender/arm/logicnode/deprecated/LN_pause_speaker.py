from arm.logicnode.arm_nodes import *

class PauseSpeakerNode(ArmLogicTreeNode):
    """Pauses playback of the given speaker object. The playback will be resumed
    at the paused position.

    @seeNode Play Speaker
    @seeNode Stop Speaker
    """
    bl_idname = 'LNPauseSoundNode'
    bl_label = 'Pause Speaker'
    bl_description = "Please use the \"Set Speaker Enabled\" node instead"
    bl_icon='ERROR'
    arm_version = 2

    def init(self, context):
        super(PauseSpeakerNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Speaker')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(PauseSpeakerNode, category=PKG_AS_CATEGORY, is_obsolete=True)
