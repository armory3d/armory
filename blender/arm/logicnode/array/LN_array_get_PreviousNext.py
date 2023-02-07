from arm.logicnode.arm_nodes import *

class ArrayGetPreviousNextNode(ArmLogicTreeNode):
    """Returns the previous or next value to be retrieve by looping the array according to the boolean condition."""
    bl_idname = 'LNArrayGetPreviousNextNode'
    bl_label = 'Array Get Previous/Next'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('ArmBoolSocket', 'Previous: 0 / Next: 1')

        self.add_output('ArmDynamicSocket', 'Value')
