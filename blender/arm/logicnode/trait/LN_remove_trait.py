from arm.logicnode.arm_nodes import *

class RemoveTraitNode(ArmLogicTreeNode):
    """Removes the given trait."""
    bl_idname = 'LNRemoveTraitNode'
    bl_label = 'Remove Trait'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmDynamicSocket', 'Trait')

        self.add_output('ArmNodeSocketAction', 'Out')
