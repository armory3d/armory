from arm.logicnode.arm_nodes import *

class GetNameNode(ArmLogicTreeNode):
    """Returns the name of the given object."""
    bl_idname = 'LNGetNameNode'
    bl_label = 'Get Object Name'
    arm_section = 'props'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')

        self.add_output('ArmStringSocket', 'Name')
