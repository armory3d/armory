from arm.logicnode.arm_nodes import *

class StopSpeakerNode(ArmLogicTreeNode):
    """Use to stop a speaker."""
    bl_idname = 'LNStopSoundNode'
    bl_label = 'Stop Speaker'
    arm_version = 1

    def init(self, context):
        super(StopSpeakerNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Speaker')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(StopSpeakerNode, category=PKG_AS_CATEGORY)
