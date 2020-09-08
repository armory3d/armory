from arm.logicnode.arm_nodes import *


class IsFalseNode(ArmLogicTreeNode):
    """Is False node"""
    bl_idname = 'LNIsFalseNode'
    bl_label = 'Is False'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketBool', 'Value')
        self.add_output('ArmNodeSocketAction', 'Out')


add_node(IsFalseNode, category=MODULE_AS_CATEGORY)
