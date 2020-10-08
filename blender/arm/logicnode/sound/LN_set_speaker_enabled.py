from arm.logicnode.arm_nodes import *

class SetSpeakerEnabledNode(ArmLogicTreeNode):
    """Sets the enabled (play/pause) state of the given speaker.

    @seeNode Stop Speaker
    @seeNode Play Sound
    """
    bl_idname = 'LNSetSpeakerEnabledNode'
    bl_label = 'Set Speaker Enabled'
    arm_version = 1

    def init(self, context):
        super(SetSpeakerEnabledSpeakerNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Speaker')
        self.add_input('NodeSocketBool', 'Enabled')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetSpeakerEnabledNode, category=PKG_AS_CATEGORY)
