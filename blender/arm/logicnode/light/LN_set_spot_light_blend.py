from arm.logicnode.arm_nodes import *

class SetSpotLightBlendNode(ArmLogicTreeNode):
    """Sets the blend of the given spot light."""
    bl_idname = 'LNSetSpotLightBlendNode'
    bl_label = 'Set Spot Light Blend'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Light')
        self.add_input('ArmFloatSocket', 'Blend')

        self.add_output('ArmNodeSocketAction', 'Out')
