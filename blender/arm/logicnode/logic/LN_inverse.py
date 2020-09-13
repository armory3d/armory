from arm.logicnode.arm_nodes import *


class InverseNode(ArmLogicTreeNode):
    """Inverse node"""
    bl_idname = 'LNInverseNode'
    bl_label = 'Inverse'
    arm_version = 1

    def init(self, context):
        super(InverseNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_output('ArmNodeSocketAction', 'Out')


add_node(InverseNode, category=PKG_AS_CATEGORY, section='flow')
