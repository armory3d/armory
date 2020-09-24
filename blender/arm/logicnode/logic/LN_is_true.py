from arm.logicnode.arm_nodes import *

class IsTrueNode(ArmLogicTreeNode):
    """Runs the output if the input value is true."""
    bl_idname = 'LNIsTrueNode'
    bl_label = 'Is True'
    arm_version = 1

    def init(self, context):
        super(IsTrueNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketBool', 'Bool')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(IsTrueNode, category=PKG_AS_CATEGORY)
