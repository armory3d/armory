from arm.logicnode.arm_nodes import *

class RemoveGroupNode(ArmLogicTreeNode):
    """Remove Group node"""
    bl_idname = 'LNRemoveGroupNode'
    bl_label = 'Remove Collection'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Collection')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(RemoveGroupNode, category=MODULE_AS_CATEGORY, section='collection')
