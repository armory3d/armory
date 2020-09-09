from arm.logicnode.arm_nodes import *

class CreateCollectionNode(ArmLogicTreeNode):
    """Add Group node"""
    bl_idname = 'LNAddGroupNode'
    bl_label = 'Create Collection'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Collection')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(CreateCollectionNode, category=PKG_AS_CATEGORY, section='collection')
