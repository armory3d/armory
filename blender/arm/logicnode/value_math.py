import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class MathNode(Node, ArmLogicTreeNode):
    '''Math node'''
    bl_idname = 'LNMathNode'
    bl_label = 'Math'
    bl_icon = 'CURVE_PATH'
    property0: EnumProperty(
        items = [('Add', 'Add', 'Add'),
                 ('Multiply', 'Multiply', 'Multiply'),
        		 ('Sine', 'Sine', 'Sine'),
                 ('Cosine', 'Cosine', 'Cosine'),
                 ('Max', 'Maximum', 'Max'),
                 ('Min', 'Minimum', 'Min'),
                 ('Abs', 'Absolute', 'Abs'),

                 ('Subtract', 'Subtract', 'Subtract'),
                 ('Divide', 'Divide', 'Divide'),
                 ('Tangent', 'Tangent', 'Tangent'),
                 ('Arcsine', 'Arcsine', 'Arcsine'),
                 ('Arccosine', 'Arccosine', 'Arccosine'),
                 ('Arctangent', 'Arctangent', 'Arctangent'),
                 ('Power', 'Power', 'Power'),
                 ('Logarithm', 'Logarithm', 'Logarithm'),
                 ('Round', 'Round', 'Round'),
                 ('Less Than', 'Less Than', 'Less Than'),
                 ('Greater Than', 'Greater Than', 'Greater Than'),
                 ('Modulo', 'Modulo', 'Modulo'),
                 ('Arctan2', 'Arctan2', 'Arctan2'),
                 ('Floor', 'Floor', 'Floor'),
                 ('Ceil', 'Ceil', 'Ceil'),
                 ('Fract', 'Fract', 'Fract'),
                 ('Square Root', 'Square Root', 'Square Root'),
                 ],
        name='', default='Add')
    
    @property
    def property1(self):
        return 'true' if self.property1_ else 'false'

    property1_: BoolProperty(name='Clamp', default=False)

    def init(self, context):
        self.inputs.new('NodeSocketFloat', 'Value')
        self.inputs[-1].default_value = 0.5
        self.inputs.new('NodeSocketFloat', 'Value')
        self.inputs[-1].default_value = 0.5
        self.outputs.new('NodeSocketFloat', 'Value')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property1_')
        layout.prop(self, 'property0')

add_node(MathNode, category='Value')
