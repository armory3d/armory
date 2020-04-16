import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class OnCanvasElementNode(Node, ArmLogicTreeNode):
    '''On canvas element node'''
    bl_idname = 'LNOnCanvasElementNode'
    bl_label = 'On Canvas Element'
    bl_icon = 'CURVE_PATH'
    property0: EnumProperty(
        items = [('Down', 'Down', 'Down'),
                 ('Started', 'Started', 'Started'),
                 ('Released', 'Released', 'Released')],
        name='', default='Down')
    property1: EnumProperty(
        items = [('left', 'left', 'left'),
                 ('right', 'right', 'right'),
                 ('middle', 'middle', 'middle')],
        name='Mouse button', default='left')
    
    def init(self, context):
        self.inputs.new('NodeSocketString','Element')
        self.outputs.new('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
        layout.prop(self, 'property1')

add_node(OnCanvasElementNode, category='Input')
