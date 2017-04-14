import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class MathNode(Node, ArmLogicTreeNode):
    '''Math node'''
    bl_idname = 'LNMathNode'
    bl_label = 'Math'
    bl_icon = 'CURVE_PATH'
    property0 = EnumProperty(
        items = [('Add', 'Add', 'Add'),
                 ('Multiply', 'Multiply', 'Multiply'),
        		 ('Sine', 'Sine', 'Sine'),
                 ('Cosine', 'Cosine', 'Cosine'),
                 ('Max', 'Max', 'Max'),
                 ('Min', 'Min', 'Min'),
                 ('Abs', 'Abs', 'Abs')],
        name='', default='Add')
    
    def init(self, context):
        self.inputs.new('NodeSocketFloat', 'Value')
        self.inputs.new('NodeSocketFloat', 'Value')
        self.outputs.new('NodeSocketFloat', 'Value')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(MathNode, category='Value')
