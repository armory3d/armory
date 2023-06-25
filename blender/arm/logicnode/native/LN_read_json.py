from arm.logicnode.arm_nodes import *


class ReadJsonNode(ArmLogicTreeNode):
    """Reads the given JSON file and returns its content.

    @input File: the asset name of the file as used by Kha.
    @input Use cache: if unchecked, re-read the file from disk every
        time the node is executed. Otherwise, cache the file after the
        first read and return the cached content.

    @output Loaded: activated after the file has been read. If the file
        doesn't exist, the output is not activated.
    @output Dynamic: the content of the file.

    @seeNode Write JSON
    """
    bl_idname = 'LNReadJsonNode'
    bl_label = 'Read JSON'
    arm_section = 'file'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'File')
        self.add_input('ArmBoolSocket', 'Use cache', default_value=1)

        self.add_output('ArmNodeSocketAction', 'Loaded')
        self.add_output('ArmDynamicSocket', 'Dynamic')
