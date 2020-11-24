from arm.logicnode.arm_nodes import *

class SetLightStrengthNode(ArmLogicTreeNode):
    """Sets the strenght of the given light."""
    bl_idname = 'LNSetLightStrengthNode'
    bl_label = 'Set Light Strength'
    arm_version = 1

    def init(self, context):
        super(SetLightStrengthNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Light')
        self.add_input('NodeSocketFloat', 'Strength', default_value=250)

        self.add_output('ArmNodeSocketAction', 'Out')
