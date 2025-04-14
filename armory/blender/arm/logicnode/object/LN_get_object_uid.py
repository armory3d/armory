from arm.logicnode.arm_nodes import *

class GetUidNode(ArmLogicTreeNode):
    """Returns the uid of the given object."""
    bl_idname = 'LNGetUidNode'
    bl_label = 'Get Object Uid'
    arm_section = 'props'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')

        self.add_output('ArmIntSocket', 'Uid')
