from arm.logicnode.arm_nodes import *

class ShowMouseNode(ArmLogicTreeNode):
    """Deprecated. Is recommended to use 'Set Cursor State' node instead."""
    bl_idname = 'LNShowMouseNode'
    bl_label = 'Set Mouse Visible'
    arm_version = 1

    def init(self, context):
        super(ShowMouseNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketBool', 'Show')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(ShowMouseNode, category=PKG_AS_CATEGORY, section='mouse')
