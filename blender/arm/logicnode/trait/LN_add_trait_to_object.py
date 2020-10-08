from arm.logicnode.arm_nodes import *

class AddTraitNode(ArmLogicTreeNode):
    """Adds trait to the given object."""
    bl_idname = 'LNAddTraitNode'
    bl_label = 'Add Trait To Object'
    arm_version = 1

    def init(self, context):
        super(AddTraitNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketShader', 'Trait')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(AddTraitNode, category=PKG_AS_CATEGORY)
