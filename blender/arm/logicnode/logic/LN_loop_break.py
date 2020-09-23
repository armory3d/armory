from arm.logicnode.arm_nodes import *

class LoopBreakNode(ArmLogicTreeNode):
    """TO DO."""
    bl_idname = 'LNLoopBreakNode'
    bl_label = 'Loop Break'
    arm_version = 1

    def init(self, context):
        super(LoopBreakNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')

add_node(LoopBreakNode, category=PKG_AS_CATEGORY, section='flow')
