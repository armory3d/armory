from arm.logicnode.arm_nodes import *

class ArrayIndexNode(ArmLogicTreeNode):
    """Returns the array index of the given value."""
    bl_idname = 'LNArrayIndexNode'
    bl_label = 'Array Index'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('ArmDynamicSocket', 'Value')

        self.add_output('ArmIntSocket', 'Index')
