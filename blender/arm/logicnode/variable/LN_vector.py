from arm.logicnode.arm_nodes import *

class VectorNode(ArmLogicTreeNode):
    """Vector node"""
    bl_idname = 'LNVectorNode'
    bl_label = 'Vector'

    def init(self, context):
        self.add_input('NodeSocketFloat', 'X')
        self.add_input('NodeSocketFloat', 'Y')
        self.add_input('NodeSocketFloat', 'Z')

        self.add_output('NodeSocketVector', 'Vector', is_var=True)

add_node(VectorNode, category=MODULE_AS_CATEGORY)
