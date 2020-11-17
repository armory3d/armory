from arm.logicnode.arm_nodes import *

class CreateCollectionNode(ArmLogicTreeNode):
    """Creates a collection."""
    bl_idname = 'LNAddGroupNode'
    bl_label = 'Create Collection'
    arm_section = 'collection'
    arm_version = 1

    def init(self, context):
        super(CreateCollectionNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Collection')

        self.add_output('ArmNodeSocketAction', 'Out')
