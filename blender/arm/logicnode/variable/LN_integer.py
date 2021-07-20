from arm.logicnode.arm_nodes import *

class IntegerNode(ArmLogicTreeNode):
    """Stores the given integer (a whole number) as a variable."""
    bl_idname = 'LNIntegerNode'
    bl_label = 'Integer'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmIntSocket', 'Int In')
        self.add_output('ArmIntSocket', 'Int Out', is_var=True)
