from arm.logicnode.arm_nodes import *

class CreateCollectionNode(ArmLogicTreeNode):
    """Creates a collection."""
    bl_idname = 'LNAddGroupNode'
    bl_label = 'Create Collection'
    arm_section = 'collection'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Collection')
        self.add_input('ArmNodeSocketArray', 'Objects')

        self.add_output('ArmNodeSocketAction', 'Out')
