from arm.logicnode.arm_nodes import *

class ArrayConcatNode(ArmLogicTreeNode):
    """Join arrays."""

    bl_idname = 'LNArrayConcatNode'
    bl_label = 'Array Concat'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('ArmNodeSocketArray', 'Array')

        self.add_output('ArmNodeSocketArray', 'Array')
