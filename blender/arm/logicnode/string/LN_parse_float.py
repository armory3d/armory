from arm.logicnode.arm_nodes import *

class ParseFloatNode(ArmLogicTreeNode):
    """Parse float node"""
    bl_idname = 'LNParseFloatNode'
    bl_label = 'Parse Float'
    arm_version = 1

    def init(self, context):
        super(ParseFloatNode, self).init(context)
        self.add_output('NodeSocketFloat', 'Float')
        self.add_input('NodeSocketString', 'String')

add_node(ParseFloatNode, category=PKG_AS_CATEGORY, section='parse')
