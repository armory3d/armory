from arm.logicnode.arm_nodes import *

class SetMaterialImageParamNode(ArmLogicTreeNode):
    """Set material image param node"""
    bl_idname = 'LNSetMaterialImageParamNode'
    bl_label = 'Set Material Image Param'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketShader', 'Material')
        self.add_input('NodeSocketString', 'Node')
        self.add_input('NodeSocketString', 'Image')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetMaterialImageParamNode, category=PKG_AS_CATEGORY, section='params')
