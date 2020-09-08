from arm.logicnode.arm_nodes import *

class SeparateVectorNode(ArmLogicTreeNode):
    """Separate vector node"""
    bl_idname = 'LNSeparateVectorNode'
    bl_label = 'Separate XYZ'

    def init(self, context):
        self.add_input('NodeSocketVector', 'Vector')
        self.add_output('NodeSocketFloat', 'X')
        self.add_output('NodeSocketFloat', 'Y')
        self.add_output('NodeSocketFloat', 'Z')

add_node(SeparateVectorNode, category=MODULE_AS_CATEGORY, section='vector')
