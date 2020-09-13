from arm.logicnode.arm_nodes import *

class GetNameNode(ArmLogicTreeNode):
    """Get name node"""
    bl_idname = 'LNGetNameNode'
    bl_label = 'Get Name'
    arm_version = 1

    def init(self, context):
        super(GetNameNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('NodeSocketString', 'Name')

add_node(GetNameNode, category=PKG_AS_CATEGORY, section='props')
