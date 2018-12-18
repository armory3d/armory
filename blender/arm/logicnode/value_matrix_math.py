import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class MatrixMathNode(Node, ArmLogicTreeNode):
    '''Matrix math node'''
    bl_idname = 'LNMatrixMathNode'
    bl_label = 'Matrix Math'
    bl_icon = 'CURVE_PATH'
    property0: EnumProperty(
        items = [('Multiply', 'Multiply', 'Multiply')],
        name='', default='Multiply')
    
    def init(self, context):
        self.inputs.new('NodeSocketShader', 'Matrix')
        self.inputs.new('NodeSocketShader', 'Matrix')
        self.outputs.new('NodeSocketShader', 'Matrix')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(MatrixMathNode, category='Value')
