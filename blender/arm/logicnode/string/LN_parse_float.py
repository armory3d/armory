from arm.logicnode.arm_nodes import *

class ParseFloatNode(ArmLogicTreeNode):
    """Parse float node"""
    bl_idname = 'LNParseFloatNode'
    bl_label = 'Parse float'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_output('NodeSocketFloat', 'Float')
        self.add_input('NodeSocketString', 'String')

add_node(ParseFloatNode, category=MODULE_AS_CATEGORY)
