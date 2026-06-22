from arm.logicnode.arm_nodes import *

class ArrayIndexNode(ArmLogicTreeNode):
    """Returns the array index of the given value."""
    bl_idname = 'LNArrayIndexNode'
    bl_label = 'Array Index'
    arm_version = 2

    def arm_init(self, context):
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('ArmDynamicSocket', 'Value')
        self.add_input('ArmIntSocket', 'From')

        self.add_output('ArmIntSocket', 'Index')

    def get_replacement_node(self, node_tree: bpy.types.NodeTree):
        if self.arm_version not in (0, 1):
            raise LookupError()
            
        return NodeReplacement.Identity(self)