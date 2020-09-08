from arm.logicnode.arm_nodes import *

class HasContactArrayNode(ArmLogicTreeNode):
    """Has contact array node"""
    bl_idname = 'LNHasContactArrayNode'
    bl_label = 'Has Contact Array'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object 1')
        self.add_input('ArmNodeSocketArray', 'Objects')
        self.add_output('NodeSocketBool', 'Bool')

add_node(HasContactArrayNode, category=MODULE_AS_CATEGORY, section='contact')
