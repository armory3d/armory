from arm.logicnode.arm_nodes import *

class ArrayInsertNode(ArmLogicTreeNode):
    """Inserts the value of the given array at the given index and increases the length of the array."""
    bl_idname = 'LNArrayInsertNode'
    bl_label = 'Array Insert'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('ArmIntSocket', 'Index')
        self.add_input('ArmDynamicSocket', 'Value')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketArray', 'Array')