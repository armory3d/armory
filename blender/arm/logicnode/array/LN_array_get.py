from arm.logicnode.arm_nodes import *

class ArrayGetNode(ArmLogicTreeNode):
    """Returns the value of the given array at the given index."""
    bl_idname = 'LNArrayGetNode'
    bl_label = 'Array Get'
    arm_version = 1

    def init(self, context):
        super(ArrayGetNode, self).init(context)
        self.add_input('ArmNodeSocketArray', 'Array')
        self.add_input('NodeSocketInt', 'Index')
        self.add_output('NodeSocketShader', 'Value')
