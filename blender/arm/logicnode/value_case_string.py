import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CaseStringNode(Node, ArmLogicTreeNode):
    '''Converts strings's case node'''
    bl_idname = 'LNCaseStringNode'
    bl_label = 'Case String'
    bl_icon = 'CURVE_PATH'
    property0: EnumProperty(
        items = [('Upper Case', 'Upper Case', 'Upper Case'),
                 ('Lower Case', 'Lower Case', 'Lower Case'),
                 ],
        name='', default='Upper Case')
    
    def init(self, context):
        self.inputs.new('NodeSocketString', 'String')
        self.outputs.new('NodeSocketString', 'String')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(CaseStringNode, category='Value')