from arm.logicnode.arm_nodes import *

class GetTransformNode(ArmLogicTreeNode):
    """Get transform node"""
    bl_idname = 'LNGetTransformNode'
    bl_label = 'Get Transform'

    def init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('NodeSocketShader', 'Transform')

add_node(GetTransformNode, category=PKG_AS_CATEGORY)
