import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class ContainsStringNode(Node, ArmLogicTreeNode):
    '''Contains string node'''
    bl_idname = 'LNContainsStringNode'
    bl_label = 'Contains String'
    bl_icon = 'CURVE_PATH'
    property0: EnumProperty(
        items = [('Contains', 'Contains', 'Contains'),
                 ('Starts With', 'Starts With', 'Starts With'),
                 ('Ends With', 'Ends With', 'Ends With'),
                 ],
        name='', default='Contains')
    
    def init(self, context):
        self.inputs.new('NodeSocketString', 'String')
        self.inputs.new('NodeSocketString', 'Find')
        self.outputs.new('NodeSocketBool', 'Bool')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(ContainsStringNode, category='Value')
