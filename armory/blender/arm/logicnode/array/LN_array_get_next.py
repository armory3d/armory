from arm.logicnode.arm_nodes import *

class ArrayGetNextNode(ArmLogicTreeNode):
    """Returns the next value to be retrieve by looping the array."""
    bl_idname = 'LNArrayGetNextNode'
    bl_label = 'Array Get Next'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketArray', 'Array')

        self.add_output('ArmDynamicSocket', 'Value')
