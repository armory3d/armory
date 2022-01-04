from arm.logicnode.arm_nodes import *

class RemoveObjectFromGroupNode(ArmLogicTreeNode):
    """Remove Object from a collection."""
    bl_idname = 'LNRemoveObjectFromGroupNode'
    bl_label = 'Remove Object from Collection'
    arm_section = 'collection'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Collection')
        self.add_input('ArmNodeSocketObject', 'Object')

        self.add_output('ArmNodeSocketAction', 'Out')
