from arm.logicnode.arm_nodes import *

class SetNameNode(ArmLogicTreeNode):
    """Set name node"""
    bl_idname = 'LNSetNameNode'
    bl_label = 'Set Name'

    def init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketString', 'Name')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetNameNode, category=PKG_AS_CATEGORY, section='props')
