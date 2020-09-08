from arm.logicnode.arm_nodes import *

class ArrayShiftNode(ArmLogicTreeNode):
    """Array shift node"""
    bl_idname = 'LNArrayShiftNode'
    bl_label = 'Array Shift'

    def init(self, context):
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_output('NodeSocketShader', 'Value')

add_node(ArrayShiftNode, category=MODULE_AS_CATEGORY)
