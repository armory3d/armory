from arm.logicnode.arm_nodes import *

class SetLightStrengthNode(ArmLogicTreeNode):
    """Set light strength node"""
    bl_idname = 'LNSetLightStrengthNode'
    bl_label = 'Set Light Strength'
    arm_version = 1

    def init(self, context):
        super(SetLightStrengthNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketFloat', 'Strength', default_value=100)
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetLightStrengthNode, category=PKG_AS_CATEGORY)
