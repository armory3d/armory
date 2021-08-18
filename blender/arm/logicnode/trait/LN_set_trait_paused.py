from arm.logicnode.arm_nodes import *

class SetTraitPausedNode(ArmLogicTreeNode):
    """Sets the paused state of the given trait."""
    bl_idname = 'LNSetTraitPausedNode'
    bl_label = 'Set Trait Paused'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmDynamicSocket', 'Trait')
        self.add_input('ArmBoolSocket', 'Paused')

        self.add_output('ArmNodeSocketAction', 'Out')
