from arm.logicnode.arm_nodes import *


class RandomStringNode(ArmLogicTreeNode):
    """Generates a random string based on a provided characters list."""
    bl_idname = 'LNRandomStringNode'
    bl_label = 'Random String'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmIntSocket', 'Length')
        self.add_input('ArmStringSocket', 'Characters')
        self.add_output('ArmStringSocket', 'String')
