from arm.logicnode.arm_nodes import *

class ArrayLengthNode(ArmLogicTreeNode):
    """Use to get the length of an array."""
    bl_idname = 'LNArrayLengthNode'
    bl_label = 'Array Length'
    arm_version = 1

    def init(self, context):
        super(ArrayLengthNode, self).init(context)
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_output('NodeSocketInt', 'Length')

add_node(ArrayLengthNode, category=PKG_AS_CATEGORY)
