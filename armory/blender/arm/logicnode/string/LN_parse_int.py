from arm.logicnode.arm_nodes import *

class ParseIntNode(ArmLogicTreeNode):
    """Returns the Ints that are in the given string."""
    bl_idname = 'LNParseIntNode'
    bl_label = 'Parse Int'
    arm_section = 'parse'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmIntSocket', 'Int')

        self.add_input('ArmStringSocket', 'String')
