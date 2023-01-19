from arm.logicnode.arm_nodes import *

class ArrayReverseNode(ArmLogicTreeNode):
    """Reverse the items order of the array."""

    bl_idname = 'LNArrayReverseNode'
    bl_label = 'Array Reverse'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketArray', 'Array')

        self.add_output('ArmNodeSocketArray', 'Array')
