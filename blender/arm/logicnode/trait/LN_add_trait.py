from arm.logicnode.arm_nodes import *

class AddTraitNode(ArmLogicTreeNode):
    """Add trait node"""
    bl_idname = 'LNAddTraitNode'
    bl_label = 'Add Trait'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketShader', 'Trait')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(AddTraitNode, category=MODULE_AS_CATEGORY)
