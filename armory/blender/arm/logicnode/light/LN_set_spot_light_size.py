from arm.logicnode.arm_nodes import *

class SetSpotLightSizeNode(ArmLogicTreeNode):
    """Sets the size of the given spot light."""
    bl_idname = 'LNSetSpotLightSizeNode'
    bl_label = 'Set Spot Light Size'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Light')
        self.add_input('ArmFloatSocket', 'Size')

        self.add_output('ArmNodeSocketAction', 'Out')
