from arm.logicnode.arm_nodes import *

class GetTransformNode(ArmLogicTreeNode):
    """Get transform node"""
    bl_idname = 'LNGetTransformNode'
    bl_label = 'Get Transform'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('NodeSocketShader', 'Transform')

add_node(GetTransformNode, category=MODULE_AS_CATEGORY)
