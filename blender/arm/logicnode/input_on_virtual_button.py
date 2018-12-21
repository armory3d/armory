import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class OnVirtualButtonNode(Node, ArmLogicTreeNode):
    '''On virtual button node'''
    bl_idname = 'LNOnVirtualButtonNode'
    bl_label = 'On Virtual Button'
    bl_icon = 'CURVE_PATH'
    property0: EnumProperty(
        items = [('Down', 'Down', 'Down'),
                 ('Started', 'Started', 'Started'),
                 ('Released', 'Released', 'Released')],
        name='', default='Started')
    property1: StringProperty(name='', default='button')
    
    def init(self, context):
        self.outputs.new('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
        layout.prop(self, 'property1')

add_node(OnVirtualButtonNode, category='Input')
