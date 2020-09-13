from arm.logicnode.arm_nodes import *

class SetLightColorNode(ArmLogicTreeNode):
    """Set light color node"""
    bl_idname = 'LNSetLightColorNode'
    bl_label = 'Set Light Color'
    arm_version = 1

    def init(self, context):
        super(SetLightColorNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketColor', 'Color', default_value=[1.0, 1.0, 1.0, 1.0])
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetLightColorNode, category=PKG_AS_CATEGORY)
