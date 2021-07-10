from arm.logicnode.arm_nodes import *

class WriteFileNode(ArmLogicTreeNode):
    """Writes the given content in the given file.

    @seeNode Read File"""
    bl_idname = 'LNWriteFileNode'
    bl_label = 'Write File'
    arm_section = 'file'
    arm_version = 1

    def init(self, context):
        super(WriteFileNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'File')
        self.add_input('ArmStringSocket', 'String')
