from arm.logicnode.arm_nodes import *

class VectorClampToSizeNode(ArmLogicTreeNode):
    """Vector clamp to size node"""
    bl_idname = 'LNVectorClampToSizeNode'
    bl_label = 'Vector Clamp To Size'

    def init(self, context):
        self.add_input('NodeSocketVector', 'Vector', default_value=[0.5, 0.5, 0.5])
        self.add_input('NodeSocketFloat', 'Min')
        self.add_input('NodeSocketFloat', 'Max')
        self.add_output('NodeSocketVector', 'Vector')

add_node(VectorClampToSizeNode, category=MODULE_AS_CATEGORY, section='vector')
