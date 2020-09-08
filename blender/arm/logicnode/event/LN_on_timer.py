from arm.logicnode.arm_nodes import *

class OnTimerNode(ArmLogicTreeNode):
    """On timer node"""
    bl_idname = 'LNOnTimerNode'
    bl_label = 'On Timer'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('NodeSocketFloat', 'Duration')
        self.add_input('NodeSocketBool', 'Repeat')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(OnTimerNode, category=MODULE_AS_CATEGORY)
