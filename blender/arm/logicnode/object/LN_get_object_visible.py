from arm.logicnode.arm_nodes import *

class GetVisibleNode(ArmLogicTreeNode):
    """Returns whether the given object or its visual components are
    visible.

    @seeNode Set Object Visible"""
    bl_idname = 'LNGetVisibleNode'
    bl_label = 'Get Object Visible'
    arm_section = 'props'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketObject', 'Object')

        self.add_output('ArmBoolSocket', 'Is Object Visible')
        self.add_output('ArmBoolSocket', 'Is Mesh Visible')
        self.add_output('ArmBoolSocket', 'Is Shadow Visible')
