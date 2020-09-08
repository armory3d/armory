import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class MatrixMathNode(ArmLogicTreeNode):
    '''Matrix math node'''
    bl_idname = 'LNMatrixMathNode'
    bl_label = 'Matrix Math'
    bl_icon = 'NONE'
    property0: EnumProperty(
        items = [('Multiply', 'Multiply', 'Multiply')],
        name='', default='Multiply')

    def init(self, context):
        self.add_input('NodeSocketShader', 'Matrix')
        self.add_input('NodeSocketShader', 'Matrix')
        self.add_output('NodeSocketShader', 'Matrix')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(MatrixMathNode, category=MODULE_AS_CATEGORY, section='matrix')
