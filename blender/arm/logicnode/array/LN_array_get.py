from arm.logicnode.arm_nodes import *

class ArrayGetNode(ArmLogicTreeNode):
    """Get the value of an array at the specified index."""
    bl_idname = 'LNArrayGetNode'
    bl_label = 'Array Get'
    arm_version = 1

    def init(self, context):
        super(ArrayGetNode, self).init(context)
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('NodeSocketInt', 'Index')
        self.add_output('NodeSocketShader', 'Value')

add_node(ArrayGetNode, category=PKG_AS_CATEGORY)
