from arm.logicnode.arm_nodes import *

class SetMaterialValueParamNode(ArmLogicTreeNode):
    """Set material value param node"""
    bl_idname = 'LNSetMaterialValueParamNode'
    bl_label = 'Set Material Value Param'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketShader', 'Material')
        self.add_input('NodeSocketString', 'Node')
        self.add_input('NodeSocketFloat', 'Value')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetMaterialValueParamNode, category=MODULE_AS_CATEGORY, section='params')
