from arm.logicnode.arm_nodes import *


class WriteFileNode(ArmLogicTreeNode):
    """Writes the given string content to the given file. If the file
    already exists, the existing content of the file is overwritten.

    > **This node is currently only implemented on Krom**

    @input File: the name of the file, relative to `Krom.getFilesLocation()`
    @input Content: the content to write to the file.

    @seeNode Read File
    """
    bl_idname = 'LNWriteFileNode'
    bl_label = 'Write File'
    arm_section = 'file'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'File')
        self.add_input('ArmStringSocket', 'Content')
