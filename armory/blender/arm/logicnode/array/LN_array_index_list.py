from arm.logicnode.arm_nodes import *

class ArrayIndexNode(ArmLogicTreeNode):
    """Returns the array index list of the given value as an array."""
    bl_idname = 'LNArrayIndexListNode'
    bl_label = 'Array Index List'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('ArmDynamicSocket', 'Value')

        self.add_output('ArmNodeSocketArray', 'Array')