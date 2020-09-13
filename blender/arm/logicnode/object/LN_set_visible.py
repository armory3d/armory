from arm.logicnode.arm_nodes import *

class SetVisibleNode(ArmLogicTreeNode):
    """Set visible node"""
    bl_idname = 'LNSetVisibleNode'
    bl_label = 'Set Visible'
    arm_version = 1

    def init(self, context):
        super(SetVisibleNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketBool', 'Visible')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetVisibleNode, category=PKG_AS_CATEGORY, section='props')
