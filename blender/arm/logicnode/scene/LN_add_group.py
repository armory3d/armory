from arm.logicnode.arm_nodes import *

class AddGroupNode(ArmLogicTreeNode):
    """Add Group node"""
    bl_idname = 'LNAddGroupNode'
    bl_label = 'Add Collection'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Collection')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(AddGroupNode, category=MODULE_AS_CATEGORY, section='collection')
