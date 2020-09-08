import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class VectorMixNode(ArmLogicTreeNode):
    """Vector mix node"""
    bl_idname = 'LNVectorMixNode'
    bl_label = 'Vector Mix'
    bl_icon = 'NONE'
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
        self.add_input('NodeSocketFloat', 'Factor', default_value=0.0)
        self.add_input('NodeSocketVector', 'Vector1', default_value=[0.0, 0.0, 0.0])
        self.add_input('NodeSocketVector', 'Vector2', default_value=[1.0, 1.0, 1.0])
        self.add_output('NodeSocketVector', 'Vector')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property2_')
        layout.prop(self, 'property0')
        if self.property0 != 'Linear':
            layout.prop(self, 'property1')

add_node(VectorMixNode, category=MODULE_AS_CATEGORY, section='vector')
