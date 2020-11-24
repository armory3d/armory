from arm.logicnode.arm_nodes import *

class ArrayLengthNode(ArmLogicTreeNode):
    """Returns the length of the given array."""
    bl_idname = 'LNArrayLengthNode'
    bl_label = 'Array Length'
    arm_version = 1

    def init(self, context):
        super(ArrayLengthNode, self).init(context)
        self.add_input('ArmNodeSocketArray', 'Array')

        self.add_output('NodeSocketInt', 'Length')
