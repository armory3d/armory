from arm.logicnode.arm_nodes import *

class SelfTraitNode(ArmLogicTreeNode):
    """Self trait node"""
    bl_idname = 'LNSelfTraitNode'
    bl_label = 'Self Trait'

    def init(self, context):
        self.add_output('NodeSocketShader', 'Trait')

add_node(SelfTraitNode, category=MODULE_AS_CATEGORY)
