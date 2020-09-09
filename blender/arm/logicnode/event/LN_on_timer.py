from arm.logicnode.arm_nodes import *

class OnTimerNode(ArmLogicTreeNode):
    """On timer node"""
    bl_idname = 'LNOnTimerNode'
    bl_label = 'On Timer'

    def init(self, context):
        self.add_input('NodeSocketFloat', 'Duration')
        self.add_input('NodeSocketBool', 'Repeat')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(OnTimerNode, category=PKG_AS_CATEGORY)
