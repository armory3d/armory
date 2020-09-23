from arm.logicnode.arm_nodes import *

class ToBoolNode(ArmLogicTreeNode):
    """Convert an output to boolean. If the output is running, the boolean is true; if not, the boolean is false."""
    bl_idname = 'LNToBoolNode'
    bl_label = 'To Bool'
    arm_version = 1

    def init(self, context):
        super(ToBoolNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_output('NodeSocketBool', 'Bool')

add_node(ToBoolNode, category=PKG_AS_CATEGORY)
