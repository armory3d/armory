from arm.logicnode.arm_nodes import *

class GetObjectGroupNode(ArmLogicTreeNode):
    """Get Object collection."""
    bl_idname = 'LNGetObjectGroupNode'
    bl_label = 'Get Object Collection'
    arm_section = 'collection'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')

        self.add_output('ArmStringSocket', 'Collection')
