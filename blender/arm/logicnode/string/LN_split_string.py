from arm.logicnode.arm_nodes import *

class SplitStringNode(ArmLogicTreeNode):
    """Split string node"""
    bl_idname = 'LNSplitStringNode'
    bl_label = 'Split String'

    def init(self, context):
        self.add_output('ArmNodeSocketArray', 'Array')
        self.add_input('NodeSocketString', 'String')
        self.add_input('NodeSocketString', 'Split')

add_node(SplitStringNode, category=PKG_AS_CATEGORY)
