from arm.logicnode.arm_nodes import *


class ArrayResizeNode(ArmLogicTreeNode):
    """Resize the array to the given length. For more details, please
    take a look at the documentation of `Array.resize()` in the
    [Haxe API](https://api.haxe.org/Array.html#resize).
    """
    bl_idname = 'LNArrayResizeNode'
    bl_label = 'Array Resize'
    arm_version = 1

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('ArmIntSocket', 'Length')

        self.add_output('ArmNodeSocketAction', 'Out')
