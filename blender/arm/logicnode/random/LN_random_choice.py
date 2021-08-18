from arm.logicnode.arm_nodes import *


class RandomChoiceNode(ArmLogicTreeNode):
    """Choose a random value from a given array."""
    bl_idname = 'LNRandomChoiceNode'
    bl_label = 'Random Choice'
    arm_version = 1

    def arm_init(self, context):

        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_output('ArmDynamicSocket', 'Value')
