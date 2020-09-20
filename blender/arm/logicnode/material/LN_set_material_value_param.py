from arm.logicnode.arm_nodes import *

class SetMaterialValueParamNode(ArmLogicTreeNode):
    """Set material value param node"""
    bl_idname = 'LNSetMaterialValueParamNode'
    bl_label = 'Set Material Value Param'
    arm_version = 1

    def init(self, context):
        super(SetMaterialValueParamNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketShader', 'Material')
        self.add_input('NodeSocketString', 'Node')
        self.add_input('NodeSocketFloat', 'Float')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetMaterialValueParamNode, category=PKG_AS_CATEGORY, section='params')
