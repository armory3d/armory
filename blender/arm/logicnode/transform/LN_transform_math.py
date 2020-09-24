from arm.logicnode.arm_nodes import *

class TransformMathNode(ArmLogicTreeNode):
    """Use to operate transform values."""
    bl_idname = 'LNTransformMathNode'
    bl_label = 'Transform Math'
    arm_version = 1

    def init(self, context):
        super(TransformMathNode, self).init(context)
        self.add_input('NodeSocketShader', 'Transform 1')
        self.add_input('NodeSocketShader', 'Transform 2')
        self.add_output('NodeSocketShader', 'Result')

add_node(TransformMathNode, category=PKG_AS_CATEGORY)
