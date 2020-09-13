from arm.logicnode.arm_nodes import *

class TransformMathNode(ArmLogicTreeNode):
    """Transform math node"""
    bl_idname = 'LNTransformMathNode'
    bl_label = 'Transform Math'
    arm_version = 1

    def init(self, context):
        super(TransformMathNode, self).init(context)
        self.add_input('NodeSocketShader', 'Transform')
        self.add_input('NodeSocketShader', 'Transform')
        self.add_output('NodeSocketShader', 'Transform')

add_node(TransformMathNode, category=PKG_AS_CATEGORY)
