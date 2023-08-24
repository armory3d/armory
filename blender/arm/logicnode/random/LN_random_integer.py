from arm.logicnode.arm_nodes import *


class RandomIntegerNode(ArmLogicTreeNode):
    """Generates a random integer."""
    bl_idname = 'LNRandomIntegerNode'
    bl_label = 'Random Integer'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmIntSocket', 'Min')
        self.add_input('ArmIntSocket', 'Max', default_value=2)
        self.add_output('ArmIntSocket', 'Int')
