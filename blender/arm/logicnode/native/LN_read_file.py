from arm.logicnode.arm_nodes import *

class ReadFileNode(ArmLogicTreeNode):
    """Returns the content of the given file.

    @seeNode Write File"""
    bl_idname = 'LNReadFileNode'
    bl_label = 'Read File'
    arm_section = 'file'
    arm_version = 1

    def init(self, context):
        super(ReadFileNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'File')
        self.add_input('NodeSocketBool', 'Use cache', default_value=1)
        self.add_output('ArmNodeSocketAction', 'Loaded')
        self.add_output('NodeSocketString', 'String')
