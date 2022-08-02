from arm.logicnode.arm_nodes import *

class ParseFloatNode(ArmLogicTreeNode):
    """Returns the floats that are in the given string."""
    bl_idname = 'LNParseFloatNode'
    bl_label = 'Parse Float'
    arm_section = 'parse'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmFloatSocket', 'Float')

        self.add_input('ArmStringSocket', 'String')
