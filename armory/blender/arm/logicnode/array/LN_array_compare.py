from arm.logicnode.arm_nodes import *

class ArrayCompareNode(ArmLogicTreeNode):
    """Compare arrays."""

    bl_idname = 'LNArrayCompareNode'
    bl_label = 'Array Compare'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('ArmNodeSocketArray', 'Array')

        self.add_output('ArmBoolSocket', 'Compare')

