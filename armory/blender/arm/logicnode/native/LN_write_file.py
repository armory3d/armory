from arm.logicnode.arm_nodes import *


class WriteFileNode(ArmLogicTreeNode):
    """Writes the given string content to the given file. If the file
    already exists, the existing content of the file is overwritten.

    @input File: the name of the file, relative to `Krom.getFilesLocation()`
    @input Content: the content to write to the file.

    @seeNode Read File
    """
    bl_idname = 'LNWriteFileNode'
    bl_label = 'Write File'
    arm_section = 'file'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'File')
        self.add_input('ArmStringSocket', 'Content')

        self.add_output('ArmNodeSocketAction', 'Out')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement.Identity(self)
