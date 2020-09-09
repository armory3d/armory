from arm.logicnode.arm_nodes import *

class HasContactNode(ArmLogicTreeNode):
    """Has contact node"""
    bl_idname = 'LNHasContactNode'
    bl_label = 'Has Contact'

    def init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object 1')
        self.add_input('ArmNodeSocketObject', 'Object 2')
        self.add_output('NodeSocketBool', 'Bool')

add_node(HasContactNode, category=PKG_AS_CATEGORY, section='contact')
