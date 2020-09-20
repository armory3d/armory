from arm.logicnode.arm_nodes import *

class MatrixMathNode(ArmLogicTreeNode):
    """Matrix math node"""
    bl_idname = 'LNMatrixMathNode'
    bl_label = 'Matrix Math'
    arm_version = 1
    property0: EnumProperty(
        items = [('Multiply', 'Multiply', 'Multiply')],
        name='', default='Multiply')

    def init(self, context):
        super(MatrixMathNode, self).init(context)
        self.add_input('NodeSocketShader', 'Matrix 1')
        self.add_input('NodeSocketShader', 'Matrix 2')
        self.add_output('NodeSocketShader', 'Result')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(MatrixMathNode, category=PKG_AS_CATEGORY, section='matrix')
