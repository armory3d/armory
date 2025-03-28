from arm.logicnode.arm_nodes import *


class ArrayLoopNode(ArmLogicTreeNode):
    """Loops through each item of the given array."""
    bl_idname = 'LNArrayLoopNode'
    bl_label = 'Array Loop'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketArray', 'Array')

        self.add_output('ArmNodeSocketAction', 'Loop')
        self.add_output('ArmDynamicSocket', 'Value')
        self.add_output('ArmIntSocket', 'Index')
        self.add_output('ArmNodeSocketAction', 'Done')
