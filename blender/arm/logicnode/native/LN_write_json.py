from arm.logicnode.arm_nodes import *

class WriteJsonNode(ArmLogicTreeNode):
    """Writes the given content in the given JSON file.

    @seeNode Read JSON"""
    bl_idname = 'LNWriteJsonNode'
    bl_label = 'Write JSON'
    arm_section = 'file'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'File')
        self.add_input('ArmDynamicSocket', 'Dynamic')
