from arm.logicnode.arm_nodes import *

class SetMaterialRgbParamNode(ArmLogicTreeNode):
    """TO DO."""
    bl_idname = 'LNSetMaterialRgbParamNode'
    bl_label = 'Set Material RGB Param'
    arm_section = 'params'
    arm_version = 1

    def init(self, context):
        super(SetMaterialRgbParamNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketShader', 'Material')
        self.add_input('NodeSocketString', 'Node')
        self.add_input('NodeSocketColor', 'Color')

        self.add_output('ArmNodeSocketAction', 'Out')
