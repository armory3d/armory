from arm.logicnode.arm_nodes import *

class SetMaterialRgbParamNode(ArmLogicTreeNode):
    """Set material rgb param node"""
    bl_idname = 'LNSetMaterialRgbParamNode'
    bl_label = 'Set Material RGB Param'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketShader', 'Material')
        self.add_input('NodeSocketString', 'Node')
        self.add_input('NodeSocketColor', 'Color')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetMaterialRgbParamNode, category=PKG_AS_CATEGORY, section='params')
