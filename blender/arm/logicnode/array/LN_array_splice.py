from arm.logicnode.arm_nodes import *

class ArraySpliceNode(ArmLogicTreeNode):
    """TO DO. Search for haxe array splice."""
    bl_idname = 'LNArraySpliceNode'
    bl_label = 'Array Splice'
    arm_version = 1

    def init(self, context):
        super(ArraySpliceNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('NodeSocketInt', 'Index')
        self.add_input('NodeSocketInt', 'Length')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(ArraySpliceNode, category=PKG_AS_CATEGORY)
