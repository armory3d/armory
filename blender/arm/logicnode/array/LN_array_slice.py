from arm.logicnode.arm_nodes import *

class ArraySliceNode(ArmLogicTreeNode):
    """Array slice node"""
    bl_idname = 'LNArraySliceNode'
    bl_label = 'Array Slice'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('NodeSocketInt', 'Index')
        self.add_input('NodeSocketInt', 'End')
        self.add_output('ArmNodeSocketArray', 'Array')

add_node(ArraySliceNode, category=MODULE_AS_CATEGORY)
