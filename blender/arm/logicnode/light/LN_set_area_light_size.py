from arm.logicnode.arm_nodes import *

class SetAreaLightSizeNode(ArmLogicTreeNode):
    """Sets the size of the given area light."""
    bl_idname = 'LNSetAreaLightSizeNode'
    bl_label = 'Set Area Light Size'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Light')
        self.add_input('ArmFloatSocket', 'Size X')
        self.add_input('ArmFloatSocket', 'Size Y')

        self.add_output('ArmNodeSocketAction', 'Out')
