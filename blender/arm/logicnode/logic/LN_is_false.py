from arm.logicnode.arm_nodes import *


class IsFalseNode(ArmLogicTreeNode):
    """Passes through its activation only if the plugged-in boolean
    equals `false`.

    @seeNode Is True"""
    bl_idname = 'LNIsFalseNode'
    bl_label = 'Is False'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmBoolSocket', 'Bool')

        self.add_output('ArmNodeSocketAction', 'Out')
