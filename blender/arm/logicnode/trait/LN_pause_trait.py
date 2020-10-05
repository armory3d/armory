from arm.logicnode.arm_nodes import *

class PauseTraitNode(ArmLogicTreeNode):
    """Pauses the given trait."""
    bl_idname = 'LNPauseTraitNode'
    bl_label = 'Pause Trait'
    arm_version = 1

    def init(self, context):
        super(PauseTraitNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketShader', 'Trait')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(PauseTraitNode, category=PKG_AS_CATEGORY)
