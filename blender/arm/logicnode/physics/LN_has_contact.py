from arm.logicnode.arm_nodes import *

class HasContactNode(ArmLogicTreeNode):
    """Use to get if a rigid body has contact with another rigid body."""
    bl_idname = 'LNHasContactNode'
    bl_label = 'Has Contact'
    arm_version = 1

    def init(self, context):
        super(HasContactNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'Rigid Body 1')
        self.add_input('ArmNodeSocketObject', 'Rigid Body 2')
        self.add_output('NodeSocketBool', 'Has Contact')

add_node(HasContactNode, category=PKG_AS_CATEGORY, section='contact')
