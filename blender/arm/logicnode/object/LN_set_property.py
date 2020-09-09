from arm.logicnode.arm_nodes import *

class SetPropertyNode(ArmLogicTreeNode):
    """Set property node"""
    bl_idname = 'LNSetPropertyNode'
    bl_label = 'Set Property'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketString', 'Property')
        self.add_input('NodeSocketShader', 'Value')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetPropertyNode, category=PKG_AS_CATEGORY, section='props')
