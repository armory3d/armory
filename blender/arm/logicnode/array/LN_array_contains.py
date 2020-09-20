from arm.logicnode.arm_nodes import *

class ArrayContainsNode(ArmLogicTreeNode):
    """Array contains node"""
    bl_idname = 'LNArrayInArrayNode'
    bl_label = 'Array Contains'
    arm_version = 1

    def init(self, context):
        super(ArrayContainsNode, self).init(context)
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('NodeSocketShader', 'Value')
        self.add_output('NodeSocketBool', 'Contains')

add_node(ArrayContainsNode, category=PKG_AS_CATEGORY)
