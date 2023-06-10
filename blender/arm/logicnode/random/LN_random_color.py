from arm.logicnode.arm_nodes import *


class RandomColorNode(ArmLogicTreeNode):
    """Generates a random color."""
    bl_idname = 'LNRandomColorNode'
    bl_label = 'Random Color'
    arm_version = 1

    def arm_init(self, context):
        self.add_output('ArmColorSocket', 'Color')
