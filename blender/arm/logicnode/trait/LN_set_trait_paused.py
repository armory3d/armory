from arm.logicnode.arm_nodes import *

class SetTraitPausedNode(ArmLogicTreeNode):
    """Sets the paused state of the given trait."""
    bl_idname = 'LNSetTraitPausedNode'
    bl_label = 'Set Trait Paused'
    arm_version = 1

    def init(self, context):
        super(SetTraitPausedNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketShader', 'Trait')
        self.add_input('NodeSocketBool', 'Paused')
        self.add_output('ArmNodeSocketAction', 'Out')
