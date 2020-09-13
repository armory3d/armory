from arm.logicnode.arm_nodes import *

class ShowMouseNode(ArmLogicTreeNode):
    """Show Mouse node"""
    bl_idname = 'LNShowMouseNode'
    bl_label = 'Show Mouse'
    arm_version = 1

    def init(self, context):
        super(ShowMouseNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketBool', 'Show')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(ShowMouseNode, category=PKG_AS_CATEGORY, section='mouse')
