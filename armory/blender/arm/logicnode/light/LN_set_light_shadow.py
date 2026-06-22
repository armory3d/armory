from arm.logicnode.arm_nodes import *

class SetLightShadowNode(ArmLogicTreeNode):
    """Sets the shadow boolean of the given light."""
    bl_idname = 'LNSetLightShadowNode'
    bl_label = 'Set Light Shadow'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Light')
        self.add_input('ArmBoolSocket', 'Shadow')

        self.add_output('ArmNodeSocketAction', 'Out')
