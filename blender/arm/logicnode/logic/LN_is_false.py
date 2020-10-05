from arm.logicnode.arm_nodes import *


class IsFalseNode(ArmLogicTreeNode):
    """Passes through its activation only if the plugged-in boolean
    equals `false`.

    @seeNode Is True"""
    bl_idname = 'LNIsFalseNode'
    bl_label = 'Is False'
    arm_version = 1

    def init(self, context):
        super(IsFalseNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketBool', 'Bool')
        self.add_output('ArmNodeSocketAction', 'Out')


add_node(IsFalseNode, category=PKG_AS_CATEGORY)
