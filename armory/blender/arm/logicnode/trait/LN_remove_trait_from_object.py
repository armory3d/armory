from arm.logicnode.arm_nodes import *

class RemoveTraitObjectNode(ArmLogicTreeNode):
    """Remove trait from the given object."""
    bl_idname = 'LNRemoveTraitObjectNode'
    bl_label = 'Remove Trait from Object'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmStringSocket', 'Trait')

        self.add_output('ArmNodeSocketAction', 'Out')
