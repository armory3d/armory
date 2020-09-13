from arm.logicnode.arm_nodes import *

class OnInitNode(ArmLogicTreeNode):
    """On init node"""
    bl_idname = 'LNOnInitNode'
    bl_label = 'On Init'

    def init(self, context):
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(OnInitNode, category=PKG_AS_CATEGORY)
