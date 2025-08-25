from arm.logicnode.arm_nodes import *

class ArraySpliceNode(ArmLogicTreeNode):
    """Removes the given amount of elements from the given array and returns it.

    @see [Haxe API](https://api.haxe.org/Array.html#splice)"""
    bl_idname = 'LNArraySpliceNode'
    bl_label = 'Array Splice'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('ArmIntSocket', 'Index')
        self.add_input('ArmIntSocket', 'Length')

        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('ArmNodeSocketArray', 'Array')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()
            
        return NodeReplacement.Identity(self)
