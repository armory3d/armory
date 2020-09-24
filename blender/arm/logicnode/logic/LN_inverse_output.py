from arm.logicnode.arm_nodes import *


class InverseNode(ArmLogicTreeNode):
    """Runs the output only if the connected input is not running."""
    bl_idname = 'LNInverseNode'
    bl_label = 'Inverse Output'
    arm_version = 1

    def init(self, context):
        super(InverseNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_output('ArmNodeSocketAction', 'Out')


add_node(InverseNode, category=PKG_AS_CATEGORY, section='flow')
