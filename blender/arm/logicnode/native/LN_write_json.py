from arm.logicnode.arm_nodes import *


class WriteJsonNode(ArmLogicTreeNode):
    """Writes the given content to the given JSON file. If the file
    already exists, the existing content of the file is overwritten.

    > **This node is currently only implemented on Krom**

    @input File: the name of the file, relative to `Krom.getFilesLocation()`,
        including the file extension.
    @input Dynamic: the content to write to the file. Can be any type that can
        be serialized to JSON.

    @seeNode Read JSON
    """
    bl_idname = 'LNWriteJsonNode'
    bl_label = 'Write JSON'
    arm_section = 'file'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'File')
        self.add_input('ArmDynamicSocket', 'Dynamic')
