from arm.logicnode.arm_nodes import *

class GetMaterialNode(ArmLogicTreeNode):
    """Get material node"""
    bl_idname = 'LNGetMaterialNode'
    bl_label = 'Get Material'

    def init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('NodeSocketShader', 'Material')

add_node(GetMaterialNode, category=PKG_AS_CATEGORY)
