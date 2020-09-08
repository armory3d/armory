from arm.logicnode.arm_nodes import *

class ArraySetNode(ArmLogicTreeNode):
    """Array set node"""
    bl_idname = 'LNArraySetNode'
    bl_label = 'Array Set'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('NodeSocketInt', 'Index')
        self.add_input('NodeSocketShader', 'Value')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(ArraySetNode, category=MODULE_AS_CATEGORY)
