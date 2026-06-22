from arm.logicnode.arm_nodes import *

class AddObjectToGroupNode(ArmLogicTreeNode):
    """Add Object to a collection."""
    bl_idname = 'LNAddObjectToGroupNode'
    bl_label = 'Add Object to Collection'
    arm_section = 'collection'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Collection')
        self.add_input('ArmNodeSocketObject', 'Object')

        self.add_output('ArmNodeSocketAction', 'Out')
