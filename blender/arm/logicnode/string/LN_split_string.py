from arm.logicnode.arm_nodes import *

class SplitStringNode(ArmLogicTreeNode):
    """Use to split a string."""
    bl_idname = 'LNSplitStringNode'
    bl_label = 'Split String'
    arm_version = 1

    def init(self, context):
        super(SplitStringNode, self).init(context)
        self.add_output('ArmNodeSocketArray', 'Array')
        self.add_input('NodeSocketString', 'String')
        self.add_input('NodeSocketString', 'Split')

add_node(SplitStringNode, category=PKG_AS_CATEGORY)
