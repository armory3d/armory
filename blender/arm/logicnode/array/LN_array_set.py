from arm.logicnode.arm_nodes import *

class ArraySetNode(ArmLogicTreeNode):
    """Sets the value of the given array at the given index."""
    bl_idname = 'LNArraySetNode'
    bl_label = 'Array Set'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('ArmIntSocket', 'Index')
        self.add_input('ArmDynamicSocket', 'Value')

        self.add_output('ArmNodeSocketAction', 'Out')
