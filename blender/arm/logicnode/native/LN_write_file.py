from arm.logicnode.arm_nodes import *

class WriteFileNode(ArmLogicTreeNode):
    """Write File node"""
    bl_idname = 'LNWriteFileNode'
    bl_label = 'Write File'
    bl_icon = 'NONE'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'File')
        self.add_input('NodeSocketString', 'String')

add_node(WriteFileNode, category=MODULE_AS_CATEGORY, section='file')
