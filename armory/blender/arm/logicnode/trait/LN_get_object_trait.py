from arm.logicnode.arm_nodes import *

class GetTraitNode(ArmLogicTreeNode):
    """Searches for a trait with the specified name which is applied to the
    given object and returns that trait."""
    bl_idname = 'LNGetTraitNode'
    bl_label = 'Get Object Trait'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('ArmStringSocket', 'Name')

        self.add_output('ArmDynamicSocket', 'Trait')
