import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class CaseStringNode(ArmLogicTreeNode):
    '''Converts strings's case node'''
    bl_idname = 'LNCaseStringNode'
    bl_label = 'Case String'
    bl_icon = 'NONE'
    property0: EnumProperty(
        items = [('Upper Case', 'Upper Case', 'Upper Case'),
                 ('Lower Case', 'Lower Case', 'Lower Case'),
                 ],
        name='', default='Upper Case')

    def init(self, context):
        self.add_input('NodeSocketString', 'String')
        self.add_output('NodeSocketString', 'String')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')

add_node(CaseStringNode, category=MODULE_AS_CATEGORY)
