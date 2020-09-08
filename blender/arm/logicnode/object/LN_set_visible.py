from arm.logicnode.arm_nodes import *

class SetVisibleNode(ArmLogicTreeNode):
    """Set visible node"""
    bl_idname = 'LNSetVisibleNode'
    bl_label = 'Set Visible'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketBool', 'Bool')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetVisibleNode, category=MODULE_AS_CATEGORY, section='props')
