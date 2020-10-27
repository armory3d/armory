from arm.logicnode.arm_nodes import *

class WriteStorageNode(ArmLogicTreeNode):
    """Writes the given content in the given key.

    @seeNode Read Storage"""
    bl_idname = 'LNWriteStorageNode'
    bl_label = 'Write Storage'
    arm_section = 'file'
    arm_version = 1

    def init(self, context):
        super(WriteStorageNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Key')
        self.add_input('NodeSocketShader', 'Value')
        self.add_output('ArmNodeSocketAction', 'Out')
