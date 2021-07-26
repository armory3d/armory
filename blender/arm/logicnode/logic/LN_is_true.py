from arm.logicnode.arm_nodes import *

class IsTrueNode(ArmLogicTreeNode):
    """Passes through its activation only if the plugged-in boolean
    equals `true`.

    @seeNode Is False"""
    bl_idname = 'LNIsTrueNode'
    bl_label = 'Is True'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmBoolSocket', 'Bool')

        self.add_output('ArmNodeSocketAction', 'Out')
