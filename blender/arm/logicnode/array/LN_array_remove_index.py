from arm.logicnode.arm_nodes import *

class ArrayRemoveIndexNode(ArmLogicTreeNode):
    """Removes the element from the given array by its index.

    @seeNode Array Remove By Value"""
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
