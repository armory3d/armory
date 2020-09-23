from arm.logicnode.arm_nodes import *

class WriteJsonNode(ArmLogicTreeNode):
    """Use to write the content of a JSON file."""
    bl_idname = 'LNWriteJsonNode'
    bl_label = 'Write JSON'
    arm_version = 1

    def init(self, context):
        super(WriteJsonNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'File')
        self.add_input('NodeSocketShader', 'Dynamic')

add_node(WriteJsonNode, category=PKG_AS_CATEGORY, section='file')
