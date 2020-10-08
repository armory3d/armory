from arm.logicnode.arm_nodes import *

class ArraySetNode(ArmLogicTreeNode):
    """Sets the value of the given array at the given index."""
    bl_idname = 'LNArraySetNode'
    bl_label = 'Array Set'
    arm_version = 1

    def init(self, context):
        super(ArraySetNode, self).init(context)
        self.add_input('ArmNodeSocketAction', 'In')
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('NodeSocketInt', 'Index')
        self.add_input('NodeSocketShader', 'Value')
        self.add_output('ArmNodeSocketAction', 'Out')

add_node(ArraySetNode, category=PKG_AS_CATEGORY)
