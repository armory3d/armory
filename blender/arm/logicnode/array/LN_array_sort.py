from arm.logicnode.arm_nodes import *

class ArraySortNode(ArmLogicTreeNode):
    """Sort the items order of the array by ascending or descending."""

    bl_idname = 'LNArraySortNode'
    bl_label = 'Array Sort'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('ArmBoolSocket', 'Descending', default_value=False)

        self.add_output('ArmNodeSocketArray', 'Array')
