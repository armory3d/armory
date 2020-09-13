from arm.logicnode.arm_nodes import *

class ArrayRemoveIndexNode(ArmLogicTreeNode):
    """Removes an element from an array given by its index."""
    bl_idname = 'LNArrayRemoveNode'
    bl_label = 'Array Remove By Index'
    arm_version = 1

    def init(self, context):
        super(ArrayRemoveIndexNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('NodeSocketInt', 'Index')
        self.add_output('ArmNodeSocketAction', 'Out')
        self.add_output('NodeSocketShader', 'Value')

add_node(ArrayRemoveIndexNode, category=PKG_AS_CATEGORY)
