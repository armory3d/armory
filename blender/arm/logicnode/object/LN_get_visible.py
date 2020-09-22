from arm.logicnode.arm_nodes import *

class GetVisibleNode(ArmLogicTreeNode):
    """Get Visible node"""
    bl_idname = 'LNGetVisibleNode'
    bl_label = 'Get Visible'
    arm_version = 1

    def init(self, context):
        super(GetVisibleNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('NodeSocketBool', 'Is Object Visible')
        self.add_output('NodeSocketBool', 'Is Mesh Visible')
        self.add_output('NodeSocketBool', 'Is Shadow Visible')

add_node(GetVisibleNode, category=PKG_AS_CATEGORY, section='props')
