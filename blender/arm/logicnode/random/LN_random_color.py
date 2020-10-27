from arm.logicnode.arm_nodes import *


class RandomColorNode(ArmLogicTreeNode):
    """Generates a random color."""
    bl_idname = 'LNRandomColorNode'
    bl_label = 'Random Color'
    arm_version = 1

    def init(self, context):
        super(RandomColorNode, self).init(context)
        self.add_output('NodeSocketColor', 'Color')
