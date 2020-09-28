from arm.logicnode.arm_nodes import *

class ReadJsonNode(ArmLogicTreeNode):
    """Get the content of a JSON file.

    @seeNode Write JSON"""
    bl_idname = 'LNReadJsonNode'
    bl_label = 'Read JSON'
    arm_version = 1

    def init(self, context):
        super(ReadJsonNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('NodeSocketString', 'File')
        self.add_input('NodeSocketBool', 'Use cache', default_value=1)
        self.add_output('ArmNodeSocketAction', 'Loaded')
        self.add_output('NodeSocketShader', 'Dynamic')

add_node(ReadJsonNode, category=PKG_AS_CATEGORY, section='file')
