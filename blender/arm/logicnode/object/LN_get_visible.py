from arm.logicnode.arm_nodes import *

class GetVisibleNode(ArmLogicTreeNode):
    """Get visible node"""
    bl_idname = 'LNGetVisibleNode'
    bl_label = 'Get Visible'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('NodeSocketBool', 'Visible')

add_node(GetVisibleNode, category=MODULE_AS_CATEGORY, section='props')
