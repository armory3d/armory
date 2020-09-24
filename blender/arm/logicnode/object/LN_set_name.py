from arm.logicnode.arm_nodes import *

class SetNameNode(ArmLogicTreeNode):
    """Use to set the name of an object."""
    bl_idname = 'LNSetNameNode'
    bl_label = 'Set Name'
    arm_version = 1

    def init(self, context):
        super(SetNameNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_input('NodeSocketString', 'Name')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(SetNameNode, category=PKG_AS_CATEGORY, section='props')
