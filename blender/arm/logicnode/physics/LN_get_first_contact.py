from arm.logicnode.arm_nodes import *

class GetFirstContactNode(ArmLogicTreeNode):
    """Get first contact node"""
    bl_idname = 'LNGetFirstContactNode'
    bl_label = 'Get First Contact'

    def init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('ArmNodeSocketObject', 'Object')

add_node(GetFirstContactNode, category=MODULE_AS_CATEGORY, section='contact')
