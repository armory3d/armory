from arm.logicnode.arm_nodes import *

class GetTraitPausedNode(ArmLogicTreeNode):
    """Returns whether the given trait is paused."""
    bl_idname = 'LNGetTraitPausedNode'
    bl_label = 'Get Trait Paused'
    arm_version = 1

    def init(self, context):
        super(GetTraitPausedNode, self).init(context)
        self.add_input('NodeSocketShader', 'Trait')

        self.add_output('NodeSocketBool', 'Is Paused')
