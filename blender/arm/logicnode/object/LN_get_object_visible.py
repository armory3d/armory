from arm.logicnode.arm_nodes import *

class GetVisibleNode(ArmLogicTreeNode):
    """Returns whether the given object or its visual components are
    visible.

    @seeNode Set Object Visible"""
    bl_idname = 'LNGetVisibleNode'
    bl_label = 'Get Object Visible'
    arm_section = 'props'
    arm_version = 1

    def init(self, context):
        super(GetVisibleNode, self).init(context)
        self.add_input('ArmNodeSocketObject', 'Object')
        self.add_output('NodeSocketBool', 'Is Object Visible')
        self.add_output('NodeSocketBool', 'Is Mesh Visible')
        self.add_output('NodeSocketBool', 'Is Shadow Visible')
