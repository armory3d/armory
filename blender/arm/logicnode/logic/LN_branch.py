from arm.logicnode.arm_nodes import *


class BranchNode(ArmLogicTreeNode):
    """Activates its `true` or `false` output, according
    to the state of the plugged-in boolean."""
    bl_idname = 'LNBranchNode'
    bl_label = 'Branch'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmBoolSocket', 'Bool')

        self.add_output('ArmNodeSocketAction', 'True')
        self.add_output('ArmNodeSocketAction', 'False')
