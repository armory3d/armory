from arm.logicnode.arm_nodes import *

class ReadStorageNode(ArmLogicTreeNode):
    """ReadStorage node"""
    bl_idname = 'LNReadStorageNode'
    bl_label = 'Read Storage'

    def init(self, context):
        self.add_input('NodeSocketString', 'Key')
        self.add_input('NodeSocketString', 'Default')
        self.add_output('NodeSocketShader', 'Value')

add_node(ReadStorageNode, category=MODULE_AS_CATEGORY, section='file')
