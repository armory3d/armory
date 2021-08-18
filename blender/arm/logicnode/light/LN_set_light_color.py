from arm.logicnode.arm_nodes import *

class SetLightColorNode(ArmLogicTreeNode):
    """Sets the color of the given light."""
    bl_idname = 'LNSetLightColorNode'
    bl_label = 'Set Light Color'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Light')
        self.add_input('ArmColorSocket', 'Color', default_value=[1.0, 1.0, 1.0, 1.0])

        self.add_output('ArmNodeSocketAction', 'Out')
