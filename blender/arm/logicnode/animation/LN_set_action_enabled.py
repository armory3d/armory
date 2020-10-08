from arm.logicnode.arm_nodes import *

class SetActionEnabledNode(ArmLogicTreeNode):
    """Sets the action enabled state of the given object."""
    bl_idname = 'LNSetActionEnabledNode'
    bl_label = 'Set Action Enabled'
    arm_version = 1

    def init(self, context):
        super(SetActionEnabledNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmNodeSocketBool', 'Enabled')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetActionEnabledNode, category=PKG_AS_CATEGORY, section='action')
