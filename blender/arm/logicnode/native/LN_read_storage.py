from arm.logicnode.arm_nodes import *

class ReadStorageNode(ArmLogicTreeNode):
    """Use to read a stored content.

    @seeNode Write Storage"""
    bl_idname = 'LNReadStorageNode'
    bl_label = 'Read Storage'
    arm_version = 1

    def init(self, context):
        super(ReadStorageNode, self).init(context)
        self.add_input('NodeSocketString', 'Key')
        self.add_input('NodeSocketString', 'Default')
        self.add_output('NodeSocketShader', 'Value')

add_node(ReadStorageNode, category=PKG_AS_CATEGORY, section='file')
