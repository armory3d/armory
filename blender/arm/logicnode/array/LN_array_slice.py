from arm.logicnode.arm_nodes import *

class ArraySliceNode(ArmLogicTreeNode):
    """Creates a shallow copy of the given array in the specified range.

    @see [Haxe API](https://api.haxe.org/Array.html#slice)"""
    bl_idname = 'LNArraySliceNode'
    bl_label = 'Array Slice'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('ArmIntSocket', 'Index')
        self.add_input('ArmIntSocket', 'End')

        self.add_output('ArmNodeSocketArray', 'Array')
