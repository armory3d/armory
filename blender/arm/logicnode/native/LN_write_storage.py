from arm.logicnode.arm_nodes import *

class WriteStorageNode(ArmLogicTreeNode):
    """Writes the given content in the given key.

    @seeNode Read Storage"""
    bl_idname = 'LNWriteStorageNode'
    bl_label = 'Write Storage'
    arm_section = 'file'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'Key')
        self.add_input('ArmDynamicSocket', 'Value')

        self.add_output('ArmNodeSocketAction', 'Out')
