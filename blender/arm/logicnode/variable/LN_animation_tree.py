from arm.logicnode.arm_nodes import *

class AnimTreeNode(ArmLogicVariableNodeMixin, ArmLogicTreeNode):
    """Stores the given animation tree as a variable."""
    bl_idname = 'LNAnimTreeNode'
    bl_label = 'Animation Tree'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAnimTree', 'Action')

        self.add_output('ArmNodeSocketAnimTree', 'Action', is_var=True)
