from arm.logicnode.arm_nodes import *


class BranchNode(ArmLogicTreeNode):
    """Runs the output True if the condition is true and the output False if the condition is false."""
    bl_idname = 'LNBranchNode'
    bl_label = 'Branch'
    arm_version = 1

    def init(self, context):
        super(BranchNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketBool', 'Bool')
        self.add_output('ArmNodeSocketAction', 'True')
        self.add_output('ArmNodeSocketAction', 'False')


add_node(BranchNode, category=PKG_AS_CATEGORY)
