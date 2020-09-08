from arm.logicnode.arm_nodes import *

class GlobalObjectNode(ArmLogicTreeNode):
    """Global object node"""
    bl_idname = 'LNGlobalObjectNode'
    bl_label = 'Global Object'

    def init(self, context):
        self.add_output('ArmNodeSocketObject', 'Object')

add_node(GlobalObjectNode, category=MODULE_AS_CATEGORY)
