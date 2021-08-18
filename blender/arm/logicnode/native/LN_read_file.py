from arm.logicnode.arm_nodes import *

class ReadFileNode(ArmLogicTreeNode):
    """Returns the content of the given file.

    @seeNode Write File"""
    bl_idname = 'LNReadFileNode'
    bl_label = 'Read File'
    arm_section = 'file'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'File')
        self.add_input('ArmBoolSocket', 'Use cache', default_value=1)

        self.add_output('ArmNodeSocketAction', 'Loaded')
        self.add_output('ArmStringSocket', 'String')
