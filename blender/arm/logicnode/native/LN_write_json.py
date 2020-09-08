from arm.logicnode.arm_nodes import *

class WriteJsonNode(ArmLogicTreeNode):
    """Write JSON node"""
    bl_idname = 'LNWriteJsonNode'
    bl_label = 'Write JSON'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'File')
        self.add_input('NodeSocketShader', 'Dynamic')

add_node(WriteJsonNode, category=MODULE_AS_CATEGORY, section='file')
