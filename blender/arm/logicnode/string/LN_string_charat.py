from arm.logicnode.arm_nodes import *


class StringCharAtNode(ArmLogicTreeNode):
    """String CharAt"""
    bl_idname = 'LNStringCharAtNode'
    bl_label = 'String CharAt'
    bl_description = 'Returns the character at position index of the String. If the index is negative or exceeds the string.length, an empty String "" is returned.'
    arm_category = 'String'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmStringSocket', 'String')
        self.add_input('ArmIntSocket', 'Index')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmStringSocket', 'Char')
