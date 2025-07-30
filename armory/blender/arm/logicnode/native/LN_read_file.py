from arm.logicnode.arm_nodes import *


class ReadFileNode(ArmLogicTreeNode):
    """Reads the given file and returns its content.

    @input File: the asset name of the file as used by Kha.
    @input Use cache: if unchecked, re-read the file from disk every
        time the node is executed. Otherwise, cache the file after the
        first read and return the cached content.

    @output Loaded: activated after the file has been read.
    @output Not Loaded: If the file doesn't exist the output is activated.
    @output Content: the content of the file.

    @seeNode Write File
    """
    bl_idname = 'LNReadFileNode'
    bl_label = 'Read File'
    arm_section = 'file'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'File')
        self.add_input('ArmBoolSocket', 'Use cache', default_value=True)

        self.add_output('ArmNodeSocketAction', 'Loaded')
        self.add_output('ArmNodeSocketAction', 'Not loaded')
        self.add_output('ArmStringSocket', 'Content')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()

        return NodeReplacement.Identity(self)
