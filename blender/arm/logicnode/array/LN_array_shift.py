from arm.logicnode.arm_nodes import *

class ArrayShiftNode(ArmLogicTreeNode):
    """Use to remove the first element of an array.

    @see [Haxe API](https://api.haxe.org/Array.html#shift)"""
    bl_idname = 'LNArrayShiftNode'
    bl_label = 'Array Shift'
    arm_version = 1

    def init(self, context):
        super(ArrayShiftNode, self).init(context)
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_output('NodeSocketShader', 'Value')

add_node(ArrayShiftNode, category=PKG_AS_CATEGORY)
