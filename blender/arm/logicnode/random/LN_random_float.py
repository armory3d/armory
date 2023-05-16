from arm.logicnode.arm_nodes import *


class RandomFloatNode(ArmLogicTreeNode):
    """Generates a random float."""
    bl_idname = 'LNRandomFloatNode'
    bl_label = 'Random Float'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmFloatSocket', 'Min')
        self.add_input('ArmFloatSocket', 'Max', default_value=1.0)
        # self.add_input('ArmIntSocket', 'Seed')
        self.add_output('ArmFloatSocket', 'Float')
