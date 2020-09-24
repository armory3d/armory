from arm.logicnode.arm_nodes import *

class GetTraitNode(ArmLogicTreeNode):
    """Use to get a trait from an object."""
    bl_idname = 'LNGetTraitNode'
    bl_label = 'Get Trait'
    arm_version = 1

    def init(self, context):
        super(GetTraitNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketString', 'Name')
        self.add_output('NodeSocketShader', 'Trait')

add_node(GetTraitNode, category=PKG_AS_CATEGORY)
