from arm.logicnode.arm_nodes import *

class StringNode(ArmLogicTreeNode):
    """Stores the given string as a variable."""
    bl_idname = 'LNStringNode'
    bl_label = 'String'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmStringSocket', 'String In')

        self.add_output('ArmStringSocket', 'String Out', is_var=True)
