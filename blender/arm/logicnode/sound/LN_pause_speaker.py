from arm.logicnode.arm_nodes import *

class PauseSpeakerNode(ArmLogicTreeNode):
    """Pause speaker node"""
    bl_idname = 'LNPauseSoundNode'
    bl_label = 'Pause Speaker'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Speaker')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(PauseSpeakerNode, category=PKG_AS_CATEGORY)
