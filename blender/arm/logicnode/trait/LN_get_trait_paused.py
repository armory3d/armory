from arm.logicnode.arm_nodes import *

class GetTraitPausedNode(ArmLogicTreeNode):
    """Returns whether the given trait is paused."""
    bl_idname = 'LNGetTraitPausedNode'
    bl_label = 'Get Trait Paused'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmDynamicSocket', 'Trait')

        self.add_output('ArmBoolSocket', 'Is Paused')
