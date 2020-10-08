from arm.logicnode.arm_nodes import *

class SetTraitEnabledNode(ArmLogicTreeNode):
    """Sets the enabled state of the given trait."""
    bl_idname = 'LNSetTraitEnabledNode'
    bl_label = 'Set Trait Enabled'
    arm_version = 1

    def init(self, context):
        super(SetTraitEnabledNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketShader', 'Trait')
        self.add_input('NodeSocketBool', 'Enabled')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetTraitEnabledNode, category=PKG_AS_CATEGORY)
