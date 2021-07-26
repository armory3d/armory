from arm.logicnode.arm_nodes import *

class ReadStorageNode(ArmLogicTreeNode):
    """Reads a stored content.

    @seeNode Write Storage"""
    bl_idname = 'LNReadStorageNode'
    bl_label = 'Read Storage'
    arm_section = 'file'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmStringSocket', 'Key')
        self.add_input('ArmStringSocket', 'Default')

        self.add_output('ArmDynamicSocket', 'Value')
