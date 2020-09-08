from arm.logicnode.arm_nodes import *

class SelfNode(ArmLogicTreeNode):
    """Self node"""
    bl_idname = 'LNSelfNode'
    bl_label = 'Self'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_output('ArmNodeSocketObject', 'Object')

add_node(SelfNode, category=MODULE_AS_CATEGORY)
