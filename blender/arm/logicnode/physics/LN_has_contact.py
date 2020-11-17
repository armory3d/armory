from arm.logicnode.arm_nodes import *

class HasContactNode(ArmLogicTreeNode):
    """Returns whether the given rigid body has contact with another given rigid body."""
    bl_idname = 'LNHasContactNode'
    bl_label = 'Has Contact'
    arm_section = 'contact'
    arm_version = 1

    def init(self, context):
        super(HasContactNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'RB 1')
        self.add_input('ArmNodeSocketObject', 'RB 2')

        self.add_output('NodeSocketBool', 'Has Contact')
