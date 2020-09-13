from arm.logicnode.arm_nodes import *

class WriteStorageNode(ArmLogicTreeNode):
    """WriteStorage node"""
    bl_idname = 'LNWriteStorageNode'
    bl_label = 'Write Storage'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'Key')
        self.add_input('NodeSocketShader', 'Value')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(WriteStorageNode, category=PKG_AS_CATEGORY, section='file')
