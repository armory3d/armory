from arm.logicnode.arm_nodes import *

class ArraySpliceNode(ArmLogicTreeNode):
    """Array splice node"""
    bl_idname = 'LNArraySpliceNode'
    bl_label = 'Array Splice'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('NodeSocketInt', 'Index')
        self.add_input('NodeSocketInt', 'Length')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(ArraySpliceNode, category=PKG_AS_CATEGORY)
