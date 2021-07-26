from arm.logicnode.arm_nodes import *

class SplitStringNode(ArmLogicTreeNode):
    """Splits the given string."""
    bl_idname = 'LNSplitStringNode'
    bl_label = 'Split String'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmNodeSocketArray', 'Array')

        self.add_input('ArmStringSocket', 'String')
        self.add_input('ArmStringSocket', 'Split')
