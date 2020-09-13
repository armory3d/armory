from arm.logicnode.arm_nodes import *

class ResumeTraitNode(ArmLogicTreeNode):
    """Resume trait node"""
    bl_idname = 'LNResumeTraitNode'
    bl_label = 'Resume Trait'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketShader', 'Trait')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(ResumeTraitNode, category=PKG_AS_CATEGORY)
