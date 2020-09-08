from arm.logicnode.arm_nodes import *

class ArrayContainsNode(ArmLogicTreeNode):
    """Array contains node"""
    bl_idname = 'LNArrayInArrayNode'
    bl_label = 'Array Contains'

    def init(self, context):
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('NodeSocketShader', 'Value')
        self.add_output('NodeSocketBool', 'Bool')

add_node(ArrayContainsNode, category=MODULE_AS_CATEGORY)
