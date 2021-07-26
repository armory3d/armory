from arm.logicnode.arm_nodes import *

class ArrayGetNode(ArmLogicTreeNode):
    """Returns the value of the given array at the given index."""
    bl_idname = 'LNArrayGetNode'
    bl_label = 'Array Get'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('ArmIntSocket', 'Index')

        self.add_output('ArmDynamicSocket', 'Value')
