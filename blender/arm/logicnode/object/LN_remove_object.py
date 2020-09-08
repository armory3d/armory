from arm.logicnode.arm_nodes import *

class RemoveObjectNode(ArmLogicTreeNode):
    """Remove object node"""
    bl_idname = 'LNRemoveObjectNode'
    bl_label = 'Remove Object'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(RemoveObjectNode, category=MODULE_AS_CATEGORY)
