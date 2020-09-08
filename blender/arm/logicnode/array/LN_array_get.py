from arm.logicnode.arm_nodes import *

class ArrayGetNode(ArmLogicTreeNode):
    """Array get node"""
    bl_idname = 'LNArrayGetNode'
    bl_label = 'Array Get'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('NodeSocketInt', 'Index')
        self.add_output('NodeSocketShader', 'Value')

add_node(ArrayGetNode, category=MODULE_AS_CATEGORY)
