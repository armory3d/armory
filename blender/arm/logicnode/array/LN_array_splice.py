from arm.logicnode.arm_nodes import *

class ArraySpliceNode(ArmLogicTreeNode):
    """Removes the given amount of elements from the given array.

    @see [Haxe API](https://api.haxe.org/Array.html#splice)"""
    bl_idname = 'LNArraySpliceNode'
    bl_label = 'Array Splice'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('ArmIntSocket', 'Index')
        self.add_input('ArmIntSocket', 'Length')

        self.add_output('ArmNodeSocketAction', 'Out')
