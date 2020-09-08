from arm.logicnode.arm_nodes import *

class ArrayRemoveNode(ArmLogicTreeNode):
    """Array remove node"""
    bl_idname = 'LNArrayRemoveNode'
    bl_label = 'Array Remove'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('NodeSocketInt', 'Index')
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('NodeSocketShader', 'Value')

add_node(ArrayRemoveNode, category=MODULE_AS_CATEGORY)
