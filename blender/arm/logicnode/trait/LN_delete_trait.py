from arm.logicnode.arm_nodes import *

class RemoveTraitNode(ArmLogicTreeNode):
    """Use to remove a trait."""
    bl_idname = 'LNRemoveTraitNode'
    bl_label = 'Delete Trait'
    arm_version = 1

    def init(self, context):
        super(RemoveTraitNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketShader', 'Trait')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(RemoveTraitNode, category=PKG_AS_CATEGORY)
