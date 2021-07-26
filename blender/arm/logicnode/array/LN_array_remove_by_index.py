from arm.logicnode.arm_nodes import *

class ArrayRemoveIndexNode(ArmLogicTreeNode):
    """Removes the element from the given array by its index.

    @seeNode Array Remove by Value"""
    bl_idname = 'LNArrayRemoveNode'
    bl_label = 'Array Remove by Index'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('ArmIntSocket', 'Index')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmDynamicSocket', 'Value')
