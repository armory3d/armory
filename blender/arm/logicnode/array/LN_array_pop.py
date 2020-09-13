from arm.logicnode.arm_nodes import *

class ArrayPopNode(ArmLogicTreeNode):
    """Array pop node"""
    bl_idname = 'LNArrayPopNode'
    bl_label = 'Array Pop'
    arm_version = 1

    def init(self, context):
        super(ArrayPopNode, self).init(context)
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_output('NodeSocketShader', 'Value')

add_node(ArrayPopNode, category=PKG_AS_CATEGORY)
