import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class MixNode(Node, ArmLogicTreeNode):
    '''Mix node'''
    bl_idname = 'LNMixNode'
    bl_label = 'Mix'
    bl_icon = 'CURVE_PATH'
    property0: EnumProperty(
        items = [('Linear', 'Linear', 'Linear'),
                 ('Sine', 'Sine', 'Sine'),
                 ('Quad', 'Quad', 'Quad'),
                 ('Cubic', 'Cubic', 'Cubic'),
                 ('Quart', 'Quart', 'Quart'),
                 ('Quint', 'Quint', 'Quint'),
                 ('Expo', 'Expo', 'Expo'),
                 ('Circ', 'Circ', 'Circ'),
                 ('Back', 'Back', 'Back'),
                 ],
        name='', default='Linear')
    property1: EnumProperty(
        items = [('In', 'In', 'In'),
                 ('Out', 'Out', 'Out'),
                 ('InOut', 'InOut', 'InOut'),
                 ],
        name='', default='Out')

    @property
    def property2(self):
        return 'true' if self.property2_ else 'false'

    property2_: BoolProperty(name='Clamp', default=False)

    def init(self, context):
        self.inputs.new('NodeSocketFloat', 'Factor')
        self.inputs[-1].default_value = 0.0
        self.inputs.new('NodeSocketFloat', 'Value1')
        self.inputs[-1].default_value = 0.0
        self.inputs.new('NodeSocketFloat', 'Value2')
        self.inputs[-1].default_value = 1.0
        self.outputs.new('NodeSocketFloat', 'Value')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property2_')
        layout.prop(self, 'property0')
        layout.prop(self, 'property1')

add_node(MixNode, category='Value')
